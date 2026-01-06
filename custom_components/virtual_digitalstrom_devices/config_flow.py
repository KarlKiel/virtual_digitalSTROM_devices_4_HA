"""Config flow for Virtual digitalSTROM Devices integration."""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import device_registry as dr

from .const import DOMAIN, DEFAULT_NAME, DEFAULT_VENDOR, CONF_DSS_PORT, DEFAULT_DSS_PORT, DSColor, DSGroupID, STORAGE_FILE
from .storage import DeviceStorage
from .models.virtual_device import VirtualDevice

_LOGGER = logging.getLogger(__name__)

# Color group options for device category selection
COLOR_GROUP_OPTIONS = {
    DSColor.YELLOW.value: "Lights - All lighting devices",
    DSColor.GRAY.value: "Blinds - Shading and blind control",
    DSColor.BLUE.value: "Climate - Heating, cooling, ventilation, windows",
    DSColor.CYAN.value: "Audio - Audio playback devices",
    DSColor.MAGENTA.value: "Video - TV and video devices",
    DSColor.RED.value: "Security - Alarms, fire, panic systems",
    DSColor.GREEN.value: "Access - Doors, doorbells, access control",
    DSColor.WHITE.value: "Single Devices - Individual appliances (fridge, coffee maker)",
    DSColor.BLACK.value: "Joker - Configurable/customizable devices",
}

# Map color to group ID
COLOR_TO_GROUP_ID = {
    DSColor.YELLOW.value: DSGroupID.LIGHTS.value,
    DSColor.GRAY.value: DSGroupID.BLINDS.value,
    DSColor.BLUE.value: DSGroupID.HEATING.value,  # Climate uses heating as default
    DSColor.CYAN.value: DSGroupID.AUDIO.value,
    DSColor.MAGENTA.value: DSGroupID.VIDEO.value,
    DSColor.RED.value: DSGroupID.SECURITY.value,
    DSColor.GREEN.value: DSGroupID.ACCESS.value,
    DSColor.WHITE.value: DSGroupID.SINGLE_DEVICE.value,
    DSColor.BLACK.value: DSGroupID.JOKER.value,
}

