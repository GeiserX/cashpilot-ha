# Entities

## Dashboard device

| Entity | Type | Description |
|--------|------|-------------|
| `sensor.cashpilot_total_earnings` | Sensor | Lifetime cumulative earnings (USD) |
| `sensor.cashpilot_today_earnings` | Sensor | Earnings for today (USD) |
| `sensor.cashpilot_month_earnings` | Sensor | Earnings for the current month (USD) |
| `sensor.cashpilot_active_services` | Sensor | Number of active services |
| `button.cashpilot_collect_earnings` | Button | Trigger manual earnings collection |

## Fleet sensors (only if fleet mode is configured)

| Entity | Type | Description |
|--------|------|-------------|
| `sensor.cashpilot_fleet_workers_online` | Sensor | Online fleet workers |
| `sensor.cashpilot_fleet_containers_running` | Sensor | Running fleet containers |

## Per-service devices (one device per deployed service)

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
