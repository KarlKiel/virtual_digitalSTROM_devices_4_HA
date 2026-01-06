"""The Virtual digitalSTROM Devices integration."""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr

from .const import DOMAIN, STORAGE_FILE, STATE_LISTENER_MAPPINGS_FILE, VDC_CONFIG_FILE, CONF_DSS_PORT
from .storage import DeviceStorage, PropertyUpdater, VdcManager
from .storage.state_restorer import restore_states_on_startup
from .listeners import StateListenerManager, DeviceListenerConfigurator

_LOGGER = logging.getLogger(__name__)

# List of platforms to support
PLATFORMS: list[Platform] = []


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Virtual digitalSTROM Devices from a config entry."""
    _LOGGER.debug("Setting up Virtual digitalSTROM Devices integration")
    
    # Get the integration directory path
    integration_dir = Path(__file__).parent
    _LOGGER.debug("Integration directory: %s", integration_dir)
    
    # Initialize vDC manager and create/update vDC entity
    vdc_config_path = integration_dir / VDC_CONFIG_FILE
    vdc_manager = VdcManager(vdc_config_path)
    
    # Get DSS port from config entry
    dss_port = entry.data.get(CONF_DSS_PORT, 8440)
    
    # Create or update vDC entity with specified properties
    vdc_config = vdc_manager.create_or_update_vdc(dss_port=dss_port)
    _LOGGER.info(
        "vDC entity initialized: dsUID=%s, name=%s, port=%d",
        vdc_config.get("dsUID"),
        vdc_config.get("name"),
        dss_port
    )
    
    # Register the vDC as a device (hub) in Home Assistant's device registry
    device_reg = dr.async_get(hass)
    vdc_device = device_reg.async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={(DOMAIN, vdc_config["dsUID"])},
        name=vdc_config.get("name", "Virtual digitalSTROM vDC"),
        manufacturer=vdc_config.get("vendorName", "KarlKiel"),
        model=vdc_config.get("model", "vDC"),
        sw_version=vdc_config.get("modelVersion", "1.0"),
    )
    _LOGGER.info("Registered vDC as hub device: %s", vdc_device.id)
    
    # Initialize device storage
    storage_path = integration_dir / STORAGE_FILE
    device_storage = DeviceStorage(storage_path)
    
    # Initialize state listener manager
    listener_mappings_path = integration_dir / STATE_LISTENER_MAPPINGS_FILE
    state_listener_manager = StateListenerManager(hass, listener_mappings_path)
    
    # Initialize device listener configurator
    device_configurator = DeviceListenerConfigurator(hass, state_listener_manager)
    
    # Initialize property updater
    property_updater = PropertyUpdater(hass, device_storage)
    
    # Restore persisted state values from YAML storage
    # This happens BEFORE listeners start tracking new changes
    _LOGGER.info("Restoring persisted state values from storage")
    restore_stats = await restore_states_on_startup(
        hass=hass,
        device_storage=device_storage,
        property_updater=property_updater,
        push_to_entities=False,  # Don't push to entities on startup (entities may not be ready)
    )
    
    if restore_stats["total_properties_restored"] > 0:
        _LOGGER.info(
            "Restored %d state properties across %d devices",
            restore_stats["total_properties_restored"],
            restore_stats["devices_with_state"],
        )
    else:
        _LOGGER.debug("No persisted state values found to restore")
    
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
        "vdc_manager": vdc_manager,
        "vdc_device_id": vdc_device.id,
        "vdc_dsuid": vdc_config["dsUID"],
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
