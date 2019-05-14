"""
Support for Nibe components.

For more details about this component, please refer to the documentation
https://home-assistant.io/components/sensor.nibe/
"""
import logging

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import CONF_NAME, CONF_SENSORS, TEMP_CELSIUS
from homeassistant.helpers.entity import Entity

from custom_components.nibeuplink import (CONF_SYSTEM_ID, CONF_SYSTEM_NAME,
                                          CONF_SYSTEM_PARAMETER, DOMAIN)

# Python libraries/modules that you would normally install for your component.
REQUIREMENTS = []

# Other HASS components that should be setup before the platform is loaded.
DEPENDENCIES = ['nibeuplink']

_LOGGER = logging.getLogger(__name__)

# Validation of the user's configuration
SENSOR_SCHEMA = vol.Schema({
    vol.Required(CONF_NAME): cv.string,
    vol.Required(CONF_SYSTEM_NAME): cv.string,
    vol.Required(CONF_SYSTEM_ID): cv.string,
    vol.Required(CONF_SYSTEM_PARAMETER): cv.string
})

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_SENSORS): vol.Schema({cv.slug: SENSOR_SCHEMA}),
})


async def async_setup_platform(hass, config, async_add_entities,
                               discovery_info=None):
    # Setup your platform inside of the event loop
    """Set up the Elero cover platform."""
    sensors = []
    sensors_conf = config.get(CONF_SENSORS, {})
    for sensor_name, sensor_conf in sensors_conf.items():
        sensors.append(NIBESensor(
            hass,
            sensor_conf.get(CONF_NAME),
            sensor_conf.get(CONF_SYSTEM_NAME),
            sensor_conf.get(CONF_SYSTEM_ID),
            sensor_conf.get(CONF_SYSTEM_PARAMETER),
        ))
    async_add_entities(sensors, True)


class NIBESensor(Entity):
    """Representation of a Sensor in a NIBE System."""

    def __init__(self, hass, name, system_name, system_id, system_parameter):
        """Initialize the sensor."""
        self.hass = hass
        self._name = name
        self._system_name = system_name
        self._system_id = system_id
        self._system_parameter = system_parameter
        self._state = None
        self._device_class = None
        self.state_attr = None

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def device_class(self):
        """Return the device class."""
        return self._device_class

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def should_poll(self):
        """Return False because entity pushes its state."""
        return True

    @property
    def available(self):
        """Return True if entity is available."""
        return True if self.state_attr else False

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return self.state_attr['unit']

    @property
    def device_state_attributes(self):
        """Return device state attributes."""
        return self.state_attr

    async def async_update(self):
        """Fetch new state data for the sensor.

        This is the only method that should fetch new data for Home Assistant.
        """
        # sensor_data = self.hass.data[DOMAIN].get_systems()
        # _LOGGER.debug("ISTI: %s", sensor_data)
        data = await self.hass.data[DOMAIN].async_get_parameters(
            self._system_id, self._system_parameter)
        self.state_attr = data[0]

        self._state = self.state_attr['displayValue']
