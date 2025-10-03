"""Tests for data_agents package."""

import json
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
import io
import sys

import pandas as pd

from data_agents.cli import create_router, main
from data_agents.core import Adapter, Router
from data_agents.adapters import TabularAdapter


class TestTabularAdapter:
    """Test cases for TabularAdapter class."""

    def test_init_empty(self):
        """Test TabularAdapter initialization without data."""
        adapter = TabularAdapter("test-adapter")
        assert adapter.name == "test-adapter"
        assert adapter.config == {}
        assert adapter.data.empty

    def test_init_with_data(self):
        """Test TabularAdapter initialization with data."""
        data = pd.DataFrame({"col1": [1, 2, 3], "col2": ["a", "b", "c"]})
        adapter = TabularAdapter("test-adapter", data)
        assert adapter.name == "test-adapter"
        pd.testing.assert_frame_equal(adapter.data, data)

    def test_query_all(self):
        """Test querying all data."""
        data = pd.DataFrame({"col1": [1, 2, 3], "col2": ["a", "b", "c"]})
        adapter = TabularAdapter("test-adapter", data)
        result = adapter.query("*")
        pd.testing.assert_frame_equal(result, data)

    def test_query_column(self):
        """Test querying specific column."""
        data = pd.DataFrame({"col1": [1, 2, 3], "col2": ["a", "b", "c"]})
        adapter = TabularAdapter("test-adapter", data)
        result = adapter.query("col1")
        expected = data[["col1"]]
        pd.testing.assert_frame_equal(result, expected)

    def test_query_filter(self):
        """Test querying with filter."""
        data = pd.DataFrame({"col1": [1, 2, 3], "col2": ["a", "b", "c"]})
        adapter = TabularAdapter("test-adapter", data)
        result = adapter.query("col1 > 1")
        expected = data[data["col1"] > 1]
        pd.testing.assert_frame_equal(result, expected)

    def test_get_schema(self):
        """Test getting schema information."""
        data = pd.DataFrame({"col1": [1, 2, 3], "col2": ["a", "b", "c"]})
        adapter = TabularAdapter("test-adapter", data)
        schema = adapter.get_schema()
        
        assert "columns" in schema
        assert "dtypes" in schema
        assert "shape" in schema
        assert "sample" in schema
        assert schema["columns"] == ["col1", "col2"]
        assert schema["shape"] == (3, 2)

    def test_add_data(self):
        """Test adding data to adapter."""
        adapter = TabularAdapter("test-adapter")
        data = pd.DataFrame({"col1": [1, 2, 3], "col2": ["a", "b", "c"]})
        adapter.add_data(data)
        pd.testing.assert_frame_equal(adapter.data, data)


