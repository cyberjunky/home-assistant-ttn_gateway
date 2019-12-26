"""
Support for reading The Things Network Gateway status.

configuration.yaml

sensor:
  - platform: ttn_gateway
    host: IP_ADDRESS
    scan_interval: 10
    resources:
      - gateway
      - hwversion
      - blversion
      - fwversion
      - uptime
      - connected
      - interface
      - ssid
      - activationlocked
      - configured
      - region
      - gwcard
      - brokerconnected
      - packetsup
      - packetsdown
      - estore
"""
import logging
from datetime import timedelta
import requests
import voluptuous as vol

from homeassistant.components.sensor import PLATFORM_SCHEMA
import homeassistant.helpers.config_validation as cv
from homeassistant.const import (
    CONF_HOST, CONF_SCAN_INTERVAL, CONF_RESOURCES
    )
from homeassistant.util import Throttle
from homeassistant.helpers.entity import Entity


BASE_URL = 'http://{0}/status.cgi'
_LOGGER = logging.getLogger(__name__)

MIN_TIME_BETWEEN_UPDATES = timedelta(seconds=10)

SENSOR_PREFIX = 'TTN_GW '
SENSOR_TYPES = {
    'gateway': ['Gateway', '', 'mdi:router-wireless'],
    'hwversion': ['Hardware Version', '', 'mdi:file-document-box'],
    'blversion': ['Bootloader Version', '', 'mdi:file-document-box'],
    'fwversion': ['Firmware Version', '', 'mdi:file-document-box'],
    'uptime': ['Uptime', 'Sec.', 'mdi:timer-sand'],
    'connected': ['Connected', '', 'mdi:power-plug'],
    'interface': ['Interface', '', 'mdi:ethernet-cable'],
    'ssid': ['SSID', '', 'mdi:access-point'],
    'activationlocked': ['Activation Locked', '', 'mdi:lock-outline'],
    'configured': ['Configured', '', 'mdi:settings'],
    'region': ['Region', '', 'mdi:map-marker-radius'],
    'gwcard': ['Gateway Card', '', 'mdi:radio-tower'],
    'brokerconnected': ['Broker Connected', '', 'mdi:forum-outline'],
    'packetsup': ['Packets Up', 'pkts', 'mdi:gauge'],
    'packetsdown': ['Packets Down', 'pkts', 'mdi:gauge'],
    'estore': ['External Storage', '', 'mdi:sd'],
}

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_HOST): cv.string,
    vol.Required(CONF_RESOURCES, default=list(SENSOR_TYPES)):
        vol.All(cv.ensure_list, [vol.In(SENSOR_TYPES)]),
})

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Setup the TTN gateway sensors."""

    scan_interval = config.get(CONF_SCAN_INTERVAL)
    host = config.get(CONF_HOST)

    data = TTNGatewayData(host)

    try:
        await data.async_update()
    except ValueError as err:
        _LOGGER.error("Error while fetching data from the TTN Gateway: %s", err)
        return

    entities = []
    for resource in config[CONF_RESOURCES]:
        sensor_type = resource.lower()
        name = SENSOR_PREFIX + SENSOR_TYPES[resource][0]
        unit = SENSOR_TYPES[resource][1]
        icon = SENSOR_TYPES[resource][2]

        _LOGGER.debug("Adding TTN Gateway sensor: {}, {}, {}, {}".format(sensor_type, name, unit, icon))
        entities.append(TTNGatewaySensor(data, sensor_type, name, unit, icon))

    async_add_entities(entities, True)


# pylint: disable=abstract-method
class TTNGatewayData(object):
    """Handle TTN Gateway object and limit updates."""

    def __init__(self, host):
        """Initialize the data."""
        self._host = host
        self._data = None

    def _build_url(self):
        """Build the URL for the requests."""
        url = BASE_URL.format(self._host)
        _LOGGER.debug("TTN Gateway fetch URL: %s", url)
        return url

    @property
    def latest_data(self):
        """Return the latest data object."""
        if self._data:
            return self._data
        return None

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    async def async_update(self):
        """Update the data from the TTN Gateway."""
        try:
            self._data = requests.get(self._build_url(), timeout=10).json()
            _LOGGER.debug("TTN Gateway fetched data = %s", self._data)
        except (requests.exceptions.RequestException) as error:
            _LOGGER.error("Unable to connect to TTN Gateway: %s", error)
            self._data = None


class TTNGatewaySensor(Entity):
    """Representation of TTN gateway data."""

    def __init__(self, data, sensor_type, name, unit, icon):
        """Initialize the sensor."""
        self._data = data
        self._type = sensor_type
        self._name = name
        self._unit = unit
        self._icon = icon

        self._state = None

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def icon(self):
        """Icon to use in the frontend, if any."""
        return self._icon

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement of this entity, if any."""
        return self._unit

    @property
    def device_state_attributes(self):
        """Return the state attributes of this device."""
        attr = {}
        return attr

    async def async_update(self):
        """Get the latest data and use it to update our sensor state."""

        await self._data.async_update()
        if not self._data:
            _LOGGER.error("Didn't receive data from TTN Gateway")
            return

        status = self._data.latest_data

        if self._type == 'gateway':
            if 'gateway' in status:
                self._state = status["gateway"]

        elif self._type == 'hwversion':
            if 'hwversion' in status:
                self._state = status["hwversion"]

        elif self._type == 'blversion':
            if 'blversion' in status:
                self._state = status["blversion"]

        elif self._type == 'fwversion':
            if 'fwversion' in status:
                self._state = status["fwversion"]

        elif self._type == 'uptime':
            if 'uptime' in status:
                self._state = status["uptime"]

        elif self._type == 'connected':
            if 'connected' in status:
                self._state = status["connected"]

        elif self._type == 'interface':
            if 'interface' in status:
                self._state = status["interface"]

        elif self._type == 'ssid':
            if 'ssid' in status:
                self._state = status["ssid"]

        elif self._type == 'activationlocked':
            if 'activation_locked' in status:
                self._state = status["activation_locked"]

        elif self._type == 'configured':
            if 'configured' in status:
                self._state = status["configured"]

        elif self._type == 'region':
            if 'region' in status:
                self._state = status["region"]

        elif self._type == 'gwcard':
            if 'gwcard' in status:
                self._state = status["gwcard"]

        elif self._type == 'brokerconnected':
            if 'connbroker' in status:
                self._state = status["connbroker"]

        elif self._type == 'packetsup':
            if 'pup' in status:
                self._state = status["pup"]

        elif self._type == 'packetsdown':
            if 'pdown' in status:
                self._state = status["pdown"]

        elif self._type == 'estore':
            if 'estor' in status:
                self._state = status["estor"]

        _LOGGER.debug("Device: {} State: {}".format(self._type, self._state))