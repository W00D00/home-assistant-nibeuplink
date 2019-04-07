"""
Provides functionality to interact with NIBE systems.

For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/nibeuplink/
"""
import logging
import os

import homeassistant.helpers.config_validation as cv
import voluptuous as vol

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
CONF_SYSTEMS = 'systems'
CONF_SYSTEM_NAME = 'system_name'
CONF_SYSTEM_ID = 'system_id'
CONF_SYSTEM_PARAMETER = 'system_parameter'
CONF_API_BASE_URL = 'api_base_url'
CONF_TOKEN_URL = 'token_url'

# Default NIBE Uplink connection details.
DEFAULT_API_BASE_URL = 'https://api.nibeuplink.com'
DEFAULT_TOKEN_URL = 'oauth/token'

# Validation of the user's configuration.
CONFIG_SCHEMA = vol.Schema({
    DOMAIN: vol.Schema({
        vol.Required(CONF_CLIENT_ID): cv.string,
        vol.Required(CONF_CLIENT_SECRET): cv.string,
        vol.Required(CONF_REDIRECT_URL): cv.string,
        vol.Required(CONF_API_BASE_URL, default=DEFAULT_API_BASE_URL):
            cv.string,
        vol.Required(CONF_TOKEN_URL, default=DEFAULT_TOKEN_URL):
            cv.string,
    }),
}, extra=vol.ALLOW_EXTRA)


def setup(hass, config):
    # Setup your component inside of the event loop.
    conf = config.get(DOMAIN)
    hass.data[DOMAIN] = NIBEUplinkAPI(conf.get(CONF_CLIENT_ID),
                                      conf.get(CONF_CLIENT_SECRET),
                                      conf.get(CONF_REDIRECT_URL),
                                      conf.get(CONF_API_BASE_URL),
                                      conf.get(CONF_TOKEN_URL),
                                      )
    # Return boolean to indicate that initialization was successfully.
    return True


class NIBEUplinkAPI():
    """API documentation: https://api.nibeuplink.com/docs/v1"""
    def __init__(self, client_id, client_secret, redirect_url,
                 api_base_url, token_url):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_url = redirect_url
        self.api_base_url = api_base_url
        self.token_url = token_url

        self.access_token = None
        self.refresh_token = None
        self.token_path = os.path.join(os.path.dirname(
            os.path.abspath(__file__)), 'token.txt')
