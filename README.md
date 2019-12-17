[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)  [![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/) [![Donate](https://img.shields.io/badge/Donate-PayPal-green.svg)](https://www.paypal.me/cyberjunkynl/)

# TheThingsNetwork Gateway Sensor Component
This components reads statistics from a local The Things Network Gateway.

## Home-Assistant Custom Component
This is a Custom Component for Home-Assistant (https://home-assistant.io)

If you have [one of these](https://www.thethingsnetwork.org/docs/gateways/gateway/) (from [kickstarter](https://www.kickstarter.com/projects/419277966/the-things-network)) you can use this component to monitor all statistics from it.

:tada: I have one for sale, new in the box btw.

NOTE: I got the original code from a GitHub Gists, but cannot find the source any more to refer too.
If you happen to find it please tell me.

### Installation

- Copy directory `custom-components/ttn_gateway` to your `<config dir>/custom-components` directory.
- Configure with config below.
- Restart Home-Assistant.

### Usage
To use this component in your installation, add the following to your `configuration.yaml` file:

```yaml
# Example configuration.yaml entry

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
```

Configuration variables:

- **host** (*Required*): The IP address of the gateway you want to monitor.
- **scan_interval** (*Optional*): Number of seconds between polls. (default = 30)
- **resources** (*Required*): This section tells the component which values to monitor.

If you want them grouped instead of having the separate sensor badges, you can use this in your `groups.yaml`:

```yaml
# Example groups.yaml entry

TTN Gateway:
  - sensor.ttn_gw_hardware_version
  - sensor.ttn_gw_bootloader_version
  - sensor.ttn_gw_firmware_version
  - sensor.ttn_gw_uptime
  - sensor.ttn_gw_connected
  - sensor.ttn_gw_interface
  - sensor.ttn_gw_gateway
  - sensor.ttn_gw_ssid
  - sensor.ttn_gw_activation_locked
  - sensor.ttn_gw_configured
  - sensor.ttn_gw_region
  - sensor.ttn_gw_gateway_card
  - sensor.ttn_gw_broker_connected
  - sensor.ttn_gw_packets_up
  - sensor.ttn_gw_packets_down
  - sensor.ttn_gw_external_storage
```

### Screenshots

![alt text](https://github.com/cyberjunky/home-assistant-ttn_gateway/blob/master/screenshots/ttn-gw-badges.png?raw=true "Screenshot TTN Gateway Badges")
![alt text](https://github.com/cyberjunky/home-assistant-ttn_gateway/blob/master/screenshots/ttn-gw-status.png?raw=true "Screenshot TTN Gateway Status")

### Changes
* first release for hacs

### Donation
[![Donate](https://img.shields.io/badge/Donate-PayPal-green.svg)](https://www.paypal.me/cyberjunkynl/)
