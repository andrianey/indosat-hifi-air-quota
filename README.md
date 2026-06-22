# Indosat HiFi Air — Home Assistant Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)

A HACS custom integration for Home Assistant that monitors your **Indosat HiFi Air** internet quota.

## Features

Exposes **7 sensors** per account:

| Sensor | Description |
|---|---|
| Remaining Quota | Current remaining data (GB) |
| Total Quota | Total allocated data for the period (GB) |
| Used Quota | Data already consumed (GB) |
| Remaining Days | Days left until package expiry |
| Expiry Date | Date when the current package expires |
| Account Status | Active / Inactive status of the account |
| Package Name | Name of the subscribed plan |

## Requirements

- Home Assistant 2024.1 or later
- HACS installed (or manual install)
- An active Indosat HiFi Air subscription
- Your registered phone number

## Installation via HACS

### Method 1: Custom Repository

1. In Home Assistant, go to **HACS → Integrations**.
2. Click the three-dot menu → **Custom repositories**.
3. Add `https://github.com/andrianey/indosat-hifi-air-quota` as an **Integration**.
4. Search for **Indosat HiFi Air** and install it.
5. Restart Home Assistant.

### Method 2: GitHub Release

1. Go to the [Releases](https://github.com/andrianey/indosat-hifi-air-quota/releases) page.
2. Download the latest `indosat_hifi_air.zip`.
3. Extract to `config/custom_components/indosat_hifi_air/`.
4. Restart Home Assistant.

## Configuration

1. Go to **Settings → Devices & Services → Add Integration**.
2. Search for **Indosat HiFi Air**.
3. Enter:
   - **Phone Number** — your HiFi Air number (`0858...`, `62858...`, or `858...`)
   - **Display Name** — custom name (e.g. "Living Room Router")
   - **Update Interval** — how often to poll (30 / 60 / 180 / 360 minutes)
4. Click **Submit**.

After setup, you can change the update interval at any time via **Configure** on the integration card.

## Sensors

After setup, the following entities are created (named with your custom display name):

- `sensor.indosat_hifi_air_<name>_remaining_quota`
- `sensor.indosat_hifi_air_<name>_total_quota`
- `sensor.indosat_hifi_air_<name>_used_quota`
- `sensor.indosat_hifi_air_<name>_remaining_days`
- `sensor.indosat_hifi_air_<name>_expiry_date`
- `sensor.indosat_hifi_air_<name>_account_status`
- `sensor.indosat_hifi_air_<name>_package_name`

The entity IDs are stable and based on the normalized MSISDN internally, so renaming the display name won't break automations.

## License

MIT
