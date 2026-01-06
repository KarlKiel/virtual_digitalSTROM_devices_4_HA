"""
dSUID Generator Module

This module implements dSUID (digitalSTROM Unique Identifier) generation
following the rules specified in ds-basics.pdf Chapter 13.3.

dSUID is a 136-bit (17 bytes) unique identifier based on RFC 4122 UUID format.
When represented as a string, it's 34 hexadecimal characters (2 * 17 bytes).

Generation rules (in priority order):
1. SGTIN-96 is available → Use this SGTIN-96
2. GTIN and serial number available → Generate UUIDv5 from SGTIN-128
3. Existing UUID available → Use it
4. Unique ID within device kind → Generate UUIDv5 in relevant namespace
5. Nothing from above → Generate random UUIDv4 (must be persisted!)
"""

import uuid
import re
from typing import Optional, Union
from dataclasses import dataclass


# =============================================================================
# UUID Namespaces for dSUID generation (UUIDv5)
# =============================================================================

# Standard UUID namespaces from RFC 4122
NAMESPACE_DNS = uuid.UUID('6ba7b810-9dad-11d1-80b4-00c04fd430c8')
NAMESPACE_URL = uuid.UUID('6ba7b811-9dad-11d1-80b4-00c04fd430c8')
NAMESPACE_OID = uuid.UUID('6ba7b812-9dad-11d1-80b4-00c04fd430c8')
NAMESPACE_X500 = uuid.UUID('6ba7b814-9dad-11d1-80b4-00c04fd430c8')

# Custom namespaces for digitalSTROM (based on common practice)
# GS1-128 namespace for SGTIN-128 (generated from DNS namespace + "gs1.org")
NAMESPACE_GS1 = uuid.uuid5(NAMESPACE_DNS, "gs1.org")

# MAC Address namespace
NAMESPACE_MAC = uuid.uuid5(NAMESPACE_DNS, "macaddress")

# EnOcean namespace
NAMESPACE_ENOCEAN = uuid.uuid5(NAMESPACE_DNS, "enocean.com")


# =============================================================================
# Helper Classes
# =============================================================================

@dataclass
class SGTIN96:
    """
    SGTIN-96 (Serialized Global Trade Item Number) structure.
    
    96-bit identifier following GS1 standard:
    - 8-bit Header (0x30)
    - 3-bit Filter Value
    - 3-bit Partition Value
    - 20-40-bit Company Prefix
    - 4-24-bit Item Reference
    - 38-bit Serial Number
    
    Note: This is a simplified implementation. For production use with
    real SGTIN-96 values, proper bit packing based on the partition
    value would be required to correctly encode variable-length fields.
    """
    header: int  # 8 bits, should be 0x30
    filter_value: int  # 3 bits
    partition: int  # 3 bits
    company_prefix: int  # Variable length based on partition
    item_reference: int  # Variable length based on partition
    serial_number: int  # 38 bits
    
    def to_bytes(self) -> bytes:
        """
        Convert SGTIN-96 to 12 bytes (96 bits).
        
        Note: This is a simplified implementation that assumes fixed
        bit lengths. For real SGTIN-96 encoding, the company_prefix
        and item_reference lengths vary based on the partition value.
        """
        value = (self.header << 88) | \
                (self.filter_value << 85) | \
                (self.partition << 82) | \
                (self.company_prefix << 42) | \
                (self.item_reference << 38) | \
                self.serial_number
        return value.to_bytes(12, byteorder='big')
    
    def to_hex(self) -> str:
        """Convert SGTIN-96 to hex string."""
        return self.to_bytes().hex().upper()


# =============================================================================
# dSUID Generation Functions
# =============================================================================

def generate_dsuid_from_sgtin96(sgtin96: SGTIN96) -> str:
    """
    Generate dSUID from SGTIN-96.
    
    Priority 1: Direct use of SGTIN-96.
    
    Args:
        sgtin96: SGTIN-96 structure
        
    Returns:
        34-character hex string (17 bytes)
    """
    # SGTIN-96 is 12 bytes, we need 17 bytes for dSUID
    # Pad with 5 zero bytes at the end
    sgtin_bytes = sgtin96.to_bytes()
    dsuid_bytes = sgtin_bytes + b'\x00' * 5
    return dsuid_bytes.hex().upper()


