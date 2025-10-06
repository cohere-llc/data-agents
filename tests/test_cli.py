"""Tests for CLI functionality."""

import io
import json
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from data_agents.cli import create_router, main
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
