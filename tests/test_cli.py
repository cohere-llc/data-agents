"""Test the new CLI functionality."""

import json
import os
import tempfile
from unittest.mock import patch

import pandas as pd
import pytest

from data_agents.cli import (
    create_adapter_from_config,
    create_router_from_config,
    create_single_adapter_from_config,
    execute_adapter_query,
    execute_router_query,
    load_config_file,
    main,
    parse_nasa_query,
)


class TestNewCLI:
    """Test the updated CLI functionality."""

    def test_help_command(self, capsys):
        """Test --help command."""
        with pytest.raises(SystemExit):
            with patch("sys.argv", ["data-agents", "--help"]):
                main()
        captured = capsys.readouterr()
        assert "Data Agents CLI" in captured.out
        assert "demo" in captured.out
        assert "info" in captured.out
        assert "list-adapters" in captured.out
        assert "discover" in captured.out
        assert "query" in captured.out

    def test_version_command(self, capsys):
        """Test --version command."""
        with pytest.raises(SystemExit):
            with patch("sys.argv", ["data-agents", "--version"]):
                main()
        captured = capsys.readouterr()
        assert "data-agents" in captured.out
        assert "0.1.0" in captured.out

    def test_demo_command(self, capsys):
        """Test demo command."""
        with patch("sys.argv", ["data-agents", "demo"]):
            main()
        captured = capsys.readouterr()
        assert "Demo router created with sample data" in captured.out
        assert "customers" in captured.out
        assert "orders" in captured.out

    def test_info_router_config(self, capsys):
        """Test info command with router config."""
        # Create a simple router config
        config_data = {
            "adapters": {
                "sample_data": {
                    "type": "tabular",
                    "csv_file": "examples/sample_data.csv",
                }
            }
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(config_data, f)
            config_file = f.name

        try:
            with patch(
                "sys.argv", ["data-agents", "info", "--router-config", config_file]
            ):
                main()
            captured = capsys.readouterr()
            assert "Router" in captured.out
            assert "sample_data" in captured.out
        finally:
            os.unlink(config_file)

    def test_info_adapter_config(self, capsys):
        """Test info command with adapter config."""
        # Create a simple adapter config
        config_data = {"type": "tabular", "csv_file": "examples/sample_data.csv"}

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(config_data, f)
            config_file = f.name

        try:
            with patch(
                "sys.argv", ["data-agents", "info", "--adapter-config", config_file]
            ):
                main()
            captured = capsys.readouterr()
            assert "TabularAdapter" in captured.out
        finally:
            os.unlink(config_file)

    def test_list_adapters_command(self, capsys):
        """Test list-adapters command."""
        # Create a simple router config
        config_data = {
            "adapters": {
                "sample_data": {
                    "type": "tabular",
                    "csv_file": "examples/sample_data.csv",
                }
            }
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(config_data, f)
            config_file = f.name

        try:
            with patch(
                "sys.argv",
                ["data-agents", "list-adapters", "--router-config", config_file],
            ):
                main()
            captured = capsys.readouterr()
            assert "Available adapters:" in captured.out
            assert "sample_data" in captured.out
            assert "TabularAdapter" in captured.out
        finally:
            os.unlink(config_file)

    def test_discover_router_config(self, capsys):
        """Test discover command with router config."""
        # Create a simple router config
        config_data = {
            "adapters": {
                "sample_data": {
                    "type": "tabular",
                    "csv_file": "examples/sample_data.csv",
                }
            }
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(config_data, f)
            config_file = f.name

        try:
            with patch(
                "sys.argv", ["data-agents", "discover", "--router-config", config_file]
            ):
                main()
            captured = capsys.readouterr()
            assert "sample_data" in captured.out
            assert "columns" in captured.out
        finally:
            os.unlink(config_file)

    def test_discover_adapter_config(self, capsys):
        """Test discover command with adapter config."""
        # Create a simple adapter config
        config_data = {"type": "tabular", "csv_file": "examples/sample_data.csv"}

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(config_data, f)
            config_file = f.name

        try:
            with patch(
                "sys.argv", ["data-agents", "discover", "--adapter-config", config_file]
            ):
                main()
            captured = capsys.readouterr()
            assert "columns" in captured.out
            assert "adapter_type" in captured.out
        finally:
            os.unlink(config_file)

    def test_query_router_config(self, capsys):
        """Test query command with router config."""
        # Create a simple router config
        config_data = {
            "adapters": {
                "sample_data": {
                    "type": "tabular",
                    "csv_file": "examples/sample_data.csv",
                }
            }
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(config_data, f)
            config_file = f.name

        try:
            with patch(
                "sys.argv",
                ["data-agents", "query", "age > 30", "--router-config", config_file],
            ):
                main()
            captured = capsys.readouterr()
            assert "Results from sample_data" in captured.out
        finally:
            os.unlink(config_file)

    def test_query_adapter_config(self, capsys):
        """Test query command with adapter config."""
        # Create a simple adapter config
        config_data = {"type": "tabular", "csv_file": "examples/sample_data.csv"}

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(config_data, f)
            config_file = f.name

        try:
            with patch(
                "sys.argv",
                ["data-agents", "query", "age > 30", "--adapter-config", config_file],
            ):
                main()
            captured = capsys.readouterr()
            # Should have actual results
            assert (
                "Charlie Brown" in captured.out
                or "Query returned no results" in captured.out
            )
        finally:
            os.unlink(config_file)

    def test_missing_config_error(self, capsys):
        """Test error when config file is missing."""
        with pytest.raises(SystemExit):
            with patch(
                "sys.argv",
                ["data-agents", "info", "--router-config", "nonexistent.json"],
            ):
                main()
        captured = capsys.readouterr()
        assert "Error:" in captured.out
        assert "not found" in captured.out

    def test_no_command_shows_help(self, capsys):
        """Test that running without command shows help."""
        with pytest.raises(SystemExit):
            with patch("sys.argv", ["data-agents"]):
                main()
        captured = capsys.readouterr()
        assert "usage:" in captured.out


class TestCLIConfigLoading:
    """Test configuration loading functionality."""

    def test_load_config_file_json_valid(self):
        """Test loading valid JSON config file."""
        test_config = {
            "adapters": {"test": {"type": "tabular", "csv_file": "test.csv"}}
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(test_config, f)
            config_file = f.name

        try:
            result = load_config_file(config_file)
            assert result == test_config
        finally:
            os.unlink(config_file)

    def test_load_config_file_json_invalid(self):
        """Test loading invalid JSON config file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write("{ invalid json")
            config_file = f.name

        try:
            with pytest.raises(ValueError, match="Invalid JSON format"):
                load_config_file(config_file)
        finally:
            os.unlink(config_file)

    def test_load_config_file_yaml_valid(self):
        """Test loading valid YAML config file."""
        test_config = {
            "adapters": {"test": {"type": "tabular", "csv_file": "test.csv"}}
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("adapters:\n  test:\n    type: tabular\n    csv_file: test.csv\n")
            config_file = f.name

        try:
            result = load_config_file(config_file)
            assert result == test_config
        finally:
            os.unlink(config_file)

    def test_load_config_file_yaml_invalid(self):
        """Test loading invalid YAML config file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("invalid: yaml: [\n")
            config_file = f.name

        try:
            with pytest.raises(ValueError, match="Invalid YAML format"):
                load_config_file(config_file)
        finally:
            os.unlink(config_file)

    def test_load_config_file_yaml_not_installed(self):
        """Test YAML file when PyYAML is not available."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("test: value\n")
            config_file = f.name

        try:
            with patch("builtins.__import__", side_effect=ImportError):
                with pytest.raises(ValueError, match="YAML support not available"):
                    load_config_file(config_file)
        finally:
            os.unlink(config_file)

    def test_load_config_file_not_found(self):
        """Test loading non-existent config file."""
        with pytest.raises(FileNotFoundError, match="Configuration file .* not found"):
            load_config_file("nonexistent.json")

    def test_load_config_file_permission_error(self):
        """Test loading config file with permission issues."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump({"test": "value"}, f)
            config_file = f.name

        try:
            permission_error = PermissionError("Permission denied")
            with patch("builtins.open", side_effect=permission_error):
                with pytest.raises(
                    ValueError, match="Failed to read configuration file"
                ):
                    load_config_file(config_file)
        finally:
            os.unlink(config_file)


class TestCLIAdapterCreation:
    """Test adapter creation functionality."""

    def test_create_adapter_from_config_rest_valid(self):
        """Test creating REST adapter with valid config."""
        config = {"type": "rest", "base_url": "https://api.example.com"}
        adapter = create_adapter_from_config(config)
        assert adapter is not None
        assert adapter.__class__.__name__ == "RESTAdapter"

    def test_create_adapter_from_config_rest_missing_base_url(self, capsys):
        """Test creating REST adapter without base_url."""
        config = {"type": "rest"}
        adapter = create_adapter_from_config(config)
        assert adapter is None
        captured = capsys.readouterr()
        assert "Error: REST adapter missing required 'base_url'" in captured.out

    def test_create_adapter_from_config_rest_with_config_file(self):
        """Test creating REST adapter with config file."""
        # Create a REST config file
        rest_config = {"headers": {"User-Agent": "Test"}, "timeout": 10}
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(rest_config, f)
            rest_config_file = f.name

        try:
            config = {
                "type": "rest",
                "base_url": "https://api.example.com",
                "config_file": rest_config_file,
            }
            adapter = create_adapter_from_config(config)
            assert adapter is not None
            assert adapter.__class__.__name__ == "RESTAdapter"
        finally:
            os.unlink(rest_config_file)

    def test_create_adapter_from_config_rest_creation_error(self, capsys):
        """Test REST adapter creation failure."""
        config = {
            "type": "rest",
            "base_url": "invalid_url",  # This might cause creation to fail
        }
        # This will still succeed with RESTAdapter, so let's patch it to fail
        creation_error = Exception("Creation failed")
        with patch("data_agents.cli.RESTAdapter", side_effect=creation_error):
            adapter = create_adapter_from_config(config)
            assert adapter is None
            captured = capsys.readouterr()
            assert "Error: Failed to create REST adapter" in captured.out

    def test_create_adapter_from_config_tabular_valid(self):
        """Test creating tabular adapter with valid config."""
        # Create a test CSV file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write("id,name,age\n1,Alice,25\n2,Bob,30\n")
            csv_file = f.name

        try:
            config = {"type": "tabular", "csv_file": csv_file}
            adapter = create_adapter_from_config(config)
            assert adapter is not None
            assert adapter.__class__.__name__ == "TabularAdapter"
        finally:
            os.unlink(csv_file)

    def test_create_adapter_from_config_tabular_missing_csv_file(self, capsys):
        """Test creating tabular adapter without csv_file."""
        config = {"type": "tabular"}
        adapter = create_adapter_from_config(config)
        assert adapter is None
        captured = capsys.readouterr()
        assert "Error: Tabular adapter missing required 'csv_file'" in captured.out

    def test_create_adapter_from_config_tabular_file_not_found(self, capsys):
        """Test creating tabular adapter with non-existent CSV file."""
        config = {"type": "tabular", "csv_file": "nonexistent.csv"}
        adapter = create_adapter_from_config(config)
        assert adapter is None
        captured = capsys.readouterr()
        assert "Error: CSV file nonexistent.csv not found" in captured.out

    def test_create_adapter_from_config_tabular_creation_error(self, capsys):
        """Test tabular adapter creation failure."""
        # Create a valid CSV file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write("id,name,age\n1,Alice,25\n")
            csv_file = f.name

        try:
            config = {"type": "tabular", "csv_file": csv_file}
            # Patch pandas.read_csv to fail
            with patch("pandas.read_csv", side_effect=Exception("CSV read failed")):
                adapter = create_adapter_from_config(config)
                assert adapter is None
                captured = capsys.readouterr()
                assert "Error: Failed to create tabular adapter" in captured.out
        finally:
            os.unlink(csv_file)

    def test_create_adapter_from_config_unknown_type(self, capsys):
        """Test creating adapter with unknown type."""
        config = {"type": "unknown"}
        adapter = create_adapter_from_config(config)
        assert adapter is None
        captured = capsys.readouterr()
        assert (
            "Error: Unknown adapter type 'unknown'. "
            "Supported types: rest, tabular, nasa_power, gbif_occurrence"
            in captured.out
        )

    def test_create_adapter_from_config_nasa_power_valid(self):
        """Test creating NASA POWER adapter with valid config."""
        config = {"type": "nasa_power"}
        adapter = create_adapter_from_config(config)
        assert adapter is not None
        assert adapter.__class__.__name__ == "NasaPowerAdapter"

    def test_create_adapter_from_config_gbif_occurrence_valid(self):
        """Test creating GBIF Occurrence adapter with valid config."""
        config = {"type": "gbif_occurrence"}
        adapter = create_adapter_from_config(config)
        assert adapter is not None
        assert adapter.__class__.__name__ == "GBIFOccurrenceAdapter"

    def test_create_single_adapter_from_config_success(self):
        """Test creating single adapter from config file."""
        # Create a CSV file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write("id,name\n1,Alice\n2,Bob\n")
            csv_file = f.name

        # Create adapter config file
        config = {"type": "tabular", "csv_file": csv_file}
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(config, f)
            config_file = f.name

        try:
            adapter = create_single_adapter_from_config(config_file)
            assert adapter is not None
            assert adapter.__class__.__name__ == "TabularAdapter"
        finally:
            os.unlink(csv_file)
            os.unlink(config_file)

    def test_create_single_adapter_from_config_file_not_found(self):
        """Test creating single adapter with non-existent config file."""
        adapter = create_single_adapter_from_config("nonexistent.json")
        assert adapter is None

    def test_create_router_from_config_success(self):
        """Test creating router from config file."""
        # Create a CSV file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write("id,name\n1,Alice\n2,Bob\n")
            csv_file = f.name

        # Create router config
        config = {
            "adapters": {"test_adapter": {"type": "tabular", "csv_file": csv_file}}
        }
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(config, f)
            config_file = f.name

        try:
            router = create_router_from_config(config_file)
            assert len(router.adapters) == 1
            assert "test_adapter" in router.adapters
        finally:
            os.unlink(csv_file)
            os.unlink(config_file)


class TestCLIErrorPaths:
    """Test CLI error handling and edge cases."""

    def test_cli_query_router_config_empty_results(self, capsys):
        """Test query command with router config that returns empty results."""
        # Create a CSV file with data that won't match the query
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write("id,name,age\n1,Alice,25\n2,Bob,30\n")
            csv_file = f.name

        config = {"adapters": {"test_data": {"type": "tabular", "csv_file": csv_file}}}
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(config, f)
            config_file = f.name

        try:
            with patch(
                "sys.argv",
                ["data-agents", "query", "age > 100", "--router-config", config_file],
            ):
                main()
            captured = capsys.readouterr()
            assert "Results from test_data" in captured.out
            assert "Query returned no results" in captured.out
        finally:
            os.unlink(csv_file)
            os.unlink(config_file)

    def test_cli_query_adapter_config_exception(self, capsys):
        """Test query command with adapter that throws exception."""
        # Create adapter config
        config = {"type": "tabular", "csv_file": "examples/sample_data.csv"}
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(config, f)
            config_file = f.name

        try:
            # Patch the adapter's query method to raise an exception
            query_error = Exception("Query failed")
            with patch(
                "data_agents.adapters.TabularAdapter.query", side_effect=query_error
            ):
                with pytest.raises(SystemExit):
                    with patch(
                        "sys.argv",
                        ["data-agents", "query", "*", "--adapter-config", config_file],
                    ):
                        main()
                captured = capsys.readouterr()
                assert "Query failed: Query failed" in captured.out
        finally:
            os.unlink(config_file)

    def test_cli_discover_adapter_config_failure(self, capsys):
        """Test discover command with adapter config that fails to create."""
        with pytest.raises(SystemExit):
            with patch(
                "sys.argv",
                ["data-agents", "discover", "--adapter-config", "nonexistent.json"],
            ):
                main()
        # The main function should exit with code 1 when adapter creation fails

    def test_cli_info_adapter_config_failure(self, capsys):
        """Test info command with adapter config that fails to create."""
        with pytest.raises(SystemExit):
            with patch(
                "sys.argv",
                ["data-agents", "info", "--adapter-config", "nonexistent.json"],
            ):
                main()
        # The main function should exit with code 1 when adapter creation fails

    def test_cli_query_adapter_config_failure(self, capsys):
        """Test query command with adapter config that fails to create."""
        with pytest.raises(SystemExit):
            with patch(
                "sys.argv",
                ["data-agents", "query", "*", "--adapter-config", "nonexistent.json"],
            ):
                main()
        # The main function should exit with code 1 when adapter creation fails


class TestCLINASAParsing:
    """Test NASA POWER query parsing and execution functionality."""

    def test_parse_nasa_query_basic(self):
        """Test basic NASA query parsing."""
        query = "T2M latitude=40.7 longitude=-74.0 temporal=daily"
        param, kwargs = parse_nasa_query(query)

        assert param == "T2M"
        assert kwargs == {"latitude": 40.7, "longitude": -74.0, "temporal": "daily"}

    def test_parse_nasa_query_integers(self):
        """Test NASA query parsing with integer values."""
        query = "PRECTOTCORR start=20230101 end=20230107 community=AG"
        param, kwargs = parse_nasa_query(query)

        assert param == "PRECTOTCORR"
        assert kwargs == {"start": 20230101, "end": 20230107, "community": "AG"}

    def test_parse_nasa_query_mixed_types(self):
        """Test NASA query parsing with mixed data types."""
        query = (
            "WS2M latitude=40.7128 longitude=-74.0060 start=20230101 "
            "elevation=10 community=AG"
        )
        param, kwargs = parse_nasa_query(query)

        assert param == "WS2M"
        assert kwargs == {
            "latitude": 40.7128,
            "longitude": -74.0060,
            "start": 20230101,
            "elevation": 10,
            "community": "AG",
        }

    def test_parse_nasa_query_empty_string(self):
        """Test NASA query parsing with empty string."""
        with pytest.raises(ValueError, match="Empty query string"):
            parse_nasa_query("")

    def test_parse_nasa_query_no_parameters(self):
        """Test NASA query parsing with just parameter name."""
        query = "T2M"
        param, kwargs = parse_nasa_query(query)

        assert param == "T2M"
        assert kwargs == {}

    def test_parse_nasa_query_malformed_pairs(self):
        """Test NASA query parsing with malformed key=value pairs."""
        query = "T2M latitude=40.7 badpair longitude=-74.0"
        param, kwargs = parse_nasa_query(query)

        assert param == "T2M"
        assert kwargs == {"latitude": 40.7, "longitude": -74.0}

    def test_parse_nasa_query_equals_in_value(self):
        """Test NASA query parsing with equals sign in value."""
        query = "T2M format=JSON units=metric=system"
        param, kwargs = parse_nasa_query(query)

        assert param == "T2M"
        assert kwargs == {"format": "JSON", "units": "metric=system"}

    def test_execute_adapter_query_nasa(self):
        """Test execute_adapter_query with NASA POWER adapter."""
        from data_agents.adapters import NasaPowerAdapter

        # Create a real NASA adapter but mock the query method
        adapter = NasaPowerAdapter()

        with patch.object(
            adapter, "query", return_value=pd.DataFrame({"test": [1, 2, 3]})
        ) as mock_query:
            query_string = "T2M latitude=40.7 longitude=-74.0"
            result = execute_adapter_query(adapter, query_string)

            # Verify the query was called with parsed parameters
            mock_query.assert_called_once_with("T2M", latitude=40.7, longitude=-74.0)
            assert len(result) == 3

    def test_execute_adapter_query_non_nasa(self):
        """Test execute_adapter_query with non-NASA adapter."""
        from data_agents.adapters import TabularAdapter

        # Create a tabular adapter
        adapter = TabularAdapter(
            {"data": pd.DataFrame({"col1": [1, 2], "col2": [3, 4]})}
        )

        # Test that it uses the query string directly
        result = execute_adapter_query(adapter, "*")
        assert len(result) == 2
        assert list(result.columns) == ["col1", "col2"]

    def test_execute_router_query_with_nasa(self):
        """Test execute_router_query with NASA adapter in router."""
        from data_agents.adapters import NasaPowerAdapter, TabularAdapter
        from data_agents.core.router import Router

        router = Router()
        nasa_adapter = NasaPowerAdapter()
        tabular_adapter = TabularAdapter({"data": pd.DataFrame({"col1": [1, 2]})})

        router["nasa"] = nasa_adapter
        router["tabular"] = tabular_adapter

        with patch.object(
            nasa_adapter, "query", return_value=pd.DataFrame({"nasa_data": [1]})
        ) as mock_nasa:
            results = execute_router_query(router, "T2M latitude=40.7")

            # NASA adapter should be called with parsed parameters
            mock_nasa.assert_called_once_with("T2M", latitude=40.7)

            # Should have results from both adapters
            assert "nasa" in results
            assert "tabular" in results
            assert len(results["nasa"]) == 1
            # Tabular adapter will return empty DataFrame for invalid query
            assert len(results["tabular"]) == 0

    def test_execute_router_query_with_error(self, capsys):
        """Test execute_router_query handles adapter errors gracefully."""
        from data_agents.adapters import NasaPowerAdapter
        from data_agents.core.router import Router

        router = Router()
        nasa_adapter = NasaPowerAdapter()
        router["nasa"] = nasa_adapter

        with patch.object(nasa_adapter, "query", side_effect=Exception("API Error")):
            results = execute_router_query(router, "T2M latitude=40.7")

            # Should capture the error and return empty DataFrame
            assert "nasa" in results
            assert len(results["nasa"]) == 0

            # Should print error message
            captured = capsys.readouterr()
            assert "Error querying adapter 'nasa': API Error" in captured.out


class TestCLIEdgeCases:
    """Test CLI edge cases and error handling."""

    def test_create_adapter_nasa_power_creation_error(self, capsys):
        """Test NASA POWER adapter creation with error."""
        config = {"type": "nasa_power"}

        with patch(
            "data_agents.cli.NasaPowerAdapter", side_effect=Exception("NASA API Error")
        ):
            adapter = create_adapter_from_config(config)
            assert adapter is None
            captured = capsys.readouterr()
            assert (
                "Error: Failed to create NASA POWER adapter: NASA API Error"
                in captured.out
            )

    def test_no_adapters_in_router(self, capsys):
        """Test list-adapters command with empty router."""
        router_config = {"adapters": {}}

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(router_config, f)
            config_file = f.name

        try:
            with patch(
                "sys.argv",
                ["data-agents", "list-adapters", "--router-config", config_file],
            ):
                main()
            captured = capsys.readouterr()
            assert "No adapters registered" in captured.out
        finally:
            os.unlink(config_file)

    def test_query_adapter_config_with_nasa_error(self, capsys):
        """Test query with NASA adapter that fails during query execution."""
        config = {"type": "nasa_power"}

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(config, f)
            config_file = f.name

        try:
            with patch(
                "data_agents.adapters.NasaPowerAdapter.query",
                side_effect=Exception("Query Error"),
            ):
                with pytest.raises(SystemExit):
                    with patch(
                        "sys.argv",
                        [
                            "data-agents",
                            "query",
                            "T2M latitude=40.7",
                            "--adapter-config",
                            config_file,
                        ],
                    ):
                        main()
                captured = capsys.readouterr()
                assert "Query failed: Query Error" in captured.out
        finally:
            os.unlink(config_file)


class TestCLIGBIFOccurrence:
    """Test GBIF Occurrence adapter CLI functionality."""

    def test_create_gbif_adapter_from_config_success(self):
        """Test creating GBIF adapter from config file works correctly."""
        config = {"type": "gbif_occurrence", "description": "GBIF biodiversity data"}

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(config, f)
            config_file = f.name

        try:
            adapter = create_single_adapter_from_config(config_file)
            assert adapter is not None
            assert adapter.__class__.__name__ == "GBIFOccurrenceAdapter"
        finally:
            os.unlink(config_file)

    @patch("data_agents.adapters.GBIFOccurrenceAdapter.query")
    def test_query_gbif_adapter_basic(self, mock_query, capsys):
        """Test basic GBIF adapter query execution through CLI."""
        # Mock successful query response
        mock_df = pd.DataFrame(
            {
                "gbifID": ["1", "2"],
                "scientificName": ["Puma concolor", "Panthera leo"],
                "country": ["US", "ZA"],
            }
        )
        mock_df.attrs = {"total_count": 2, "limit": 20, "offset": 0}
        mock_query.return_value = mock_df

        config = {"type": "gbif_occurrence"}

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(config, f)
            config_file = f.name

        try:
            with patch(
                "sys.argv",
                [
                    "data-agents",
                    "query",
                    "scientificName=Puma concolor",
                    "--adapter-config",
                    config_file,
                ],
            ):
                main()

            captured = capsys.readouterr()
            assert "gbifID" in captured.out
            assert "Puma concolor" in captured.out
            # CLI doesn't print metadata - only DataFrame content
            mock_query.assert_called_once_with("scientificName=Puma concolor")
        finally:
            os.unlink(config_file)

    @patch("data_agents.adapters.GBIFOccurrenceAdapter.query")
    def test_query_gbif_adapter_complex(self, mock_query, capsys):
        """Test complex GBIF adapter query with multiple parameters."""
        # Mock successful query response
        mock_df = pd.DataFrame(
            {
                "gbifID": ["123"],
                "scientificName": ["Homo sapiens"],
                "country": ["US"],
                "year": [2023],
            }
        )
        mock_df.attrs = {"total_count": 1, "limit": 20, "offset": 0}
        mock_query.return_value = mock_df

        config = {"type": "gbif_occurrence"}

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(config, f)
            config_file = f.name

        try:
            with patch(
                "sys.argv",
                [
                    "data-agents",
                    "query",
                    "scientificName=Homo sapiens&country=US&year=2023",
                    "--adapter-config",
                    config_file,
                ],
            ):
                main()

            captured = capsys.readouterr()
            assert "gbifID" in captured.out
            assert "Homo sapiens" in captured.out
            # CLI doesn't print metadata - only DataFrame content
            mock_query.assert_called_once_with(
                "scientificName=Homo sapiens&country=US&year=2023"
            )
        finally:
            os.unlink(config_file)

    def test_query_gbif_adapter_config_with_error(self, capsys):
        """Test query with GBIF adapter that fails during query execution."""
        config = {"type": "gbif_occurrence"}

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(config, f)
            config_file = f.name

        try:
            with patch(
                "data_agents.adapters.GBIFOccurrenceAdapter.query",
                side_effect=Exception("GBIF API Error"),
            ):
                with pytest.raises(SystemExit):
                    with patch(
                        "sys.argv",
                        [
                            "data-agents",
                            "query",
                            "scientificName=Puma concolor",
                            "--adapter-config",
                            config_file,
                        ],
                    ):
                        main()
                captured = capsys.readouterr()
                assert "Query failed: GBIF API Error" in captured.out
        finally:
            os.unlink(config_file)

    def test_gbif_adapter_in_router_config(self, capsys):
        """Test GBIF adapter creation and listing in router configuration."""
        router_config = {
            "adapters": {
                "gbif_mammals": {
                    "type": "gbif_occurrence",
                    "description": "GBIF mammal occurrences",
                }
            }
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(router_config, f)
            config_file = f.name

        try:
            with patch(
                "sys.argv",
                ["data-agents", "list-adapters", "--router-config", config_file],
            ):
                main()
            captured = capsys.readouterr()
            assert "gbif_mammals" in captured.out
            assert "GBIFOccurrenceAdapter" in captured.out
            # CLI doesn't show descriptions in list-adapters output
        finally:
            os.unlink(config_file)