class TestRouter:
    """Test cases for Router class."""

    def test_init(self):
        """Test Router initialization."""
        router = Router("test-router")
        assert router.name == "test-router"
        assert router.config == {}
        assert len(router.adapters) == 0

    def test_init_with_config(self):
        """Test Router initialization with configuration."""
        config = {"setting1": "value1", "setting2": 42}
        router = Router("test-router", config)
        assert router.name == "test-router"
        assert router.config == config

    def test_register_adapter(self):
        """Test registering an adapter."""
        router = Router("test-router")
        adapter = TabularAdapter("test-adapter")
        router.register_adapter(adapter)
        
        assert len(router.adapters) == 1
        assert "test-adapter" in router.adapters
        assert router.adapters["test-adapter"] is adapter

    def test_unregister_adapter(self):
        """Test unregistering an adapter."""
        router = Router("test-router")
        adapter = TabularAdapter("test-adapter")
        router.register_adapter(adapter)
        
        result = router.unregister_adapter("test-adapter")
        assert result is True
        assert len(router.adapters) == 0
        
        # Test unregistering non-existent adapter
        result = router.unregister_adapter("nonexistent")
        assert result is False

    def test_get_adapter(self):
        """Test getting a specific adapter."""
        router = Router("test-router")
        adapter = TabularAdapter("test-adapter")
        router.register_adapter(adapter)
        
        retrieved = router.get_adapter("test-adapter")
        assert retrieved is adapter
        
        # Test getting non-existent adapter
        retrieved = router.get_adapter("nonexistent")
        assert retrieved is None

    def test_list_adapters(self):
        """Test listing all adapters."""
        router = Router("test-router")
        adapter1 = TabularAdapter("adapter1")
        adapter2 = TabularAdapter("adapter2")
        
        router.register_adapter(adapter1)
        router.register_adapter(adapter2)
        
        adapters = router.list_adapters()
        assert set(adapters) == {"adapter1", "adapter2"}

    def test_query(self):
        """Test querying a specific adapter."""
        router = Router("test-router")
        data = pd.DataFrame({"col1": [1, 2, 3], "col2": ["a", "b", "c"]})
        adapter = TabularAdapter("test-adapter", data)
        router.register_adapter(adapter)
        
        result = router.query("test-adapter", "*")
        pd.testing.assert_frame_equal(result, data)

    def test_query_nonexistent_adapter(self):
        """Test querying a non-existent adapter."""
        router = Router("test-router")
        
        try:
            router.query("nonexistent", "*")
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "not found" in str(e)

    def test_query_all(self):
        """Test querying all adapters."""
        router = Router("test-router")
        data1 = pd.DataFrame({"col1": [1, 2], "col2": ["a", "b"]})
        data2 = pd.DataFrame({"col1": [3, 4], "col2": ["c", "d"]})
        
        adapter1 = TabularAdapter("adapter1", data1)
        adapter2 = TabularAdapter("adapter2", data2)
        
        router.register_adapter(adapter1)
        router.register_adapter(adapter2)
        
        results = router.query_all("*")
        assert len(results) == 2
        assert "adapter1" in results
        assert "adapter2" in results
        pd.testing.assert_frame_equal(results["adapter1"], data1)
        pd.testing.assert_frame_equal(results["adapter2"], data2)

    def test_add_adapter(self):
        """Test adding an adapter (alias for register_adapter)."""
        router = Router("test-router")
        adapter = TabularAdapter("test-adapter")
        router.add_adapter(adapter)
        
        assert len(router.adapters) == 1
        assert "test-adapter" in router.adapters

    def test_process(self):
        """Test data processing functionality."""
        router = Router("test-router")
        result = router.process("test data")
        assert result == "Processed: test data"

    def test_get_info(self):
        """Test router information retrieval."""
        config = {"key": "value"}
        router = Router("test-router", config)
        info = router.get_info()

        assert info["name"] == "test-router"
        assert info["config"] == config
        assert info["type"] == "Router"
        assert info["adapter_count"] == 0


class TestCLI:
    """Test cases for CLI functionality."""

    def test_create_router_without_config(self):
        """Test creating router without configuration file."""
        router = create_router("test-cli-router")
        assert router.name == "test-cli-router"
        assert router.config == {}

    def test_create_router_with_config(self):
        """Test creating router with configuration file."""
        config_data = {"test_setting": "test_value"}

        # Create temporary config file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(config_data, f)
            config_file = f.name

        try:
            router = create_router("test-cli-router", config_file)
            assert router.name == "test-cli-router"
            assert router.config == config_data
        finally:
            # Clean up
            Path(config_file).unlink()

    def test_create_router_missing_config(self):
        """Test creating router with missing configuration file."""
        router = create_router("test-cli-router", "nonexistent.json")
        assert router.name == "test-cli-router"
        assert router.config == {}

    def test_create_router_invalid_json_config(self):
        """Test creating router with invalid JSON configuration file."""
        # Create temporary file with invalid JSON
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write("{ invalid json }")
            config_file = f.name

        try:
            router = create_router("test-cli-router", config_file)
            assert router.name == "test-cli-router"
            assert router.config == {}
        finally:
            # Clean up
            Path(config_file).unlink()


