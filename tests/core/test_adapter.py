"""Tests for base Adapter class."""

import pandas as pd
import pytest

from data_agents.core.adapter import Adapter


class ConcreteAdapter(Adapter):
    """Concrete implementation of Adapter for testing."""

    def __init__(self, config: dict = None):
        super().__init__(config)
        self.data = pd.DataFrame({"col1": [1, 2, 3], "col2": ["a", "b", "c"]})

    def query(self, query: str, **kwargs) -> pd.DataFrame:
        """Simple query implementation for testing."""
        if query == "*":
            return self.data
        elif query in self.data.columns:
            return self.data[[query]]
        else:
            return pd.DataFrame()

    def discover(self) -> dict:
        """Simple discovery implementation for testing."""
        return {
            "adapter_type": "concrete",
            "columns": list(self.data.columns),
            "shape": self.data.shape,
        }


class TestAdapter:
    """Test cases for base Adapter class."""

    def test_init(self):
        """Test Adapter initialization."""
        adapter = ConcreteAdapter()
        assert adapter.config == {}

    def test_init_with_config(self):
        """Test Adapter initialization with config."""
        config = {"setting1": "value1", "setting2": 42}
        adapter = ConcreteAdapter(config)
        assert adapter.config == config

    def test_query_abstract_method(self):
        """Test that query is abstract and must be implemented."""
        with pytest.raises(TypeError):
            Adapter()  # Should fail because query is abstract

    def test_discover_abstract_method(self):
        """Test that discover is abstract and must be implemented."""
        # This is tested implicitly by the fact that we can't instantiate
        # Adapter directly - we need ConcreteAdapter
        pass

    def test_concrete_query(self):
        """Test query method in concrete implementation."""
        adapter = ConcreteAdapter()

        # Test querying all data
        result = adapter.query("*")
        pd.testing.assert_frame_equal(result, adapter.data)

        # Test querying specific column
        result = adapter.query("col1")
        expected = adapter.data[["col1"]]
        pd.testing.assert_frame_equal(result, expected)

        # Test querying non-existent data
        result = adapter.query("nonexistent")
        assert result.empty

    def test_concrete_discover(self):
        """Test discover method in concrete implementation."""
        adapter = ConcreteAdapter()
        discovery = adapter.discover()

        assert discovery["adapter_type"] == "concrete"
        assert discovery["columns"] == ["col1", "col2"]
        assert discovery["shape"] == (3, 2)

    def test_to_dict(self):
        """Test to_dict method."""
        config = {"test_setting": "test_value"}
        adapter = ConcreteAdapter(config)

        info = adapter.to_dict()
        assert info["type"] == "ConcreteAdapter"
        assert info["config"] == config
