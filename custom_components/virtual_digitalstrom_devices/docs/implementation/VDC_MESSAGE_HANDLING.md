# vDC API Message Handling - Usage Guide

This document explains how to use the vDC API message handling system to communicate with the digitalSTROM server (vDSM).

## Overview

The message handling system consists of three main components:

1. **MessageBuilder** (`message_builder.py`) - Creates outgoing protobuf messages
2. **MessageHandler** (`message_handler.py`) - Parses incoming protobuf messages
3. **VdcMessageDispatcher** (`vdc_message_dispatcher.py`) - Processes messages and integrates with device/property systems

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         vDSM (Server)                        │
└───────────────────────┬─────────────────────────────────────┘
                        │ Protobuf Messages
                        │ over TCP/IP
┌───────────────────────▼─────────────────────────────────────┐
│                    MessageHandler                            │
│  - Parse incoming protobuf bytes                             │
│  - Extract message type, ID, dSUID, payload                  │
│  - Route to registered handlers                              │
└───────────────────────┬─────────────────────────────────────┘
                        │ ParsedMessage
┌───────────────────────▼─────────────────────────────────────┐
│               VdcMessageDispatcher                           │
│  - Handle specific message types                             │
│  - Get/Set device properties                                 │
│  - Process scene notifications                               │
│  - Handle channel/control value changes                      │
└───────────────────────┬─────────────────────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
        ▼               ▼               ▼
┌──────────────┐ ┌─────────────┐ ┌──────────────┐
│DeviceStorage │ │PropertyUpdater│ │   HA Core    │
└──────────────┘ └─────────────┘ └──────────────┘
```

## Basic Usage

### 1. Initialize the Components

```python
from homeassistant.core import HomeAssistant
from .device_storage import DeviceStorage
from .property_updater import PropertyUpdater
from .message_handler import MessageHandler
from .message_builder import MessageBuilder
from .vdc_message_dispatcher import VdcMessageDispatcher
from . import genericVDC_pb2 as pb

# Initialize components
vdc_dsuid = "YOUR_VDC_DSUID_HERE"
device_storage = DeviceStorage(storage_path)
property_updater = PropertyUpdater(hass, device_storage)

# Create message handler and builder
message_handler = MessageHandler()
message_builder = MessageBuilder(vdc_dsuid)

# Create dispatcher
dispatcher = VdcMessageDispatcher(
    hass=hass,
    vdc_dsuid=vdc_dsuid,
    device_storage=device_storage,
    property_updater=property_updater,
)
```

### 2. Register Message Handlers

```python
# Register handlers for different message types
message_handler.register_handler(
    pb.VDSM_REQUEST_HELLO,
    dispatcher.handle_request_hello,
)

message_handler.register_handler(
    pb.VDSM_REQUEST_GET_PROPERTY,
    dispatcher.handle_request_get_property,
)

message_handler.register_handler(
    pb.VDSM_REQUEST_SET_PROPERTY,
    dispatcher.handle_request_set_property,
)

message_handler.register_handler(
    pb.VDSM_SEND_PING,
    dispatcher.handle_send_ping,
)

message_handler.register_handler(
    pb.VDSM_NOTIFICATION_CALL_SCENE,
    dispatcher.handle_notification_call_scene,
)

message_handler.register_handler(
    pb.VDSM_NOTIFICATION_SET_OUTPUT_CHANNEL_VALUE,
    dispatcher.handle_notification_set_output_channel_value,
)

# Register other handlers as needed...
```

### 3. Process Incoming Messages

```python
async def process_incoming_message(data: bytes):
    """Process an incoming protobuf message from vDSM."""
    
    # Parse the message
    parsed_msg = message_handler.parse_message(data)
    
    if not parsed_msg:
        _LOGGER.error("Failed to parse message")
        return None
    
    # Handle the message
    response = await message_handler.handle_message(parsed_msg)
    
    # Send response if available
    if response:
        response_bytes = response.SerializeToString()
        # Send response_bytes back to vDSM via your transport layer
        return response_bytes
    
    return None
```

### 4. Send Outgoing Messages

```python
async def announce_new_device(device_dsuid: str):
    """Announce a new device to the vDSM."""
    
    # Create announcement message
    msg = message_builder.create_announce_device(device_dsuid)
    
    # Serialize and send
    msg_bytes = msg.SerializeToString()
    # Send msg_bytes to vDSM via your transport layer
```

```python
async def push_property_change(device_dsuid: str, property_name: str, value: Any):
    """Push a property change notification to vDSM."""
    
    from .message_builder import create_property_dict
    
    # Build property list
    properties = [
        create_property_dict(property_name, value)
    ]
    
    # Create push property message
    msg = message_builder.create_push_property(device_dsuid, properties)
    
    # Serialize and send
    msg_bytes = msg.SerializeToString()
    # Send msg_bytes to vDSM via your transport layer
