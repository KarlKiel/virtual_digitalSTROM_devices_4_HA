# dSUID Generator Documentation

## Overview

The dSUID (digitalSTROM Unique Identifier) Generator implements the dSUID generation rules from **ds-basics.pdf Chapter 13.3**. It generates proper 136-bit (17 byte) unique identifiers represented as 34 hexadecimal characters.

## What is a dSUID?

A dSUID is a unique identifier used by the digitalSTROM system to identify devices, vDCs, and other addressable entities. It is based on the RFC 4122 UUID standard but uses 17 bytes instead of 16 bytes.

**Format:** 34 hexadecimal characters (e.g., `F4E0230D657B553F926E8D0EDA91ACFE00`)

## Generation Rules (Priority Order)

The dSUID generator follows these prioritized rules from the specification:

1. **SGTIN-96 available** → Use the SGTIN-96 directly
2. **GTIN + serial number** → Generate UUIDv5 from SGTIN-128 in GS1 namespace
3. **Existing UUID** → Use the existing UUID
4. **Unique ID within device kind** → Generate UUIDv5 in relevant namespace (MAC, EnOcean, etc.)
5. **Nothing from above** → Generate random UUIDv4 (⚠️ **must be persisted!**)

## Module: `dsuid_generator.py`

### Quick Start

```python
from dsuid_generator import generate_dsuid

# Generate from Home Assistant entity ID (most common for this integration)
dsuid = generate_dsuid(unique_name="sensor.living_room_temperature")
# Result: 2571D9E639925FB3BF45889C00AC5CA100

# Generate from MAC address
dsuid = generate_dsuid(mac_address="45:A2:00:BC:73:B8")
# Result: A9E61F66F4E35E8B869DAED0012F178F00

# Generate from hardware GUID (auto-detects format)
dsuid = generate_dsuid(hardware_guid="macaddress:12:34:56:78:90:AB")
# Result: DB083BE1C1FC5B66AF28F8F2444BAAC900
```

### Main Function: `generate_dsuid()`

```python
def generate_dsuid(
    sgtin96: Optional[SGTIN96] = None,
    gtin: Optional[str] = None,
    serial: Optional[str] = None,
    existing_uuid: Optional[str] = None,
    hardware_guid: Optional[str] = None,
    mac_address: Optional[str] = None,
    enocean_address: Optional[str] = None,
    unique_name: Optional[str] = None,
) -> str:
    """Generate dSUID following prioritized rules."""
```

**Parameters:**
- `sgtin96`: SGTIN96 structure (priority 1)
- `gtin`: GTIN number (priority 2, requires `serial`)
- `serial`: Serial number (priority 2, requires `gtin`)
- `existing_uuid`: Existing UUID string (priority 3)
- `hardware_guid`: Hardware GUID in URN format (priority 4, auto-detects format)
- `mac_address`: MAC address (priority 4)
- `enocean_address`: EnOcean address (priority 4)
- `unique_name`: Unique identifier/name (priority 4)

**Returns:** 34-character hex string

### Supported Hardware GUID Formats

The `hardware_guid` parameter supports auto-detection of these formats:

```python
# GS1 format with GTIN and serial
generate_dsuid(hardware_guid="gs1:(01)4050300870342(21)3696724640")

# MAC address
generate_dsuid(hardware_guid="macaddress:45:A2:00:BC:73:B8")

# EnOcean address
generate_dsuid(hardware_guid="enoceanaddress:A4BC23D2")

# UUID
generate_dsuid(hardware_guid="uuid:2f402f80-ea50-11e1-9b23-001778216465")

# Any other format (used as unique name)
generate_dsuid(hardware_guid="vendorname:CustomDevice123")
```

### Helper Functions

#### `generate_dsuid_from_gtin_serial(gtin, serial)`
Generate dSUID from GTIN and serial number.

```python
dsuid = generate_dsuid_from_gtin_serial("4050300870342", "3696724640")
```

