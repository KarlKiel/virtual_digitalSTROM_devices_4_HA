"""Examples demonstrating property update system for virtual digitalSTROM devices.

This script shows how to update CONFIG and STATE properties with:
- CONFIG updates: Always persisted to YAML
- STATE updates: 
  - OUTPUT/CONTROL properties: Pushed to mapped HA entities + selective persistence
  - INPUT properties (sensors, binary inputs): Persisted only, NOT pushed to HA (read-only)
"""

from homeassistant.core import HomeAssistant

from .device_storage import DeviceStorage
from .property_updater import PropertyUpdater
from .state_listener import StatePropertyType
from .virtual_device import VirtualDevice


async def example_1_update_config_properties(
    hass: HomeAssistant,
    updater: PropertyUpdater,
):
    """Example 1: Update CONFIG properties (device description).
    
    CONFIG properties describe the device and are always persisted to YAML.
    """
    print("\n=== Example 1: Update CONFIG Properties ===\n")
    
    device_id = "living_room_light"
    
    # Update single CONFIG property
    await updater.update_property(
        device_id=device_id,
        property_type="name",
        value="Living Room Main Light",
    )
    print(f"✓ Updated device name")
    
    # Update zone assignment
    await updater.update_property(
        device_id=device_id,
        property_type="zone_id",
        value=5,
    )
    print(f"✓ Updated zone_id to zone 5")
    
    # Update model information
    await updater.update_property(
        device_id=device_id,
        property_type="model_version",
        value="2.0.0",
    )
    print(f"✓ Updated model_version to 2.0.0")
    
    # Update nested attribute
    await updater.config_updater.update_config_property(
        device_id=device_id,
        property_path="attributes.num_channels",
        value=4,
    )
    print(f"✓ Updated num_channels attribute")
    
    # All changes automatically persisted to YAML


async def example_2_update_state_properties(
    hass: HomeAssistant,
    updater: PropertyUpdater,
):
    """Example 2: Update STATE properties with HA entity push.
    
    STATE properties are runtime values that get pushed to mapped HA entities.
    """
    print("\n=== Example 2: Update STATE Properties ===\n")
    
    device_id = "living_room_light"
    
    # Update channel value (brightness)
    # This will:
    # 1. Push value to mapped HA entity (light.living_room)
    # 2. Persist value locally for display after restart
    await updater.update_property(
        device_id=device_id,
        property_type=StatePropertyType.CHANNEL_VALUE.value,
        value=75.0,  # 75% brightness
        index=0,  # First channel
    )
    print(f"✓ Updated channel[0] to 75% (pushed to HA entity)")
    
    # Update sensor value (READ-ONLY INPUT)
    # Sensor values are INPUT properties (read from HA entities via listeners)
    # They are NOT pushed back to HA entities (read-only)
    # We persist the value to avoid waiting for slow sensors after restart
    await updater.update_property(
        device_id=device_id,
        property_type=StatePropertyType.SENSOR_VALUE.value,
        value=23.5,  # Temperature reading
        index=0,
        persist_state=True,  # Force persistence
    )
    print(f"✓ Updated sensor[0] to 23.5°C (persisted only, NOT pushed - read-only input)")
    
    # Update button value (transient event, READ-ONLY INPUT)
    # Button clicks are INPUT events (read from HA entities)
    # NOT pushed back to HA entities and not persisted by default
    await updater.update_property(
        device_id=device_id,
        property_type=StatePropertyType.BUTTON_VALUE.value,
        value=True,  # Button pressed
        index=0,
        persist_state=False,  # Don't persist transient event
    )
    print(f"✓ Updated button[0] to pressed (pushed to HA entity, not persisted)")


async def example_3_critical_control_values(
    hass: HomeAssistant,
    updater: PropertyUpdater,
):
    """Example 3: Update critical control values (heating radiator use case).
    
    Control values MUST be persisted to ensure device functionality during
    DSS connection interruptions.
    """
    print("\n=== Example 3: Critical Control Values ===\n")
    
    device_id = "heating_radiator_bedroom"
    
    # Update heating level (target temperature)
    # CRITICAL: Must persist so radiator continues working if DSS connection breaks
    await updater.update_property(
        device_id=device_id,
        property_type=StatePropertyType.CONTROL_HEATING_LEVEL.value,
        value=21.5,  # 21.5°C target
        # persist_state=True is automatic for control values
    )
    print(f"✓ Updated heating level to 21.5°C (CRITICAL - auto-persisted)")
    
    # Update cooling level
    await updater.update_property(
        device_id="climate_living_room",
        property_type=StatePropertyType.CONTROL_COOLING_LEVEL.value,
        value=24.0,  # 24°C cooling target
    )
    print(f"✓ Updated cooling level to 24.0°C (CRITICAL - auto-persisted)")
    
    # Update ventilation level
    await updater.update_property(
        device_id="ventilation_system",
        property_type=StatePropertyType.CONTROL_VENTILATION_LEVEL.value,
        value=50.0,  # 50% fan speed
    )
    print(f"✓ Updated ventilation level to 50% (CRITICAL - auto-persisted)")


