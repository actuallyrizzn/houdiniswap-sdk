"""Unit tests for configuration management."""

import os
import json
import pytest
import tempfile
from pathlib import Path
from houdiniswap.config import Config


class TestConfig:
    """Tests for Config class."""
    
    def test_config_defaults(self):
        """Test that config loads with defaults."""
        config = Config()
        assert config.get("base_url") is not None
        assert config.get("timeout") == 30
        assert config.get("api_version") == "v1"
    
    def test_config_from_env(self, monkeypatch):
        """Test that config loads from environment variables."""
        monkeypatch.setenv("HOUDINI_SWAP_API_URL", "https://test.example.com")
        monkeypatch.setenv("HOUDINI_SWAP_TIMEOUT", "60")
        config = Config()
        assert config.get("base_url") == "https://test.example.com"
        assert config.get("timeout") == 60
    
    def test_config_from_json_file(self, tmp_path):
        """Test loading config from JSON file."""
        config_file = tmp_path / "houdiniswap.json"
        config_data = {
            "prod": {
                "base_url": "https://prod.example.com",
                "timeout": 45
            }
        }
        config_file.write_text(json.dumps(config_data))
        
        config = Config(profile="prod", config_file=str(config_file))
        assert config.get("base_url") == "https://prod.example.com"
        assert config.get("timeout") == 45
    
    def test_config_profile_selection(self, tmp_path):
        """Test that correct profile is selected."""
        config_file = tmp_path / "houdiniswap.json"
        config_data = {
            "dev": {"base_url": "https://dev.example.com"},
            "staging": {"base_url": "https://staging.example.com"},
            "prod": {"base_url": "https://prod.example.com"}
        }
        config_file.write_text(json.dumps(config_data))
        
        dev_config = Config(profile="dev", config_file=str(config_file))
        assert dev_config.get("base_url") == "https://dev.example.com"
        
        prod_config = Config(profile="prod", config_file=str(config_file))
        assert prod_config.get("base_url") == "https://prod.example.com"
    
    def test_config_env_overrides_file(self, tmp_path, monkeypatch):
        """Test that environment variables override file config."""
        config_file = tmp_path / "houdiniswap.json"
        config_data = {"prod": {"base_url": "https://file.example.com"}}
        config_file.write_text(json.dumps(config_data))
        
        monkeypatch.setenv("HOUDINI_SWAP_API_URL", "https://env.example.com")
        config = Config(profile="prod", config_file=str(config_file))
        assert config.get("base_url") == "https://env.example.com"
    
    def test_config_get_all(self):
        """Test getting all config values."""
        config = Config()
        all_config = config.get_all()
        assert isinstance(all_config, dict)
        assert "base_url" in all_config
        assert "timeout" in all_config
    
    def test_config_load_classmethod(self):
        """Test Config.load() class method."""
        config = Config.load()
        assert isinstance(config, Config)
        assert config.get("base_url") is not None

