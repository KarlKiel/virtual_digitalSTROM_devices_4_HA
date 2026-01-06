"""Message handler for parsing and processing vDC API protobuf messages.

This module provides utilities to parse incoming messages from the vDSM
(digitalSTROM server) and route them to appropriate handlers.

Based on genericVDC.proto specification.
"""

from __future__ import annotations

import logging
from typing import Any, Callable, Optional

from . import genericVDC_pb2 as pb

_LOGGER = logging.getLogger(__name__)


class ParsedMessage:
    """Represents a parsed protobuf message with metadata."""
    
    def __init__(
        self,
        message_type: int,
        message_id: int,
        dsuid: Optional[str] = None,
        payload: Optional[Any] = None,
    ):
        """Initialize a parsed message.
        
        Args:
            message_type: Type enum value (from pb.Type)
            message_id: Message ID for request/response matching
            dsuid: dSUID from the message (if present)
            payload: The specific message payload (e.g., vdsm_RequestHello)
        """
        self.message_type = message_type
        self.message_id = message_id
        self.dsuid = dsuid
        self.payload = payload
    
    @property
    def type_name(self) -> str:
        """Get human-readable message type name."""
        return pb.Type.Name(self.message_type)
    
    def __repr__(self) -> str:
        """String representation of parsed message."""
        return (
            f"ParsedMessage(type={self.type_name}, "
            f"id={self.message_id}, dsuid={self.dsuid})"
        )


class MessageHandler:
    """Handler for parsing and routing vDC API protobuf messages."""
    
    def __init__(self):
        """Initialize the message handler."""
        self._handlers: dict[int, Callable] = {}
    
    def parse_message(self, data: bytes) -> Optional[ParsedMessage]:
        """Parse a protobuf message from bytes.
        
        Args:
            data: Raw protobuf message bytes
            
        Returns:
            ParsedMessage object or None if parsing fails
        """
        try:
            msg = pb.Message()
            msg.ParseFromString(data)
            
            message_type = msg.type
            message_id = msg.message_id if msg.HasField("message_id") else 0
            
            # Extract dSUID and payload based on message type
            dsuid, payload = self._extract_payload(msg, message_type)
            
            parsed = ParsedMessage(
                message_type=message_type,
                message_id=message_id,
                dsuid=dsuid,
                payload=payload,
            )
            
            _LOGGER.debug(f"Parsed message: {parsed}")
            return parsed
            
        except Exception as e:
            _LOGGER.error(f"Failed to parse message: {e}", exc_info=True)
            return None
    
    def register_handler(
        self,
        message_type: int,
        handler: Callable[[ParsedMessage], Any],
    ) -> None:
        """Register a handler for a specific message type.
        
        Args:
            message_type: Type enum value (from pb.Type)
            handler: Callable that takes a ParsedMessage and returns a response
        """
        self._handlers[message_type] = handler
        _LOGGER.debug(f"Registered handler for {pb.Type.Name(message_type)}")
    
    async def handle_message(
        self,
        parsed_msg: ParsedMessage,
    ) -> Optional[pb.Message]:
        """Route a parsed message to its registered handler.
        
        Args:
            parsed_msg: ParsedMessage object
            
        Returns:
            Response message or None if no handler or no response needed
        """
        handler = self._handlers.get(parsed_msg.message_type)
        
        if not handler:
            _LOGGER.warning(f"No handler registered for {parsed_msg.type_name}")
            return None
        
        try:
            _LOGGER.debug(f"Dispatching {parsed_msg.type_name} to handler")
            response = await handler(parsed_msg)
            return response
            
        except Exception as e:
            _LOGGER.error(
                f"Error handling {parsed_msg.type_name}: {e}",
                exc_info=True,
            )
            # Return error response
            # Note: vDC dSUID is not needed for generic error responses
            from .message_builder import MessageBuilder
            builder = MessageBuilder("")
            return builder.create_generic_response(
                code=pb.ERR_MESSAGE_UNKNOWN,
                description=f"Handler error: {str(e)}",
                message_id=parsed_msg.message_id,
            )
    
    def _extract_payload(
        self,
        msg: pb.Message,
        message_type: int,
    ) -> tuple[Optional[str], Optional[Any]]:
        """Extract dSUID and payload from a message based on type.
        
        Args:
            msg: Protobuf Message
            message_type: Type enum value
            
        Returns:
            Tuple of (dsuid, payload) where payload is the specific message object
        """
        dsuid = None
        payload = None
        
        # Requests
        if message_type == pb.VDSM_REQUEST_HELLO:
            if msg.HasField("vdsm_request_hello"):
                payload = msg.vdsm_request_hello
                dsuid = payload.dSUID if payload.HasField("dSUID") else None
        
        elif message_type == pb.VDSM_REQUEST_GET_PROPERTY:
            if msg.HasField("vdsm_request_get_property"):
                payload = msg.vdsm_request_get_property
                dsuid = payload.dSUID if payload.HasField("dSUID") else None
        
        elif message_type == pb.VDSM_REQUEST_SET_PROPERTY:
            if msg.HasField("vdsm_request_set_property"):
                payload = msg.vdsm_request_set_property
                dsuid = payload.dSUID if payload.HasField("dSUID") else None
        
        elif message_type == pb.VDSM_REQUEST_GENERIC_REQUEST:
            if msg.HasField("vdsm_request_generic_request"):
                payload = msg.vdsm_request_generic_request
                dsuid = payload.dSUID if payload.HasField("dSUID") else None
        
        # Pings and control messages
        elif message_type == pb.VDSM_SEND_PING:
            if msg.HasField("vdsm_send_ping"):
                payload = msg.vdsm_send_ping
                dsuid = payload.dSUID if payload.HasField("dSUID") else None
        
        elif message_type == pb.VDSM_SEND_REMOVE:
            if msg.HasField("vdsm_send_remove"):
                payload = msg.vdsm_send_remove
                dsuid = payload.dSUID if payload.HasField("dSUID") else None
        
        elif message_type == pb.VDSM_SEND_BYE:
            if msg.HasField("vdsm_send_bye"):
                payload = msg.vdsm_send_bye
                dsuid = payload.dSUID if payload.HasField("dSUID") else None
        
        # Scene notifications
        elif message_type == pb.VDSM_NOTIFICATION_CALL_SCENE:
            if msg.HasField("vdsm_send_call_scene"):
                payload = msg.vdsm_send_call_scene
                # Note: CallScene has repeated dSUID field
                if len(payload.dSUID) > 0:
                    dsuid = payload.dSUID[0]  # Take first device
        
        elif message_type == pb.VDSM_NOTIFICATION_SAVE_SCENE:
            if msg.HasField("vdsm_send_save_scene"):
                payload = msg.vdsm_send_save_scene
                if len(payload.dSUID) > 0:
                    dsuid = payload.dSUID[0]
        
        elif message_type == pb.VDSM_NOTIFICATION_UNDO_SCENE:
            if msg.HasField("vdsm_send_undo_scene"):
                payload = msg.vdsm_send_undo_scene
                if len(payload.dSUID) > 0:
                    dsuid = payload.dSUID[0]
        
        elif message_type == pb.VDSM_NOTIFICATION_SET_LOCAL_PRIO:
            if msg.HasField("vdsm_send_set_local_prio"):
                payload = msg.vdsm_send_set_local_prio
                if len(payload.dSUID) > 0:
                    dsuid = payload.dSUID[0]
        
        elif message_type == pb.VDSM_NOTIFICATION_CALL_MIN_SCENE:
            if msg.HasField("vdsm_send_call_min_scene"):
                payload = msg.vdsm_send_call_min_scene
                if len(payload.dSUID) > 0:
                    dsuid = payload.dSUID[0]
        
        # Device notifications
        elif message_type == pb.VDSM_NOTIFICATION_IDENTIFY:
            if msg.HasField("vdsm_send_identify"):
                payload = msg.vdsm_send_identify
                if len(payload.dSUID) > 0:
                    dsuid = payload.dSUID[0]
        
        elif message_type == pb.VDSM_NOTIFICATION_SET_CONTROL_VALUE:
            if msg.HasField("vdsm_send_set_control_value"):
                payload = msg.vdsm_send_set_control_value
                if len(payload.dSUID) > 0:
                    dsuid = payload.dSUID[0]
        
        elif message_type == pb.VDSM_NOTIFICATION_DIM_CHANNEL:
            if msg.HasField("vdsm_send_dim_channel"):
                payload = msg.vdsm_send_dim_channel
                if len(payload.dSUID) > 0:
                    dsuid = payload.dSUID[0]
        
        elif message_type == pb.VDSM_NOTIFICATION_SET_OUTPUT_CHANNEL_VALUE:
            if msg.HasField("vdsm_send_output_channel_value"):
                payload = msg.vdsm_send_output_channel_value
                if len(payload.dSUID) > 0:
                    dsuid = payload.dSUID[0]
        
        return dsuid, payload


