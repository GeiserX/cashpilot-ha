# Usage

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

Each service gets a device named after it, and its entities take that name: the Honeygain device shows "Honeygain Balance" as `sensor.honeygain_balance`. In the table, `<service>` is the service name in lower case with spaces and punctuation turned into `_`.

| Entity | Type | Description |
|--------|------|-------------|
| `sensor.<service>_balance` | Sensor | Service balance (USD) |
| `sensor.<service>_health_score` | Sensor | Health score (0-100%) |
| `sensor.<service>_uptime` | Sensor | Uptime percentage |
| `sensor.<service>_cpu` | Sensor | CPU usage (diagnostic) |
| `sensor.<service>_memory` | Sensor | Memory usage in MB (diagnostic) |
| `binary_sensor.<service>_running` | Binary Sensor | Whether the container is running |
| `switch.<service>` | Switch | Start / stop the service |
| `button.<service>_restart` | Button | Restart the service |
