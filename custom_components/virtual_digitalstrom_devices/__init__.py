"""The Virtual digitalSTROM Devices integration."""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import DOMAIN, STORAGE_FILE, STATE_LISTENER_MAPPINGS_FILE
from .device_storage import DeviceStorage
from .state_listener_manager import StateListenerManager
from .device_listener_configurator import DeviceListenerConfigurator
from .property_updater import PropertyUpdater

_LOGGER = logging.getLogger(__name__)

# List of platforms to support
PLATFORMS: list[Platform] = []


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Virtual digitalSTROM Devices from a config entry."""
    _LOGGER.debug("Setting up Virtual digitalSTROM Devices integration")
    
    # Initialize device storage
    storage_path = Path(hass.config.path(STORAGE_FILE))
    device_storage = DeviceStorage(storage_path)
    
    # Initialize state listener manager
    listener_mappings_path = Path(hass.config.path(STATE_LISTENER_MAPPINGS_FILE))
    state_listener_manager = StateListenerManager(hass, listener_mappings_path)
    
    # Initialize device listener configurator
    device_configurator = DeviceListenerConfigurator(hass, state_listener_manager)
    
    # Initialize property updater
    property_updater = PropertyUpdater(hass, device_storage)
    
    # Load existing listener mappings
    await state_listener_manager.async_load_mappings()
    
    # Auto-configure listeners for all existing devices
    devices = device_storage.get_all_devices()
    _LOGGER.info("Auto-configuring listeners for %d existing devices", len(devices))
    
    total_listeners = 0
    for device in devices:
        try:
            count = await device_configurator.async_configure_from_device_attributes(device)
            total_listeners += count
        except Exception as err:
            _LOGGER.error(
                "Error configuring listeners for device %s: %s",
                device.name,
                err,
                exc_info=True,
            )
    
    if total_listeners > 0:
        _LOGGER.info("Auto-configured %d state listeners for existing devices", total_listeners)
        # Save the auto-generated mappings
        await state_listener_manager.async_save_mappings()
    
    # Store an instance of the integration data
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "device_storage": device_storage,
        "state_listener_manager": state_listener_manager,
        "device_configurator": device_configurator,
        "property_updater": property_updater,
    }
    
    # Forward the setup to the platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    _LOGGER.info("Virtual digitalSTROM Devices integration setup complete")
    
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    _LOGGER.debug("Unloading Virtual digitalSTROM Devices integration")
    
    # Stop all state listeners
    state_listener_manager = hass.data[DOMAIN][entry.entry_id].get("state_listener_manager")
    if state_listener_manager:
        await state_listener_manager.async_stop_all()
        # Save listener mappings before unloading
        await state_listener_manager.async_save_mappings()
        _LOGGER.info("Saved listener mappings and stopped all listeners")
    
    # Unload platforms
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)
    
    return unload_ok