def extract_property_value(prop_value: pb.PropertyValue) -> Any:
    """Extract Python value from a PropertyValue protobuf message.
    
    Args:
        prop_value: PropertyValue protobuf message
        
    Returns:
        Python value (bool, int, float, str, or bytes)
    """
    if prop_value.HasField("v_bool"):
        return prop_value.v_bool
    elif prop_value.HasField("v_uint64"):
        return prop_value.v_uint64
    elif prop_value.HasField("v_int64"):
        return prop_value.v_int64
    elif prop_value.HasField("v_double"):
        return prop_value.v_double
    elif prop_value.HasField("v_string"):
        return prop_value.v_string
    elif prop_value.HasField("v_bytes"):
        return prop_value.v_bytes
    else:
        return None


def extract_property_elements(
    elements: list[pb.PropertyElement],
) -> list[dict[str, Any]]:
    """Extract a list of property elements into Python dictionaries.
    
    Args:
        elements: List of PropertyElement protobuf messages
        
    Returns:
        List of dictionaries with 'name', 'value', and optional 'elements' keys
    """
    result = []
    
    for elem in elements:
        prop_dict = {}
        
        if elem.HasField("name"):
            prop_dict["name"] = elem.name
        
        if elem.HasField("value"):
            prop_dict["value"] = extract_property_value(elem.value)
        
        if len(elem.elements) > 0:
            prop_dict["elements"] = extract_property_elements(elem.elements)
        
        result.append(prop_dict)
    
    return result