#### `generate_dsuid_from_mac(mac_address)`
Generate dSUID from MAC address.

```python
dsuid = generate_dsuid_from_mac("45:A2:00:BC:73:B8")
# or
dsuid = generate_dsuid_from_mac("45-A2-00-BC-73-B8")
```

#### `generate_dsuid_from_enocean(enocean_address)`
Generate dSUID from EnOcean address.

```python
dsuid = generate_dsuid_from_enocean("A4BC23D2")
```

#### `generate_dsuid_from_uuid(uuid_str)`
Generate dSUID from existing UUID.

```python
dsuid = generate_dsuid_from_uuid("2f402f80-ea50-11e1-9b23-001778216465")
```

#### `generate_dsuid_from_name(name, namespace=None)`
Generate dSUID from arbitrary unique name.

```python
dsuid = generate_dsuid_from_name("sensor.temperature")
```

#### `generate_random_dsuid()`
Generate random dSUID (last resort).

⚠️ **WARNING:** Random dSUIDs MUST be stored persistently and never change!

```python
dsuid = generate_random_dsuid()
# Store this value and reuse it!
```

#### `validate_dsuid(dsuid)`
Validate dSUID format.

```python
is_valid = validate_dsuid("F4E0230D657B553F926E8D0EDA91ACFE00")  # True
is_valid = validate_dsuid("invalid")  # False
```

## Integration with VirtualDevice

The `VirtualDevice` class automatically uses the dSUID generator:

```python
from virtual_device import VirtualDevice

# Create a device - dSUID is auto-generated from ha_entity_id
device = VirtualDevice(
    name="Living Room Light",
    ha_entity_id="light.living_room_main",
    group_id=1,
    zone_id=0,
)

print(f"Generated dSUID: {device.dsid}")
# Output: 7D4A2E74BE7F4B5D820AC7B84D1793EA00
```

### Generation Priority in VirtualDevice

1. **hardware_guid** (if set) → Parsed and used
2. **ha_entity_id** (if set) → Used as unique name
3. **name** (if set) → Used as unique name
4. **Random** → Generated and must be persisted

### Manual Regeneration

```python
# Regenerate with specific parameters
new_dsuid = device.regenerate_dsuid(
    mac_address="12:34:56:78:90:AB"
)
```

## Examples

### Example 1: Temperature Sensor from HA Entity

```python
from dsuid_generator import generate_dsuid

# Generate reproducible dSUID from HA entity ID
entity_id = "sensor.living_room_temperature"
dsuid = generate_dsuid(unique_name=entity_id)

print(f"dSUID for {entity_id}: {dsuid}")
# Always produces: 2571D9E639925FB3BF45889C00AC5CA100
```

### Example 2: Network Device with MAC Address

```python
# For a network-connected device
mac = "AA:BB:CC:DD:EE:FF"
dsuid = generate_dsuid(mac_address=mac)

print(f"dSUID for MAC {mac}: {dsuid}")
```

### Example 3: EnOcean Device

```python
# For an EnOcean wireless device
enocean_addr = "A4BC23D2"
dsuid = generate_dsuid(enocean_address=enocean_addr)

print(f"dSUID for EnOcean {enocean_addr}: {dsuid}")
```

### Example 4: Device with GTIN and Serial

```python
# For a device with GTIN and serial number
gtin = "4050300870342"
serial = "3696724640"
dsuid = generate_dsuid(gtin=gtin, serial=serial)

print(f"dSUID for GTIN {gtin} / Serial {serial}: {dsuid}")
```

### Example 5: Virtual Device Creation

```python
from virtual_device import VirtualDevice

# Create device with hardware GUID
device = VirtualDevice(
    name="Smart Plug",
    ha_entity_id="switch.smart_plug_1",
    hardware_guid="macaddress:11:22:33:44:55:66",
    model="Virtual Smart Plug",
    vendor_name="Example Corp",
    active=True,
)

print(f"Device: {device.name}")
print(f"dSUID: {device.dsid}")
print(f"Hardware GUID: {device.hardware_guid}")
```

