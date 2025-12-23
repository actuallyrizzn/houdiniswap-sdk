"""Configuration management for Houdini Swap SDK."""

import os
import json
from typing import Optional, Dict, Any
from pathlib import Path


class Config:
    """Configuration manager for SDK settings."""
    
    DEFAULT_CONFIG_PATHS = [
        "houdiniswap.json",
        "houdiniswap.yaml",
        "houdiniswap.yml",
        "houdiniswap.toml",
        ".houdiniswap.json",
        ".houdiniswap.yaml",
        ".houdiniswap.yml",
        ".houdiniswap.toml",
        os.path.expanduser("~/.houdiniswap.json"),
        os.path.expanduser("~/.houdiniswap.yaml"),
        os.path.expanduser("~/.houdiniswap.yml"),
        os.path.expanduser("~/.houdiniswap.toml"),
    ]
    
    def __init__(self, profile: Optional[str] = None, config_file: Optional[str] = None):
        """
        Initialize configuration.
        
        Args:
            profile: Profile name (dev, staging, prod). Defaults to 'prod'.
            config_file: Path to configuration file. If None, searches default locations.
        """
        self.profile = profile or os.getenv("HOUDINI_SWAP_PROFILE", "prod")
        self.config_file = config_file
        self._config: Dict[str, Any] = {}
        self._load_config()
    
    def _load_config(self) -> None:
        """Load configuration from file and environment variables."""
        # Start with defaults
        self._config = {
            "base_url": os.getenv("HOUDINI_SWAP_API_URL", "https://api-partner.houdiniswap.com"),
            "timeout": int(os.getenv("HOUDINI_SWAP_TIMEOUT", "30")),
            "api_version": os.getenv("HOUDINI_SWAP_API_VERSION", "v1"),
            "verify_ssl": os.getenv("HOUDINI_SWAP_VERIFY_SSL", "true").lower() == "true",
            "max_retries": int(os.getenv("HOUDINI_SWAP_MAX_RETRIES", "3")),
            "retry_backoff_factor": float(os.getenv("HOUDINI_SWAP_RETRY_BACKOFF_FACTOR", "1.0")),
            "cache_enabled": os.getenv("HOUDINI_SWAP_CACHE_ENABLED", "false").lower() == "true",
            "cache_ttl": int(os.getenv("HOUDINI_SWAP_CACHE_TTL", "300")),
        }
        
        # Load from config file if specified or found
        config_data = self._load_from_file()
        if config_data:
            # Apply profile-specific config
            if self.profile in config_data:
                profile_config = config_data[self.profile]
                self._config.update(profile_config)
            # Apply global config
            if "global" in config_data:
                self._config.update(config_data["global"])
        
        # Environment variables override everything
        self._apply_env_overrides()
    
    def _load_from_file(self) -> Optional[Dict[str, Any]]:
        """Load configuration from file."""
        config_paths = [self.config_file] if self.config_file else self.DEFAULT_CONFIG_PATHS
        
        for path_str in config_paths:
            if not path_str:
                continue
            path = Path(path_str)
            if path.exists() and path.is_file():
                try:
                    if path.suffix in [".json"]:
                        with open(path, "r", encoding="utf-8") as f:
                            return json.load(f)
                    elif path.suffix in [".yaml", ".yml"]:
                        try:
                            import yaml
                            with open(path, "r", encoding="utf-8") as f:
                                return yaml.safe_load(f)
                        except ImportError:
                            # YAML not available, skip
                            continue
                    elif path.suffix == ".toml":
                        try:
                            import tomllib  # Python 3.11+
                        except ImportError:
                            try:
                                import tomli  # Python < 3.11
                            except ImportError:
                                # TOML not available, skip
                                continue
                        with open(path, "rb") as f:
                            if "tomllib" in globals():
                                return tomllib.load(f)
                            else:
                                return tomli.load(f)
                except Exception:
                    # Skip invalid config files
                    continue
        
        return None
    
    def _apply_env_overrides(self) -> None:
        """Apply environment variable overrides."""
        env_mappings = {
            "HOUDINI_SWAP_API_URL": "base_url",
            "HOUDINI_SWAP_TIMEOUT": ("timeout", int),
            "HOUDINI_SWAP_API_VERSION": "api_version",
            "HOUDINI_SWAP_VERIFY_SSL": ("verify_ssl", lambda x: x.lower() == "true"),
            "HOUDINI_SWAP_MAX_RETRIES": ("max_retries", int),
            "HOUDINI_SWAP_RETRY_BACKOFF_FACTOR": ("retry_backoff_factor", float),
            "HOUDINI_SWAP_CACHE_ENABLED": ("cache_enabled", lambda x: x.lower() == "true"),
            "HOUDINI_SWAP_CACHE_TTL": ("cache_ttl", int),
        }
        
        for env_var, config_key in env_mappings.items():
            value = os.getenv(env_var)
            if value is not None:
                if isinstance(config_key, tuple):
                    key, converter = config_key
                    self._config[key] = converter(value)
                else:
                    self._config[config_key] = value
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        return self._config.get(key, default)
    
    def get_all(self) -> Dict[str, Any]:
        """Get all configuration values."""
        return self._config.copy()
    
    @classmethod
    def load(cls, profile: Optional[str] = None, config_file: Optional[str] = None) -> "Config":
        """
        Load configuration.
        
        Args:
            profile: Profile name (dev, staging, prod)
            config_file: Path to configuration file
            
        Returns:
            Config instance
        """
        return cls(profile=profile, config_file=config_file)

