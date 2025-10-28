#!/usr/bin/env python3
"""
Configuration Manager

This script manages configuration settings for the LLM distillation pipeline.
It handles loading, validation, and management of configuration files.
"""

import json
import yaml
import argparse
from pathlib import Path
from typing import Dict, Any


class ConfigManager:
    """Manage configuration for LLM distillation pipeline."""
    
    DEFAULT_CONFIG = {
        "project": {
            "name": "ProjectNekoMuseMeta",
            "version": "1.0.0",
            "description": "Neko Muse Character Meta Distillation"
        },
        "paths": {
            "data_dir": "data",
            "output_dir": "output",
            "templates_dir": "templates"
        },
        "extraction": {
            "include_personality": True,
            "include_dialogue": True,
            "include_relationships": True,
            "max_dialogue_samples": 100
        },
        "dataset": {
            "train_split": 0.8,
            "val_split": 0.1,
            "test_split": 0.1,
            "shuffle": True
        },
        "formatting": {
            "default_format": "alpaca",
            "ensure_ascii": False,
            "indent": 2
        }
    }
    
    def __init__(self, config_path: str = None):
        """Initialize the config manager.
        
        Args:
            config_path: Optional path to existing config file
        """
        self.config_path = Path(config_path) if config_path else None
        self.config = self.DEFAULT_CONFIG.copy()
        
        if self.config_path and self.config_path.exists():
            self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file.
        
        Returns:
            Configuration dictionary
        """
        if not self.config_path.exists():
            print(f"Config file not found: {self.config_path}")
            return self.config
        
        with open(self.config_path, 'r', encoding='utf-8') as f:
            if self.config_path.suffix in ['.yaml', '.yml']:
                loaded_config = yaml.safe_load(f)
            else:
                loaded_config = json.load(f)
        
        # Merge with defaults
        self._merge_configs(self.config, loaded_config)
        print(f"Configuration loaded from: {self.config_path}")
        return self.config
    
    def _merge_configs(self, base: Dict, updates: Dict) -> None:
        """Recursively merge configuration dictionaries.
        
        Args:
            base: Base configuration (modified in place)
            updates: Updates to apply
        """
        for key, value in updates.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._merge_configs(base[key], value)
            else:
                base[key] = value
    
    def save_config(self, output_path: str, format: str = 'json') -> None:
        """Save configuration to file.
        
        Args:
            output_path: Path to save configuration
            format: Output format ('json' or 'yaml')
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            if format == 'yaml':
                yaml.dump(self.config, f, default_flow_style=False, allow_unicode=True)
            else:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        
        print(f"Configuration saved to: {output_path}")
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """Get configuration value by dot-notation key path.
        
        Args:
            key_path: Dot-separated key path (e.g., 'paths.data_dir')
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        keys = key_path.split('.')
        value = self.config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value
    
    def set(self, key_path: str, value: Any) -> None:
        """Set configuration value by dot-notation key path.
        
        Args:
            key_path: Dot-separated key path (e.g., 'paths.data_dir')
            value: Value to set
        """
        keys = key_path.split('.')
        config = self.config
        
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        
        config[keys[-1]] = value
    
    def print_config(self) -> None:
        """Print current configuration."""
        print(json.dumps(self.config, indent=2, ensure_ascii=False))


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Manage configuration for LLM distillation pipeline"
    )
    parser.add_argument(
        "--load",
        "-l",
        help="Load configuration from file"
    )
    parser.add_argument(
        "--save",
        "-s",
        help="Save configuration to file"
    )
    parser.add_argument(
        "--format",
        "-f",
        choices=['json', 'yaml'],
        default='json',
        help="Output format for saved configuration"
    )
    parser.add_argument(
        "--print",
        "-p",
        action='store_true',
        help="Print current configuration"
    )
    parser.add_argument(
        "--init",
        "-i",
        help="Initialize default configuration file"
    )
    
    args = parser.parse_args()
    
    config_mgr = ConfigManager(args.load)
    
    if args.init:
        config_mgr.save_config(args.init, args.format)
        print(f"Default configuration initialized: {args.init}")
    elif args.print or (not args.save):
        config_mgr.print_config()
    
    if args.save:
        config_mgr.save_config(args.save, args.format)


if __name__ == "__main__":
    main()
