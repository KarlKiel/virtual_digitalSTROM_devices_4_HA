# vDC Entity - Virtual Device Connector

## Overview

The vDC (Virtual Device Connector) entity represents the integration itself as a digitalSTROM virtual device connector. This entity is automatically created during the installation of the Home Assistant integration and persisted across restarts.

## Properties

The vDC entity is configured with the following properties as defined in the vDC-API-properties specification (July 2022), chapters 2 and 3:

### Chapter 2: Common Properties (Required)

| Property | Value | Description |
|----------|-------|-------------|
| `dsUID` | Generated from MAC address | digitalSTROM Unique Identifier (34 hex characters) |
| `displayId` | "KarlKiels generic vDC" | Human-readable identification |
| `type` | "vDC" | Entity type (vDC = Virtual Device Connector) |
| `model` | "vDC to control 3rd party devices in DS" | Device model description |
| `modelVersion` | "1.0" | Model/firmware version |
| `modelUID` | "SW-gvDC400" | Unique identifier for the functional model |
| `vendorName` | "KarlKiel" | Vendor/manufacturer name |
| `name` | "KarlKiels generic vDC" | Device name |

### Chapter 2: Common Properties (Optional)

These properties are available and persisted but initially empty. They can be set using the `update_vdc_property()` method:

| Property | Description |
|----------|-------------|
| `hardwareVersion` | Hardware version string |
| `hardwareGuid` | Hardware GUID in URN format (e.g., gs1:, macaddress:, uuid:) |
| `hardwareModelGuid` | Hardware model GUID |
| `vendorGuid` | Vendor GUID |
| `oemGuid` | OEM product GUID |
| `oemModelGuid` | OEM model GUID |
| `deviceClass` | Device class profile name |
| `deviceClassVersion` | Device class version |

### Chapter 3: vDC-Level Properties

These vDC-specific properties are available for advanced configuration:

| Property | Default Value | Description |
|----------|---------------|-------------|
| `implementationId` | "" (empty) | Implementation identifier |
| `configURL` | "" (empty) | Configuration web UI URL |
| `apiVersion` | "1.0" | vDC API version |

All properties are automatically persisted to YAML storage and preserved across updates and restarts.

## dsUID Generation

The `dsUID` (digitalSTROM Unique Identifier) is a 136-bit (17 bytes = 34 hex characters) unique identifier that is generated once during the initial installation and preserved across all subsequent restarts and updates.

### Generation Method

The dsUID is generated from the MAC address of the Home Assistant server using the existing `dsuid_generator` module:

1. Retrieve the MAC address using `uuid.getnode()`
2. Generate a UUIDv5 in the MAC namespace
3. Extend to 17 bytes (136 bits) for dSUID format
4. Convert to 34 uppercase hexadecimal characters

**Example dsUID:** `54BD4C445AC35C2698630AEB23F6BE4E00`

### Stability

The dsUID remains stable across:
- Integration restarts
- Home Assistant restarts
- Configuration updates (e.g., changing the DSS port)

This ensures consistent identification of the vDC entity in the digitalSTROM system.

## Configuration

During installation, the integration prompts for the following configuration:

### DSS TCP Port

The TCP port number for connecting to the digitalSTROM server (dSS).

- **Default:** 8440
- **Range:** 1-65535
- **Purpose:** Will be used for future TCP connection implementation to the dSS

## Persistence

The vDC configuration is persisted to a YAML file within the integration folder:

```
custom_components/virtual_digitalstrom_devices/virtual_digitalstrom_vdc_config.yaml
```

### Example YAML Structure

The YAML file includes all required Chapter 2 properties and optional properties (shown with empty values if not set):

