"""Example integration script for vDC API message handling.

This example demonstrates how to set up and use the message handling
system to communicate with a digitalSTROM server (vDSM).

This is a reference implementation showing the patterns. Actual usage
would integrate with Home Assistant's async architecture.
"""

import asyncio
import logging
from pathlib import Path

# Import the message handling components
from message_builder import MessageBuilder, create_property_dict
from message_handler import MessageHandler
from vdc_message_dispatcher import VdcMessageDispatcher
import genericVDC_pb2 as pb

# These would come from the actual integration
# from homeassistant.core import HomeAssistant
# from .device_storage import DeviceStorage
# from .property_updater import PropertyUpdater

logging.basicConfig(level=logging.DEBUG)
_LOGGER = logging.getLogger(__name__)


class ExampleVdcIntegration:
    """Example vDC integration showing message handling setup."""
    
    def __init__(self, vdc_dsuid: str):
        """Initialize the example integration.
        
        Args:
            vdc_dsuid: The dSUID for this vDC
        """
        self.vdc_dsuid = vdc_dsuid
        
        # In real implementation, these would be initialized from HA
        # self.hass = hass
        # self.device_storage = DeviceStorage(storage_path)
        # self.property_updater = PropertyUpdater(hass, device_storage)
        
        # Initialize message handling components
        self.message_handler = MessageHandler()
        self.message_builder = MessageBuilder(vdc_dsuid)
        
        # In real implementation:
        # self.dispatcher = VdcMessageDispatcher(
        #     hass=hass,
        #     vdc_dsuid=vdc_dsuid,
        #     device_storage=device_storage,
        #     property_updater=property_updater,
        # )
        
        # Register message handlers
        self._register_handlers()
    
    def _register_handlers(self):
        """Register handlers for different message types."""
        
        # Register request handlers (expect responses)
        self.message_handler.register_handler(
            pb.VDSM_REQUEST_HELLO,
            self._handle_hello,  # In real: dispatcher.handle_request_hello
        )
        
        self.message_handler.register_handler(
            pb.VDSM_REQUEST_GET_PROPERTY,
            self._handle_get_property,  # In real: dispatcher.handle_request_get_property
        )
        
        self.message_handler.register_handler(
            pb.VDSM_REQUEST_SET_PROPERTY,
            self._handle_set_property,  # In real: dispatcher.handle_request_set_property
        )
        
        self.message_handler.register_handler(
            pb.VDSM_SEND_PING,
            self._handle_ping,  # In real: dispatcher.handle_send_ping
        )
        
        # Register notification handlers (no response expected)
        self.message_handler.register_handler(
            pb.VDSM_NOTIFICATION_CALL_SCENE,
            self._handle_call_scene,  # In real: dispatcher.handle_notification_call_scene
        )
        
        self.message_handler.register_handler(
            pb.VDSM_NOTIFICATION_SET_OUTPUT_CHANNEL_VALUE,
            self._handle_set_channel,  # In real: dispatcher.handle_notification_set_output_channel_value
        )
        
        _LOGGER.info(f"Registered {len(self.message_handler._handlers)} message handlers")
    
    # Example handler implementations (simplified)
    
    async def _handle_hello(self, parsed_msg):
        """Example hello handler."""
        _LOGGER.info(f"Received HELLO from vDSM: {parsed_msg.dsuid}")
        return self.message_builder.create_response_hello(parsed_msg.message_id)
    
    async def _handle_get_property(self, parsed_msg):
        """Example get property handler."""
        _LOGGER.info(f"Received GET_PROPERTY for: {parsed_msg.dsuid}")
        
        # Example: return some properties
        properties = [
            create_property_dict("name", "Example Device"),
            create_property_dict("zoneID", 1),
            create_property_dict("primaryGroup", 1),
        ]
        
        return self.message_builder.create_response_get_property(
            properties=properties,
            message_id=parsed_msg.message_id,
        )
    
    async def _handle_set_property(self, parsed_msg):
        """Example set property handler."""
        _LOGGER.info(f"Received SET_PROPERTY for: {parsed_msg.dsuid}")
        
        return self.message_builder.create_generic_response(
            code=pb.ERR_OK,
            message_id=parsed_msg.message_id,
        )
    
    async def _handle_ping(self, parsed_msg):
        """Example ping handler."""
        _LOGGER.debug(f"Received PING for: {parsed_msg.dsuid}")
        
        return self.message_builder.create_pong(
            device_dsuid=parsed_msg.dsuid or self.vdc_dsuid,
            message_id=parsed_msg.message_id,
        )
    
    async def _handle_call_scene(self, parsed_msg):
        """Example call scene handler (notification - no response)."""
        payload = parsed_msg.payload
        _LOGGER.info(
            f"Received CALL_SCENE: devices={list(payload.dSUID)}, "
            f"scene={payload.scene}"
        )
        # No response for notifications
        return None
    
    async def _handle_set_channel(self, parsed_msg):
        """Example set channel handler (notification - no response)."""
        payload = parsed_msg.payload
        _LOGGER.info(
            f"Received SET_OUTPUT_CHANNEL_VALUE: devices={list(payload.dSUID)}, "
            f"channel={payload.channel}, value={payload.value}"
        )
        # No response for notifications
        return None
    
    async def process_incoming_message(self, data: bytes) -> bytes | None:
        """Process an incoming protobuf message.
        
        Args:
            data: Raw protobuf message bytes from vDSM
            
        Returns:
            Response bytes to send back, or None if no response
        """
        # Parse the message
        parsed_msg = self.message_handler.parse_message(data)
        
        if not parsed_msg:
            _LOGGER.error("Failed to parse incoming message")
            return None
        
        _LOGGER.info(f"Processing message: {parsed_msg}")
        
        # Handle the message
        response = await self.message_handler.handle_message(parsed_msg)
        
        # Serialize response if available
        if response:
            response_bytes = response.SerializeToString()
            _LOGGER.debug(f"Sending response: {len(response_bytes)} bytes")
            return response_bytes
        
        return None
    
    async def announce_vdc(self) -> bytes:
        """Create and return vDC announcement message.
        
        Returns:
            Serialized announcement message bytes
        """
        msg = self.message_builder.create_announce_vdc()
        return msg.SerializeToString()
    
    async def announce_device(self, device_dsuid: str) -> bytes:
        """Create and return device announcement message.
        
        Args:
            device_dsuid: dSUID of device to announce
            
        Returns:
            Serialized announcement message bytes
        """
        msg = self.message_builder.create_announce_device(device_dsuid)
        return msg.SerializeToString()
    
    async def push_property_change(
        self,
        device_dsuid: str,
        properties: list[dict],
    ) -> bytes:
        """Create and return property push notification.
        
        Args:
            device_dsuid: dSUID of device with changed properties
            properties: List of property dicts with 'name' and 'value'
            
        Returns:
            Serialized push property message bytes
        """
        msg = self.message_builder.create_push_property(device_dsuid, properties)
        return msg.SerializeToString()


