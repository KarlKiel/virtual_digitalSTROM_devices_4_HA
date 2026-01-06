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

from .const import DOMAIN, DEFAULT_NAME, CONF_DSS_PORT, DEFAULT_DSS_PORT, DSColor, DSGroupID
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


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Virtual digitalSTROM Devices."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._data: dict[str, Any] = {}

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
        return await self.async_step_integration_setup(user_input)

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
        self.config_entry = config_entry
        self._data: dict[str, Any] = {}

    def _get_device_storage(self) -> DeviceStorage:
        """Get the device storage instance."""
        integration_dir = Path(__file__).parent
        storage_path = integration_dir / "virtual_digitalstrom_devices.yaml"
        return DeviceStorage(storage_path)

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options - entry point."""
        return await self.async_step_device_menu(user_input)

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
            # Store the selected category (color value like 'yellow')
            category_value = user_input["category"]
            self._data = {"category": category_value}
            
            # Get the display name for the title
            category_name = _extract_category_name(category_value)
            
            # Get device storage
            device_storage = self._get_device_storage()
            
            # Get group_id from color
            group_id = COLOR_TO_GROUP_ID.get(category_value, 0)
            
            # Create a new virtual device
            device = VirtualDevice(
                name=f"Virtual {category_name} Device",
                group_id=group_id,
                device_class=category_value,
                model=f"{category_name} Device",
                vendor_name="KarlKiel",
            )
            
            # Add to storage
            if device_storage.add_device(device):
                # Register device in Home Assistant's device registry as a child of the vDC hub
                device_reg = dr.async_get(self.hass)
                
                # Get the vDC hub device identifier
                vdc_data = self.hass.data.get(DOMAIN, {}).get(self.config_entry.entry_id, {})
                vdc_dsuid = vdc_data.get("vdc_dsuid")
                
                if vdc_dsuid:
                    device_reg.async_get_or_create(
                        config_entry_id=self.config_entry.entry_id,
                        identifiers={(DOMAIN, device.dsid)},
                        name=device.name,
                        manufacturer="KarlKiel",
                        model=f"{category_name} Device",
                        via_device=(DOMAIN, vdc_dsuid),  # Link to vDC hub
                    )
                    _LOGGER.info("Created virtual device: %s (category: %s)", device.name, category_name)
                
                # Return to main menu after successful device creation
                return self.async_abort(reason="device_created")
            else:
                errors["base"] = "device_creation_failed"

        # Create schema for category selection
        category_schema = vol.Schema({
            vol.Required("category"): vol.In(COLOR_GROUP_OPTIONS),
        })

        return self.async_show_form(
            step_id="device_category",
            data_schema=category_schema,
            errors=errors,
        )

    async def async_step_list_devices(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """List existing devices."""
        # Get device storage
        device_storage = self._get_device_storage()
        
        devices = device_storage.get_all_devices()
        
        if not devices:
            device_list = "No virtual devices created yet."
        else:
            device_list = "\n".join([f"• {device.name} (ID: {device.device_id})" for device in devices])
        
        return self.async_show_form(
            step_id="list_devices",
            data_schema=vol.Schema({}),
            description_placeholders={"device_list": device_list},
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""
