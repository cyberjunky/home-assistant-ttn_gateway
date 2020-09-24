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
import aiohttp
import asyncio
import async_timeout
import voluptuous as vol

from homeassistant.components.sensor import PLATFORM_SCHEMA
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.aiohttp_client import async_get_clientsession
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
    'hwversion': ['Hardware Version', '', 'mdi:file-document'],
    'blversion': ['Bootloader Version', '', 'mdi:file-document'],
    'fwversion': ['Firmware Version', '', 'mdi:file-document'],
    'uptime': ['Uptime', 'Sec.', 'mdi:timer-sand'],
    'connected': ['Connected', '', 'mdi:power-plug'],
    'interface': ['Interface', '', 'mdi:ethernet-cable'],
    'ssid': ['SSID', '', 'mdi:access-point'],
    'activationlocked': ['Activation Locked', '', 'mdi:lock-outline'],
    'configured': ['Configured', '', 'mdi:cog'],
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

    ttndata = TTNGatewayData(hass, host)
    await ttndata.async_update()

    entities = []
    for resource in config[CONF_RESOURCES]:
        sensor_type = resource.lower()
        name = SENSOR_PREFIX + SENSOR_TYPES[resource][0]
        unit = SENSOR_TYPES[resource][1]
        icon = SENSOR_TYPES[resource][2]

        _LOGGER.debug("Adding TTN Gateway sensor: {}, {}, {}, {}".format(name, sensor_type, unit, icon))
        entities.append(TTNGatewaySensor(ttndata, name, sensor_type, unit, icon))

    async_add_entities(entities, True)


# pylint: disable=abstract-method
class TTNGatewayData(object):
    """Handle TTN Gateway object and limit updates."""
    def __init__(self, hass, host):
        """Initialize the data."""
        self._hass = hass
        self._host = host

        self._url = BASE_URL.format(self._host)
        self._data = None

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    async def async_update(self):
        """Update the data from the TTN Gateway."""
        _LOGGER.debug(
                "Downloading data from TTN Gateway: %s", self._url
        )

        try:
            websession = async_get_clientsession(self._hass)
            with async_timeout.timeout(5):
                response = await websession.get(self._url)
            _LOGGER.debug(
                "Response status from TTN Gateway: %s", response.status
            )
        except (asyncio.TimeoutError, aiohttp.ClientError) as err:
            _LOGGER.error("Cannot connect to TTN Gateway: %s", err)
            self._data = None
            return
        except Exception as err:
            _LOGGER.error("Error downloading from TTN Gateway: %s", err)
            self._data = None
            return

        try:
            self._data = await response.json(content_type='text/html')
            _LOGGER.debug("Data received from TTN Gateway: %s", self._data)
        except Exception as err:
            _LOGGER.error("Cannot parse data from TTN Gateway: %s", err)
            self._data = None
            return

    @property
    def latest_data(self):
        """Return the latest data object."""
        if self._data:
            return self._data
        return None


class TTNGatewaySensor(Entity):
    """Representation of TTN gateway data."""

    def __init__(self, ttndata, name, sensor_type, unit, icon):
        """Initialize the sensor."""
        self._ttndata = ttndata
        self._name = name
        self._type = sensor_type
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

        await self._ttndata.async_update()
        ttnstatus = self._ttndata.latest_data

        if ttnstatus:
            if self._type == 'gateway':
                if 'gateway' in ttnstatus:
                    self._state = ttnstatus["gateway"]

            elif self._type == 'hwversion':
                if 'hwversion' in ttnstatus:
                    self._state = ttnstatus["hwversion"]

            elif self._type == 'blversion':
                if 'blversion' in ttnstatus:
                    self._state = ttnstatus["blversion"]

            elif self._type == 'fwversion':
                if 'fwversion' in ttnstatus:
                    self._state = ttnstatus["fwversion"]

            elif self._type == 'uptime':
                if 'uptime' in ttnstatus:
                    self._state = ttnstatus["uptime"]

            elif self._type == 'connected':
                if 'connected' in ttnstatus:
                    self._state = ttnstatus["connected"]

            elif self._type == 'interface':
                if 'interface' in ttnstatus:
                    self._state = ttnstatus["interface"]

            elif self._type == 'ssid':
                if 'ssid' in ttnstatus:
                    self._state = ttnstatus["ssid"]

            elif self._type == 'activationlocked':
                if 'activation_locked' in ttnstatus:
                    self._state = ttnstatus["activation_locked"]

            elif self._type == 'configured':
                if 'configured' in ttnstatus:
                    self._state = ttnstatus["configured"]

            elif self._type == 'region':
                if 'region' in ttnstatus:
                    self._state = ttnstatus["region"]

            elif self._type == 'gwcard':
                if 'gwcard' in ttnstatus:
                    self._state = ttnstatus["gwcard"]

            elif self._type == 'brokerconnected':
                if 'connbroker' in ttnstatus:
                    self._state = ttnstatus["connbroker"]

            elif self._type == 'packetsup':
                if 'pup' in ttnstatus:
                    self._state = ttnstatus["pup"]

            elif self._type == 'packetsdown':
                if 'pdown' in ttnstatus:
                    self._state = ttnstatus["pdown"]

            elif self._type == 'estore':
                if 'estor' in ttnstatus:
                    self._state = ttnstatus["estor"]

            _LOGGER.debug("Device: {} State: {}".format(self._type, self._state))
