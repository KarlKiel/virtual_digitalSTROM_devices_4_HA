"""vDC Property Tree Structures.

This module defines the hierarchical property tree structure as specified in
vDC-API-properties July 2022, Sections 4.1.2, 4.1.3, and 4.1.4.

The 'configurations' property (Section 4.1.1) is a list of property elements where
each configuration contains nested structures for inputs, outputs/channels, and scenes.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from enum import Enum


# =============================================================================
# Section 4.1.2: Configuration Input Properties
# =============================================================================

@dataclass
class ConfigurationInputDescriptions:
    """Input descriptions within a configuration (Section 4.1.2).
    
    Contains references to button inputs, binary inputs, and sensor inputs
    that are available in this specific configuration.
    """
    button_input_ids: List[int] = field(default_factory=list)
    binary_input_ids: List[int] = field(default_factory=list)
    sensor_input_ids: List[int] = field(default_factory=list)
    
    def to_property_elements(self) -> Dict[str, Any]:
        """Convert to vDC property elements structure."""
        elements = {}
        
        # Add button input references
        for idx, button_id in enumerate(self.button_input_ids):
            elements[str(idx)] = {"buttonInputId": button_id}
        
        return elements


# =============================================================================
# Section 4.1.3: Configuration Output and Channel Properties
# =============================================================================

@dataclass
class ConfigurationOutputChannels:
    """Output and channel configuration (Section 4.1.3).
    
    Defines which output and channels are active in this configuration.
    """
    output_id: Optional[int] = None
    channel_ids: List[int] = field(default_factory=list)
    
    def to_property_elements(self) -> Dict[str, Any]:
        """Convert to vDC property elements structure."""
        elements = {}
        
        if self.output_id is not None:
            elements["outputId"] = self.output_id
        
        if self.channel_ids:
            elements["channels"] = {
                str(idx): {"channelId": ch_id}
                for idx, ch_id in enumerate(self.channel_ids)
            }
        
        return elements


# =============================================================================
# Section 4.1.4: Configuration Scene Properties  
# =============================================================================

@dataclass
class ConfigurationScenes:
    """Scene configuration (Section 4.1.4).
    
    Defines which scenes are available in this configuration.
    """
    scene_ids: List[int] = field(default_factory=list)
    
    def to_property_elements(self) -> Dict[str, Any]:
        """Convert to vDC property elements structure."""
        elements = {}
        
        for idx, scene_id in enumerate(self.scene_ids):
            elements[str(scene_id)] = {"sceneId": scene_id}
        
        return elements


# =============================================================================
# Configuration Property Tree
# =============================================================================

@dataclass
class ConfigurationPropertyTree:
    """Complete property tree for a single configuration.
    
    As per vDC spec, each configuration in the 'configurations' property
    contains nested property elements for inputs (4.1.2), outputs/channels (4.1.3),
    and scenes (4.1.4).
    """
    config_id: str
    description: str = ""
    
    # Section 4.1.2: Input properties
    inputs: ConfigurationInputDescriptions = field(default_factory=ConfigurationInputDescriptions)
    
    # Section 4.1.3: Output and channel properties
    outputs: ConfigurationOutputChannels = field(default_factory=ConfigurationOutputChannels)
    
    # Section 4.1.4: Scene properties
    scenes: ConfigurationScenes = field(default_factory=ConfigurationScenes)
    
    def to_property_element(self) -> Dict[str, Any]:
        """Convert to a vDC property element.
        
        Returns:
            Dictionary representing this configuration as a property element
        """
        element = {
            "id": self.config_id,
            "description": self.description,
        }
        
        # Add inputs if present
        inputs_elements = self.inputs.to_property_elements()
        if inputs_elements:
            element["inputs"] = inputs_elements
        
        # Add outputs if present
        outputs_elements = self.outputs.to_property_elements()
        if outputs_elements:
            element["outputs"] = outputs_elements
        
        # Add scenes if present
        scenes_elements = self.scenes.to_property_elements()
        if scenes_elements:
            element["scenes"] = scenes_elements
        
        return element
    
    @classmethod
    def from_property_element(cls, element: Dict[str, Any]) -> ConfigurationPropertyTree:
        """Create from a vDC property element.
        
        Args:
            element: Dictionary containing configuration property element
            
        Returns:
            ConfigurationPropertyTree instance
        """
        config_id = element.get("id", "")
        description = element.get("description", "")
        
        # Parse inputs
        inputs = ConfigurationInputDescriptions()
        if "inputs" in element:
            inputs_data = element["inputs"]
            # Extract button input IDs
            for key, value in inputs_data.items():
                if "buttonInputId" in value:
                    inputs.button_input_ids.append(value["buttonInputId"])
        
        # Parse outputs
        outputs = ConfigurationOutputChannels()
        if "outputs" in element:
            outputs_data = element["outputs"]
            if "outputId" in outputs_data:
                outputs.output_id = outputs_data["outputId"]
            if "channels" in outputs_data:
                for key, value in outputs_data["channels"].items():
                    if "channelId" in value:
                        outputs.channel_ids.append(value["channelId"])
        
        # Parse scenes
        scenes = ConfigurationScenes()
        if "scenes" in element:
            scenes_data = element["scenes"]
            for key, value in scenes_data.items():
                if "sceneId" in value:
                    scenes.scene_ids.append(value["sceneId"])
        
        return cls(
            config_id=config_id,
            description=description,
            inputs=inputs,
            outputs=outputs,
            scenes=scenes,
        )


# =============================================================================
# Configurations Container
# =============================================================================

@dataclass
class DeviceConfigurations:
    """Container for all device configurations.
    
    The 'configurations' property in Section 4.1.1 is implemented as a list
    of property elements (ConfigurationPropertyTree instances).
    """
    configurations: List[ConfigurationPropertyTree] = field(default_factory=list)
    current_config_id: Optional[str] = None
    
    def add_configuration(self, config: ConfigurationPropertyTree) -> None:
        """Add a configuration to the device."""
        self.configurations.append(config)
    
    def get_configuration(self, config_id: str) -> Optional[ConfigurationPropertyTree]:
        """Get a configuration by ID."""
        for config in self.configurations:
            if config.config_id == config_id:
                return config
        return None
    
    def to_property_elements(self) -> Dict[str, Any]:
        """Convert to vDC property elements structure.
        
        Returns:
            Dictionary where keys are configuration IDs and values are property elements
        """
        elements = {}
        for config in self.configurations:
            elements[config.config_id] = config.to_property_element()
        return elements
    
    def to_config_id_list(self) -> List[str]:
        """Get list of configuration IDs (for backward compatibility).
        
        Returns:
            List of configuration ID strings
        """
        return [config.config_id for config in self.configurations]
    
    @classmethod
    def from_property_elements(cls, elements: Dict[str, Any]) -> DeviceConfigurations:
        """Create from vDC property elements.
        
        Args:
            elements: Dictionary of configuration property elements
            
        Returns:
            DeviceConfigurations instance
        """
        configs = cls()
        for config_id, element in elements.items():
            element["id"] = config_id  # Ensure ID is set
            config = ConfigurationPropertyTree.from_property_element(element)
            configs.add_configuration(config)
        return configs
    
    @classmethod
    def create_default(cls, config_id: str = "default") -> DeviceConfigurations:
        """Create a default configuration setup.
        
        Args:
            config_id: Configuration ID (default: "default")
            
        Returns:
            DeviceConfigurations with one default configuration
        """
        configs = cls()
        default_config = ConfigurationPropertyTree(
            config_id=config_id,
            description="Default configuration",
        )
        configs.add_configuration(default_config)
        configs.current_config_id = config_id
        return configs
