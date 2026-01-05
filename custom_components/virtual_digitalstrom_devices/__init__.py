"""The Virtual digitalSTROM Devices integration."""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import DOMAIN, STORAGE_FILE
from .device_storage import DeviceStorage

_LOGGER = logging.getLogger(__name__)

# List of platforms to support
PLATFORMS: list[Platform] = []


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Virtual digitalSTROM Devices from a config entry."""
    _LOGGER.debug("Setting up Virtual digitalSTROM Devices integration")
    
    # Initialize device storage
    storage_path = Path(hass.config.path(STORAGE_FILE))
    device_storage = DeviceStorage(storage_path)
    
    # Store an instance of the integration data
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "device_storage": device_storage,
    }
    
    # Forward the setup to the platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    _LOGGER.debug("Unloading Virtual digitalSTROM Devices integration")
    
    # Unload platforms
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)
    
    return unload_ok