```

## Message Flow Examples

### Example 1: Initial Handshake

```
vDSM → vDC: VDSM_REQUEST_HELLO
            {
              dSUID: "vdsm_12345...",
              api_version: 3
            }

vDC → vDSM: VDC_RESPONSE_HELLO
            {
              dSUID: "vdc_67890..."
            }

vDC → vDSM: VDC_SEND_ANNOUNCE_VDC
            {
              dSUID: "vdc_67890..."
            }
```

### Example 2: Get Device Properties

```
vDSM → vDC: VDSM_REQUEST_GET_PROPERTY
            {
              dSUID: "device_abcde...",
              query: [
                {name: "name"},
                {name: "zoneID"},
                {name: "primaryGroup"}
              ]
            }

vDC → vDSM: VDC_RESPONSE_GET_PROPERTY
            {
              properties: [
                {name: "name", value: "Living Room Light"},
                {name: "zoneID", value: 1},
                {name: "primaryGroup", value: 1}
              ]
            }
```

### Example 3: Set Output Channel Value

```
vDSM → vDC: VDSM_NOTIFICATION_SET_OUTPUT_CHANNEL_VALUE
            {
              dSUID: ["device_abcde..."],
              channel: 0,
              value: 75.5,
              apply_now: true
            }

(No response expected - notification)
```

### Example 4: Property Change Push Notification

```
vDC → vDSM: VDC_SEND_PUSH_PROPERTY
            {
              dSUID: "device_abcde...",
              properties: [
                {
                  name: "channel[0].value",
                  value: 50.0
                }
              ]
            }

(No response expected unless error)
```

### Example 5: Call Scene

```
vDSM → vDC: VDSM_NOTIFICATION_CALL_SCENE
            {
              dSUID: ["device_1...", "device_2...", "device_3..."],
              scene: 5,
              force: false,
              group: 1,
              zone_id: 1
            }

(No response expected - notification)
```

## Property Handling

### Getting Properties

Properties are retrieved through the `_get_device_properties` method which:
1. Maps common vDC properties to device attributes
2. Includes state values if available
3. Returns only requested properties (or all if query is empty)

### Setting Properties

Properties are set through the `PropertyUpdater` which:
1. Routes CONFIG properties to `ConfigPropertyUpdater`
2. Routes STATE properties to `StatePropertyUpdater`
3. Handles persistence automatically
4. Pushes OUTPUT/CONTROL properties to HA entities

## Notification Handling

Notifications don't expect responses. The dispatcher processes them and:
- **Scene notifications**: Apply saved scene configuration to devices
- **Channel value notifications**: Update output channel values via PropertyUpdater
- **Control value notifications**: Update control values (heating, cooling, etc.)
- **Dim channel notifications**: Start/stop dimming operations

## Error Handling

When errors occur:
1. Parse errors return `None` from `parse_message()`
2. Handler errors return `GenericResponse` with error code
3. Common error codes:
   - `ERR_OK` (0) - Success
   - `ERR_NOT_FOUND` (11) - Device/property not found
   - `ERR_MESSAGE_UNKNOWN` (1) - Unknown message or handler error
   - `ERR_NOT_IMPLEMENTED` (6) - Feature not yet implemented

Example error response:
```python
return message_builder.create_generic_response(
    code=pb.ERR_NOT_FOUND,
    description="Device abc123 not found",
    message_id=parsed_msg.message_id,
)
```

## Integration with Existing Systems

The message handling system integrates with:

1. **DeviceStorage**: Get/save device configurations
2. **PropertyUpdater**: Update CONFIG and STATE properties
3. **Home Assistant Core**: Push values to HA entities via service calls
4. **State Listeners**: React to HA entity state changes (separate system)

## Transport Layer (Not Included)

The message handling system works with protobuf messages but doesn't include:
- TCP/IP connection management
- TLS/encryption
- Message framing/length prefixes
- Reconnection logic

You'll need to implement a transport layer that:
1. Establishes connection to vDSM
2. Receives raw bytes and calls `process_incoming_message()`
3. Sends outgoing message bytes to vDSM
4. Handles connection lifecycle

## Next Steps

To complete the vDC implementation:
1. Implement TCP/IP transport layer for vDSM connection
2. Add connection initialization sequence
3. Implement automatic device announcements on startup
4. Add push notifications when device states change
5. Handle vDSM disconnection/reconnection
6. Add comprehensive error handling and logging
