"""
Provides functionality to interact with NIBE systems.

For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/nibeuplink/
"""

__version__ = '1.2'

import asyncio
import json
import logging
import os

import aiohttp
import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant.exceptions import HomeAssistantError

# Python libraries/modules that you would normally install for your component.
REQUIREMENTS = []

# Other HASS components that should be setup before the platform is loaded.
DEPENDENCIES = []

_LOGGER = logging.getLogger(__name__)

# The domain of your component. Equal to the filename of your component.
DOMAIN = 'nibeuplink'

# Configs to the NIBE Uplink connection.
CONF_CLIENT_ID = 'client_id'
CONF_CLIENT_SECRET = 'client_secret'
CONF_REDIRECT_URL = 'redirect_url'
CONF_SCOPE = 'scope'
# Configs to the NIBE Uplink systems.
CONF_SYSTEMS = 'systems'
CONF_SYSTEM_NAME = 'system_name'
CONF_SYSTEM_ID = 'system_id'
CONF_SYSTEM_PARAMETER = 'system_parameter'
# Configs to NIBE API connection
CONF_API_AUTH_URL = 'api_auth_url'
CONF_API_FUNCTIONS_URL = 'api_functions_url'

# Default NIBE Uplink connection details.
DEFAULT_API_AUTH_URL = 'https://api.nibeuplink.com/oauth/token'
DEFAULT_API_FUNCTIONS_URL = 'https://api.nibeuplink.com/api/v1'
DEFAULT_AUTH_DATA_FILE = 'nibeuplink_auth_data.json'
DEFAULT_SCOPES = ['READSYSTEM', 'WRITESYSTEM']
DEFAULT_SESSION_HEADERS = {
    'Accept': 'application/json',
    'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8'
}

# Validation of the user's configuration.
CONFIG_SCHEMA = vol.Schema({
    DOMAIN: vol.Schema({
        vol.Required(CONF_CLIENT_ID): cv.string,
        vol.Required(CONF_CLIENT_SECRET): cv.string,
        vol.Required(CONF_REDIRECT_URL): cv.string,
        vol.Optional(CONF_SCOPE, default=[DEFAULT_SCOPES[0]]):
            vol.All(cv.ensure_list, [vol.In(DEFAULT_SCOPES)]),
        vol.Optional(CONF_API_AUTH_URL, default=DEFAULT_API_AUTH_URL):
            cv.string,
        vol.Optional(CONF_API_FUNCTIONS_URL,
                     default=DEFAULT_API_FUNCTIONS_URL):
            cv.string,
    }),
}, extra=vol.ALLOW_EXTRA)


async def async_setup(hass, config):
    # Setup your component inside of the event loop.
    try:
        conf = config.get(DOMAIN)
        nibeuplinkapi = NIBEUplinkAPI(
            hass,
            conf.get(CONF_CLIENT_ID),
            conf.get(CONF_CLIENT_SECRET),
            conf.get(CONF_REDIRECT_URL),
            conf.get(CONF_SCOPE),
            conf.get(CONF_API_AUTH_URL),
            conf.get(CONF_API_FUNCTIONS_URL),
            )

        await nibeuplinkapi.async_load_auth_data_from_file()
        hass.data[DOMAIN] = nibeuplinkapi

        # Return boolean to indicate that initialization was successfully.
        return True
    except (HomeAssistantError, KeyError) as err:
        _LOGGER.error("Error on NIBE API init: {}".format(err))
        # Return boolean to indicate that initialization was unsuccessfully.
        return False


def auth_data_refresher(func):
    """Refreshing the authorization data."""
    async def wrapper(*args, **kwargs):
        """ """
        while True:
            try:
                return await func(*args, **kwargs)
            except RequestError as e:
                if e.code == 401:
                    await args[0].async_refresh_authorization_data()
                else:
                    raise e
    return wrapper


class RequestError(Exception):
    """ """
    def __init__(self, code):
        _LOGGER.error("Request Error: '{}'".format(code))
        super(RequestError, self).__init__()
        self.code = code


class InvalidResponseError(Exception):
    """ """
    def __init__(self, code):
        _LOGGER.error("Invalid Response Error: '%s'", code)
        super(InvalidResponseError, self).__init__()
        self.code = code


class BearerAuthorization(aiohttp.BasicAuth):
    """A bearer token can use it to get access to the associated resources."""
    def __init__(self, access_token):
        self.access_token = access_token

    def encode(self):
        """Create a bearer playload."""
        return "Bearer {}".format(self.access_token)