async def example_4_batch_updates(
    hass: HomeAssistant,
    updater: PropertyUpdater,
):
    """Example 4: Batch update multiple properties.
    
    For efficiency, update multiple properties in a single transaction.
    """
    print("\n=== Example 4: Batch Updates ===\n")
    
    device_id = "rgb_light_bedroom"
    
    # Batch CONFIG updates
    config_updates = {
        "name": "Bedroom RGB Light Strip",
        "zone_id": 3,
        "attributes.num_channels": 4,
    }
    await updater.config_updater.update_multiple_config_properties(
        device_id=device_id,
        updates=config_updates,
    )
    print(f"✓ Updated {len(config_updates)} CONFIG properties in batch")
    
    # Batch STATE updates
    state_updates = {
        (StatePropertyType.CHANNEL_VALUE, 0): 100.0,  # Brightness to 100%
        (StatePropertyType.CHANNEL_VALUE, 1): 255.0,  # Red to max
        (StatePropertyType.CHANNEL_VALUE, 2): 0.0,    # Green to 0
        (StatePropertyType.CHANNEL_VALUE, 3): 0.0,    # Blue to 0
    }
    await updater.state_updater.update_multiple_state_properties(
        device_id=device_id,
        updates=state_updates,
        persist=True,
    )
    print(f"✓ Updated 4 channel values in batch (RGB: red at full brightness)")


async def example_5_indexed_config_properties(
    hass: HomeAssistant,
    updater: PropertyUpdater,
):
    """Example 5: Update indexed CONFIG properties.
    
    Many CONFIG properties are arrays (buttonInputSettings, sensorInputSettings, etc.)
    """
    print("\n=== Example 5: Indexed CONFIG Properties ===\n")
    
    device_id = "button_panel_8"
    
    # Update button input setting for button 0
    await updater.config_updater.update_config_property(
        device_id=device_id,
        property_path="buttonInputSettings[0].group",
        value=1,  # Yellow group (lights)
        index=0,
    )
    print(f"✓ Updated buttonInputSettings[0].group to 1 (lights)")
    
    # Update button input setting for button 1
    await updater.config_updater.update_config_property(
        device_id=device_id,
        property_path="buttonInputSettings[1].group",
        value=2,  # Gray group (blinds)
        index=1,
    )
    print(f"✓ Updated buttonInputSettings[1].group to 2 (blinds)")
    
    # Update sensor input description
    await updater.config_updater.update_config_property(
        device_id="multi_sensor",
        property_path="sensorInputDescriptions[0].name",
        value="Temperature Sensor",
        index=0,
    )
    print(f"✓ Updated sensorInputDescriptions[0].name")
    
    # Update channel description
    await updater.config_updater.update_config_property(
        device_id="rgb_light",
        property_path="channelDescriptions[0].name",
        value="Brightness",
        index=0,
    )
    print(f"✓ Updated channelDescriptions[0].name")


async def example_6_multi_instance_state_updates(
    hass: HomeAssistant,
    updater: PropertyUpdater,
):
    """Example 6: Update STATE properties for devices with multiple instances.
    
    Many devices have multiple buttons, sensors, or channels.
    """
    print("\n=== Example 6: Multi-Instance STATE Updates ===\n")
    
    # 8-button control panel
    device_id = "button_panel_8"
    
    for i in range(8):
        await updater.update_property(
            device_id=device_id,
            property_type=StatePropertyType.BUTTON_VALUE.value,
            value=False,  # All buttons released
            index=i,
            persist_state=False,  # Don't persist button events
        )
    print(f"✓ Updated 8 button values")
    
    # Multi-zone climate system (3 zones)
    for zone_idx in range(3):
        # Each zone has heating, cooling, and ventilation controls
        await updater.update_property(
            device_id=f"climate_zone_{zone_idx}",
            property_type=StatePropertyType.CONTROL_HEATING_LEVEL.value,
            value=20.0 + zone_idx,  # Different temp per zone
            index=0,
        )
    print(f"✓ Updated 3 zone heating levels")
    
    # RGB+W light (4 channels)
    rgb_values = [100.0, 255.0, 128.0, 64.0]  # Brightness, R, G, B
    for i, value in enumerate(rgb_values):
        await updater.update_property(
            device_id="rgb_light",
            property_type=StatePropertyType.CHANNEL_VALUE.value,
            value=value,
            index=i,
        )
    print(f"✓ Updated 4 channel values (RGBW)")