def generate_dsuid_from_gtin_serial(gtin: str, serial: str) -> str:
    """
    Generate dSUID from GTIN and serial number.
    
    Priority 2: Combine GTIN and serial to form SGTIN-128 with Application
    Identifier 21, then generate UUIDv5 in GS1-128 namespace.
    
    Args:
        gtin: GTIN (Global Trade Item Number)
        serial: Serial number
        
    Returns:
        34-character hex string (17 bytes)
    """
    # Format as SGTIN-128: "(01)<GTIN>(21)<serial>"
    sgtin_128 = f"(01){gtin}(21){serial}"
    
    # Generate UUIDv5 in GS1 namespace
    uuid_obj = uuid.uuid5(NAMESPACE_GS1, sgtin_128)
    
    # UUID is 16 bytes, we need 17 bytes for dSUID
    # Add one byte (0x00) to make it 17 bytes
    dsuid_bytes = uuid_obj.bytes + b'\x00'
    return dsuid_bytes.hex().upper()


def generate_dsuid_from_uuid(uuid_str: str) -> str:
    """
    Generate dSUID from existing UUID.
    
    Priority 3: Use existing UUID.
    
    Args:
        uuid_str: UUID string (with or without hyphens)
        
    Returns:
        34-character hex string (17 bytes)
    """
    # Parse UUID
    uuid_obj = uuid.UUID(uuid_str)
    
    # UUID is 16 bytes, we need 17 bytes for dSUID
    # Add one byte (0x00) to make it 17 bytes
    dsuid_bytes = uuid_obj.bytes + b'\x00'
    return dsuid_bytes.hex().upper()


def generate_dsuid_from_mac(mac_address: str) -> str:
    """
    Generate dSUID from MAC address.
    
    Priority 4: Generate name-based UUIDv5 from MAC address.
    
    Args:
        mac_address: MAC address (e.g., "12:34:56:78:90:AB" or "12-34-56-78-90-AB")
        
    Returns:
        34-character hex string (17 bytes)
    """
    # Normalize MAC address (remove separators)
    mac_clean = mac_address.replace(':', '').replace('-', '').replace('.', '').upper()
    
    if len(mac_clean) != 12:
        raise ValueError(f"Invalid MAC address: {mac_address}")
    
    # Generate UUIDv5 in MAC namespace
    uuid_obj = uuid.uuid5(NAMESPACE_MAC, mac_clean)
    
    # UUID is 16 bytes, we need 17 bytes for dSUID
    # Add one byte (0x00) to make it 17 bytes
    dsuid_bytes = uuid_obj.bytes + b'\x00'
    return dsuid_bytes.hex().upper()


def generate_dsuid_from_enocean(enocean_address: str) -> str:
    """
    Generate dSUID from EnOcean address.
    
    Priority 4: Generate name-based UUIDv5 from EnOcean address.
    
    Args:
        enocean_address: 8 hex digit EnOcean address (e.g., "A4BC23D2")
        
    Returns:
        34-character hex string (17 bytes)
    """
    # Normalize EnOcean address
    enocean_clean = enocean_address.replace(' ', '').upper()
    
    if len(enocean_clean) != 8:
        raise ValueError(f"Invalid EnOcean address: {enocean_address}")
    
    # Generate UUIDv5 in EnOcean namespace
    uuid_obj = uuid.uuid5(NAMESPACE_ENOCEAN, enocean_clean)
    
    # UUID is 16 bytes, we need 17 bytes for dSUID
    # Add one byte (0x00) to make it 17 bytes
    dsuid_bytes = uuid_obj.bytes + b'\x00'
    return dsuid_bytes.hex().upper()


def generate_dsuid_from_name(name: str, namespace: Optional[uuid.UUID] = None) -> str:
    """
    Generate dSUID from arbitrary unique name.
    
    Priority 4: Generate name-based UUIDv5 from unique identifier.
    
    Args:
        name: Unique identifier/name
        namespace: UUID namespace to use (defaults to DNS namespace)
        
    Returns:
        34-character hex string (17 bytes)
    """
    if namespace is None:
        namespace = NAMESPACE_DNS
    
    # Generate UUIDv5
    uuid_obj = uuid.uuid5(namespace, name)
    
    # UUID is 16 bytes, we need 17 bytes for dSUID
    # Add one byte (0x00) to make it 17 bytes
    dsuid_bytes = uuid_obj.bytes + b'\x00'
    return dsuid_bytes.hex().upper()


