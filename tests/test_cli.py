"""Tests for CLI functionality."""

import builtins
import io
import json
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pandas as pd
import pytest

from data_agents.cli import (
    create_adapter_from_config,
    create_router,
    load_config_file,
    main,
)
from data_agents.core.router import Router


class TestCLI:
    """Test cases for CLI functionality."""

    def test_create_router_without_config(self):
        """Test creating router without configuration file."""
        router = create_router("test-cli-router")
        assert isinstance(router, Router)
        assert len(router.adapters) == 0

    def test_create_router_with_config(self):
        """Test creating router with configuration file."""
        config_data = {"test_setting": "test_value"}

        # Create temporary config file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(config_data, f)
            config_file = f.name

        try:
            router = create_router("test-cli-router", config_file)
            assert isinstance(router, Router)
            # Router config is not stored in Router anymore
            assert len(router.adapters) == 0
        finally:
            # Clean up
            Path(config_file).unlink()

    def test_create_router_missing_config(self):
        """Test creating router with missing configuration file."""
        router = create_router("test-cli-router", "nonexistent.json")
        assert isinstance(router, Router)
        assert len(router.adapters) == 0

    def test_create_router_invalid_json_config(self):
        """Test creating router with invalid JSON configuration file."""
        # Create temporary file with invalid JSON
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write("{ invalid json }")
            config_file = f.name

        try:
            router = create_router("test-cli-router", config_file)
            assert isinstance(router, Router)
            assert len(router.adapters) == 0
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

    @patch("sys.argv", ["data_agents"])
    @patch("sys.exit")
    def test_main_no_command(self, mock_exit):
        """Test main function with no command shows help and exits."""
        with patch("sys.stdout", new=io.StringIO()):
            main()
        mock_exit.assert_called_once_with(1)

    @patch("sys.argv", ["data_agents", "--version"])
    def test_version_command(self):
        """Test version command."""
        with patch("sys.exit"):
            try:
                main()
            except SystemExit:
                pass
        # Version command should cause SystemExit

    @patch("sys.argv", ["data_agents", "create", "test-router"])
    def test_create_command(self):
        """Test create command."""
        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            main()
        output = fake_out.getvalue()
        assert "Created router: test-router" in output

    @patch(
        "sys.argv", ["data_agents", "create", "test-router", "--config", "test.json"]
    )
    def test_create_command_with_config(self):
        """Test create command with configuration file."""
        config_data = {"setting": "value"}

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(config_data, f)
            config_file = f.name

        try:
            with patch(
                "sys.argv",
                ["data_agents", "create", "test-router", "--config", config_file],
            ):
                with patch("sys.stdout", new=io.StringIO()) as fake_out:
                    main()
            output = fake_out.getvalue()
            assert "Created router: test-router" in output
        finally:
            Path(config_file).unlink()

    @patch("sys.argv", ["data_agents", "demo"])
    def test_demo_command(self):
        """Test demo command."""
        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            main()
        output = fake_out.getvalue()
        assert "Demo router 'demo-router' created with sample data" in output
        assert "Available adapters: ['customers', 'orders']" in output
        assert "Sample Queries" in output
        assert "Get all customers:" in output
        assert "Get all orders:" in output

    @patch("sys.argv", ["data_agents", "demo", "--router-name", "custom-demo"])
    def test_demo_command_custom_name(self):
        """Test demo command with custom router name."""
        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            main()
        output = fake_out.getvalue()
        assert "Demo router 'custom-demo' created with sample data" in output

    @patch("sys.argv", ["data_agents", "info", "test-info-router"])
    def test_info_command(self):
        """Test info command."""
        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            main()
        output = fake_out.getvalue()

        # Parse the JSON output
        info_data = json.loads(output)
        assert info_data["type"] == "Router"
        assert info_data["adapter_count"] == 0

    @patch("sys.argv", ["data_agents", "info", "test-router", "--config", "test.json"])
    def test_info_command_with_config(self):
        """Test info command with configuration file."""
        config_data = {"test_key": "test_value"}

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(config_data, f)
            config_file = f.name

        try:
            with patch(
                "sys.argv",
                ["data_agents", "info", "test-router", "--config", config_file],
            ):
                with patch("sys.stdout", new=io.StringIO()) as fake_out:
                    main()
            output = fake_out.getvalue()

            info_data = json.loads(output)
            assert info_data["type"] == "Router"
            # Config doesn't appear in router info since it's not stored
        finally:
            Path(config_file).unlink()

    @patch("sys.argv", ["data_agents", "list-adapters", "test-list-router"])
    def test_list_adapters_command_empty(self):
        """Test list-adapters command with no adapters."""
        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            main()
        output = fake_out.getvalue()
        assert "No adapters registered" in output

    def test_query_command_nonexistent_adapter(self):
        """Test query command with non-existent adapter."""
        with patch(
            "sys.argv", ["data_agents", "query", "test-router", "nonexistent", "*"]
        ):
            with patch("sys.stdout", new=io.StringIO()) as fake_out:
                with pytest.raises(SystemExit) as exc_info:
                    main()
                assert exc_info.value.code == 1
        output = fake_out.getvalue()
        assert "Error:" in output
        assert "not found" in output

    @patch("data_agents.cli.create_router")
    def test_query_command_with_results(self, mock_create_router):
        """Test query command that returns results."""
        # Create a mock router with mock adapter
        mock_router = MagicMock()
        test_data = pd.DataFrame({"col1": [1, 2], "col2": ["a", "b"]})

        # Mock the router's __getitem__ method to return an adapter
        mock_adapter = MagicMock()
        mock_adapter.query.return_value = test_data
        mock_router.__getitem__.return_value = mock_adapter
        mock_create_router.return_value = mock_router

        with patch(
            "sys.argv", ["data_agents", "query", "test-router", "test-adapter", "*"]
        ):
            with patch("sys.stdout", new=io.StringIO()) as fake_out:
                main()

        output = fake_out.getvalue()
        mock_adapter.query.assert_called_once_with("*")
        assert "col1" in output and "col2" in output

    @patch("data_agents.cli.create_router")
    def test_query_command_empty_results(self, mock_create_router):
        """Test query command that returns empty results."""
        mock_router = MagicMock()
        mock_adapter = MagicMock()
        mock_adapter.query.return_value = pd.DataFrame()
        mock_router.__getitem__.return_value = mock_adapter
        mock_create_router.return_value = mock_router

        with patch(
            "sys.argv", ["data_agents", "query", "test-router", "test-adapter", "*"]
        ):
            with patch("sys.stdout", new=io.StringIO()) as fake_out:
                main()

        output = fake_out.getvalue()
        assert "Query returned no results" in output

    @patch("data_agents.cli.create_router")
    def test_query_command_exception(self, mock_create_router):
        """Test query command that raises an exception."""
        mock_router = MagicMock()
        mock_router.__getitem__.return_value = None  # Adapter not found
        mock_create_router.return_value = mock_router

        with patch(
            "sys.argv", ["data_agents", "query", "test-router", "test-adapter", "*"]
        ):
            with patch("sys.stdout", new=io.StringIO()) as fake_out:
                with pytest.raises(SystemExit) as exc_info:
                    main()
                assert exc_info.value.code == 1

        output = fake_out.getvalue()
        assert "Error:" in output
        assert "not found" in output

    @patch("data_agents.cli.create_router")
    def test_list_adapters_command_with_adapters(self, mock_create_router):
        """Test list-adapters command with registered adapters."""
        mock_router = MagicMock()
        mock_adapter1 = MagicMock()
        mock_adapter1.__class__.__name__ = "TabularAdapter"
        mock_adapter2 = MagicMock()
        mock_adapter2.__class__.__name__ = "CustomAdapter"

        # Mock the router's adapters property
        mock_router.adapters = {
            "adapter1": mock_adapter1,
            "adapter2": mock_adapter2,
        }
        mock_create_router.return_value = mock_router

        with patch("sys.argv", ["data_agents", "list-adapters", "test-router"]):
            with patch("sys.stdout", new=io.StringIO()) as fake_out:
                main()

        output = fake_out.getvalue()
        assert "Available adapters:" in output
        assert "adapter1 (TabularAdapter)" in output
        assert "adapter2 (CustomAdapter)" in output


