"""Unit tests for utility functions."""

import warnings
import pytest
from houdiniswap.utils import deprecated, deprecated_parameter


class TestDeprecated:
    """Tests for deprecated decorator."""
    
    def test_deprecated_function(self):
        """Test deprecated decorator on function."""
        @deprecated(reason="Use new_func instead", version="0.2.0", replacement="new_func")
        def old_func():
            return "result"
        
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = old_func()
            
            assert result == "result"
            assert len(w) == 1
            assert issubclass(w[0].category, DeprecationWarning)
            assert "old_func is deprecated" in str(w[0].message)
            assert "0.2.0" in str(w[0].message)
            assert "new_func" in str(w[0].message)
    
    def test_deprecated_with_removal(self):
        """Test deprecated decorator with removal version."""
        @deprecated(version="0.2.0", removal_version="0.3.0")
        def old_func():
            return "result"
        
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            old_func()
            
            assert len(w) == 1
            assert "0.3.0" in str(w[0].message)
    
    def test_deprecated_method(self):
        """Test deprecated decorator on method."""
        class TestClass:
            @deprecated(reason="Use new_method instead", replacement="new_method")
            def old_method(self):
                return "result"
        
        obj = TestClass()
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = obj.old_method()
            
            assert result == "result"
            assert len(w) == 1


class TestDeprecatedParameter:
    """Tests for deprecated_parameter decorator."""
    
    def test_deprecated_parameter_used(self):
        """Test deprecated_parameter when parameter is used."""
        @deprecated_parameter("old_param", replacement="new_param", version="0.2.0")
        def test_func(new_param=None, old_param=None):
            return old_param or new_param
        
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = test_func(old_param="value")
            
            assert result == "value"
            assert len(w) == 1
            assert issubclass(w[0].category, DeprecationWarning)
            assert "Parameter 'old_param' is deprecated" in str(w[0].message)
            assert "new_param" in str(w[0].message)
    
    def test_deprecated_parameter_not_used(self):
        """Test deprecated_parameter when parameter is not used."""
        @deprecated_parameter("old_param", replacement="new_param")
        def test_func(new_param=None, old_param=None):
            return new_param
        
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = test_func(new_param="value")
            
            assert result == "value"
            assert len(w) == 0  # No warning when deprecated param not used
    
    def test_deprecated_parameter_none(self):
        """Test deprecated_parameter when parameter is None."""
        @deprecated_parameter("old_param", replacement="new_param")
        def test_func(new_param=None, old_param=None):
            return new_param
        
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = test_func(old_param=None)
            
            assert result is None
            assert len(w) == 0  # No warning when deprecated param is None