class TestCLICommands:
    """Test cases for CLI command-line interface."""

    def capture_output(self, func, *args):
        """Helper method to capture stdout."""
        old_stdout = sys.stdout
        sys.stdout = captured_output = io.StringIO()
        try:
            func(*args)
        finally:
            sys.stdout = old_stdout
        return captured_output.getvalue()

    @patch('sys.argv', ['data_agents'])
    @patch('sys.exit')
    def test_main_no_command(self, mock_exit):
        """Test main function with no command shows help and exits."""
        with patch('sys.stdout', new=io.StringIO()) as fake_out:
            main()
        mock_exit.assert_called_once_with(1)

    @patch('sys.argv', ['data_agents', '--version'])
    def test_version_command(self):
        """Test version command."""
        with patch('sys.exit') as mock_exit:
            try:
                main()
            except SystemExit:
                pass
        # Version command should cause SystemExit

    @patch('sys.argv', ['data_agents', 'create', 'test-router'])
    def test_create_command(self):
        """Test create command."""
        with patch('sys.stdout', new=io.StringIO()) as fake_out:
            main()
        output = fake_out.getvalue()
        assert "Created router: test-router" in output

    @patch('sys.argv', ['data_agents', 'create', 'test-router', '--config', 'test.json'])
    def test_create_command_with_config(self):
        """Test create command with configuration file."""
        config_data = {"setting": "value"}
        
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(config_data, f)
            config_file = f.name

        try:
            with patch('sys.argv', ['data_agents', 'create', 'test-router', '--config', config_file]):
                with patch('sys.stdout', new=io.StringIO()) as fake_out:
                    main()
            output = fake_out.getvalue()
            assert "Created router: test-router" in output
            assert "Configuration:" in output
        finally:
            Path(config_file).unlink()

    @patch('sys.argv', ['data_agents', 'demo'])
    def test_demo_command(self):
        """Test demo command."""
        with patch('sys.stdout', new=io.StringIO()) as fake_out:
            main()
        output = fake_out.getvalue()
        assert "Demo router 'demo-router' created with sample data" in output
        assert "Available adapters: ['customers', 'orders']" in output
        assert "Sample Queries" in output
        assert "Get all customers:" in output
        assert "Get all orders:" in output

    @patch('sys.argv', ['data_agents', 'demo', '--router-name', 'custom-demo'])
    def test_demo_command_custom_name(self):
        """Test demo command with custom router name."""
        with patch('sys.stdout', new=io.StringIO()) as fake_out:
            main()
        output = fake_out.getvalue()
        assert "Demo router 'custom-demo' created with sample data" in output

    @patch('sys.argv', ['data_agents', 'info', 'test-info-router'])
    def test_info_command(self):
        """Test info command."""
        with patch('sys.stdout', new=io.StringIO()) as fake_out:
            main()
        output = fake_out.getvalue()
        
        # Parse the JSON output
        info_data = json.loads(output)
        assert info_data["name"] == "test-info-router"
        assert info_data["type"] == "Router"
        assert info_data["adapter_count"] == 0

    @patch('sys.argv', ['data_agents', 'info', 'test-router', '--config', 'test.json'])
    def test_info_command_with_config(self):
        """Test info command with configuration file."""
        config_data = {"test_key": "test_value"}
        
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(config_data, f)
            config_file = f.name

        try:
            with patch('sys.argv', ['data_agents', 'info', 'test-router', '--config', config_file]):
                with patch('sys.stdout', new=io.StringIO()) as fake_out:
                    main()
            output = fake_out.getvalue()
            
            info_data = json.loads(output)
            assert info_data["name"] == "test-router"
            assert info_data["config"] == config_data
        finally:
            Path(config_file).unlink()

    @patch('sys.argv', ['data_agents', 'process', 'test-process-router', 'test-data'])
    def test_process_command(self):
        """Test process command."""
        with patch('sys.stdout', new=io.StringIO()) as fake_out:
            main()
        output = fake_out.getvalue()
        assert "Result: Processed: test-data" in output

    @patch('sys.argv', ['data_agents', 'list-adapters', 'test-list-router'])
    def test_list_adapters_command_empty(self):
        """Test list-adapters command with no adapters."""
        with patch('sys.stdout', new=io.StringIO()) as fake_out:
            main()
        output = fake_out.getvalue()
        assert "No adapters registered" in output

    def test_query_command_nonexistent_adapter(self):
        """Test query command with non-existent adapter."""
        with patch('sys.argv', ['data_agents', 'query', 'test-router', 'nonexistent', '*']):
            with patch('sys.stdout', new=io.StringIO()) as fake_out:
                main()
        output = fake_out.getvalue()
        assert "Error:" in output
        assert "not found" in output

    @patch('data_agents.cli.create_router')
    def test_query_command_with_results(self, mock_create_router):
        """Test query command that returns results."""
        # Create a mock router with mock adapter
        mock_router = MagicMock()
        test_data = pd.DataFrame({"col1": [1, 2], "col2": ["a", "b"]})
        mock_router.query.return_value = test_data
        mock_create_router.return_value = mock_router

        with patch('sys.argv', ['data_agents', 'query', 'test-router', 'test-adapter', '*']):
            with patch('sys.stdout', new=io.StringIO()) as fake_out:
                main()
        
        output = fake_out.getvalue()
        mock_router.query.assert_called_once_with('test-adapter', '*')
        assert "col1" in output and "col2" in output

    @patch('data_agents.cli.create_router')
    def test_query_command_empty_results(self, mock_create_router):
        """Test query command that returns empty results."""
        mock_router = MagicMock()
        mock_router.query.return_value = pd.DataFrame()
        mock_create_router.return_value = mock_router

        with patch('sys.argv', ['data_agents', 'query', 'test-router', 'test-adapter', '*']):
            with patch('sys.stdout', new=io.StringIO()) as fake_out:
                main()
        
        output = fake_out.getvalue()
        assert "Query returned no results" in output

    @patch('data_agents.cli.create_router')
    def test_query_command_exception(self, mock_create_router):
        """Test query command that raises an exception."""
        mock_router = MagicMock()
        mock_router.query.side_effect = Exception("Query execution failed")
        mock_create_router.return_value = mock_router

        with patch('sys.argv', ['data_agents', 'query', 'test-router', 'test-adapter', '*']):
            with patch('sys.stdout', new=io.StringIO()) as fake_out:
                main()
        
        output = fake_out.getvalue()
        assert "Query failed:" in output
        assert "Query execution failed" in output

    @patch('data_agents.cli.create_router')
    def test_list_adapters_command_with_adapters(self, mock_create_router):
        """Test list-adapters command with registered adapters."""
        mock_router = MagicMock()
        mock_adapter1 = MagicMock()
        mock_adapter1.__class__.__name__ = "TabularAdapter"
        mock_adapter2 = MagicMock()
        mock_adapter2.__class__.__name__ = "CustomAdapter"
        
        mock_router.list_adapters.return_value = ["adapter1", "adapter2"]
        mock_router.get_adapter.side_effect = lambda name: {
            "adapter1": mock_adapter1,
            "adapter2": mock_adapter2
        }[name]
        mock_create_router.return_value = mock_router

        with patch('sys.argv', ['data_agents', 'list-adapters', 'test-router']):
            with patch('sys.stdout', new=io.StringIO()) as fake_out:
                main()
        
        output = fake_out.getvalue()
        assert "Available adapters:" in output
        assert "adapter1 (TabularAdapter)" in output
        assert "adapter2 (CustomAdapter)" in output