async def example_usage():
    """Example usage of the vDC integration."""
    
    # Initialize the integration
    vdc_dsuid = "0123456789ABCDEF0123456789ABCDEF01"  # Example vDC dSUID
    integration = ExampleVdcIntegration(vdc_dsuid)
    
    print("\n=== Example 1: Handling HELLO request ===")
    
    # Create a simulated hello request from vDSM
    hello_request = pb.Message()
    hello_request.type = pb.VDSM_REQUEST_HELLO
    hello_request.message_id = 1
    hello_request.vdsm_request_hello.dSUID = "FEDCBA9876543210FEDCBA9876543210"
    hello_request.vdsm_request_hello.api_version = 3
    
    # Serialize to bytes (simulating network reception)
    hello_bytes = hello_request.SerializeToString()
    
    # Process the message
    response_bytes = await integration.process_incoming_message(hello_bytes)
    
    if response_bytes:
        # Parse response for display
        response = pb.Message()
        response.ParseFromString(response_bytes)
        print(f"Response type: {pb.Type.Name(response.type)}")
        print(f"Response dSUID: {response.vdc_response_hello.dSUID}")
    
    print("\n=== Example 2: Handling GET_PROPERTY request ===")
    
    # Create a get property request
    get_prop_request = pb.Message()
    get_prop_request.type = pb.VDSM_REQUEST_GET_PROPERTY
    get_prop_request.message_id = 2
    get_prop_request.vdsm_request_get_property.dSUID = "ABCD1234ABCD1234ABCD1234ABCD1234"
    
    # Add query elements
    query_elem = get_prop_request.vdsm_request_get_property.query.add()
    query_elem.name = "name"
    
    query_elem2 = get_prop_request.vdsm_request_get_property.query.add()
    query_elem2.name = "zoneID"
    
    # Process the message
    response_bytes = await integration.process_incoming_message(
        get_prop_request.SerializeToString()
    )
    
    if response_bytes:
        response = pb.Message()
        response.ParseFromString(response_bytes)
        print(f"Response type: {pb.Type.Name(response.type)}")
        print(f"Properties returned: {len(response.vdc_response_get_property.properties)}")
        for prop in response.vdc_response_get_property.properties:
            print(f"  - {prop.name}: {prop.value.v_string if prop.value.HasField('v_string') else prop.value.v_uint64}")
    
    print("\n=== Example 3: Sending device announcement ===")
    
    # Announce a new device
    device_dsuid = "1111222233334444555566667777888899"
    announce_bytes = await integration.announce_device(device_dsuid)
    
    # Parse to show what was created
    announce_msg = pb.Message()
    announce_msg.ParseFromString(announce_bytes)
    print(f"Announcement type: {pb.Type.Name(announce_msg.type)}")
    print(f"Device dSUID: {announce_msg.vdc_send_announce_device.dSUID}")
    print(f"vDC dSUID: {announce_msg.vdc_send_announce_device.vdc_dSUID}")
    
    print("\n=== Example 4: Pushing property change ===")
    
    # Push a property change notification
    properties = [
        create_property_dict("channel[0].value", 75.5),
        create_property_dict("connectionStatus", 0),  # 0 = connected
    ]
    
    push_bytes = await integration.push_property_change(device_dsuid, properties)
    
    # Parse to show what was created
    push_msg = pb.Message()
    push_msg.ParseFromString(push_bytes)
    print(f"Push type: {pb.Type.Name(push_msg.type)}")
    print(f"Device dSUID: {push_msg.vdc_send_push_property.dSUID}")
    print(f"Properties: {len(push_msg.vdc_send_push_property.properties)}")
    for prop in push_msg.vdc_send_push_property.properties:
        print(f"  - {prop.name}")
    
    print("\n=== Example 5: Handling scene notification ===")
    
    # Create a call scene notification
    scene_notif = pb.Message()
    scene_notif.type = pb.VDSM_NOTIFICATION_CALL_SCENE
    scene_notif.message_id = 0  # Notifications have ID 0
    scene_notif.vdsm_send_call_scene.dSUID.append(device_dsuid)
    scene_notif.vdsm_send_call_scene.scene = 5
    scene_notif.vdsm_send_call_scene.force = False
    scene_notif.vdsm_send_call_scene.group = 1
    scene_notif.vdsm_send_call_scene.zone_id = 1
    
    # Process (notifications don't return responses)
    response_bytes = await integration.process_incoming_message(
        scene_notif.SerializeToString()
    )
    
    if response_bytes is None:
        print("Scene notification processed (no response expected)")
    
    print("\n=== Example complete ===")


if __name__ == "__main__":
    # Run the example
    asyncio.run(example_usage())
