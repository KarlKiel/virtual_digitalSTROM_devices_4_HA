"""The Virtual digitalSTROM Devices integration."""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import voluptuous as vol

from homeassistant.const import Platform, CONF_NAME
from homeassistant.core import HomeAssistant
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers import device_registry as dr

from .const import DOMAIN, STORAGE_FILE, STATE_LISTENER_MAPPINGS_FILE, VDC_CONFIG_FILE, CONF_DSS_PORT, DEFAULT_DSS_PORT, DEFAULT_NAME, DEFAULT_VENDOR
from .storage import DeviceStorage, PropertyUpdater, VdcManager
from .storage.state_restorer import restore_states_on_startup
from .listeners import StateListenerManager, DeviceListenerConfigurator

_LOGGER = logging.getLogger(__name__)

# List of platforms to support
PLATFORMS: list[Platform] = []

# Configuration schema for YAML
CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
                vol.Optional(CONF_DSS_PORT, default=DEFAULT_DSS_PORT): cv.port,
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)


async def async_setup(hass: HomeAssistant, config: dict[str, Any]) -> bool:
    """Set up the Virtual digitalSTROM Devices integration from YAML configuration."""
    if DOMAIN not in config:
        return True
    
    conf = config[DOMAIN]
    _LOGGER.debug("Setting up Virtual digitalSTROM Devices from YAML configuration")
    
    # Get the integration directory path
    integration_dir = Path(__file__).parent
    _LOGGER.debug("Integration directory: %s", integration_dir)
    
    # Initialize vDC manager and create/update vDC entity
    vdc_config_path = integration_dir / VDC_CONFIG_FILE
    vdc_manager = VdcManager(vdc_config_path)
    
    # Load vDC configuration in executor to avoid blocking I/O
    await hass.async_add_executor_job(vdc_manager.load)
    
    # Get DSS port from config
    dss_port = conf.get(CONF_DSS_PORT, DEFAULT_DSS_PORT)
    
    # Create or update vDC entity with specified properties (use executor to avoid blocking I/O)
    vdc_config = await hass.async_add_executor_job(vdc_manager.create_or_update_vdc, dss_port)
    _LOGGER.info(
        "vDC entity initialized: dsUID=%s, name=%s, port=%d",
        vdc_config.get("dsUID"),
        vdc_config.get("name"),
        dss_port
    )
    
    # Initialize device storage
    storage_path = integration_dir / STORAGE_FILE
    device_storage = DeviceStorage(storage_path)
    
    # Load device storage in executor to avoid blocking I/O
    await hass.async_add_executor_job(device_storage.load)
    
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
    
    # Register existing devices in device registry
    device_reg = dr.async_get(hass)
    for device in devices:
        try:
            # Register each device directly under the integration
            device_reg.async_get_or_create(
                config_entry_id=None,
                identifiers={(DOMAIN, device.dsid)},
                name=device.name,
                manufacturer=device.vendor_name or DEFAULT_VENDOR,
                model=device.model or "Virtual Device",
            )
            _LOGGER.debug("Registered device in device registry: %s", device.name)
        except Exception as err:
            _LOGGER.error(
                "Error registering device %s in device registry: %s",
                device.name,
                err,
                exc_info=True,
            )
    
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
    hass.data[DOMAIN] = {
        "vdc_manager": vdc_manager,
        "vdc_dsuid": vdc_config["dsUID"],
        "device_storage": device_storage,
        "state_listener_manager": state_listener_manager,
        "device_configurator": device_configurator,
        "property_updater": property_updater,
    }
    
    _LOGGER.info("Virtual digitalSTROM Devices integration setup complete")
    
    return True

