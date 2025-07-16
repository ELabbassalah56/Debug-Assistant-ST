"""
Configuration management for the Debug Assistant application.
"""

import os
import yaml
from typing import Dict, Any, Optional


class Config:
    """Configuration manager for the Debug Assistant application."""
    
    def __init__(self, config_file: str = "config.yaml"):
        self.config_file = config_file
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or create default config."""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    return yaml.safe_load(f) or {}
            except Exception as e:
                print(f"⚠️ Error loading config file: {e}")
                return self._get_default_config()
        else:
            config = self._get_default_config()
            self._save_config(config)
            return config
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration."""
        return {
            'app': {
                'title': 'Debug Assistant',
                'host': '0.0.0.0',
                'port': 8050,
                'debug': False
            },
            'data': {
                'directory': './data',
                'log_file': 'adaptive.log',
                'dlt_file': 'dltlog_0.dlt',
                'pcap_json_file': 'full_pcap.json',
                'max_messages_per_source': 500,
                'discovery_line_limit': 1000
            },
            'processing': {
                'progress_update_interval': 100,
                'thread_timeout': 30,
                'auto_search_on_selection': True
            },
            'ui': {
                'refresh_interval': 500,
                'table_page_size': 10,
                'max_display_height': '300px'
            }
        }
    
    def _save_config(self, config: Dict[str, Any]) -> None:
        """Save configuration to file."""
        try:
            with open(self.config_file, 'w') as f:
                yaml.dump(config, f, default_flow_style=False, indent=2)
        except Exception as e:
            print(f"⚠️ Error saving config file: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value using dot notation (e.g., 'app.port')."""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value using dot notation."""
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
        self._save_config(self.config)
    
    def get_data_files(self) -> Dict[str, str]:
        """Get data file paths."""
        data_dir = self.get('data.directory', './data')
        return {
            'log_file': os.path.join(data_dir, self.get('data.log_file', '')),
            'dlt_file': os.path.join(data_dir, self.get('data.dlt_file', '')),
            'pcap_json_file': os.path.join(data_dir, self.get('data.pcap_json_file', ''))
        }


# Global configuration instance
config = Config()

