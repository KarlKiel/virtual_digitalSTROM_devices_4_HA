"""Property Element - Core vDC API message structure.

This module implements the PropertyElement structure as defined in genericVDC.proto.
PropertyElement is the fundamental building block for all vDC API messages.

From genericVDC.proto:
    message PropertyValue {
        optional bool v_bool = 1;
        optional uint64 v_uint64 = 2;
        optional int64 v_int64 = 3;
        optional double v_double = 4;
        optional string v_string = 5;
        optional bytes v_bytes = 6;
    }

    message PropertyElement {
        optional string name  = 1;
        optional PropertyValue value = 2;
        repeated PropertyElement elements = 3;
    }

A PropertyElement either contains:
- A name and a value (leaf node)
- A name and a list of nested PropertyElements (branch node)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union
from enum import Enum


# =============================================================================
# Property Value Types
# =============================================================================

PropertyValueType = Union[bool, int, float, str, bytes, None]


@dataclass
class PropertyValue:
    """Property value matching protobuf PropertyValue message.
    
    Can hold one of: bool, uint64, int64, double, string, bytes
    """
    v_bool: Optional[bool] = None
    v_uint64: Optional[int] = None
    v_int64: Optional[int] = None
    v_double: Optional[float] = None
    v_string: Optional[str] = None
    v_bytes: Optional[bytes] = None
    
    @classmethod
    def from_python(cls, value: PropertyValueType) -> PropertyValue:
        """Create PropertyValue from Python value.
        
        Args:
            value: Python value (bool, int, float, str, bytes, or None)
            
        Returns:
            PropertyValue instance
        """
        if value is None:
            return cls()
        elif isinstance(value, bool):
            return cls(v_bool=value)
        elif isinstance(value, int):
            # Choose uint64 for positive, int64 for negative
            if value >= 0:
                return cls(v_uint64=value)
            else:
                return cls(v_int64=value)
        elif isinstance(value, float):
            return cls(v_double=value)
        elif isinstance(value, str):
            return cls(v_string=value)
        elif isinstance(value, bytes):
            return cls(v_bytes=value)
        else:
            raise ValueError(f"Unsupported value type: {type(value)}")
    
    def to_python(self) -> PropertyValueType:
        """Convert to Python value.
        
        Returns:
            Python value (bool, int, float, str, bytes, or None)
        """
        if self.v_bool is not None:
            return self.v_bool
        elif self.v_uint64 is not None:
            return self.v_uint64
        elif self.v_int64 is not None:
            return self.v_int64
        elif self.v_double is not None:
            return self.v_double
        elif self.v_string is not None:
            return self.v_string
        elif self.v_bytes is not None:
            return self.v_bytes
        else:
            return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        result = {}
        if self.v_bool is not None:
            result["v_bool"] = self.v_bool
        if self.v_uint64 is not None:
            result["v_uint64"] = self.v_uint64
        if self.v_int64 is not None:
            result["v_int64"] = self.v_int64
        if self.v_double is not None:
            result["v_double"] = self.v_double
        if self.v_string is not None:
            result["v_string"] = self.v_string
        if self.v_bytes is not None:
            result["v_bytes"] = self.v_bytes.hex() if isinstance(self.v_bytes, bytes) else self.v_bytes
        return result


# =============================================================================
# Property Element
# =============================================================================

@dataclass
class PropertyElement:
    """Property element matching protobuf PropertyElement message.
    
    This is the core structure for vDC API communication. A PropertyElement
    represents a node in the property tree and can be either:
    
    1. Leaf node: Has name + value
    2. Branch node: Has name + list of child elements
    
    The property tree for a device is built from nested PropertyElements.
    
    Examples:
        # Leaf node (simple property)
        PropertyElement(name="dSUID", value=PropertyValue.from_python("ABC123..."))
        
        # Branch node (container with children)
        PropertyElement(
            name="buttonInputDescriptions",
            elements=[
                PropertyElement(
                    name="0",
                    elements=[
                        PropertyElement(name="name", value=PropertyValue.from_python("Switch")),
                        PropertyElement(name="dsIndex", value=PropertyValue.from_python(0)),
                    ]
                )
            ]
        )
    """
    name: str
    value: Optional[PropertyValue] = None
    elements: List[PropertyElement] = field(default_factory=list)
    
    def is_leaf(self) -> bool:
        """Check if this is a leaf node (has value, no children)."""
        return self.value is not None and len(self.elements) == 0
    
    def is_branch(self) -> bool:
        """Check if this is a branch node (has children, no value)."""
        return len(self.elements) > 0 and self.value is None
    
    def add_element(self, element: PropertyElement) -> None:
        """Add a child element to this branch node."""
        if self.value is not None:
            raise ValueError("Cannot add elements to a leaf node with a value")
        self.elements.append(element)
    
    def get_element(self, name: str) -> Optional[PropertyElement]:
        """Get a child element by name.
        
        Args:
            name: Name of the child element
            
        Returns:
            PropertyElement if found, None otherwise
        """
        for element in self.elements:
            if element.name == name:
                return element
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization.
        
        Returns:
            Dictionary representation
        """
        result = {"name": self.name}
        
        if self.value is not None:
            result["value"] = self.value.to_dict()
        
        if self.elements:
            result["elements"] = [elem.to_dict() for elem in self.elements]
        
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> PropertyElement:
        """Create PropertyElement from dictionary.
        
        Args:
            data: Dictionary with name, value, and/or elements
            
        Returns:
            PropertyElement instance
        """
        name = data.get("name", "")
        
        # Parse value if present
        value = None
        if "value" in data:
            value_data = data["value"]
            value = PropertyValue(
                v_bool=value_data.get("v_bool"),
                v_uint64=value_data.get("v_uint64"),
                v_int64=value_data.get("v_int64"),
                v_double=value_data.get("v_double"),
                v_string=value_data.get("v_string"),
                v_bytes=bytes.fromhex(value_data["v_bytes"]) if "v_bytes" in value_data else None,
            )
        
        # Parse elements if present
        elements = []
        if "elements" in data:
            elements = [cls.from_dict(elem) for elem in data["elements"]]
        
        return cls(name=name, value=value, elements=elements)
    
    @classmethod
    def create_leaf(cls, name: str, value: PropertyValueType) -> PropertyElement:
        """Create a leaf node with a simple value.
        
        Args:
            name: Property name
            value: Python value (bool, int, float, str, bytes)
            
        Returns:
            PropertyElement leaf node
        """
        return cls(name=name, value=PropertyValue.from_python(value))
    
    @classmethod
    def create_branch(cls, name: str, children: List[PropertyElement]) -> PropertyElement:
        """Create a branch node with child elements.
        
        Args:
            name: Property name
            children: List of child PropertyElements
            
        Returns:
            PropertyElement branch node
        """
        return cls(name=name, elements=children)


