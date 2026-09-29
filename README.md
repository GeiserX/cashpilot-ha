<p align="center">
  <img src="docs/images/banner.svg" alt="CashPilot for Home Assistant" width="900"/>
</p>

# CashPilot for Home Assistant

[![GitHub Release](https://img.shields.io/github/v/release/GeiserX/cashpilot-ha)](https://github.com/GeiserX/cashpilot-ha/releases)
[![Tests](https://github.com/GeiserX/cashpilot-ha/actions/workflows/tests.yml/badge.svg)](https://github.com/GeiserX/cashpilot-ha/actions/workflows/tests.yml)
[![License](https://img.shields.io/github/license/GeiserX/cashpilot-ha)](LICENSE)
[![GitHub Stars](https://img.shields.io/github/stars/GeiserX/cashpilot-ha)](https://github.com/GeiserX/cashpilot-ha)
[![HACS](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)

A Home Assistant custom integration that monitors your [CashPilot](https://github.com/GeiserX/CashPilot) passive income dashboard. Track earnings, service health, and manage containers directly from HA.

## Features

- **Earnings overview** -- total, today, and monthly earnings as sensors
- **Per-service monitoring** -- balance, health score, uptime, CPU, and memory for every deployed service
- **Service control** -- start, stop, and restart individual services via switches and buttons
- **Fleet overview** -- online workers and running containers (if fleet mode is configured)
- **Manual collection** -- trigger an earnings refresh on demand
- **Refreshes every 5 minutes** -- see [polling interval](docs/getting-started.md#polling-interval)

## Quick start

1. In HACS, add `https://github.com/GeiserX/cashpilot-ha` as a custom repository with category **Integration**, install "CashPilot" and restart Home Assistant.
2. Go to **Settings > Devices & Services > Add Integration** and pick **CashPilot**.
3. Enter the URL of your CashPilot instance (e.g., `http://cashpilot:8080`) and your CashPilot username and password.

Needs Home Assistant 2024.1.0 or later and a [CashPilot](https://github.com/GeiserX/CashPilot) instance it can reach. Manual install and details are in [Getting started](docs/getting-started.md).

## Documentation

- [Getting started](docs/getting-started.md): prerequisites, HACS, manual install, configuration, polling interval
- [Usage](docs/usage.md): every sensor, switch and button, per device
- [Example automations](docs/automations.md): daily earnings notification, service down alert, auto-restart
- [Development](docs/development.md): tests and coverage
- [Related projects](docs/related.md): the CashPilot family and other Home Assistant integrations by GeiserX

Bugs and feature requests go to the [issue tracker](https://github.com/GeiserX/cashpilot-ha/issues).

## License

[GPL-3.0-or-later](LICENSE)
