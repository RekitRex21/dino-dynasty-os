"""Configuration management for Dino Dynasty OS."""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml


class Config:
    """Configuration management with YAML support."""

    def __init__(self, config_path: Optional[str] = None):
        """Initialize configuration.
        
        Args:
            config_path: Path to config.yaml file. Defaults to project root.
        """
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config.yaml"
        self.config_path = Path(config_path)
        self._config: Dict[str, Any] = {}
        self.load()

    def load(self) -> None:
        """Load configuration from YAML file."""
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                self._config = yaml.safe_load(f) or {}
        else:
            self._config = {}

    def save(self) -> None:
        """Save configuration to YAML file."""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, 'w') as f:
            yaml.dump(self._config, f, default_flow_style=False)

    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value using dot notation.
        
        Args:
            key: Key in dot notation (e.g., "database.path")
            default: Default value if key not found
            
        Returns:
            Configuration value or default.
        """
        keys = key.split('.')
        value = self._config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value

    def set(self, key: str, value: Any) -> None:
        """Set a configuration value using dot notation.
        
        Args:
            key: Key in dot notation (e.g., "database.path")
            value: Value to set
        """
        keys = key.split('.')
        current = self._config
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]
        current[keys[-1]] = value

    # === LLM Provider Methods ===
    
    def get_enabled_providers(self) -> List[Dict[str, Any]]:
        """Get list of enabled LLM providers in priority order.
        
        Returns:
            List of enabled provider configs.
        """
        providers = self.get('llm.providers', [])
        return [p for p in providers if p.get('enabled', True)]

    def get_provider(self, name: str) -> Optional[Dict[str, Any]]:
        """Get a specific provider by name.
        
        Args:
            name: Provider name
            
        Returns:
            Provider config or None.
        """
        providers = self.get('llm.providers', [])
        for p in providers:
            if p.get('name') == name:
                return p
        return None

    def get_default_llm_settings(self) -> Dict[str, Any]:
        """Get default LLM settings.
        
        Returns:
            Dict with temperature, max_tokens, timeout.
        """
        return {
            'temperature': self.get('llm.default_temperature', 0.7),
            'max_tokens': self.get('llm.default_max_tokens', 4096),
            'timeout': self.get('llm.timeout', 60),
            'retry_attempts': self.get('llm.retry_attempts', 2)
        }

    # === Sandbox Methods ===
    
    def is_sandbox_enabled(self) -> bool:
        """Check if sandbox is enabled."""
        return self.get('sandbox.enabled', True)

    def is_workspace_restricted(self) -> bool:
        """Check if file operations are restricted to workspace."""
        return self.get('sandbox.restrictToWorkspace', True)

    def get_workspace_path(self) -> Path:
        """Get the allowed workspace path.
        
        Returns:
            Path object for workspace directory.
        """
        ws_path = self.get('sandbox.workspace_path', '')
        if ws_path:
            return Path(ws_path)
        # Default to parent of dino_dynasty_os
        return Path(__file__).parent.parent

    # === Channel Methods ===
    
    def get_channel_config(self, channel: str) -> Dict[str, Any]:
        """Get configuration for a specific channel.
        
        Args:
            channel: Channel name (telegram, discord, whatsapp)
            
        Returns:
            Channel config dict.
        """
        return self.get(f'channels.{channel}', {})

    def is_channel_enabled(self, channel: str) -> bool:
        """Check if a channel is enabled:
            channel:.
        
        Args Channel name
            
        Returns:
            True if enabled.
        """
        return self.get(f'channels.{channel}.enabled', False)

    # === Legacy Properties (backwards compatibility) ===
    
    @property
    def database_path(self) -> str:
        """Get database file path."""
        return self.get('memory.path', str(Path(__file__).parent.parent / "dino_memory.db"))

    @property
    def skills_path(self) -> str:
        """Get skills directory path."""
        return self.get('skills.path', str(Path(__file__).parent.parent / "skills"))

    @property
    def log_level(self) -> str:
        """Get log level."""
        return self.get('logging.level', 'INFO')


# Default configuration
DEFAULT_CONFIG = {
    'database': {
        'path': 'dino_memory.db'
    },
    'skills': {
        'path': 'skills'
    },
    'logging': {
        'level': 'INFO'
    },
    'security': {
        'api_keys_enabled': False,
        'rate_limit_enabled': True
    }
}
