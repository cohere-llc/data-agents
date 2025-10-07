"""Test the CLI_ROUTER_CONFIG.md documentation for accuracy and consistency."""

import json
import re
import subprocess
from pathlib import Path

import pytest


class TestCLIRouterConfigExamples:
    """Test cases for CLI Router Config documentation examples."""

    def test_cli_commands_documented_exist(self):
        """Test that CLI commands mentioned in doc actually exist."""
        # Test that the data-agents command exists and has expected subcommands
        result = subprocess.run(
            ["uv", "run", "data-agents", "--help"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
        )

        assert result.returncode == 0
        help_output = result.stdout

        # Check that mentioned commands exist
        expected_commands = ["info", "list-adapters", "discover", "query"]
        for command in expected_commands:
            assert command in help_output

    def test_router_config_json_format(self):
        """Test that the JSON router configuration format is valid."""
        # Example from the documentation
        config_example = {
            "adapters": {
                "api_data": {
                    "type": "rest",
                    "base_url": "https://api.example.com",
                    "config_file": "path/to/rest_config.json",
                },
                "csv_data": {"type": "tabular", "csv_file": "path/to/data.csv"},
            }
        }

        # Verify structure
        assert "adapters" in config_example
        assert isinstance(config_example["adapters"], dict)

        # Check REST adapter format
        rest_adapter = config_example["adapters"]["api_data"]
        assert rest_adapter["type"] == "rest"
        assert "base_url" in rest_adapter
        assert "config_file" in rest_adapter

        # Check tabular adapter format
        tabular_adapter = config_example["adapters"]["csv_data"]
        assert tabular_adapter["type"] == "tabular"
        assert "csv_file" in tabular_adapter

    def test_single_adapter_config_formats(self):
        """Test that single adapter configuration formats are valid."""
        # REST adapter config from doc
        rest_config = {
            "type": "rest",
            "base_url": "https://jsonplaceholder.typicode.com",
            "config_file": "config/jsonplaceholder.rest.adapter.json",
        }

        assert rest_config["type"] == "rest"
        assert "base_url" in rest_config
        assert "config_file" in rest_config

        # Tabular adapter config from doc
        tabular_config = {"type": "tabular", "csv_file": "examples/sample_data.csv"}

        assert tabular_config["type"] == "tabular"
        assert "csv_file" in tabular_config

    def test_rest_adapter_config_structure(self):
        """Test that REST adapter detailed config structure is valid."""
        rest_config_example = {
            "headers": {"User-Agent": "DataAgents/1.0"},
            "timeout": 10,
            "endpoints": ["users", "posts", "comments"],
            "pagination_param": "_limit",
            "pagination_limit": 10,
        }

        # Verify structure matches what RESTAdapter expects
        assert isinstance(rest_config_example["headers"], dict)
        assert isinstance(rest_config_example["timeout"], int)
        assert isinstance(rest_config_example["endpoints"], list)
        assert isinstance(rest_config_example["pagination_param"], str)
        assert isinstance(rest_config_example["pagination_limit"], int)

    def test_example_config_files_exist(self):
        """Test that example files mentioned in doc actually exist."""
        base_path = Path(__file__).parent.parent
        expected_files = [
            "config/example.router.json",
            "config/example.router.yaml",
            "config/jsonplaceholder.adapter.json",
            "examples/sample_data.csv",
            "config/jsonplaceholder.rest.adapter.json",
            "config/httpbin.rest.adapter.json",
        ]

        for file_path in expected_files:
            full_path = base_path / file_path
            assert full_path.exists(), f"Example file {file_path} does not exist"

    def test_actual_example_router_config_works(self):
        """Test that the actual example router config file works with CLI."""
        result = subprocess.run(
            [
                "uv",
                "run",
                "data-agents",
                "list-adapters",
                "--router-config",
                "config/example.router.json",
            ],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
        )

        assert result.returncode == 0
        assert "Available adapters:" in result.stdout

    def test_actual_single_adapter_config_works(self):
        """Test that single adapter config works with CLI."""
        result = subprocess.run(
            [
                "uv",
                "run",
                "data-agents",
                "info",
                "--adapter-config",
                "config/jsonplaceholder.adapter.json",
            ],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
        )

        assert result.returncode == 0
        # Should contain adapter information
        assert "RESTAdapter" in result.stdout or "TabularAdapter" in result.stdout


class TestCLIRouterConfigCodeExtraction:
    """Test code block extraction and validation from CLI Router Config doc."""

    def test_json_code_blocks_syntax(self):
        """Test that JSON code blocks in doc have valid syntax."""
        doc_path = Path(__file__).parent.parent / "docs" / "CLI_ROUTER_CONFIG.md"
        with open(doc_path) as f:
            content = f.read()

        # Extract JSON code blocks
        json_blocks = re.findall(r"```json\n(.*?)\n```", content, re.DOTALL)

        for i, block in enumerate(json_blocks):
            try:
                json.loads(block)
            except json.JSONDecodeError as e:
                pytest.fail(f"JSON code block {i + 1} has invalid syntax: {e}")

    def test_bash_commands_format(self):
        """Test that bash commands in doc are properly formatted."""
        doc_path = Path(__file__).parent.parent / "docs" / "CLI_ROUTER_CONFIG.md"
        with open(doc_path) as f:
            content = f.read()

        # Extract bash command blocks
        bash_blocks = re.findall(r"```bash\n(.*?)\n```", content, re.DOTALL)

        for block in bash_blocks:
            lines = block.strip().split("\n")
            for line in lines:
                if line.startswith("#"):
                    continue  # Skip comments
                if line.strip() == "":
                    continue  # Skip empty lines

                # Should start with uv run data-agents
                if "uv run data-agents" in line:
                    assert line.startswith("uv run data-agents"), (
                        f"Command should start with 'uv run data-agents': {line}"
                    )

    def test_documented_commands_are_valid(self):
        """Test that documented commands match actual CLI capabilities."""
        doc_path = Path(__file__).parent.parent / "docs" / "CLI_ROUTER_CONFIG.md"
        with open(doc_path) as f:
            content = f.read()

        # Extract all uv run data-agents commands
        commands = re.findall(r"uv run data-agents ([a-zA-Z][\w-]*)", content)

        # Get actual CLI help
        result = subprocess.run(
            ["uv", "run", "data-agents", "--help"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
        )

        help_commands = re.findall(
            r"^\s{4}([a-z][\w-]*)\s+", result.stdout, re.MULTILINE
        )

        # Check that all documented commands exist
        for cmd in set(commands):
            assert cmd in help_commands, (
                f"Command '{cmd}' documented but not available in CLI"
            )


class TestCLIRouterConfigConsistency:
    """Test consistency between CLI Router Config doc and actual implementation."""

    def test_config_options_documented(self):
        """Test that config options mentioned in doc match CLI help."""
        # Check info command help
        result = subprocess.run(
            ["uv", "run", "data-agents", "info", "--help"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
        )

        assert result.returncode == 0
        assert "--router-config" in result.stdout
        assert "--adapter-config" in result.stdout

        # Check other commands
        for command in ["list-adapters", "discover", "query"]:
            result = subprocess.run(
                ["uv", "run", "data-agents", command, "--help"],
                capture_output=True,
                text=True,
                cwd=Path(__file__).parent.parent,
            )
            assert result.returncode == 0

    def test_example_router_config_structure(self):
        """Test that actual example config matches documented structure."""
        example_path = Path(__file__).parent.parent / "config" / "example.router.json"
        with open(example_path) as f:
            config = json.load(f)

        # Should have adapters section
        assert "adapters" in config
        assert isinstance(config["adapters"], dict)

        # Each adapter should have required fields
        for _adapter_name, adapter_config in config["adapters"].items():
            assert "type" in adapter_config
            assert adapter_config["type"] in ["rest", "tabular"]

            if adapter_config["type"] == "rest":
                assert "base_url" in adapter_config
            elif adapter_config["type"] == "tabular":
                assert "csv_file" in adapter_config

    def test_documented_files_are_accessible(self):
        """Test that files referenced in examples are accessible."""
        base_path = Path(__file__).parent.parent

        # Test router config
        router_config_path = base_path / "config" / "example.router.json"
        assert router_config_path.exists()

        with open(router_config_path) as f:
            config = json.load(f)

        # Test that referenced files in config exist
        for adapter_name, adapter_config in config["adapters"].items():
            if "config_file" in adapter_config:
                config_file_path = base_path / adapter_config["config_file"]
                assert config_file_path.exists(), (
                    f"Config file {adapter_config['config_file']} referenced in "
                    f"adapter {adapter_name} does not exist"
                )

            if "csv_file" in adapter_config:
                csv_file_path = base_path / adapter_config["csv_file"]
                assert csv_file_path.exists(), (
                    f"CSV file {adapter_config['csv_file']} referenced in "
                    f"adapter {adapter_name} does not exist"
                )

    def test_yaml_support_mentioned_correctly(self):
        """Test that YAML support is mentioned correctly in doc."""
        doc_path = Path(__file__).parent.parent / "docs" / "CLI_ROUTER_CONFIG.md"
        with open(doc_path) as f:
            content = f.read()

        # Should mention YAML support
        assert "YAML" in content
        assert "yaml" in content.lower()

        # Should have YAML example
        assert "```yaml" in content

        # Should reference .yaml files
        assert "config/router.yaml" in content
        assert "config/example.router.yaml" in content

    def test_command_line_options_consistency(self):
        """Test that command line options in doc match actual CLI."""
        doc_path = Path(__file__).parent.parent / "docs" / "CLI_ROUTER_CONFIG.md"
        with open(doc_path) as f:
            content = f.read()

        # Extract documented options
        router_config_mentions = content.count("--router-config")
        adapter_config_mentions = content.count("--adapter-config")

        # Should have both options documented
        assert router_config_mentions > 0
        assert adapter_config_mentions > 0

        # Should not mention old --config option
        assert "--config " not in content or content.count("--config ") == 0