async def example_7_connection_status_update(
    hass: HomeAssistant,
    updater: PropertyUpdater,
):
    """Example 7: Update connection and system status.
    
    These STATE properties track device connectivity and operational status.
    """
    print("\n=== Example 7: Connection and System Status ===\n")
    
    device_id = "network_device"
    
    # Update connection status
    await updater.update_property(
        device_id=device_id,
        property_type=StatePropertyType.CONNECTION_STATUS.value,
        value="connected",
        persist_state=True,  # Persist to show status after restart
    )
    print(f"✓ Updated connection_status to 'connected'")
    
    # Update system status
    await updater.update_property(
        device_id=device_id,
        property_type=StatePropertyType.SYSTEM_STATUS.value,
        value="operational",
        persist_state=True,
    )
    print(f"✓ Updated system_status to 'operational'")
    
    # Update programming mode
    await updater.update_property(
        device_id=device_id,
        property_type=StatePropertyType.PROG_MODE.value,
        value=False,
        persist_state=True,
    )
    print(f"✓ Updated progMode to False")


async def example_8_error_handling(
    hass: HomeAssistant,
    updater: PropertyUpdater,
):
    """Example 8: Error handling for property updates."""
    print("\n=== Example 8: Error Handling ===\n")
    
    from .property_updater import PropertyUpdateError
    
    # Try to update non-existent device
    try:
        await updater.update_property(
            device_id="non_existent_device",
            property_type="name",
            value="Test",
        )
    except PropertyUpdateError as e:
        print(f"✓ Caught expected error: {e}")
    
    # Try to update with invalid value type (will be logged but may succeed)
    try:
        await updater.update_property(
            device_id="test_device",
            property_type=StatePropertyType.CHANNEL_VALUE.value,
            value="invalid_number",  # Should be numeric
            index=0,
        )
    except Exception as e:
        print(f"✓ Caught type error: {e}")


async def example_9_complete_workflow(
    hass: HomeAssistant,
    storage: DeviceStorage,
):
    """Example 9: Complete workflow - create device, configure, update states.
    
    This demonstrates the full lifecycle of a virtual device.
    """
    print("\n=== Example 9: Complete Workflow ===\n")
    
    # 1. Create a new RGB light device
    device = VirtualDevice(
        device_id="rgb_light_kitchen",
        dsid="550e8400-e29b-41d4-a716-446655440000",
        display_id="RGBLIGHT-KITCHEN-001",
        type="vdSD",
        model="Virtual RGB Light",
        model_version="1.0.0",
        model_uid="vdSD-rgb-light-v1",
        name="Kitchen RGB Light",
        group_id=1,  # Lights group
        zone_id=4,   # Kitchen zone
        attributes={
            "num_channels": 4,  # Brightness + RGB
            "entity_mappings": {
                "channel[0].value": "light.kitchen_rgb",
                "channel[1].value": "light.kitchen_rgb@red",
                "channel[2].value": "light.kitchen_rgb@green",
                "channel[3].value": "light.kitchen_rgb@blue",
            }
        }
    )
    storage.add_device(device)
    print(f"✓ Created device: {device.name}")
    
    # 2. Initialize property updater
    updater = PropertyUpdater(hass, storage)
    
    # 3. Update CONFIG properties (device settings)
    await updater.config_updater.update_config_property(
        device_id=device.device_id,
        property_path="channelDescriptions[0].name",
        value="Master Brightness",
        index=0,
    )
    print(f"✓ Configured channel descriptions")
    
    # 4. Update STATE properties (runtime values)
    # Set initial color: White at 50% brightness
    state_updates = {
        (StatePropertyType.CHANNEL_VALUE, 0): 50.0,   # Brightness
        (StatePropertyType.CHANNEL_VALUE, 1): 255.0,  # Red
        (StatePropertyType.CHANNEL_VALUE, 2): 255.0,  # Green
        (StatePropertyType.CHANNEL_VALUE, 3): 255.0,  # Blue
    }
    await updater.state_updater.update_multiple_state_properties(
        device_id=device.device_id,
        updates=state_updates,
        persist=True,
    )
    print(f"✓ Set initial color to white at 50%")
    
    # 5. Simulate color change: Blue at full brightness
    state_updates = {
        (StatePropertyType.CHANNEL_VALUE, 0): 100.0,  # Brightness to 100%
        (StatePropertyType.CHANNEL_VALUE, 1): 0.0,    # Red off
        (StatePropertyType.CHANNEL_VALUE, 2): 0.0,    # Green off
        (StatePropertyType.CHANNEL_VALUE, 3): 255.0,  # Blue full
    }
    await updater.state_updater.update_multiple_state_properties(
        device_id=device.device_id,
        updates=state_updates,
        persist=True,
    )
    print(f"✓ Changed color to blue at full brightness")
    
    print(f"\n✓ Workflow complete - all changes persisted to YAML")


async def main():
    """Run all examples."""
    print("=" * 60)
    print("Property Update System Examples")
    print("=" * 60)
    
    # Note: These examples require a running Home Assistant instance
    # In real usage, you would get hass from the integration setup
    
    print("\nThese examples demonstrate:")
    print("- CONFIG property updates (always persisted)")
    print("- STATE property updates (pushed to HA entities + selective persistence)")
    print("- Batch updates for efficiency")
    print("- Multi-instance property handling")
    print("- Critical control value persistence")
    print("- Error handling")
    print("\nSee the code for implementation details.")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
