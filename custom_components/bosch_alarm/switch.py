""" Support for Bosch Alarm Panel outputs as switches """

from __future__ import annotations

import logging

from homeassistant.components.switch import SwitchEntity

from .const import DOMAIN
from .device import device_info_from_panel

_LOGGER = logging.getLogger(__name__)

class PanelOutputEntity(SwitchEntity):
    def __init__(self, id, output, device_info, data):
        self._observer = output.status_observer
        self._attr_has_entity_name = True
        self._attr_device_info = device_info
        self._panel = data.panel
        self._data = data
        self._id = id
        self._output = output

    @property
    def unique_id(self): return f'{self._data.unique_id}_output_{self._id}'

    @property
    def should_poll(self): return False

    async def async_added_to_hass(self):
        self._observer.attach(self.schedule_update_ha_state)

    async def async_will_remove_from_hass(self):
        self._observer.detach(self.schedule_update_ha_state)

    @property
    def is_on(self) -> bool:
        return self._output.is_active()

    @property
    def name(self): return self._output.name

    async def async_turn_on(self, **kwargs):
        await self._panel.set_output_active(self._id)

    async def async_turn_off(self, **kwargs):
        await self._panel.set_output_inactive(self._id)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up switch entities for outputs"""

    data = hass.data[DOMAIN][config_entry.entry_id]
    panel = data.panel

    def setup():
        device_info = device_info_from_panel(data)
        async_add_entities(
            PanelOutputEntity(id, output, device_info, data)
                for (id, output) in panel.outputs.items())

    data.register_entity_setup(setup)

