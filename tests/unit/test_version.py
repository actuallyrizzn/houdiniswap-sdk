"""Unit tests for version utilities."""

import pytest
import houdiniswap


class TestVersionUtilities:
    """Tests for version checking utilities."""
    
    def test_get_version(self):
        """Test get_version() returns version string."""
        version = houdiniswap.get_version()
        assert isinstance(version, str)
        assert version == "0.1.0"
        assert version == houdiniswap.__version__
    
    def test_get_version_info(self):
        """Test get_version_info() returns version tuple."""
        version_info = houdiniswap.get_version_info()
        assert isinstance(version_info, tuple)
        assert len(version_info) == 3
        assert version_info == (0, 1, 0)
    
    def test_compare_version_equal(self):
        """Test compare_version() with equal versions."""
        result = houdiniswap.compare_version("0.1.0")
        assert result == 0
    
    def test_compare_version_newer(self):
        """Test compare_version() with newer version."""
        result = houdiniswap.compare_version("0.0.9")
        assert result == 1  # Current version is newer
    
    def test_compare_version_older(self):
        """Test compare_version() with older version."""
        result = houdiniswap.compare_version("0.2.0")
        assert result == -1  # Current version is older
    
    def test_compare_version_invalid(self):
        """Test compare_version() with invalid version."""
        with pytest.raises(ValueError, match="Invalid version format"):
            houdiniswap.compare_version("invalid")
    
    def test_is_compatible_with_true(self):
        """Test is_compatible_with() when compatible."""
        assert houdiniswap.is_compatible_with("0.0.9") is True
        assert houdiniswap.is_compatible_with("0.1.0") is True
    
    def test_is_compatible_with_false(self):
        """Test is_compatible_with() when not compatible."""
        assert houdiniswap.is_compatible_with("0.2.0") is False
        assert houdiniswap.is_compatible_with("1.0.0") is False
    
    def test_version_accessible(self):
        """Test that __version__ is accessible."""
        assert hasattr(houdiniswap, '__version__')
        assert houdiniswap.__version__ == "0.1.0"

