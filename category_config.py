from shared_tag_parser import *
from typing import Optional, List, Dict

class CategoryConfig:
    """
    Represents configuration for a single tag category
    """

    def __init__(self, name: str): 
        self.name = name
        self.can_have_parents = False
        self.parent_types = []
        self.can_have_children = False
        self.child_types = []
        self.time_based = False
        self.custom_attributes = []

    def to_dict(self) -> dict:
        """
        Convert to dictionary for JSON serialization
        """
        return {
            'can_have_parents': self.can_have_parents,
            'parent_types': self.parent_types,
            'can_have_children': self.can_have_children,
            'child_types': self.child_types,
            'time_based': self.time_based,
            'custom_attributes': self.custom_attributes
        }
    
    @classmethod
    def from_dict(cls, name: str, data: dict) -> 'CategoryConfig':
        """
        Create from dictionary (for loading configs)
        
        :param cls: class
        :param name: Description
        :type name: str
        :param data: FIX THIS
        :type data: dict
        :return: FIX THIS
        :rtype: CategoryConfig
        """
        # creates new instance of class
        config = cls(name)
        config.can_have_parents = data.get('can_have_parents', False)
        config.parent_types = data.get('parent_types', [])
        config.can_have_children = data.get('can_have_children', False)
        config.child_types = data.get('child_types', [])
        config.time_based = data.get('time_based', False)
        config.custom_attributes = data.get('custom_attributes', [])
        return config
    
    def __str__(self) -> str:
        """String representation for display"""
        parts = []
        if self.can_have_parents: 
            parts.append(f"parents: {', '.join(self.parent_types)}")
        if self.can_have_children:
            parts.append(f"children: {', '.join(self.child_types)}")
        if self.time_based:
            parts.append("time-based")
        if self.custom_attributes:
            parts.append(f"attributes: {', '.join(self.custom_attributes)}")

        return f"{self.name}: [{', '.join(parts)}]" if parts else f"{self.name}: [no relationships]"
    