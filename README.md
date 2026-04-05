<p align="center">
  <img src="docs/images/banner.svg" alt="CashPilot for Home Assistant banner" width="900"/>
</p>

# CashPilot for Home Assistant

[![HACS](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![GitHub Release](https://img.shields.io/github/v/release/GeiserX/cashpilot-ha)](https://github.com/GeiserX/cashpilot-ha/releases)
[![GitHub Stars](https://img.shields.io/github/stars/GeiserX/cashpilot-ha)](https://github.com/GeiserX/cashpilot-ha)
[![License: GPL-3.0](https://img.shields.io/github/license/GeiserX/cashpilot-ha)](LICENSE)

A Home Assistant custom integration that monitors your [CashPilot](https://github.com/GeiserX/CashPilot) passive income dashboard. Track earnings, service health, and manage containers directly from HA.

## Features

- **Earnings overview** -- total, today, and monthly earnings as sensors
- **Per-service monitoring** -- balance, health score, uptime, CPU, and memory for every deployed service
- **Service control** -- start, stop, and restart individual services via switches and buttons
- **Fleet overview** -- online workers and running containers (if fleet mode is configured)
- **Manual collection** -- trigger an earnings refresh on demand

## Prerequisites

- A running [CashPilot](https://github.com/GeiserX/CashPilot) instance reachable from Home Assistant
- CashPilot login credentials (username and password)
- Home Assistant 2024.1.0 or later

## Installation

### HACS (recommended)

1. Open HACS in Home Assistant
2. Click the three dots in the top right and select **Custom repositories**
3. Add `https://github.com/GeiserX/cashpilot-ha` with category **Integration**
4. Search for "CashPilot" and install it
5. Restart Home Assistant

### Manual

1. Copy the `custom_components/cashpilot/` directory into your HA `config/custom_components/` folder
2. Restart Home Assistant

## Configuration

1. Go to **Settings > Devices & Services > Add Integration**
2. Search for **CashPilot**
3. Enter the URL of your CashPilot instance (e.g., `http://cashpilot:8080`)
4. Enter your CashPilot username and password
5. Click **Submit**

## Entities

### Dashboard device

| Entity | Type | Description |
|--------|------|-------------|
| `sensor.cashpilot_total_earnings` | Sensor | Lifetime cumulative earnings (USD) |
| `sensor.cashpilot_today_earnings` | Sensor | Earnings for today (USD) |
| `sensor.cashpilot_month_earnings` | Sensor | Earnings for the current month (USD) |
| `sensor.cashpilot_active_services` | Sensor | Number of active services |
| `button.cashpilot_collect_earnings` | Button | Trigger manual earnings collection |

### Fleet sensors (only if fleet mode is configured)

| Entity | Type | Description |
|--------|------|-------------|
| `sensor.cashpilot_fleet_workers_online` | Sensor | Online fleet workers |
| `sensor.cashpilot_fleet_containers_running` | Sensor | Running fleet containers |

### Per-service devices (one device per deployed service)

| Entity | Type | Description |
|--------|------|-------------|
| `sensor.cashpilot_{slug}_balance` | Sensor | Service balance (USD) |
| `sensor.cashpilot_{slug}_health_score` | Sensor | Health score (0-100%) |
| `sensor.cashpilot_{slug}_uptime` | Sensor | Uptime percentage |
| `sensor.cashpilot_{slug}_cpu` | Sensor | CPU usage (diagnostic) |
| `sensor.cashpilot_{slug}_memory` | Sensor | Memory usage in MB (diagnostic) |
| `binary_sensor.cashpilot_{slug}_running` | Binary Sensor | Whether the container is running |
| `switch.cashpilot_{slug}` | Switch | Start / stop the service |
| `button.cashpilot_{slug}_restart` | Button | Restart the service |

## Example Automations

### Daily earnings notification

```yaml
automation:
  - alias: "CashPilot daily earnings summary"
    trigger:
      - platform: time
        at: "22:00:00"
    action:
      - service: notify.mobile_app_phone
        data:
          title: "CashPilot Earnings"
          message: >
            Today: ${{ states('sensor.cashpilot_today_earnings') }}
            Month: ${{ states('sensor.cashpilot_month_earnings') }}
            Total: ${{ states('sensor.cashpilot_total_earnings') }}
```

### Alert when a service goes down

```yaml
automation:
  - alias: "CashPilot service down alert"
    trigger:
      - platform: state
        entity_id: binary_sensor.cashpilot_honeygain_running
        to: "off"
        for:
          minutes: 10
    action:
      - service: notify.mobile_app_phone
        data:
          title: "CashPilot Alert"
          message: "Honeygain has been down for 10 minutes."
```

### Auto-restart unhealthy service

```yaml
automation:
  - alias: "CashPilot auto-restart low health"
    trigger:
      - platform: numeric_state
        entity_id: sensor.cashpilot_honeygain_health_score
        below: 50
        for:
          minutes: 15
    action:
      - service: button.press
        target:
          entity_id: button.cashpilot_honeygain_restart
```

## Polling interval

Data is refreshed every **5 minutes** by default. This is not user-configurable through the UI at this time.

## Links

- [CashPilot](https://github.com/GeiserX/CashPilot) -- the self-hosted passive income platform this integration connects to
- [Issue Tracker](https://github.com/GeiserX/cashpilot-ha/issues) -- report bugs or request features

## Other Home Assistant Integrations by GeiserX

- [duplicacy-ha](https://github.com/GeiserX/duplicacy-ha) — Backup status monitoring
- [genieacs-ha](https://github.com/GeiserX/genieacs-ha) — TR-069 router management sensors
- [pumperly-ha](https://github.com/GeiserX/pumperly-ha) — Fuel and EV charging price sensors

## License

[GPL-3.0](LICENSE)
