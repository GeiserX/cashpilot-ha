# Getting started

## Prerequisites

- A running [CashPilot](https://github.com/GeiserX/CashPilot) instance reachable from Home Assistant
- CashPilot login credentials (username and password)
- Home Assistant 2024.1.0 or later

## HACS (recommended)

1. Open HACS in Home Assistant
2. Click the three dots in the top right and select **Custom repositories**
3. Add `https://github.com/GeiserX/cashpilot-ha` with category **Integration**
4. Search for "CashPilot" and install it
5. Restart Home Assistant

## Manual

1. Copy the `custom_components/cashpilot/` directory into your HA `config/custom_components/` folder
2. Restart Home Assistant

## Configuration

1. Go to **Settings > Devices & Services > Add Integration**
2. Search for **CashPilot**
3. Enter the URL of your CashPilot instance (e.g., `http://cashpilot:8080`)
4. Enter your CashPilot username and password
5. Click **Submit**

## Polling interval

Data is refreshed every **5 minutes** by default. This is not user-configurable through the UI at this time.