## Important Notes

### Reproducibility

✅ **Reproducible methods** (same input = same dSUID):
- SGTIN-96
- GTIN + serial
- Existing UUID
- MAC address
- EnOcean address
- Unique name (entity ID, device name, etc.)

❌ **NOT reproducible**:
- Random generation (UUIDv4)

### Persistence

For devices using random dSUID generation:

1. **Generate once** during device creation
2. **Store immediately** in YAML/database
3. **Reuse forever** - never regenerate!

The `VirtualDevice` class handles this automatically through its persistence layer.

### Best Practices

1. **Prefer deterministic methods**: Use `ha_entity_id`, `mac_address`, or `hardware_guid` when possible
2. **Document the source**: Store which method was used in device metadata
3. **Validate before use**: Use `validate_dsuid()` to check format
4. **Never modify**: Once assigned, a dSUID should never change
5. **Unique within system**: Ensure different devices get different dSUIDs

## Testing

Run the example code:

```bash
python3 custom_components/documentation/dsuid_generator.py
```

This will demonstrate all generation methods and validate reproducibility.

## Technical Details

### Format Specification

- **Length**: 17 bytes (136 bits)
- **Representation**: 34 hexadecimal characters
- **Base**: RFC 4122 UUID (16 bytes) + 1 byte padding
- **Padding**: Always `0x00` as the 17th byte

### UUID Namespaces Used

```python
NAMESPACE_DNS = uuid.UUID('6ba7b810-9dad-11d1-80b4-00c04fd430c8')
NAMESPACE_GS1 = uuid.uuid5(NAMESPACE_DNS, "gs1.org")
NAMESPACE_MAC = uuid.uuid5(NAMESPACE_DNS, "macaddress")
NAMESPACE_ENOCEAN = uuid.uuid5(NAMESPACE_DNS, "enocean.com")
```

### Conversion Process

For methods using UUIDv5:

1. Hash input using SHA-1 in namespace
2. Extract first 16 bytes as UUID
3. Set version and variant bits (RFC 4122)
4. Append one 0x00 byte
5. Convert to 34 hex characters

## Troubleshooting

### Problem: Different dSUIDs for same input

**Check:**
- Are you using random generation? (Not reproducible)
- Is the input exactly the same? (Case-sensitive)
- Is persistence working? (Random dSUIDs not saved)

### Problem: Invalid dSUID format

**Check:**
- Length should be exactly 34 characters
- Should contain only hexadecimal characters (0-9, A-F)
- Use `validate_dsuid()` to verify

### Problem: Import error in VirtualDevice

**Expected behavior:**
- **In standalone testing**: Uses fallback (random UUIDs with padding)
  - ⚠️ Not reproducible - this is expected for testing only
  - ✅ Correct format (34 hex chars, 17 bytes)
- **In Home Assistant**: Uses full dsuid_generator module
  - ✅ Fully reproducible from same inputs
  - ✅ Follows all specification rules

**Verification:**
```python
# Test the real module directly (always reproducible)
from dsuid_generator import generate_dsuid
dsuid1 = generate_dsuid(unique_name="test")
dsuid2 = generate_dsuid(unique_name="test")
assert dsuid1 == dsuid2  # Always True

# Test through VirtualDevice
# - In testing: Uses fallback (not reproducible)
# - In HA: Uses real module (reproducible)
from virtual_device import VirtualDevice
device = VirtualDevice(ha_entity_id="test")
```

**Solution:** No action needed - this is by design. The fallback ensures the code works even during development/testing without Home Assistant dependencies.

## References

- **ds-basics.pdf Chapter 13.3**: dSUID specification
- **RFC 4122**: UUID specification
- **vDC-API-properties.pdf Chapter 2**: Common entity properties

## License

Part of the virtual_digitalSTROM_devices_4_HA project.
