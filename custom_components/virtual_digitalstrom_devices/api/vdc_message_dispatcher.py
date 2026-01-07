"""Message dispatcher for handling specific vDC API message types.

This module provides handlers for different message types that interact with
the device storage and property updater systems to process requests and
notifications from the vDSM.

Based on genericVDC.proto specification.
"""

from __future__ import annotations

import logging
from typing import Any, Optional

from homeassistant.core import HomeAssistant

from . import genericVDC_pb2 as pb
from .device_storage import DeviceStorage
from .message_builder import MessageBuilder, create_property_dict
from .message_handler import ParsedMessage, extract_property_elements
from .property_updater import PropertyUpdater
from .state_listener import StatePropertyType
from .virtual_device import VirtualDevice

_LOGGER = logging.getLogger(__name__)


def _safe_get_field(payload: Any, field_name: str, default: Any = None) -> Any:
    """Safely get a field from a protobuf message.
    
    Args:
        payload: Protobuf message object
        field_name: Name of the field to get
        default: Default value if field is not present
        
    Returns:
        Field value if present, otherwise default
    """
    if hasattr(payload, "HasField") and payload.HasField(field_name):
        return getattr(payload, field_name)
    return default


class VdcMessageDispatcher:
    """Dispatcher for handling vDC API messages and integrating with HA."""
    
    def __init__(
        self,
        hass: HomeAssistant,
        vdc_dsuid: str,
        device_storage: DeviceStorage,
        property_updater: PropertyUpdater,
    ):
        """Initialize the message dispatcher.
        
        Args:
            hass: Home Assistant instance
            vdc_dsuid: dSUID of this vDC
            device_storage: DeviceStorage instance
            property_updater: PropertyUpdater instance
        """
        self.hass = hass
        self.vdc_dsuid = vdc_dsuid
        self.device_storage = device_storage
        self.property_updater = property_updater
        self.message_builder = MessageBuilder(vdc_dsuid)
    
    async def handle_request_hello(
        self,
        parsed_msg: ParsedMessage,
    ) -> pb.Message:
        """Handle VDSM_REQUEST_HELLO message.
        
        The vDSM sends this during initial handshake to identify itself
        and negotiate API version.
        
        Args:
            parsed_msg: Parsed hello request
            
        Returns:
            ResponseHello message
        """
        payload = parsed_msg.payload
        
        if payload.HasField("dSUID"):
            vdsm_dsuid = payload.dSUID
            _LOGGER.info(f"Received hello from vDSM: {vdsm_dsuid}")
        
        if payload.HasField("api_version"):
            api_version = payload.api_version
            _LOGGER.info(f"vDSM API version: {api_version}")
        
        # Respond with our vDC dSUID
        return self.message_builder.create_response_hello(
            message_id=parsed_msg.message_id,
        )
    
    async def handle_request_get_property(
        self,
        parsed_msg: ParsedMessage,
    ) -> pb.Message:
        """Handle VDSM_REQUEST_GET_PROPERTY message.
        
        The vDSM requests property values for a device or the vDC itself.
        
        Args:
            parsed_msg: Parsed get property request
            
        Returns:
            ResponseGetProperty message with requested properties
        """
        payload = parsed_msg.payload
        dsuid = parsed_msg.dsuid
        
        # Extract query parameters
        query_elements = extract_property_elements(payload.query)
        
        _LOGGER.debug(f"GetProperty request for {dsuid}: {query_elements}")
        
        # Get the device (or vDC if dsuid matches our vDC)
        if dsuid == self.vdc_dsuid:
            # Request for vDC properties
            properties = self._get_vdc_properties(query_elements)
        else:
            # Request for device properties
            device = self._find_device_by_dsuid(dsuid)
            if device:
                properties = self._get_device_properties(device, query_elements)
            else:
                _LOGGER.warning(f"Device not found: {dsuid}")
                return self.message_builder.create_generic_response(
                    code=pb.ERR_NOT_FOUND,
                    description=f"Device {dsuid} not found",
                    message_id=parsed_msg.message_id,
                )
        
        return self.message_builder.create_response_get_property(
            properties=properties,
            message_id=parsed_msg.message_id,
        )
    
    async def handle_request_set_property(
        self,
        parsed_msg: ParsedMessage,
    ) -> pb.Message:
        """Handle VDSM_REQUEST_SET_PROPERTY message.
        
        The vDSM requests to set property values on a device or the vDC.
        
        Args:
            parsed_msg: Parsed set property request
            
        Returns:
            GenericResponse message indicating success or failure
        """
        payload = parsed_msg.payload
        dsuid = parsed_msg.dsuid
        
        # Extract properties to set
        properties = extract_property_elements(payload.properties)
        
        _LOGGER.debug(f"SetProperty request for {dsuid}: {properties}")
        
        try:
            if dsuid == self.vdc_dsuid:
                # Set vDC properties
                self._set_vdc_properties(properties)
            else:
                # Set device properties
                device = self._find_device_by_dsuid(dsuid)
                if not device:
                    return self.message_builder.create_generic_response(
                        code=pb.ERR_NOT_FOUND,
                        description=f"Device {dsuid} not found",
                        message_id=parsed_msg.message_id,
                    )
                
                await self._set_device_properties(device, properties)
            
            return self.message_builder.create_generic_response(
                code=pb.ERR_OK,
                message_id=parsed_msg.message_id,
            )
            
        except Exception as e:
            _LOGGER.error(f"Error setting properties: {e}", exc_info=True)
            return self.message_builder.create_generic_response(
                code=pb.ERR_MESSAGE_UNKNOWN,
                description=str(e),
                message_id=parsed_msg.message_id,
            )
    
    async def handle_send_ping(
        self,
        parsed_msg: ParsedMessage,
    ) -> pb.Message:
        """Handle VDSM_SEND_PING message.
        
        The vDSM sends ping to check if vDC/device is alive.
        
        Args:
            parsed_msg: Parsed ping message
            
        Returns:
            Pong message
        """
        dsuid = parsed_msg.dsuid or self.vdc_dsuid
        
        _LOGGER.debug(f"Received ping for {dsuid}")
        
        return self.message_builder.create_pong(
            device_dsuid=dsuid,
            message_id=parsed_msg.message_id,
        )
    
    async def handle_notification_call_scene(
        self,
        parsed_msg: ParsedMessage,
    ) -> None:
        """Handle VDSM_NOTIFICATION_CALL_SCENE message.
        
        The vDSM requests to activate a scene on one or more devices.
        Notifications don't expect responses.
        
        Args:
            parsed_msg: Parsed call scene notification
        """
        payload = parsed_msg.payload
        
        device_dsuids = list(payload.dSUID)
        scene = _safe_get_field(payload, "scene")
        force = _safe_get_field(payload, "force", False)
        group = _safe_get_field(payload, "group")
        zone_id = _safe_get_field(payload, "zone_id")
        
        _LOGGER.info(
            f"CallScene: devices={device_dsuids}, scene={scene}, "
            f"force={force}, group={group}, zone={zone_id}"
        )
        
        # Process scene for each device
        for dsuid in device_dsuids:
            device = self._find_device_by_dsuid(dsuid)
            if device:
                await self._apply_scene_to_device(device, scene, force)
            else:
                _LOGGER.warning(f"Device not found for scene call: {dsuid}")
    
    async def handle_notification_save_scene(
        self,
        parsed_msg: ParsedMessage,
    ) -> None:
        """Handle VDSM_NOTIFICATION_SAVE_SCENE message.
        
        The vDSM requests to save current state as a scene.
        
        Args:
            parsed_msg: Parsed save scene notification
        """
        payload = parsed_msg.payload
        
        device_dsuids = list(payload.dSUID)
        scene = _safe_get_field(payload, "scene")
        
        _LOGGER.info(f"SaveScene: devices={device_dsuids}, scene={scene}")
        
        # Process scene save for each device
        for dsuid in device_dsuids:
            device = self._find_device_by_dsuid(dsuid)
            if device:
                await self._save_scene_for_device(device, scene)
    
    async def handle_notification_set_output_channel_value(
        self,
        parsed_msg: ParsedMessage,
    ) -> None:
        """Handle VDSM_NOTIFICATION_SET_OUTPUT_CHANNEL_VALUE message.
        
        The vDSM requests to set an output channel value.
        
        Args:
            parsed_msg: Parsed set output channel value notification
        """
        payload = parsed_msg.payload
        
        device_dsuids = list(payload.dSUID)
        channel = _safe_get_field(payload, "channel")
        value = _safe_get_field(payload, "value")
        apply_now = _safe_get_field(payload, "apply_now", True)
        channel_id = _safe_get_field(payload, "channelId")
        
        _LOGGER.info(
            f"SetOutputChannelValue: devices={device_dsuids}, "
            f"channel={channel}/{channel_id}, value={value}, apply_now={apply_now}"
        )
        
        # Process channel value for each device
        for dsuid in device_dsuids:
            device = self._find_device_by_dsuid(dsuid)
            if device:
                await self._set_output_channel_value(
                    device, channel, value, apply_now, channel_id
                )
    
    async def handle_notification_dim_channel(
        self,
        parsed_msg: ParsedMessage,
    ) -> None:
        """Handle VDSM_NOTIFICATION_DIM_CHANNEL message.
        
        The vDSM requests to dim/brighten a channel.
        
        Args:
            parsed_msg: Parsed dim channel notification
        """
        payload = parsed_msg.payload
        
        device_dsuids = list(payload.dSUID)
        channel = _safe_get_field(payload, "channel")
        mode = _safe_get_field(payload, "mode")
        
        _LOGGER.info(
            f"DimChannel: devices={device_dsuids}, "
            f"channel={channel}, mode={mode}"
        )
        
        # Process dimming for each device
        for dsuid in device_dsuids:
            device = self._find_device_by_dsuid(dsuid)
            if device:
                await self._dim_channel(device, channel, mode)
    
    async def handle_notification_set_control_value(
        self,
        parsed_msg: ParsedMessage,
    ) -> None:
        """Handle VDSM_NOTIFICATION_SET_CONTROL_VALUE message.
        
        The vDSM requests to set a control value (heating, cooling, etc.).
        
        Args:
            parsed_msg: Parsed set control value notification
        """
        payload = parsed_msg.payload
        
        device_dsuids = list(payload.dSUID)
        name = _safe_get_field(payload, "name")
        value = _safe_get_field(payload, "value")
        
        _LOGGER.info(
            f"SetControlValue: devices={device_dsuids}, "
            f"name={name}, value={value}"
        )
        
        # Process control value for each device
        for dsuid in device_dsuids:
            device = self._find_device_by_dsuid(dsuid)
            if device:
                await self._set_control_value(device, name, value)
    
    async def handle_send_remove(
        self,
        parsed_msg: ParsedMessage,
    ) -> None:
        """Handle VDSM_SEND_REMOVE message.
        
        The vDSM requests to remove a device.
        
        Args:
            parsed_msg: Parsed remove message
        """
        dsuid = parsed_msg.dsuid
        
        _LOGGER.info(f"Remove device: {dsuid}")
        
        device = self._find_device_by_dsuid(dsuid)
        if device:
            # Use executor to avoid blocking I/O during save
            await self.hass.async_add_executor_job(
                self.device_storage.delete_device, device.device_id
            )
            _LOGGER.info(f"Device {dsuid} removed")
        else:
            _LOGGER.warning(f"Device not found for removal: {dsuid}")
    
    # Helper methods
    
    def _find_device_by_dsuid(self, dsuid: str) -> Optional[VirtualDevice]:
        """Find a device by its dSUID.
        
        Args:
            dsuid: Device dSUID
            
        Returns:
            VirtualDevice or None if not found
        """
        devices = self.device_storage.get_all_devices()
        for device in devices:
            if device.dsid == dsuid:
                return device
        return None
    
    def _get_vdc_properties(
        self,
        query_elements: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """Get vDC properties based on query.
        
        Args:
            query_elements: List of queried property names
            
        Returns:
            List of property dictionaries
        """
        properties = []
        
        # Common vDC properties
        vdc_info = {
            "dSUID": self.vdc_dsuid,
            "modelName": "Virtual digitalSTROM Devices for Home Assistant",
            "modelVersion": "0.1.0",
            "vendorName": "Home Assistant Community",
        }
        
        # If query is empty, return all properties
        if not query_elements:
            for name, value in vdc_info.items():
                properties.append(create_property_dict(name, value))
        else:
            # Return only requested properties
            for query in query_elements:
                prop_name = query.get("name")
                if prop_name in vdc_info:
                    properties.append(
                        create_property_dict(prop_name, vdc_info[prop_name])
                    )
        
        return properties
    
    def _get_device_properties(
        self,
        device: VirtualDevice,
        query_elements: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """Get device properties based on query.
        
        Args:
            device: VirtualDevice instance
            query_elements: List of queried property names
            
        Returns:
            List of property dictionaries
        """
        properties = []
        
        # Build device property map
        device_props = {
            "dSUID": device.dsid,
            "name": device.name,
            "zoneID": device.zone_id,
            "primaryGroup": device.group_id,
            "model": device.model,
            "modelVersion": device.model_version,
            "displayId": device.display_id,
        }
        
        # Add state values if available
        if "state_values" in device.attributes:
            device_props["state"] = device.attributes["state_values"]
        
        # If query is empty, return all properties
        if not query_elements:
            for name, value in device_props.items():
                properties.append(create_property_dict(name, value))
        else:
            # Return only requested properties
            for query in query_elements:
                prop_name = query.get("name")
                if prop_name in device_props:
                    properties.append(
                        create_property_dict(prop_name, device_props[prop_name])
                    )
                elif prop_name in device.attributes:
                    # Check in custom attributes
                    properties.append(
                        create_property_dict(prop_name, device.attributes[prop_name])
                    )
        
        return properties
    
    def _set_vdc_properties(
        self,
        properties: list[dict[str, Any]],
    ) -> None:
        """Set vDC properties.
        
        Args:
            properties: List of property dictionaries to set
        """
        # Most vDC properties are read-only
        # Log the attempt but don't actually change anything critical
        _LOGGER.info(f"vDC property set request (read-only): {properties}")
    
    async def _set_device_properties(
        self,
        device: VirtualDevice,
        properties: list[dict[str, Any]],
    ) -> None:
        """Set device properties using PropertyUpdater.
        
        Args:
            device: VirtualDevice instance
            properties: List of property dictionaries to set
        """
        for prop in properties:
            prop_name = prop.get("name")
            prop_value = prop.get("value")
            
            # Check that name exists and 'value' key is in property dict
            # This allows setting properties to any value including falsy values
            # (0, False, empty string, etc.), but filters out properties without a name
            if prop_name is not None and "value" in prop:
                # Use property updater to set the property
                await self.property_updater.update_property(
                    device_id=device.device_id,
                    property_type=prop_name,
                    value=prop_value,
                )
    
    async def _apply_scene_to_device(
        self,
        device: VirtualDevice,
        scene: int,
        force: bool,
    ) -> None:
        """Apply a scene to a device.
        
        Args:
            device: VirtualDevice instance
            scene: Scene number
            force: Whether to force apply (overrides conditions if True)
        """
        # Look up scene configuration in device attributes
        scenes = device.attributes.get("scenes", {})
        scene_config = scenes.get(str(scene))
        
        if scene_config:
            _LOGGER.info(
                f"Applying scene {scene} to device {device.name} "
                f"(force={force})"
            )
            # Apply scene properties
            # Note: 'force' would typically override dimming operations or local priority
            # In this simplified implementation, we always apply the scene values
            for prop_name, prop_value in scene_config.items():
                await self.property_updater.update_property(
                    device_id=device.device_id,
                    property_type=prop_name,
                    value=prop_value,
                )
        else:
            _LOGGER.debug(f"No scene {scene} configured for device {device.name}")
    
    async def _save_scene_for_device(
        self,
        device: VirtualDevice,
        scene: int,
    ) -> None:
        """Save current device state as a scene.
        
        Args:
            device: VirtualDevice instance
            scene: Scene number to save
        """
        _LOGGER.info(f"Saving scene {scene} for device {device.name}")
        
        # Get current state values
        state_values = device.attributes.get("state_values", {})
        
        # Store as scene configuration
        if "scenes" not in device.attributes:
            device.attributes["scenes"] = {}
        
        device.attributes["scenes"][str(scene)] = dict(state_values)
        
        # Persist (use executor to avoid blocking I/O)
        await self.hass.async_add_executor_job(self.device_storage.save_device, device)
    
    async def _set_output_channel_value(
        self,
        device: VirtualDevice,
        channel: Optional[int],
        value: Optional[float],
        apply_now: bool,
        channel_id: Optional[str],
    ) -> None:
        """Set output channel value on a device.
        
        Args:
            device: VirtualDevice instance
            channel: Channel index (legacy)
            value: Channel value (None if not present in payload)
            apply_now: Whether to apply immediately
            channel_id: Channel ID string (API v3)
        """
        # Return early if no value provided (None is different from 0 or False)
        # In the vDC API, value is required for SetOutputChannelValue notification
        if value is None:
            _LOGGER.warning(
                f"No value provided for channel {channel} on device {device.name}"
            )
            return
        
        # Use channel_id if available (API v3), otherwise use index
        channel_index = channel if channel is not None else 0
        
        _LOGGER.info(
            f"Setting channel {channel_index} to {value} for device {device.name}"
        )
        
        # Update via property updater
        await self.property_updater.update_property(
            device_id=device.device_id,
            property_type=StatePropertyType.CHANNEL_VALUE.value,
            value=value,
            index=channel_index,
        )
    
    async def _dim_channel(
        self,
        device: VirtualDevice,
        channel: int,
        mode: int,
    ) -> None:
        """Dim/brighten a channel.
        
        Args:
            device: VirtualDevice instance
            channel: Channel index
            mode: Dim mode (1=start dimming up, 2=start dimming down, 0=stop)
        """
        _LOGGER.info(
            f"Dimming channel {channel} mode {mode} for device {device.name}"
        )
        
        # Dimming implementation notes:
        # - Mode 1 (dim up): Start continuous brightness increase
        # - Mode 2 (dim down): Start continuous brightness decrease  
        # - Mode 0 (stop): Stop dimming at current level
        # 
        # Full implementation would:
        # 1. Store dimming state in device attributes
        # 2. Start/stop a background task that increments/decrements channel value
        # 3. Respect min/max bounds and update PropertyUpdater periodically
        #
        # For now, we just log the action. Actual dimming would be implemented
        # when the transport layer and background task infrastructure exists.
        
        # Store dimming state for future implementation
        if "dimming_state" not in device.attributes:
            device.attributes["dimming_state"] = {}
        
        device.attributes["dimming_state"][str(channel)] = {
            "mode": mode,
            "active": mode != 0,
        }
        
        # Use executor to avoid blocking I/O
        await self.hass.async_add_executor_job(self.device_storage.save_device, device)
    
    async def _set_control_value(
        self,
        device: VirtualDevice,
        name: str,
        value: float,
    ) -> None:
        """Set a control value (heating, cooling, etc.).
        
        Args:
            device: VirtualDevice instance
            name: Control name
            value: Control value
        """
        _LOGGER.info(
            f"Setting control {name} to {value} for device {device.name}"
        )
        
        # Map control name to property type
        control_mapping = {
            "heatingLevel": "control.heatingLevel",
            "coolingLevel": "control.coolingLevel",
            "ventilationLevel": "control.ventilationLevel",
        }
        
        property_type = control_mapping.get(name, name)
        
        await self.property_updater.update_property(
            device_id=device.device_id,
            property_type=property_type,
            value=value,
        )