class NIBEUplinkAPI():
    """The NIBE Uplink API is a RESTful api.

    API documentation: https://api.nibeuplink.com/docs/v1
    """
    def __init__(self, hass, client_id, client_secret, redirect_url, scope,
                 api_auth_url, api_functions_url):
        """Initialize a NIBE API client."""
        self.hass = hass
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_url = redirect_url
        self.scope = scope
        self.api_auth_url = api_auth_url
        self.api_functions_url = api_functions_url
        # hass.config.path(DEFAULT_AUTH_DATA_FILE)
        self.auth_data_file_path = os.path.join(
            os.path.dirname(__file__), DEFAULT_AUTH_DATA_FILE)
        self.access_token = None
        self.refresh_token = None

        self.asyncio_lock = asyncio.Lock()

        self.session = aiohttp.ClientSession(
            headers=DEFAULT_SESSION_HEADERS,
            auth=aiohttp.BasicAuth(self.client_id, self.client_secret)
        )

        _LOGGER.info("Nibe Uplink lib version: {}".format(__version__))

    def __load_auth_data_from_file(self):
        """Loading the authorization data from file."""
        try:
            with open(self.auth_data_file_path, 'r') as f:
                data = json.load(f)
                self.access_token = data['access_token']
                self.refresh_token = data['refresh_token']
        except (FileNotFoundError, ValueError, OSError, IOError) as err:
            self.access_token = None
            self.refresh_token = None
            _LOGGER.error(
                "Can't load authorization data from file: '{}'".format(err))

    async def async_load_auth_data_from_file(self):
        """Loading the authorization data from file."""
        await self.hass.async_add_job(self.__load_auth_data_from_file)

    def __save_auth_data_to_file(self, data):
        """Saving the authorization data into file."""
        try:
            with open(self.auth_data_file_path, 'w') as f:
                json.dump(data,
                          f,
                          indent=2)
        except (OSError, IOError) as err:
            _LOGGER.error(
                "Can't save authorization data into the '{}' file: '{}'."
                .format(self.auth_data_file_path, err))

    async def async_handle_auth_data(self, data):
        """Saving the authorization data into file."""
        try:
            self.access_token = data['access_token']
            self.refresh_token = data['refresh_token']
        except ValueError as err:
            _LOGGER.error(
                "Missing authorization data: '{}' '{}'".format(data, err))
        await self.hass.async_add_job(self.__save_auth_data_to_file, data)

    async def async_refresh_authorization_data(self):
        """Refresing the authorization data."""
        if not self.refresh_token:
            _LOGGER.error("Unable to refresh the authorization data "
                          "without refresh token.")
            return
        async with self.session.post(
            self.api_auth_url,
            data={'grant_type': 'refresh_token',
                  'refresh_token': self.refresh_token
                  }
        ) as response:
            if response.status != 200:
                raise RequestError(response.status)
            data = await response.json()
            if 'access_token' not in data or 'refresh_token' not in data:
                raise InvalidResponseError(response.status)
            await self.async_handle_auth_data(data)

    async def async_get_bearer_authorization(self):
        """Getting access to the associated resources."""
        return BearerAuthorization(self.access_token)

    @auth_data_refresher
    async def async_call_api_function(self, fun, *args, **kw):
        """Decorator is used to handle the errors."""
        # _LOGGER.debug("Calling NIBE API...")
        async with self.asyncio_lock:
            async with fun(*args,
                           auth=await self.async_get_bearer_authorization(),
                           **kw) as response:
                if response.status != 200:
                    raise RequestError(response.status)

                return response, await response.json()

    async def async_get_parameters(self, system_id, param_id):
        """
        Get parameter info and their value.
        Further description details:
        https://api.nibeuplink.com/docs/v1/Api/GET-api-v1-systems-
        systemId-parameters_parameterIds[0]_parameterIds[1]
        """
        # _LOGGER.debug('Getting parameters from a system...')
        response, data = await self.async_call_api_function(
            self.session.get,
            '{}/systems/{}/parameters'.format(
                self.api_functions_url, system_id),
            params={'parameterIds': param_id},
            headers={})
        # _LOGGER.debug('Systems: {}'.format(response))
        _LOGGER.debug('Systems: {}'.format(data))

        return data

    async def async_get_systems(self):
        """List the user's connected systems.

        The results are paged, please use the URI parameters
        to specify paging options.
        Further description details:
        https://api.nibeuplink.com/docs/v1/Api/GET-api-v1-
        systems_page_itemsPerPage
        """
        # _LOGGER.debug("Getting systems...")
        response, data = await self.async_call_api_function(
            self.session.get,
            '{}/{}'.format(self.api_functions_url, 'systems'))
        # _LOGGER.debug('Systems: {}'.format(response))
        # _LOGGER.debug('Systems: {}'.format(data))

        return data['objects']