# =============================================================================
# Helper Functions
# =============================================================================

def build_property_tree_from_dict(data: Dict[str, Any], name: str = "root") -> PropertyElement:
    """Build a PropertyElement tree from a Python dictionary.
    
    This converts a nested dictionary structure into a PropertyElement tree
    that can be serialized to protobuf messages.
    
    Args:
        data: Dictionary with property values
        name: Name for the root element
        
    Returns:
        PropertyElement tree
    
    Example:
        data = {
            "dSUID": "ABC123",
            "type": "vdSD",
            "primaryGroup": 1,
            "buttonInputDescriptions": {
                "0": {
                    "name": "Switch",
                    "dsIndex": 0
                }
            }
        }
        tree = build_property_tree_from_dict(data, "device")
    """
    elements = []
    
    for key, value in data.items():
        if isinstance(value, dict):
            # Nested dictionary - create branch node
            child_elements = []
            for sub_key, sub_value in value.items():
                if isinstance(sub_value, dict):
                    # Recursively build nested structure
                    child_elements.append(build_property_tree_from_dict(sub_value, sub_key))
                else:
                    # Leaf node
                    child_elements.append(PropertyElement.create_leaf(sub_key, sub_value))
            elements.append(PropertyElement.create_branch(key, child_elements))
        elif isinstance(value, list):
            # List of values - create indexed branch node
            list_elements = []
            for idx, item in enumerate(value):
                if isinstance(item, dict):
                    list_elements.append(build_property_tree_from_dict(item, str(idx)))
                else:
                    list_elements.append(PropertyElement.create_leaf(str(idx), item))
            elements.append(PropertyElement.create_branch(key, list_elements))
        else:
            # Simple value - create leaf node
            elements.append(PropertyElement.create_leaf(key, value))
    
    return PropertyElement.create_branch(name, elements)


def property_tree_to_dict(element: PropertyElement) -> Dict[str, Any]:
    """Convert a PropertyElement tree back to a Python dictionary.
    
    Args:
        element: Root PropertyElement
        
    Returns:
        Python dictionary
    """
    if element.is_leaf():
        return {element.name: element.value.to_python() if element.value else None}
    
    result = {}
    for child in element.elements:
        if child.is_leaf():
            result[child.name] = child.value.to_python() if child.value else None
        else:
            # Branch - recursively convert
            child_dict = {}
            for sub_child in child.elements:
                if sub_child.is_leaf():
                    child_dict[sub_child.name] = sub_child.value.to_python() if sub_child.value else None
                else:
                    # Nested branch
                    nested = property_tree_to_dict(sub_child)
                    child_dict.update(nested)
            result[child.name] = child_dict
    
    return result