def generate_random_dsuid() -> str:
    """
    Generate random dSUID.
    
    Priority 5 (last resort): Generate random UUIDv4.
    WARNING: This dSUID MUST be stored persistently and never change!
    
    Returns:
        34-character hex string (17 bytes)
    """
    # Generate UUIDv4
    uuid_obj = uuid.uuid4()
    
    # UUID is 16 bytes, we need 17 bytes for dSUID
    # Add one byte (0x00) to make it 17 bytes
    dsuid_bytes = uuid_obj.bytes + b'\x00'
    return dsuid_bytes.hex().upper()


def generate_dsuid_from_hardware_guid(hardware_guid: str) -> str:
    """
    Generate dSUID from hardware GUID in URN format.
    
    This function parses the hardware GUID and uses the appropriate
    generation method based on the format.
    
    Supported formats:
    - gs1:(01)<GTIN>(21)<serial> → Use GTIN + serial
    - macaddress:<MAC> → Use MAC address
    - enoceanaddress:<ADDRESS> → Use EnOcean address
    - uuid:<UUID> → Use existing UUID
    - Other formats → Use as name in DNS namespace
    
    Args:
        hardware_guid: Hardware GUID in URN format
        
    Returns:
        34-character hex string (17 bytes)
    """
    if not hardware_guid:
        raise ValueError("hardware_guid cannot be empty")
    
    # Parse GS1 format: gs1:(01)<GTIN>(21)<serial>
    if hardware_guid.startswith("gs1:"):
        match = re.search(r'\(01\)(\d+)\(21\)(\w+)', hardware_guid)
        if match:
            gtin = match.group(1)
            serial = match.group(2)
            return generate_dsuid_from_gtin_serial(gtin, serial)
    
    # Parse MAC address format: macaddress:<MAC>
    if hardware_guid.startswith("macaddress:"):
        mac = hardware_guid.split(":", 1)[1]
        return generate_dsuid_from_mac(mac)
    
    # Parse EnOcean format: enoceanaddress:<ADDRESS>
    if hardware_guid.startswith("enoceanaddress:"):
        address = hardware_guid.split(":", 1)[1]
        return generate_dsuid_from_enocean(address)
    
    # Parse UUID format: uuid:<UUID>
    if hardware_guid.startswith("uuid:"):
        uuid_str = hardware_guid.split(":", 1)[1]
        return generate_dsuid_from_uuid(uuid_str)
    
    # For other formats, use as name
    return generate_dsuid_from_name(hardware_guid)


def validate_dsuid(dsuid: str) -> bool:
    """
    Validate that a dSUID is correctly formatted.
    
    Args:
        dsuid: dSUID string to validate
        
    Returns:
        True if valid, False otherwise
    """
    # dSUID should be 34 hex characters (17 bytes * 2)
    if len(dsuid) != 34:
        return False
    
    # Check if all characters are valid hex
    try:
        int(dsuid, 16)
        return True
    except ValueError:
        return False


def format_dsuid(dsuid_bytes: bytes) -> str:
    """
    Format dSUID bytes as a hex string.
    
    Args:
        dsuid_bytes: 17 bytes
        
    Returns:
        34-character hex string
    """
    if len(dsuid_bytes) != 17:
        raise ValueError(f"dSUID must be exactly 17 bytes, got {len(dsuid_bytes)}")
    
    return dsuid_bytes.hex().upper()


