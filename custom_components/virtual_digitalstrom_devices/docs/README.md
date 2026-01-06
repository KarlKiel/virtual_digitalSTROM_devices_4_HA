# Documentation Index

This folder contains all documentation for the Virtual digitalSTROM Devices integration.

## Structure

### `implementation/`
Technical documentation about how the integration works:

- **DEVICE_CLASSES.md**: digitalSTROM device classifications and color groups
- **DEVICE_STORAGE.md**: How devices are persisted to YAML
- **DEVICE_CREATION_UI.md**: User interface flow for creating devices
- **STATE_RESTORATION.md**: State restoration system on startup
- **STATE_LISTENER_SYSTEM.md**: Entity state tracking system
- **PROPERTY_UPDATE_SYSTEM.md**: Property update and persistence
- **VDC_ENTITY.md**: vDC entity management
- **VDC_MESSAGE_HANDLING.md**: vDC protocol message handling
- **UI_MOCKUPS.md**: Visual mockups of the user interface
- **IMPLEMENTATION_SUMMARY.md**: Overall implementation summary
- **COMPLETE_PROPERTY_CLASSIFICATION.md**: Complete property classifications
- **PROPERTY_CLASSIFICATION_PROPOSAL.md**: Property classification proposals
- **PROPERTY_CLASSIFICATION_UPDATES.md**: Updates to property classifications

### `examples/`
Example scripts demonstrating how to use the integration components:

- **example_device_classes.py**: Working with device classes
- **example_device_storage.py**: Using the device storage system
- **example_message_handling.py**: Handling vDC protocol messages
- **example_property_updates.py**: Updating device properties
- **example_state_listeners.py**: Setting up state listeners
- **example_state_restoration.py**: Restoring device states

### `api/`
API reference documentation (to be populated)

## Quick Start

1. **Understanding Device Classes**: Start with `implementation/DEVICE_CLASSES.md`
2. **Creating Devices**: See `implementation/DEVICE_CREATION_UI.md`
3. **Device Storage**: Read `implementation/DEVICE_STORAGE.md`
4. **State Management**: Check `implementation/STATE_LISTENER_SYSTEM.md`

## External References

Additional reference materials are located in `/docs/external/`:
- digitalSTROM specifications (ds-basics.pdf)
- vDC API documentation (vDC-API.pdf)
- Other protocol documentation

## Contributing

When adding new documentation:
- Technical docs go in `implementation/`
- Example code goes in `examples/`
- API docs go in `api/`
- Keep docs focused and well-organized
- Cross-reference related documents