```yaml
# Chapter 2: Required Common Properties
dsUID: 54BD4C445AC35C2698630AEB23F6BE4E00
displayId: KarlKiels generic vDC
type: vDC
model: vDC to control 3rd party devices in DS
modelVersion: '1.0'
modelUID: SW-gvDC400
vendorName: KarlKiel
name: KarlKiels generic vDC

# Chapter 2: Optional Common Properties
hardwareVersion: ''
hardwareGuid: ''
hardwareModelGuid: ''
vendorGuid: ''
oemGuid: ''
oemModelGuid: ''
deviceClass: ''
deviceClassVersion: ''

# Chapter 3: vDC-Level Properties
implementationId: ''
configURL: ''
apiVersion: '1.0'

# Integration Configuration
dss_port: 8440

# Metadata (timestamps)
created_at: '2026-01-06T08:15:54.591458'
updated_at: '2026-01-06T08:15:54.591458'
```

Note: Empty optional properties may be omitted from the YAML file but are still accessible programmatically.

## Lifecycle

### Installation

1. User installs the integration via Home Assistant UI
2. User provides the DSS TCP port (default: 8440)
3. Integration creates the vDC entity with:
   - Fixed properties (displayId, type, model, etc.)
   - Generated dsUID from MAC address
   - User-provided DSS port
4. Configuration is persisted to YAML file

### Startup

1. Integration loads on Home Assistant startup
2. VdcManager reads the persisted YAML configuration
3. vDC entity is restored with the same dsUID
4. Integration continues normal operation

### Updates

When the integration configuration is updated (e.g., changing the DSS port):
- The dsUID is preserved
- Required properties are updated with their defined values
- Optional Chapter 2 and Chapter 3 properties are preserved if previously set
- Timestamps are updated
- Configuration is saved to YAML

### Updating Optional Properties

Optional Chapter 2 and Chapter 3 properties can be updated programmatically:

```python
# Access vDC manager
vdc_manager = hass.data[DOMAIN][entry.entry_id]["vdc_manager"]

# Update an optional property
vdc_manager.update_vdc_property("hardwareVersion", "v2.1")
vdc_manager.update_vdc_property("configURL", "http://example.com/config")
vdc_manager.update_vdc_property("implementationId", "ha-vdc-impl-001")
```

Updatable properties include:
- `hardwareVersion`, `hardwareGuid`, `hardwareModelGuid`
- `vendorGuid`, `oemGuid`, `oemModelGuid`
- `deviceClass`, `deviceClassVersion`
- `implementationId`, `configURL`, `apiVersion`

## Implementation

### Core Components

1. **VdcManager** (`vdc_manager.py`)
   - Manages vDC entity lifecycle
   - Handles YAML persistence
   - Generates/retrieves dsUID
   - Provides access methods

2. **Integration Setup** (`__init__.py`)
   - Initializes VdcManager during setup
   - Creates/updates vDC entity
   - Stores manager in integration data

3. **Configuration Flow** (`config_flow.py`)
   - Prompts for DSS port
   - Validates input
   - Stores configuration

### Usage in Code

```python
# Access vDC configuration
vdc_manager = hass.data[DOMAIN][entry.entry_id]["vdc_manager"]
vdc_config = vdc_manager.get_vdc_config()

# Get specific properties
dsuid = vdc_manager.get_dsuid()
dss_port = vdc_manager.get_dss_port()

# Get all properties including Chapter 2 and Chapter 3
all_properties = vdc_manager.get_all_properties()

# Update optional properties
vdc_manager.update_vdc_property("hardwareVersion", "1.2.3")

# Check if vDC exists
if vdc_manager.has_vdc():
    # vDC is configured
    pass
```

## Future Enhancements

The DSS TCP port is configured but not yet used. Future implementations will:
- Establish TCP connection to the digitalSTROM server
- Use the vDC entity for communication with dSS
- Implement full vDC-API protocol support

## References

- vDC-API-properties specification (July 2022) - Chapters 2 and 3
- ds-basics.pdf - Chapter 13.3 (dSUID generation)
- `dsuid_generator.py` - dSUID generation implementation
- `vdc_manager.py` - vDC entity management
