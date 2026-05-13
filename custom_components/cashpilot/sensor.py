"""Sensor platform for the CashPilot integration."""

from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import EntityCategory, PERCENTAGE, UnitOfInformation
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DATA_FLEET, DATA_SERVICES, DATA_SUMMARY, DOMAIN
from .coordinator import CashPilotConfigEntry, CashPilotCoordinator
from .entity import CashPilotEntity, CashPilotServiceEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: CashPilotConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up CashPilot sensor entities."""
    coordinator: CashPilotCoordinator = hass.data[DOMAIN][entry.entry_id]
    entry_id = entry.entry_id
    entities: list[SensorEntity] = []

    # Dashboard sensors
    entities.extend(
        [
            CashPilotTotalEarningsSensor(coordinator, entry_id),
            CashPilotTodayEarningsSensor(coordinator, entry_id),
            CashPilotMonthEarningsSensor(coordinator, entry_id),
            CashPilotActiveServicesSensor(coordinator, entry_id),
        ]
    )

    # Fleet sensors (only if fleet data is available)
    fleet = coordinator.data.get(DATA_FLEET)
    if fleet:
        entities.extend(
            [
                CashPilotFleetWorkersSensor(coordinator, entry_id),
                CashPilotFleetContainersSensor(coordinator, entry_id),
            ]
        )

    # Per-service sensors
    known_slugs: set[str] = set()
    services = coordinator.data.get(DATA_SERVICES, [])
    for svc in services:
        slug = svc.get("slug", "")
        name = svc.get("name", slug)
        if not slug:
            continue
        known_slugs.add(slug)
        entities.extend(
            _create_service_sensors(coordinator, entry_id, slug, name)
        )

    async_add_entities(entities)

    # Register listener for dynamic service discovery
    def _handle_new_services() -> None:
        """Add entities for newly discovered services."""
        new_entities: list[SensorEntity] = []
        current_services = coordinator.data.get(DATA_SERVICES, [])
        for svc in current_services:
            slug = svc.get("slug", "")
            name = svc.get("name", slug)
            if not slug or slug in known_slugs:
                continue
            known_slugs.add(slug)
            new_entities.extend(
                _create_service_sensors(coordinator, entry_id, slug, name)
            )
        if new_entities:
            async_add_entities(new_entities)

    coordinator.async_add_listener(_handle_new_services)


def _create_service_sensors(
    coordinator: CashPilotCoordinator,
    entry_id: str,
    slug: str,
    name: str,
) -> list[SensorEntity]:
    """Create the set of sensors for a single service."""
    return [
        CashPilotServiceBalanceSensor(coordinator, entry_id, slug, name),
        CashPilotServiceHealthSensor(coordinator, entry_id, slug, name),
        CashPilotServiceUptimeSensor(coordinator, entry_id, slug, name),
        CashPilotServiceCpuSensor(coordinator, entry_id, slug, name),
        CashPilotServiceMemorySensor(coordinator, entry_id, slug, name),
    ]


# ---------------------------------------------------------------------------
# Dashboard sensors
# ---------------------------------------------------------------------------


class CashPilotTotalEarningsSensor(CashPilotEntity, SensorEntity):
    """Total lifetime earnings."""

    _attr_translation_key = "total_earnings"
    _attr_icon = "mdi:currency-usd"
    _attr_native_unit_of_measurement = "USD"
    _attr_state_class = SensorStateClass.TOTAL
    _attr_suggested_display_precision = 2

    def __init__(
        self, coordinator: CashPilotCoordinator, entry_id: str
    ) -> None:
        super().__init__(coordinator, entry_id)
        self._attr_unique_id = f"{entry_id}_total_earnings"

    @property
    def native_value(self) -> float | None:
        summary = self.coordinator.data.get(DATA_SUMMARY, {})
        return summary.get("total")


class CashPilotTodayEarningsSensor(CashPilotEntity, SensorEntity):
    """Earnings for today."""

    _attr_translation_key = "today_earnings"
    _attr_icon = "mdi:cash-plus"
    _attr_native_unit_of_measurement = "USD"
    _attr_state_class = SensorStateClass.TOTAL
    _attr_suggested_display_precision = 2

    def __init__(
        self, coordinator: CashPilotCoordinator, entry_id: str
    ) -> None:
        super().__init__(coordinator, entry_id)
        self._attr_unique_id = f"{entry_id}_today_earnings"

    @property
    def native_value(self) -> float | None:
        summary = self.coordinator.data.get(DATA_SUMMARY, {})
        return summary.get("today")

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        summary = self.coordinator.data.get(DATA_SUMMARY, {})
        change = summary.get("today_change")
        if change is not None:
            return {"change": change}
        return {}


class CashPilotMonthEarningsSensor(CashPilotEntity, SensorEntity):
    """Earnings for the current month."""

    _attr_translation_key = "month_earnings"
    _attr_icon = "mdi:calendar-month"
    _attr_native_unit_of_measurement = "USD"
    _attr_state_class = SensorStateClass.TOTAL
    _attr_suggested_display_precision = 2

    def __init__(
        self, coordinator: CashPilotCoordinator, entry_id: str
    ) -> None:
        super().__init__(coordinator, entry_id)
        self._attr_unique_id = f"{entry_id}_month_earnings"

    @property
    def native_value(self) -> float | None:
        summary = self.coordinator.data.get(DATA_SUMMARY, {})
        return summary.get("month")

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        summary = self.coordinator.data.get(DATA_SUMMARY, {})
        change = summary.get("month_change")
        if change is not None:
            return {"change": change}
        return {}


class CashPilotActiveServicesSensor(CashPilotEntity, SensorEntity):
    """Number of active services."""

    _attr_translation_key = "active_services"
    _attr_icon = "mdi:apps"
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(
        self, coordinator: CashPilotCoordinator, entry_id: str
    ) -> None:
        super().__init__(coordinator, entry_id)
        self._attr_unique_id = f"{entry_id}_active_services"

    @property
    def native_value(self) -> int | None:
        summary = self.coordinator.data.get(DATA_SUMMARY, {})
        return summary.get("active_services")


# ---------------------------------------------------------------------------
# Fleet sensors
# ---------------------------------------------------------------------------


class CashPilotFleetWorkersSensor(CashPilotEntity, SensorEntity):
    """Number of online fleet workers."""

    _attr_translation_key = "fleet_workers_online"
    _attr_icon = "mdi:server-network"
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(
        self, coordinator: CashPilotCoordinator, entry_id: str
    ) -> None:
        super().__init__(coordinator, entry_id)
        self._attr_unique_id = f"{entry_id}_fleet_workers_online"

    @property
    def native_value(self) -> int | None:
        fleet = self.coordinator.data.get(DATA_FLEET)
        if fleet is None:
            return None
        return fleet.get("online_workers")

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        fleet = self.coordinator.data.get(DATA_FLEET)
        if fleet is None:
            return {}
        total = fleet.get("total_workers")
        if total is not None:
            return {"total_workers": total}
        return {}


class CashPilotFleetContainersSensor(CashPilotEntity, SensorEntity):
    """Number of running fleet containers."""

    _attr_translation_key = "fleet_containers_running"
    _attr_icon = "mdi:docker"
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(
        self, coordinator: CashPilotCoordinator, entry_id: str
    ) -> None:
        super().__init__(coordinator, entry_id)
        self._attr_unique_id = f"{entry_id}_fleet_containers_running"

    @property
    def native_value(self) -> int | None:
        fleet = self.coordinator.data.get(DATA_FLEET)
        if fleet is None:
            return None
        return fleet.get("running_containers")

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        fleet = self.coordinator.data.get(DATA_FLEET)
        if fleet is None:
            return {}
        total = fleet.get("total_containers")
        if total is not None:
            return {"total_containers": total}
        return {}


# ---------------------------------------------------------------------------
# Per-service sensors
# ---------------------------------------------------------------------------


class CashPilotServiceBalanceSensor(CashPilotServiceEntity, SensorEntity):
    """Balance for a specific service."""

    _attr_translation_key = "service_balance"
    _attr_icon = "mdi:wallet"
    _attr_native_unit_of_measurement = "USD"
    _attr_state_class = SensorStateClass.TOTAL
    _attr_suggested_display_precision = 2

    def __init__(
        self,
        coordinator: CashPilotCoordinator,
        entry_id: str,
        slug: str,
        service_name: str,
    ) -> None:
        super().__init__(coordinator, entry_id, slug, service_name)
        self._attr_unique_id = f"{entry_id}_{slug}_balance"

    @property
    def native_value(self) -> float | None:
        for svc in self.coordinator.data.get(DATA_SERVICES, []):
            if svc.get("slug") == self._slug:
                return svc.get("balance")
        return None


class CashPilotServiceHealthSensor(CashPilotServiceEntity, SensorEntity):
    """Health score for a specific service (0-100)."""

    _attr_translation_key = "service_health_score"
    _attr_icon = "mdi:heart-pulse"
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_suggested_display_precision = 1

    def __init__(
        self,
        coordinator: CashPilotCoordinator,
        entry_id: str,
        slug: str,
        service_name: str,
    ) -> None:
        super().__init__(coordinator, entry_id, slug, service_name)
        self._attr_unique_id = f"{entry_id}_{slug}_health_score"

    @property
    def native_value(self) -> float | None:
        for svc in self.coordinator.data.get(DATA_SERVICES, []):
            if svc.get("slug") == self._slug:
                return svc.get("health_score")
        return None


class CashPilotServiceUptimeSensor(CashPilotServiceEntity, SensorEntity):
    """Uptime percentage for a specific service."""

    _attr_translation_key = "service_uptime"
    _attr_icon = "mdi:clock-check"
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_suggested_display_precision = 1

    def __init__(
        self,
        coordinator: CashPilotCoordinator,
        entry_id: str,
        slug: str,
        service_name: str,
    ) -> None:
        super().__init__(coordinator, entry_id, slug, service_name)
        self._attr_unique_id = f"{entry_id}_{slug}_uptime"

    @property
    def native_value(self) -> float | None:
        for svc in self.coordinator.data.get(DATA_SERVICES, []):
            if svc.get("slug") == self._slug:
                return svc.get("uptime_pct")
        return None


class CashPilotServiceCpuSensor(CashPilotServiceEntity, SensorEntity):
    """CPU usage for a specific service."""

    _attr_translation_key = "service_cpu"
    _attr_icon = "mdi:cpu-64-bit"
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_suggested_display_precision = 1

    def __init__(
        self,
        coordinator: CashPilotCoordinator,
        entry_id: str,
        slug: str,
        service_name: str,
    ) -> None:
        super().__init__(coordinator, entry_id, slug, service_name)
        self._attr_unique_id = f"{entry_id}_{slug}_cpu"

    @property
    def native_value(self) -> float | None:
        for svc in self.coordinator.data.get(DATA_SERVICES, []):
            if svc.get("slug") == self._slug:
                raw = svc.get("cpu")
                if raw is not None:
                    try:
                        return float(raw)
                    except (ValueError, TypeError):
                        return None
        return None


class CashPilotServiceMemorySensor(CashPilotServiceEntity, SensorEntity):
    """Memory usage for a specific service."""

    _attr_translation_key = "service_memory"
    _attr_icon = "mdi:memory"
    _attr_device_class = SensorDeviceClass.DATA_SIZE
    _attr_native_unit_of_measurement = UnitOfInformation.MEGABYTES
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_suggested_display_precision = 1

    def __init__(
        self,
        coordinator: CashPilotCoordinator,
        entry_id: str,
        slug: str,
        service_name: str,
    ) -> None:
        super().__init__(coordinator, entry_id, slug, service_name)
        self._attr_unique_id = f"{entry_id}_{slug}_memory"

    @property
    def native_value(self) -> float | None:
        for svc in self.coordinator.data.get(DATA_SERVICES, []):
            if svc.get("slug") == self._slug:
                raw = svc.get("memory", "")
                if isinstance(raw, (int, float)):
                    return float(raw)
                if isinstance(raw, str):
                    # Parse strings like "150.5 MB"
                    cleaned = raw.replace("MB", "").replace("mb", "").strip()
                    try:
                        return float(cleaned)
                    except (ValueError, TypeError):
                        return None
        return None