# Configuration schema
STEP_USER_DATA_SCHEMA = vol.Schema({
    vol.Required("name", default=DEFAULT_NAME): str,
    vol.Required(CONF_DSS_PORT, default=DEFAULT_DSS_PORT): vol.All(
        vol.Coerce(int), vol.Range(min=1, max=65535)
    ),
})


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect.
    
    Data has the keys from STEP_USER_DATA_SCHEMA with values provided by the user.
    """
    # For now, we just accept the input as is
    # In the future, you can add validation logic here
    
    return {"title": data["name"]}


def _extract_category_name(category_value: str) -> str:
    """Extract the category display name from the color group option.
    
    Args:
        category_value: The color value (e.g., 'yellow')
        
    Returns:
        The category name (e.g., 'Lights')
    """
    category_display = COLOR_GROUP_OPTIONS.get(category_value, category_value)
    # Extract just the category name (before the dash)
    category_name = category_display.split(" - ")[0] if " - " in category_display else category_display
    return category_name


def _get_device_storage() -> DeviceStorage:
    """Get the device storage instance (unloaded).
    
    Returns:
        DeviceStorage instance (not loaded yet - call load() before use)
    """
    integration_dir = Path(__file__).parent
    storage_path = integration_dir / STORAGE_FILE
    return DeviceStorage(storage_path)


async def _get_device_storage_async(hass: HomeAssistant) -> DeviceStorage:
    """Get the device storage instance (async, loaded).
    
    Args:
        hass: Home Assistant instance
        
    Returns:
        DeviceStorage instance (loaded)
    """
    storage = _get_device_storage()
    await hass.async_add_executor_job(storage.load)
    return storage


async def _create_virtual_device(
    hass: HomeAssistant,
    category_value: str,
    config_entry_id: str,
) -> bool:
    """Create and register a virtual device.

    Args:
        hass: Home Assistant instance
        category_value: The device category (color value)
        config_entry_id: The config entry ID to register the device under

    Returns:
        True if device was created successfully, False otherwise
    """
    # Get the display name for the title
    category_name = _extract_category_name(category_value)
    
    # Get device storage (async to avoid blocking I/O)
    device_storage = await _get_device_storage_async(hass)
    
    # Get group_id from color
    group_id = COLOR_TO_GROUP_ID.get(category_value, 0)
    
    # Create a new virtual device
    device = VirtualDevice(
        name=f"Virtual {category_name} Device",
        group_id=group_id,
        device_class=category_value,
        model=f"{category_name} Device",
        vendor_name=DEFAULT_VENDOR,
    )
    
    # Add to storage (use executor to avoid blocking I/O during save)
    if await hass.async_add_executor_job(device_storage.add_device, device):
        # Register device in Home Assistant's device registry
        device_reg = dr.async_get(hass)
        device_reg.async_get_or_create(
            config_entry_id=config_entry_id,
            identifiers={(DOMAIN, device.dsid)},
            name=device.name,
            manufacturer=device.vendor_name,
            model=device.model,
        )
        _LOGGER.info("Created virtual device: %s (category: %s)", device.name, category_name)
        return True
    
    return False


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Virtual digitalSTROM Devices."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._data: dict[str, Any] = {}
        self._extended_config: dict[str, Any] = {}

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the user step - only for integration setup."""
        # Check if we already have a config entry (integration already set up)
        existing_entries = self._async_current_entries()
        
        if existing_entries:
            # Integration is already set up
            # Only allow one instance of this integration
            return self.async_abort(reason="single_instance_allowed")
        
        # First time setup - configure the integration
        _LOGGER.debug("First time setup, configuring integration")
        return await self.async_step_integration_setup(user_input)

    async def async_step_pair(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle device pairing - for compatibility with hub integrations."""
        _LOGGER.debug("Device pairing initiated (redirecting to device_category)")
        return await self.async_step_device_category(user_input)

    async def async_step_integration_setup(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial integration setup."""
        errors: dict[str, str] = {}
        
        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                return self.async_create_entry(title=info["title"], data=user_input)

        return self.async_show_form(
            step_id="integration_setup",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )

    async def async_step_device_category(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the device category selection step."""
        errors: dict[str, str] = {}
        
        if user_input is not None:
            # Store the selected category
            category_value = user_input["category"]
            self._data = {"category": category_value}
            
            # Proceed to device configuration screen
            return await self.async_step_device_config(None)

        # Create schema for category selection
        category_schema = vol.Schema({
            vol.Required("category"): vol.In(COLOR_GROUP_OPTIONS),
        })

        return self.async_show_form(
            step_id="device_category",
            data_schema=category_schema,
            errors=errors,
        )
    
    async def async_step_device_config(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle device configuration step (required CONFIG properties)."""
        errors: dict[str, str] = {}
        category_value = self._data.get("category", "")
        is_black_device = category_value == DSColor.BLACK.value
        
        if user_input is not None:
            # Check which action button was clicked
            next_action = user_input.get("next_action")
            
            # Store the configuration data (excluding the action button)
            config_data = {k: v for k, v in user_input.items() if k != "next_action"}
            self._data.update(config_data)
            
            # Route based on user's button choice
            if next_action == "create_device":
                # User clicked "Create Device" - finish and create
                return await self.async_step_create_device(None)
            elif next_action == "show_extended_config":
                # User clicked "Extended Configuration" - show optional fields
                return await self.async_step_extended_config(None)
            elif next_action == "go_back":
                # User clicked "Back" - return to category selection
                return await self.async_step_back_to_category(None)
            elif next_action == "cancel":
                # User clicked "Cancel" - abort device creation
                return await self.async_step_cancel_creation(None)
        
        # Build schema with required fields
        schema_dict = {
            vol.Required("name", default=self._data.get("name", "")): str,
            vol.Required("model", default=self._data.get("model", "")): str,
            vol.Required("display_id", default=self._data.get("display_id", "")): str,
        }
        
        # For Black/Joker devices, add primary group selection
        if is_black_device:
            # Create dropdown options for primary group (exclude Black itself)
            primary_group_options = {
                k: v for k, v in COLOR_GROUP_OPTIONS.items() 
                if k != DSColor.BLACK.value
            }
            schema_dict[vol.Required("primary_group_selection", default=self._data.get("primary_group_selection"))] = vol.In(primary_group_options)
        
        # Add navigation/action selector as the last field
        schema_dict[vol.Required("next_action", default="create_device")] = vol.In({
            "create_device": "✓ Create Device (Finish)",
            "show_extended_config": "⚙ Extended Configuration (Optional)",
            "go_back": "← Back to Category Selection",
            "cancel": "✗ Cancel Device Creation",
        })
        
        config_schema = vol.Schema(schema_dict)
        
        return self.async_show_form(
            step_id="device_config",
            data_schema=config_schema,
            errors=errors,
        )
    
    async def async_step_create_device(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Create the device with current configuration."""
        errors: dict[str, str] = {}
        
        # Get the first (and only) config entry for this integration
        existing_entries = self._async_current_entries()
        if existing_entries:
            # Create the device with collected configuration
            if await self._create_configured_device(existing_entries[0].entry_id):
                return self.async_abort(reason="device_created")
            else:
                errors["base"] = "device_creation_failed"
        else:
            errors["base"] = "device_creation_failed"
        
        # If creation failed, go back to config
        return await self.async_step_device_config(None)
    
    async def async_step_back_to_category(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Go back to category selection."""
        # Clear stored data except extended config
        self._data = {}
        return await self.async_step_device_category(None)
    
    async def async_step_cancel_creation(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Cancel device creation."""
        return self.async_abort(reason="user_cancelled")
    
    async def async_step_extended_config(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle extended configuration popup (optional CONFIG properties)."""
        errors: dict[str, str] = {}
        
        if user_input is not None:
            # Store extended configuration
            self._extended_config.update(user_input)
            
            # Return to main device config screen
            return await self.async_step_device_config(None)

        # Build schema for optional properties
        schema_dict = {
            vol.Optional("model_version", default=self._extended_config.get("model_version", "")): str,
            vol.Optional("model_uid", default=self._extended_config.get("model_uid", "")): str,
            vol.Optional("hardware_version", default=self._extended_config.get("hardware_version", "")): str,
            vol.Optional("hardware_guid", default=self._extended_config.get("hardware_guid", "")): str,
            vol.Optional("hardware_model_guid", default=self._extended_config.get("hardware_model_guid", "")): str,
            vol.Optional("vendor_name", default=self._extended_config.get("vendor_name", "")): str,
            vol.Optional("vendor_guid", default=self._extended_config.get("vendor_guid", "")): str,
            vol.Optional("oem_guid", default=self._extended_config.get("oem_guid", "")): str,
            vol.Optional("oem_model_guid", default=self._extended_config.get("oem_model_guid", "")): str,
            vol.Optional("device_class", default=self._extended_config.get("device_class", "")): str,
            vol.Optional("device_class_version", default=self._extended_config.get("device_class_version", "")): str,
            vol.Optional("ha_entity_id", default=self._extended_config.get("ha_entity_id", "")): str,
        }
        
        # Add active as boolean selector
        if "active" in self._extended_config:
            schema_dict[vol.Optional("active", default=self._extended_config["active"])] = bool
        else:
            schema_dict[vol.Optional("active")] = bool
        
        extended_schema = vol.Schema(schema_dict)
        
        return self.async_show_form(
            step_id="extended_config",
            data_schema=extended_schema,
            errors=errors,
        )
    
    async def _create_configured_device(self, config_entry_id: str) -> bool:
        """Create device with all collected configuration data.
        
        Args:
            config_entry_id: The config entry ID to register the device under
            
        Returns:
            True if device was created successfully, False otherwise
        """
        category_value = self._data.get("category", "")
        category_name = _extract_category_name(category_value)
        
        # Get device storage
        device_storage = await _get_device_storage_async(self.hass)
        
        # Determine group_id
        # For Black devices, use the selected primary_group_selection
        # For others, use the category color mapping
        if category_value == DSColor.BLACK.value and "primary_group_selection" in self._data:
            group_id = COLOR_TO_GROUP_ID.get(self._data["primary_group_selection"], DSGroupID.JOKER.value)
        else:
            group_id = COLOR_TO_GROUP_ID.get(category_value, 0)
        
        # Merge extended config into data
        all_config = {**self._data, **self._extended_config}
        
        # Create device with user-provided configuration
        device = VirtualDevice(
            # Auto-derived properties
            # device_id is auto-generated by default factory
            # dsid will be auto-generated by __post_init__
            type="vdSD",  # Always vdSD
            
            # Required CONFIG properties from user
            name=all_config.get("name", f"Virtual {category_name} Device"),
            model=all_config.get("model", f"{category_name} Device"),
            display_id=all_config.get("display_id", ""),
            
            # Group/zone properties
            group_id=group_id,
            zone_id=0,  # NULL/0 as initial value per requirements
            
            # Device class
            device_class=all_config.get("device_class", category_value),
            
            # Optional CONFIG properties from extended config
            model_version=all_config.get("model_version", ""),
            model_uid=all_config.get("model_uid", ""),
            hardware_version=all_config.get("hardware_version", ""),
            hardware_guid=all_config.get("hardware_guid", ""),
            hardware_model_guid=all_config.get("hardware_model_guid", ""),
            vendor_name=all_config.get("vendor_name", DEFAULT_VENDOR),
            vendor_guid=all_config.get("vendor_guid", ""),
            oem_guid=all_config.get("oem_guid", ""),
            oem_model_guid=all_config.get("oem_model_guid", ""),
            device_class_version=all_config.get("device_class_version", ""),
            active=all_config.get("active", None),
            ha_entity_id=all_config.get("ha_entity_id", ""),
        )
        
        # Add to storage
        if await self.hass.async_add_executor_job(device_storage.add_device, device):
            # Register device in Home Assistant's device registry
            device_reg = dr.async_get(self.hass)
            device_reg.async_get_or_create(
                config_entry_id=config_entry_id,
                identifiers={(DOMAIN, device.dsid)},
                name=device.name,
                manufacturer=device.vendor_name or DEFAULT_VENDOR,
                model=device.model,
            )
            _LOGGER.info("Created configured virtual device: %s (category: %s)", device.name, category_name)
            return True
        
        return False
    
    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> OptionsFlowHandler:
        """Get the options flow for this handler."""
        return OptionsFlowHandler(config_entry)


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow for Virtual digitalSTROM Devices."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self._data: dict[str, Any] = {}
        self._extended_config: dict[str, Any] = {}

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options - entry point."""
        # Show device management menu (original behavior)
        return await self.async_step_device_menu(user_input)

    async def async_step_main_menu(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Show main options menu."""
        return self.async_show_menu(
            step_id="main_menu",
            menu_options=["integration_settings", "device_menu"],
        )

    async def async_step_integration_settings(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle integration settings (port configuration)."""
        errors: dict[str, str] = {}
        
        if user_input is not None:
            try:
                # Update the config entry with new port
                self.hass.config_entries.async_update_entry(
                    self.config_entry,
                    data={**self.config_entry.data, CONF_DSS_PORT: user_input[CONF_DSS_PORT]},
                )
                return self.async_create_entry(title="", data={})
            except Exception as err:
                _LOGGER.error("Error updating config entry: %s", err, exc_info=True)
                errors["base"] = "unknown"
        
        # Get current port value with fallback
        current_port = self.config_entry.data.get(CONF_DSS_PORT, DEFAULT_DSS_PORT)
        
        # Schema for port configuration
        settings_schema = vol.Schema({
            vol.Required(CONF_DSS_PORT, default=current_port): vol.All(
                vol.Coerce(int), vol.Range(min=1, max=65535)
            ),
        })
        
        return self.async_show_form(
            step_id="integration_settings",
            data_schema=settings_schema,
            errors=errors,
        )

    async def async_step_device_menu(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Show device management menu."""
        return self.async_show_menu(
            step_id="device_menu",
            menu_options=["add_device", "list_devices"],
        )

    async def async_step_add_device(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle adding a new virtual device."""
        return await self.async_step_device_category(user_input)

    async def async_step_device_category(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the device category selection step."""
        errors: dict[str, str] = {}
        
        if user_input is not None:
            # Store the selected category
            category_value = user_input["category"]
            self._data = {"category": category_value}
            
            # Proceed to device configuration screen
            return await self.async_step_device_config(None)

        # Create schema for category selection
        category_schema = vol.Schema({
            vol.Required("category"): vol.In(COLOR_GROUP_OPTIONS),
        })

        return self.async_show_form(
            step_id="device_category",
            data_schema=category_schema,
            errors=errors,
        )

    async def async_step_device_config(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle device configuration step (required CONFIG properties)."""
        errors: dict[str, str] = {}
        category_value = self._data.get("category", "")
        is_black_device = category_value == DSColor.BLACK.value
        
        if user_input is not None:
            # Check which action button was clicked
            next_action = user_input.get("next_action")
            
            # Store the configuration data (excluding the action button)
            config_data = {k: v for k, v in user_input.items() if k != "next_action"}
            self._data.update(config_data)
            
            # Route based on user's button choice
            if next_action == "create_device":
                # User clicked "Create Device" - finish and create
                return await self.async_step_create_device(None)
            elif next_action == "show_extended_config":
                # User clicked "Extended Configuration" - show optional fields
                return await self.async_step_extended_config(None)
            elif next_action == "go_back":
                # User clicked "Back" - return to category selection
                return await self.async_step_back_to_category(None)
            elif next_action == "cancel":
                # User clicked "Cancel" - abort device creation
                return await self.async_step_cancel_creation(None)
        
        # Build schema with required fields
        schema_dict = {
            vol.Required("name", default=self._data.get("name", "")): str,
            vol.Required("model", default=self._data.get("model", "")): str,
            vol.Required("display_id", default=self._data.get("display_id", "")): str,
        }
        
        # For Black/Joker devices, add primary group selection
        if is_black_device:
            # Create dropdown options for primary group (exclude Black itself)
            primary_group_options = {
                k: v for k, v in COLOR_GROUP_OPTIONS.items() 
                if k != DSColor.BLACK.value
            }
            schema_dict[vol.Required("primary_group_selection", default=self._data.get("primary_group_selection"))] = vol.In(primary_group_options)
        
        # Add navigation/action selector as the last field
        schema_dict[vol.Required("next_action", default="create_device")] = vol.In({
            "create_device": "✓ Create Device (Finish)",
            "show_extended_config": "⚙ Extended Configuration (Optional)",
            "go_back": "← Back to Category Selection",
            "cancel": "✗ Cancel Device Creation",
        })
        
        config_schema = vol.Schema(schema_dict)
        
        return self.async_show_form(
            step_id="device_config",
            data_schema=config_schema,
            errors=errors,
        )
    
    async def async_step_create_device(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Create the device with current configuration."""
        errors: dict[str, str] = {}
        
        # Create the device with collected configuration
        if await self._create_configured_device():
            return self.async_abort(reason="device_created")
        else:
            errors["base"] = "device_creation_failed"
        
        # If creation failed, go back to config
        return await self.async_step_device_config(None)
    
    async def async_step_back_to_category(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Go back to category selection."""
        # Clear stored data except extended config
        self._data = {}
        return await self.async_step_device_category(None)
    
    async def async_step_cancel_creation(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Cancel device creation."""
        return self.async_abort(reason="user_cancelled")
    
    async def async_step_extended_config(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle extended configuration popup (optional CONFIG properties)."""
        errors: dict[str, str] = {}
        
        if user_input is not None:
            # Store extended configuration
            self._extended_config.update(user_input)
            
            # Return to main device config screen
            return await self.async_step_device_config(None)

        # Build schema for optional properties
        schema_dict = {
            vol.Optional("model_version", default=self._extended_config.get("model_version", "")): str,
            vol.Optional("model_uid", default=self._extended_config.get("model_uid", "")): str,
            vol.Optional("hardware_version", default=self._extended_config.get("hardware_version", "")): str,
            vol.Optional("hardware_guid", default=self._extended_config.get("hardware_guid", "")): str,
            vol.Optional("hardware_model_guid", default=self._extended_config.get("hardware_model_guid", "")): str,
            vol.Optional("vendor_name", default=self._extended_config.get("vendor_name", "")): str,
            vol.Optional("vendor_guid", default=self._extended_config.get("vendor_guid", "")): str,
            vol.Optional("oem_guid", default=self._extended_config.get("oem_guid", "")): str,
            vol.Optional("oem_model_guid", default=self._extended_config.get("oem_model_guid", "")): str,
            vol.Optional("device_class", default=self._extended_config.get("device_class", "")): str,
            vol.Optional("device_class_version", default=self._extended_config.get("device_class_version", "")): str,
            vol.Optional("ha_entity_id", default=self._extended_config.get("ha_entity_id", "")): str,
        }
        
        # Add active as boolean selector
        if "active" in self._extended_config:
            schema_dict[vol.Optional("active", default=self._extended_config["active"])] = bool
        else:
            schema_dict[vol.Optional("active")] = bool
        
        extended_schema = vol.Schema(schema_dict)
        
        return self.async_show_form(
            step_id="extended_config",
            data_schema=extended_schema,
            errors=errors,
        )
    
    async def _create_configured_device(self) -> bool:
        """Create device with all collected configuration data.
        
        Returns:
            True if device was created successfully, False otherwise
        """
        category_value = self._data.get("category", "")
        category_name = _extract_category_name(category_value)
        
        # Get device storage
        device_storage = await _get_device_storage_async(self.hass)
        
        # Determine group_id
        # For Black devices, use the selected primary_group_selection
        # For others, use the category color mapping
        if category_value == DSColor.BLACK.value and "primary_group_selection" in self._data:
            group_id = COLOR_TO_GROUP_ID.get(self._data["primary_group_selection"], DSGroupID.JOKER.value)
        else:
            group_id = COLOR_TO_GROUP_ID.get(category_value, 0)
        
        # Merge extended config into data
        all_config = {**self._data, **self._extended_config}
        
        # Create device with user-provided configuration
        device = VirtualDevice(
            # Auto-derived properties
            # device_id is auto-generated by default factory
            # dsid will be auto-generated by __post_init__
            type="vdSD",  # Always vdSD
            
            # Required CONFIG properties from user
            name=all_config.get("name", f"Virtual {category_name} Device"),
            model=all_config.get("model", f"{category_name} Device"),
            display_id=all_config.get("display_id", ""),
            
            # Group/zone properties
            group_id=group_id,
            zone_id=0,  # NULL/0 as initial value per requirements
            
            # Device class
            device_class=all_config.get("device_class", category_value),
            
            # Optional CONFIG properties from extended config
            model_version=all_config.get("model_version", ""),
            model_uid=all_config.get("model_uid", ""),
            hardware_version=all_config.get("hardware_version", ""),
            hardware_guid=all_config.get("hardware_guid", ""),
            hardware_model_guid=all_config.get("hardware_model_guid", ""),
            vendor_name=all_config.get("vendor_name", DEFAULT_VENDOR),
            vendor_guid=all_config.get("vendor_guid", ""),
            oem_guid=all_config.get("oem_guid", ""),
            oem_model_guid=all_config.get("oem_model_guid", ""),
            device_class_version=all_config.get("device_class_version", ""),
            active=all_config.get("active", None),
            ha_entity_id=all_config.get("ha_entity_id", ""),
        )
        
        # Add to storage
        if await self.hass.async_add_executor_job(device_storage.add_device, device):
            # Register device in Home Assistant's device registry
            device_reg = dr.async_get(self.hass)
            device_reg.async_get_or_create(
                config_entry_id=self.config_entry.entry_id,
                identifiers={(DOMAIN, device.dsid)},
                name=device.name,
                manufacturer=device.vendor_name or DEFAULT_VENDOR,
                model=device.model,
            )
            _LOGGER.info("Created configured virtual device: %s (category: %s)", device.name, category_name)
            return True
        
        return False

    async def async_step_list_devices(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """List existing devices."""
        # Get device storage (async to avoid blocking I/O)
        device_storage = await _get_device_storage_async(self.hass)
        
        devices = device_storage.get_all_devices()
        
        if not devices:
            device_list = "No virtual devices created yet."
        else:
            device_list = "\n".join([f"• {device.name} (dsUID: {device.dsid})" for device in devices])
        
        return self.async_show_form(
            step_id="list_devices",
            data_schema=vol.Schema({}),
            description_placeholders={"device_list": device_list},
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""