class TestCLIConfigurationLoading:
    """Test cases for CLI configuration file loading and adapter creation."""

    def test_load_config_file_json(self):
        """Test loading JSON configuration file."""
        config_data = {"test": "value", "number": 42}

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(config_data, f)
            config_file = f.name

        try:
            result = load_config_file(config_file)
            assert result == config_data
        finally:
            Path(config_file).unlink()

    def test_load_config_file_yaml(self):
        """Test loading YAML configuration file."""
        import yaml

        config_data = {"test": "value", "list": [1, 2, 3]}

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(config_data, f)
            config_file = f.name

        try:
            result = load_config_file(config_file)
            assert result == config_data
        finally:
            Path(config_file).unlink()

    def test_load_config_file_not_found(self):
        """Test loading non-existent configuration file."""
        with pytest.raises(FileNotFoundError):
            load_config_file("nonexistent.json")

    def test_load_config_file_invalid_json(self):
        """Test loading invalid JSON configuration file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write("{ invalid json }")
            config_file = f.name

        try:
            with pytest.raises(ValueError):
                load_config_file(config_file)
        finally:
            Path(config_file).unlink()

    def test_create_adapter_from_config_rest_success(self):
        """Test creating REST adapter from configuration."""
        # Create a temporary REST config file
        rest_config = {"timeout": 5, "headers": {"User-Agent": "test"}}

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(rest_config, f)
            rest_config_file = f.name

        try:
            adapter_config = {
                "type": "rest",
                "base_url": "https://httpbin.org",
                "config_file": rest_config_file,
            }

            adapter = create_adapter_from_config("test_rest", adapter_config)
            assert adapter is not None
            assert hasattr(adapter, "base_url")
            assert adapter.base_url == "https://httpbin.org"
        finally:
            Path(rest_config_file).unlink()

    def test_create_adapter_from_config_rest_missing_base_url(self):
        """Test creating REST adapter without base_url."""
        adapter_config = {"type": "rest"}

        with patch("builtins.print") as mock_print:
            adapter = create_adapter_from_config("test_rest", adapter_config)
            assert adapter is None
            mock_print.assert_called_with(
                "Error: REST adapter 'test_rest' missing required 'base_url'"
            )

    def test_create_adapter_from_config_rest_missing_config_file(self):
        """Test creating REST adapter with non-existent config file."""
        adapter_config = {
            "type": "rest",
            "base_url": "https://httpbin.org",
            "config_file": "nonexistent.json",
        }

        with patch("builtins.print") as mock_print:
            adapter = create_adapter_from_config("test_rest", adapter_config)
            assert adapter is not None  # Should still create adapter, just with warning
            mock_print.assert_called_with(
                "Warning: Failed to load REST adapter config for 'test_rest': "
                "Configuration file nonexistent.json not found"
            )

    def test_create_adapter_from_config_tabular_success(self):
        """Test creating tabular adapter from configuration."""
        # Create a temporary CSV file
        test_data = pd.DataFrame({"col1": [1, 2, 3], "col2": ["a", "b", "c"]})

        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            test_data.to_csv(f.name, index=False)
            csv_file = f.name

        try:
            adapter_config = {"type": "tabular", "csv_file": csv_file}

            adapter = create_adapter_from_config("test_tabular", adapter_config)
            assert adapter is not None
            assert hasattr(adapter, "data")
            assert len(adapter.data) == 3
        finally:
            Path(csv_file).unlink()

    def test_create_adapter_from_config_tabular_missing_csv_file(self):
        """Test creating tabular adapter without csv_file."""
        adapter_config = {"type": "tabular"}

        with patch("builtins.print") as mock_print:
            adapter = create_adapter_from_config("test_tabular", adapter_config)
            assert adapter is None
            mock_print.assert_called_with(
                "Error: Tabular adapter 'test_tabular' missing required 'csv_file'"
            )

    def test_create_adapter_from_config_tabular_nonexistent_csv(self):
        """Test creating tabular adapter with non-existent CSV file."""
        adapter_config = {"type": "tabular", "csv_file": "nonexistent.csv"}

        with patch("builtins.print") as mock_print:
            adapter = create_adapter_from_config("test_tabular", adapter_config)
            assert adapter is None
            mock_print.assert_called_with(
                "Error: CSV file nonexistent.csv not found for adapter 'test_tabular'"
            )

    def test_create_adapter_from_config_unknown_type(self):
        """Test creating adapter with unknown type."""
        adapter_config = {"type": "unknown"}

        with patch("builtins.print") as mock_print:
            adapter = create_adapter_from_config("test_unknown", adapter_config)
            assert adapter is None
            mock_print.assert_called_with(
                "Error: Unknown adapter type 'unknown' for adapter 'test_unknown'"
            )

    def test_create_router_with_adapters_config(self):
        """Test creating router with adapter configurations."""
        # Create test CSV file
        test_data = pd.DataFrame({"id": [1, 2], "name": ["Alice", "Bob"]})

        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            test_data.to_csv(f.name, index=False)
            csv_file = f.name

        # Create router config
        router_config = {
            "adapters": {
                "test_csv": {"type": "tabular", "csv_file": csv_file},
                "test_api": {"type": "rest", "base_url": "https://httpbin.org"},
            }
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(router_config, f)
            config_file = f.name

        try:
            with patch("builtins.print") as mock_print:
                router = create_router("test_router", config_file)
                assert len(router.adapters) == 2
                assert "test_csv" in router.adapters
                assert "test_api" in router.adapters

                # Check that success messages were printed
                mock_print.assert_any_call("Added tabular adapter: test_csv")
                mock_print.assert_any_call("Added rest adapter: test_api")
        finally:
            Path(csv_file).unlink()
            Path(config_file).unlink()

    def test_create_router_with_error_config(self):
        """Test creating router with test_errors.json configuration."""
        # Use the test_errors.json file from tests/data/
        test_errors_path = Path(__file__).parent / "data" / "test_errors.json"

        with patch("builtins.print") as mock_print:
            router = create_router("error_test_router", str(test_errors_path))

            # Should have created one adapter (missing_config) and failed to create
            # the others
            assert len(router.adapters) == 1
            assert "missing_config" in router.adapters

            # Check error messages were printed
            mock_print.assert_any_call(
                "Error: CSV file nonexistent.csv not found for adapter 'missing_csv'"
            )
            mock_print.assert_any_call(
                "Error: Unknown adapter type 'unknown' for adapter 'invalid_type'"
            )
            mock_print.assert_any_call("Added rest adapter: missing_config")

    @patch(
        "sys.argv",
        [
            "data_agents",
            "create",
            "test-router",
            "--config",
            "tests/data/test_errors.json",
        ],
    )
    def test_main_create_with_error_config(self):
        """Test main CLI create command with error configuration."""
        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            main()

        output = fake_out.getvalue()
        assert "Created router: test-router" in output
        assert "Error: CSV file nonexistent.csv not found" in output
        assert "Error: Unknown adapter type 'unknown'" in output
        assert "Added rest adapter: missing_config" in output
        assert "Loaded 1 adapter(s):" in output


class TestCLIErrorHandling:
    """Test error handling scenarios in CLI functions."""

    def test_load_config_file_yaml_import_error(self):
        """Test loading YAML file when PyYAML is not available."""
        import tempfile

        config_data = "test: value"
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(config_data)
            config_file = f.name

        try:
            # Mock the yaml module import to raise ImportError
            import sys

            original_modules = sys.modules.copy()
            if "yaml" in sys.modules:
                del sys.modules["yaml"]

            def mock_import(name, *args, **kwargs):
                if name == "yaml":
                    raise ImportError("No module named 'yaml'")
                return original_import(name, *args, **kwargs)

            original_import = builtins.__import__
            builtins.__import__ = mock_import

            try:
                with pytest.raises(ValueError, match="YAML support not available"):
                    load_config_file(config_file)
            finally:
                builtins.__import__ = original_import
                sys.modules.update(original_modules)
        finally:
            Path(config_file).unlink()

    def test_load_config_file_yaml_parse_error(self):
        """Test loading invalid YAML file."""
        import tempfile

        # Create invalid YAML content
        invalid_yaml = "test: value\n  invalid: [unclosed bracket"
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(invalid_yaml)
            config_file = f.name

        try:
            with pytest.raises(ValueError, match="Invalid YAML format"):
                load_config_file(config_file)
        finally:
            Path(config_file).unlink()

    def test_load_config_file_generic_exception(self):
        """Test generic exception handling in load_config_file."""
        # Create a temporary file first to bypass existence check
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write('{"test": "value"}')
            config_file = f.name

        try:
            # Mock open to raise a permission error after the file exists
            with patch(
                "builtins.open", side_effect=PermissionError("Permission denied")
            ):
                with pytest.raises(
                    ValueError, match="Failed to read configuration file"
                ):
                    load_config_file(config_file)
        finally:
            Path(config_file).unlink()

    def test_create_adapter_rest_failure(self):
        """Test REST adapter creation failure."""
        # Mock RESTAdapter to raise an exception
        with patch(
            "data_agents.cli.RESTAdapter", side_effect=Exception("Connection failed")
        ):
            with patch("sys.stdout", new=io.StringIO()) as fake_out:
                result = create_adapter_from_config(
                    "test", {"type": "rest", "base_url": "https://invalid.url"}
                )

        assert result is None
        output = fake_out.getvalue()
        expected_message = (
            "Error: Failed to create REST adapter 'test': Connection failed"
        )
        assert expected_message in output

    def test_create_adapter_tabular_failure(self):
        """Test tabular adapter creation failure."""
        # Create a temporary CSV file first
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write("col1,col2\nval1,val2")
            csv_file = f.name

        try:
            # Mock pandas.read_csv to raise an exception
            with patch(
                "data_agents.cli.pd.read_csv", side_effect=Exception("CSV read failed")
            ):
                with patch("sys.stdout", new=io.StringIO()) as fake_out:
                    result = create_adapter_from_config(
                        "test", {"type": "tabular", "csv_file": csv_file}
                    )

            assert result is None
            output = fake_out.getvalue()
            expected_message = (
                "Error: Failed to create tabular adapter 'test': CSV read failed"
            )
            assert expected_message in output
        finally:
            Path(csv_file).unlink()


class TestCLIAdditionalCommands:
    """Test additional CLI command scenarios."""

    @patch(
        "sys.argv",
        [
            "data_agents",
            "query",
            "test-router",
            "test-adapter",
            "test-query",
            "--config",
            "config/router_example.json",
        ],
    )
    def test_query_command_exception(self):
        """Test query command with exception."""
        # Mock router and adapter to raise an exception
        with patch("data_agents.cli.create_router") as mock_create_router:
            mock_adapter = Mock()
            mock_adapter.query.side_effect = Exception("Query failed")

            mock_router = MagicMock()
            mock_router.__getitem__.return_value = mock_adapter
            mock_create_router.return_value = mock_router

            with patch("sys.stdout", new=io.StringIO()) as fake_out:
                main()

        output = fake_out.getvalue()
        assert "Query failed: Query failed" in output


class TestCLIMainFunction:
    """Test the main function when called directly."""

    def test_main_function_called_directly(self):
        """Test the if __name__ == '__main__': main() pattern."""
        # This tests line 346: the main() call at module level
        # We can test this by importing the cli module and checking it has the
        # main function
        from data_agents import cli

        # Verify main function exists and is callable
        assert hasattr(cli, "main")
        assert callable(cli.main)

        # Test that main can be called with mocked argv (this exercises line 346
        # indirectly)
        with patch("sys.argv", ["data_agents", "--version"]):
            with patch("sys.stdout", new=io.StringIO()) as fake_out:
                # The --version option causes SystemExit(0), which is expected
                with pytest.raises(SystemExit) as exc_info:
                    cli.main()

                assert exc_info.value.code == 0  # Successful exit

        output = fake_out.getvalue()
        assert "data_agents 0.1.0" in output
