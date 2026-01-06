"""Message builder for creating vDC API protobuf messages.

This module provides utilities to build outgoing messages from the vDC
to the vDSM (digitalSTROM server), including:
- Response messages (ResponseHello, ResponseGetProperty, GenericResponse)
- Push notifications (PushProperty, PushNotification)
- Announcement messages (AnnounceDevice, AnnounceVdc)
- Helper methods for PropertyElement creation

Based on genericVDC.proto specification.
"""

from __future__ import annotations

import logging
from typing import Any, Optional, Union

from . import genericVDC_pb2 as pb

_LOGGER = logging.getLogger(__name__)


class MessageBuilder:
    """Builder for creating vDC API protobuf messages."""
    
    def __init__(self, vdc_dsuid: str):
        """Initialize the message builder.
        
        Args:
            vdc_dsuid: The dSUID of this vDC (virtual device container)
        """
        self.vdc_dsuid = vdc_dsuid
    
    def create_response_hello(self, message_id: int = 0) -> pb.Message:
        """Create a ResponseHello message.
        
        Sent in response to vdsm_RequestHello during initial handshake.
        
        Args:
            message_id: Message ID to match the request
            
        Returns:
            ResponseHello message
        """
        msg = pb.Message()
        msg.type = pb.VDC_RESPONSE_HELLO
        msg.message_id = message_id
        
        response = msg.vdc_response_hello
        response.dSUID = self.vdc_dsuid
        
        _LOGGER.debug(f"Created ResponseHello for vDC {self.vdc_dsuid}")
        return msg
    
    def create_generic_response(
        self,
        code: pb.ResultCode = pb.ERR_OK,
        description: Optional[str] = None,
        message_id: int = 0,
    ) -> pb.Message:
        """Create a GenericResponse message.
        
        Used to acknowledge requests like SetProperty or to report errors.
        
        Args:
            code: Result code (ERR_OK, ERR_NOT_FOUND, etc.)
            description: Optional error description
            message_id: Message ID to match the request
            
        Returns:
            GenericResponse message
        """
        msg = pb.Message()
        msg.type = pb.GENERIC_RESPONSE
        msg.message_id = message_id
        
        response = msg.generic_response
        response.code = code
        if description:
            response.description = description
        
        _LOGGER.debug(f"Created GenericResponse: code={code}, desc={description}")
        return msg
    
    def create_response_get_property(
        self,
        properties: list[dict[str, Any]],
        message_id: int = 0,
    ) -> pb.Message:
        """Create a ResponseGetProperty message.
        
        Sent in response to vdsm_RequestGetProperty to return property values.
        
        Args:
            properties: List of property dictionaries with 'name' and 'value' keys
            message_id: Message ID to match the request
            
        Returns:
            ResponseGetProperty message
        """
        msg = pb.Message()
        msg.type = pb.VDC_RESPONSE_GET_PROPERTY
        msg.message_id = message_id
        
        response = msg.vdc_response_get_property
        
        # Build property elements
        for prop in properties:
            prop_elem = self._build_property_element(prop)
            response.properties.append(prop_elem)
        
        _LOGGER.debug(f"Created ResponseGetProperty with {len(properties)} properties")
        return msg
    
    def create_push_property(
        self,
        device_dsuid: str,
        properties: list[dict[str, Any]],
    ) -> pb.Message:
        """Create a PushProperty message.
        
        Used to push property changes from vDC to vDSM without being requested.
        
        Args:
            device_dsuid: dSUID of the device whose properties changed
            properties: List of property dictionaries with 'name' and 'value' keys
            
        Returns:
            PushProperty message
        """
        msg = pb.Message()
        msg.type = pb.VDC_SEND_PUSH_PROPERTY
        msg.message_id = 0  # Push messages don't have message IDs
        
        push = msg.vdc_send_push_property
        push.dSUID = device_dsuid
        
        # Build property elements
        for prop in properties:
            prop_elem = self._build_property_element(prop)
            push.properties.append(prop_elem)
        
        _LOGGER.debug(f"Created PushProperty for device {device_dsuid} with {len(properties)} properties")
        return msg
    
    def create_push_notification(
        self,
        device_dsuid: str,
        changed_properties: Optional[list[dict[str, Any]]] = None,
        device_events: Optional[list[dict[str, Any]]] = None,
    ) -> pb.Message:
        """Create a PushNotification message (API v2c and later).
        
        Used to notify vDSM of property changes and device events.
        
        Args:
            device_dsuid: dSUID of the device
            changed_properties: List of changed property dictionaries
            device_events: List of device event dictionaries
            
        Returns:
            PushNotification message
        """
        msg = pb.Message()
        msg.type = pb.VDC_SEND_PUSH_PROPERTY  # Note: Type is still PUSH_PROPERTY
        msg.message_id = 0
        
        # Note: The proto file shows vdc_SendPushNotification message type exists
        # but it's not in the Type enum. Using the structure from the .proto file
        # In practice, we might need to use a different approach or wait for
        # the proto to be updated. For now, using PushProperty.
        
        push = msg.vdc_send_push_property
        push.dSUID = device_dsuid
        
        # Build changed properties
        if changed_properties:
            for prop in changed_properties:
                prop_elem = self._build_property_element(prop)
                push.properties.append(prop_elem)
        
        # Device events would be added here if using the full PushNotification message
        # This is a placeholder for future API v2c support
        
        _LOGGER.debug(f"Created PushNotification for device {device_dsuid}")
        return msg
    
    def create_announce_device(
        self,
        device_dsuid: str,
    ) -> pb.Message:
        """Create an AnnounceDevice message.
        
        Sent when a new device is added to the vDC to inform vDSM.
        
        Args:
            device_dsuid: dSUID of the new device
            
        Returns:
            AnnounceDevice message
        """
        msg = pb.Message()
        msg.type = pb.VDC_SEND_ANNOUNCE_DEVICE
        msg.message_id = 0
        
        announce = msg.vdc_send_announce_device
        announce.dSUID = device_dsuid
        announce.vdc_dSUID = self.vdc_dsuid
        
        _LOGGER.info(f"Created AnnounceDevice for device {device_dsuid}")
        return msg
    
    def create_announce_vdc(self) -> pb.Message:
        """Create an AnnounceVdc message.
        
        Sent during initialization to announce this vDC to the vDSM.
        
        Returns:
            AnnounceVdc message
        """
        msg = pb.Message()
        msg.type = pb.VDC_SEND_ANNOUNCE_VDC
        msg.message_id = 0
        
        announce = msg.vdc_send_announce_vdc
        announce.dSUID = self.vdc_dsuid
        
        _LOGGER.info(f"Created AnnounceVdc for vDC {self.vdc_dsuid}")
        return msg
    
    def create_vanish(self, device_dsuid: str) -> pb.Message:
        """Create a Vanish message.
        
        Sent when a device is removed from the vDC.
        
        Args:
            device_dsuid: dSUID of the device being removed
            
        Returns:
            Vanish message
        """
        msg = pb.Message()
        msg.type = pb.VDC_SEND_VANISH
        msg.message_id = 0
        
        vanish = msg.vdc_send_vanish
        vanish.dSUID = device_dsuid
        
        _LOGGER.info(f"Created Vanish for device {device_dsuid}")
        return msg
    
    def create_pong(self, device_dsuid: str, message_id: int = 0) -> pb.Message:
        """Create a Pong message.
        
        Sent in response to vdsm_SendPing.
        
        Args:
            device_dsuid: dSUID to respond with (usually vDC or device)
            message_id: Message ID to match the ping
            
        Returns:
            Pong message
        """
        msg = pb.Message()
        msg.type = pb.VDC_SEND_PONG
        msg.message_id = message_id
        
        pong = msg.vdc_send_pong
        pong.dSUID = device_dsuid
        
        _LOGGER.debug(f"Created Pong for {device_dsuid}")
        return msg
    
    def _build_property_element(
        self,
        property_dict: dict[str, Any],
    ) -> pb.PropertyElement:
        """Build a PropertyElement from a dictionary.
        
        Handles nested properties and arrays.
        
        Args:
            property_dict: Dictionary with 'name', 'value', and optional 'elements' keys
            
        Returns:
            PropertyElement protobuf message
        """
        elem = pb.PropertyElement()
        
        if "name" in property_dict:
            elem.name = property_dict["name"]
        
        # Handle value
        if "value" in property_dict:
            value = property_dict["value"]
            prop_value = self._build_property_value(value)
            elem.value.CopyFrom(prop_value)
        
        # Handle nested elements (for objects and arrays)
        if "elements" in property_dict and isinstance(property_dict["elements"], list):
            for sub_elem_dict in property_dict["elements"]:
                sub_elem = self._build_property_element(sub_elem_dict)
                elem.elements.append(sub_elem)
        
        return elem
    
    def _build_property_value(self, value: Any) -> pb.PropertyValue:
        """Build a PropertyValue from a Python value.
        
        Args:
            value: Python value (bool, int, float, str, bytes)
            
        Returns:
            PropertyValue protobuf message
        """
        prop_value = pb.PropertyValue()
        
        if isinstance(value, bool):
            prop_value.v_bool = value
        elif isinstance(value, int):
            if value >= 0:
                prop_value.v_uint64 = value
            else:
                prop_value.v_int64 = value
        elif isinstance(value, float):
            prop_value.v_double = value
        elif isinstance(value, str):
            prop_value.v_string = value
        elif isinstance(value, bytes):
            prop_value.v_bytes = value
        else:
            # Default to string representation
            prop_value.v_string = str(value)
            _LOGGER.warning(f"Unknown value type {type(value)}, converting to string")
        
        return prop_value


def create_property_dict(
    name: str,
    value: Optional[Any] = None,
    elements: Optional[list[dict[str, Any]]] = None,
) -> dict[str, Any]:
    """Helper function to create a property dictionary.
    
    Args:
        name: Property name
        value: Property value (for simple properties)
        elements: Nested elements (for complex/array properties)
        
    Returns:
        Property dictionary suitable for message building
    """
    prop = {"name": name}
    
    if value is not None:
        prop["value"] = value
    
    if elements:
        prop["elements"] = elements
    
    return prop