# =============================================================================
# High-Level dSUID Generator
# =============================================================================

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
    """
    Generate dSUID following the prioritized rules from ds-basics.pdf 13.3.
    
    Priority order:
    1. Use SGTIN-96 if available
    2. Use GTIN + serial to generate SGTIN-128 UUIDv5
    3. Use existing UUID
    4. Use hardware GUID (auto-detects format)
    5. Use MAC address to generate UUIDv5
    6. Use EnOcean address to generate UUIDv5
    7. Use unique name to generate UUIDv5
    8. Generate random UUIDv4 (MUST be persisted!)
    
    Args:
        sgtin96: SGTIN-96 structure
        gtin: GTIN number
        serial: Serial number (used with GTIN)
        existing_uuid: Existing UUID string
        hardware_guid: Hardware GUID in URN format
        mac_address: MAC address
        enocean_address: EnOcean address
        unique_name: Unique name/identifier
        
    Returns:
        34-character hex string (17 bytes)
        
    Examples:
        >>> # Using GTIN and serial
        >>> dsuid = generate_dsuid(gtin="4050300870342", serial="3696724640")
        
        >>> # Using MAC address
        >>> dsuid = generate_dsuid(mac_address="45:A2:00:BC:73:B8")
        
        >>> # Using hardware GUID
        >>> dsuid = generate_dsuid(hardware_guid="macaddress:45:A2:00:BC:73:B8")
        
        >>> # Using unique name (e.g., HA entity ID)
        >>> dsuid = generate_dsuid(unique_name="sensor.living_room_temperature")
    """
    # Priority 1: SGTIN-96
    if sgtin96 is not None:
        return generate_dsuid_from_sgtin96(sgtin96)
    
    # Priority 2: GTIN + serial
    if gtin is not None and serial is not None:
        return generate_dsuid_from_gtin_serial(gtin, serial)
    
    # Priority 3: Existing UUID
    if existing_uuid is not None:
        return generate_dsuid_from_uuid(existing_uuid)
    
    # Priority 4: Hardware GUID (auto-detect format)
    if hardware_guid is not None:
        return generate_dsuid_from_hardware_guid(hardware_guid)
    
    # Priority 4: MAC address
    if mac_address is not None:
        return generate_dsuid_from_mac(mac_address)
    
    # Priority 4: EnOcean address
    if enocean_address is not None:
        return generate_dsuid_from_enocean(enocean_address)
    
    # Priority 4: Unique name
    if unique_name is not None:
        return generate_dsuid_from_name(unique_name)
    
    # Priority 5 (last resort): Random UUIDv4
    # WARNING: This MUST be persisted!
    return generate_random_dsuid()


# =============================================================================
# Example Usage
# =============================================================================

if __name__ == "__main__":
    print("dSUID Generator Examples\n" + "="*60)
    
    # Example 1: From GTIN and serial
    dsuid1 = generate_dsuid(gtin="4050300870342", serial="3696724640")
    print(f"\n1. From GTIN + serial:")
    print(f"   GTIN: 4050300870342, Serial: 3696724640")
    print(f"   dSUID: {dsuid1}")
    print(f"   Valid: {validate_dsuid(dsuid1)}")
    
    # Example 2: From MAC address
    dsuid2 = generate_dsuid(mac_address="45:A2:00:BC:73:B8")
    print(f"\n2. From MAC address:")
    print(f"   MAC: 45:A2:00:BC:73:B8")
    print(f"   dSUID: {dsuid2}")
    print(f"   Valid: {validate_dsuid(dsuid2)}")
    
    # Example 3: From hardware GUID
    dsuid3 = generate_dsuid(hardware_guid="macaddress:12:34:56:78:90:AB")
    print(f"\n3. From hardware GUID:")
    print(f"   GUID: macaddress:12:34:56:78:90:AB")
    print(f"   dSUID: {dsuid3}")
    print(f"   Valid: {validate_dsuid(dsuid3)}")
    
    # Example 4: From EnOcean address
    dsuid4 = generate_dsuid(enocean_address="A4BC23D2")
    print(f"\n4. From EnOcean address:")
    print(f"   Address: A4BC23D2")
    print(f"   dSUID: {dsuid4}")
    print(f"   Valid: {validate_dsuid(dsuid4)}")
    
    # Example 5: From unique name (e.g., Home Assistant entity ID)
    dsuid5 = generate_dsuid(unique_name="sensor.living_room_temperature")
    print(f"\n5. From unique name:")
    print(f"   Name: sensor.living_room_temperature")
    print(f"   dSUID: {dsuid5}")
    print(f"   Valid: {validate_dsuid(dsuid5)}")
    
    # Example 6: From existing UUID
    dsuid6 = generate_dsuid(existing_uuid="2f402f80-ea50-11e1-9b23-001778216465")
    print(f"\n6. From existing UUID:")
    print(f"   UUID: 2f402f80-ea50-11e1-9b23-001778216465")
    print(f"   dSUID: {dsuid6}")
    print(f"   Valid: {validate_dsuid(dsuid6)}")
    
    # Example 7: Random (last resort - must be persisted!)
    dsuid7 = generate_random_dsuid()
    print(f"\n7. Random (last resort):")
    print(f"   dSUID: {dsuid7}")
    print(f"   Valid: {validate_dsuid(dsuid7)}")
    print(f"   WARNING: This must be stored persistently!")
    
    # Verify same input produces same output (reproducibility)
    dsuid5_again = generate_dsuid(unique_name="sensor.living_room_temperature")
    print(f"\n8. Reproducibility test:")
    print(f"   First call:  {dsuid5}")
    print(f"   Second call: {dsuid5_again}")
    print(f"   Same: {dsuid5 == dsuid5_again}")
