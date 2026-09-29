# Example automations

## Daily earnings notification

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

## Alert when a service goes down

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

## Auto-restart unhealthy service

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
