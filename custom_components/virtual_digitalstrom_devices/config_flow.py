"""Config flow for Virtual digitalSTROM Devices integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

from .const import DOMAIN, DEFAULT_NAME, CONF_DSS_PORT, DEFAULT_DSS_PORT, DSColor

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


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Virtual digitalSTROM Devices."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._data: dict[str, Any] = {}

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the user step - either integration setup or device creation."""
        # Check if we already have a config entry (integration already set up)
        existing_entries = self._async_current_entries()
        
        if existing_entries:
            # Integration is already set up, this is for creating a new device
            # Don't pass user_input as it's not relevant for the device category step
            return await self.async_step_device_category(None)
        else:
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

    async def async_step_device_category(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the device category selection step."""
        errors: dict[str, str] = {}
        
        if user_input is not None:
            # Store the selected category (color value like 'yellow')
            category_value = user_input["category"]
            self._data = {"category": category_value}
            
            # Get the descriptive name from the COLOR_GROUP_OPTIONS
            category_display = COLOR_GROUP_OPTIONS.get(category_value, category_value)
            # Extract just the category name (before the dash)
            category_name = category_display.split(" - ")[0] if " - " in category_display else category_display
            
            # For now, we'll just create an entry with the category
            # Future steps will be added to configure the device details
            return self.async_create_entry(
                title=f"Virtual Device ({category_name})",
                data=self._data
            )

        # Create schema for category selection
        category_schema = vol.Schema({
            vol.Required("category"): vol.In(COLOR_GROUP_OPTIONS),
        })

        return self.async_show_form(
            step_id="device_category",
            data_schema=category_schema,
            errors=errors,
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""
