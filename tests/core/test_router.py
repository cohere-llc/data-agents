"""Tests for Router class."""

from copy import copy, deepcopy
from unittest.mock import MagicMock

import pandas as pd

from data_agents.adapters import TabularAdapter
from data_agents.core import Router


class TestRouter:
    """Test cases for Router class."""

    def test_init(self):
        """Test Router initialization."""
        router = Router("test-router")
        assert router.name == "test-router"
        assert len(router.adapters) == 0

    def test_init_with_adapters(self):
        """Test Router initialization with adapters."""
        adapter1 = TabularAdapter("adapter1")
        adapter2 = TabularAdapter("adapter2")
        adapters = {"adapter1": adapter1, "adapter2": adapter2}

        router = Router("test-router", adapters)
        assert router.name == "test-router"
        assert len(router.adapters) == 2
        assert router.adapters["adapter1"] is adapter1
        assert router.adapters["adapter2"] is adapter2

    def test_setitem(self):
        """Test __setitem__ method for registering adapters."""
        router = Router("test-router")
        adapter = TabularAdapter("test-adapter")

        router["test-adapter"] = adapter
        assert len(router.adapters) == 1
        assert router.adapters["test-adapter"] is adapter

    def test_getitem(self):
        """Test __getitem__ method for retrieving adapters."""
        router = Router("test-router")
        adapter = TabularAdapter("test-adapter")
        router["test-adapter"] = adapter

        retrieved = router["test-adapter"]
        assert retrieved is adapter

        # Test getting non-existent adapter
        retrieved = router["nonexistent"]
        assert retrieved is None

    def test_delitem(self):
        """Test __delitem__ method for removing adapters."""
        router = Router("test-router")
        adapter = TabularAdapter("test-adapter")
        router["test-adapter"] = adapter

        # Test successful deletion
        result = router.__delitem__("test-adapter")
        assert result is True
        assert len(router.adapters) == 0

        # Test deleting non-existent adapter
        result = router.__delitem__("nonexistent")
        assert result is False

    def test_len(self):
        """Test __len__ method."""
        router = Router("test-router")
        assert len(router) == 0

        adapter1 = TabularAdapter("adapter1")
        adapter2 = TabularAdapter("adapter2")
        router["adapter1"] = adapter1
        router["adapter2"] = adapter2

        assert len(router) == 2

    def test_iter(self):
        """Test __iter__ method."""
        router = Router("test-router")
        adapter1 = TabularAdapter("adapter1")
        adapter2 = TabularAdapter("adapter2")
        router["adapter1"] = adapter1
        router["adapter2"] = adapter2

        adapters_list = list(router)
        assert len(adapters_list) == 2
        assert adapter1 in adapters_list
        assert adapter2 in adapters_list

    def test_contains(self):
        """Test __contains__ method."""
        router = Router("test-router")
        adapter = TabularAdapter("test-adapter")
        router["test-adapter"] = adapter

        assert "test-adapter" in router
        assert "nonexistent" not in router

    def test_repr(self):
        """Test __repr__ method."""
        router = Router("test-router")
        adapter = TabularAdapter("test-adapter")
        router["test-adapter"] = adapter

        repr_str = repr(router)
        assert "Router name=test-router" in repr_str
        assert "test-adapter" in repr_str

    def test_str(self):
        """Test __str__ method."""
        router = Router("test-router")
        adapter = TabularAdapter("test-adapter")
        router["test-adapter"] = adapter

        str_repr = str(router)
        assert "Router 'test-router' with 1 adapters" == str_repr

    def test_hash(self):
        """Test __hash__ method."""
        router1 = Router("test-router")
        router2 = Router("test-router")
        adapter = TabularAdapter("test-adapter")

        # Same name, no adapters
        assert hash(router1) == hash(router2)

        # Add same adapter to both
        router1["test-adapter"] = adapter
        router2["test-adapter"] = adapter
        assert hash(router1) == hash(router2)

        # Different names should have different hashes (usually)
        router3 = Router("different-name")
        assert hash(router1) != hash(router3)

    def test_eq(self):
        """Test __eq__ method."""
        router1 = Router("test-router")
        router2 = Router("test-router")
        adapter = TabularAdapter("test-adapter")

        # Same name, no adapters
        assert router1 == router2

        # Add same adapter to both
        router1["test-adapter"] = adapter
        router2["test-adapter"] = adapter
        assert router1 == router2

        # Different names
        router3 = Router("different-name")
        assert router1 != router3

        # Test with non-Router object
        assert router1 != "not a router"

    def test_copy(self):
        """Test __copy__ method."""
        router = Router("test-router")
        adapter = TabularAdapter("test-adapter")
        router["test-adapter"] = adapter

        router_copy = copy(router)
        assert router_copy.name == router.name
        assert len(router_copy.adapters) == len(router.adapters)
        # Shallow copy
        assert router_copy.adapters["test-adapter"] is router.adapters["test-adapter"]
        assert router_copy is not router

    def test_deepcopy(self):
        """Test __deepcopy__ method."""
        router = Router("test-router")
        adapter = TabularAdapter("test-adapter")
        router["test-adapter"] = adapter

        router_deepcopy = deepcopy(router)
        assert router_deepcopy.name == router.name
        assert len(router_deepcopy.adapters) == len(router.adapters)
        # Deep copy
        assert (
            router_deepcopy.adapters["test-adapter"]
            is not router.adapters["test-adapter"]
        )
        assert router_deepcopy is not router

    def test_query_all(self):
        """Test querying all adapters."""
        router = Router("test-router")
        data1 = pd.DataFrame({"col1": [1, 2], "col2": ["a", "b"]})
        data2 = pd.DataFrame({"col1": [3, 4], "col2": ["c", "d"]})

        adapter1 = TabularAdapter("adapter1", data1)
        adapter2 = TabularAdapter("adapter2", data2)

        router["adapter1"] = adapter1
        router["adapter2"] = adapter2

        results = router.query_all("*")
        assert len(results) == 2
        assert "adapter1" in results
        assert "adapter2" in results
        pd.testing.assert_frame_equal(results["adapter1"], data1)
        pd.testing.assert_frame_equal(results["adapter2"], data2)

    def test_query_all_with_error(self):
        """Test query_all when one adapter raises an error."""
        router = Router("test-router")
        data = pd.DataFrame({"col1": [1, 2], "col2": ["a", "b"]})

        good_adapter = TabularAdapter("good_adapter", data)
        bad_adapter = MagicMock()
        bad_adapter.query.side_effect = Exception("Query failed")

        router["good_adapter"] = good_adapter
        router["bad_adapter"] = bad_adapter

        results = router.query_all("*")
        assert len(results) == 2
        assert "good_adapter" in results
        assert "bad_adapter" in results
        pd.testing.assert_frame_equal(results["good_adapter"], data)
        assert results["bad_adapter"].empty  # Should be empty DataFrame on error

    def test_discover_all(self):
        """Test discovering all adapters."""
        router = Router("test-router")
        data1 = pd.DataFrame({"col1": [1, 2], "col2": ["a", "b"]})
        data2 = pd.DataFrame({"col1": [3, 4], "col2": ["c", "d"]})

        adapter1 = TabularAdapter("adapter1", data1)
        adapter2 = TabularAdapter("adapter2", data2)

        router["adapter1"] = adapter1
        router["adapter2"] = adapter2

        discoveries = router.discover_all()
        assert len(discoveries) == 2
        assert "adapter1" in discoveries
        assert "adapter2" in discoveries
        assert discoveries["adapter1"]["adapter_type"] == "tabular"
        assert discoveries["adapter2"]["adapter_type"] == "tabular"

    def test_discover_all_with_error(self):
        """Test discover_all when one adapter raises an error."""
        router = Router("test-router")
        data = pd.DataFrame({"col1": [1, 2], "col2": ["a", "b"]})

        good_adapter = TabularAdapter("good_adapter", data)
        bad_adapter = MagicMock()
        bad_adapter.discover.side_effect = Exception("Discovery failed")

        router["good_adapter"] = good_adapter
        router["bad_adapter"] = bad_adapter

        discoveries = router.discover_all()
        assert len(discoveries) == 2
        assert "good_adapter" in discoveries
        assert "bad_adapter" in discoveries
        assert discoveries["good_adapter"]["adapter_type"] == "tabular"
        assert discoveries["bad_adapter"] == {}  # Should be empty dict on error

    def test_to_dict(self):
        """Test router information dictionary."""
        router = Router("test-router")
        data = pd.DataFrame({"col1": [1, 2], "col2": ["a", "b"]})
        adapter = TabularAdapter("test-adapter", data)
        router["test-adapter"] = adapter

        info = router.to_dict()
        assert info["name"] == "test-router"
        assert info["type"] == "Router"
        assert info["adapter_count"] == 1
        assert "adapters" in info
        assert "test-adapter" in info["adapters"]
        assert info["adapters"]["test-adapter"]["name"] == "test-adapter"
        assert info["adapters"]["test-adapter"]["type"] == "TabularAdapter"
