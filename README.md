# Indosat HiFi Air — Home Assistant Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)

A HACS custom integration for Home Assistant that monitors your **Indosat HiFi Air** (FTTH) internet quota.

## Features

Exposes **5 sensors** per account:

| Sensor | Description |
|---|---|
| Remaining Quota | Current remaining data (GB) |
| Total Quota | Total allocated data for the period (GB) |
| Expiry Date | Date when the current package expires |
| Account Status | Active / Inactive status of the account |
| Package Name | Name of the subscribed plan |

## Requirements

- Home Assistant 2024.1 or later
- HACS installed
- An active Indosat HiFi Air subscription
- Your registered phone number (MSISDN)

## Installation via HACS

1. In Home Assistant, go to **HACS → Integrations**.
2. Click the three-dot menu → **Custom repositories**.
3. Add `https://github.com/andrianey/indosat-hifi-air-quota` as an **Integration**.
4. Search for **Indosat HiFi Air** and install it.
5. Restart Home Assistant.

## Configuration

1. Go to **Settings → Devices & Services → Add Integration**.
2. Search for **Indosat HiFi Air**.
3. Enter your HiFi Air phone number (MSISDN, e.g. `085XXXXXXXXX`).
4. Click **Submit**.

The integration will poll the Indosat API every 30 minutes and update all sensors automatically.

## Sensors

After setup, the following entities are created (prefixed with your MSISDN):

- `sensor.indosat_hifi_air_<msisdn>_remaining_quota`
- `sensor.indosat_hifi_air_<msisdn>_total_quota`
- `sensor.indosat_hifi_air_<msisdn>_expiry_date`
- `sensor.indosat_hifi_air_<msisdn>_account_status`
- `sensor.indosat_hifi_air_<msisdn>_package_name`

## License

MIT
