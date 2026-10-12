"""Switch platform for the CashPilot integration."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .api import CashPilotError
from .const import DATA_SERVICES, DOMAIN
from .coordinator import CashPilotConfigEntry, CashPilotCoordinator
from .entity import CashPilotServiceEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: CashPilotConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up CashPilot switch entities."""
    coordinator: CashPilotCoordinator = hass.data[DOMAIN][entry.entry_id]
    entry_id = entry.entry_id
    entities: list[SwitchEntity] = []

    services = coordinator.data.get(DATA_SERVICES, [])
    for svc in services:
        slug = svc.get("slug", "")
        name = svc.get("name", slug)
        if not slug:
            continue
        entities.append(
            CashPilotServiceSwitch(coordinator, entry_id, slug, name)
        )

    async_add_entities(entities)


class CashPilotServiceSwitch(CashPilotServiceEntity, SwitchEntity):
    """Switch to start/stop a service."""

    # The switch is the service's main feature, so it takes the device name
    # alone ("Wipter", switch.wipter) instead of a name of its own.
    _attr_name = None
    _attr_icon = "mdi:power"

    def __init__(
        self,
        coordinator: CashPilotCoordinator,
        entry_id: str,
        slug: str,
        service_name: str,
    ) -> None:
        super().__init__(coordinator, entry_id, slug, service_name)
        self._attr_unique_id = f"{entry_id}_{slug}_switch"

    @property
    def is_on(self) -> bool | None:
        for svc in self.coordinator.data.get(DATA_SERVICES, []):
            if svc.get("slug") == self._slug:
                return svc.get("container_status", "").lower() == "running"
        return None

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Start the service."""
        try:
            await self.coordinator.client.async_start_service(self._slug)
        except CashPilotError:
            _LOGGER.exception("Failed to start service %s", self._slug)
            return
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Stop the service."""
        try:
            await self.coordinator.client.async_stop_service(self._slug)
        except CashPilotError:
            _LOGGER.exception("Failed to stop service %s", self._slug)
            return
        await self.coordinator.async_request_refresh()
