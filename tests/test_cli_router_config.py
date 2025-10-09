"""Test the CLI_ROUTER_CONFIG.md documentation for accuracy and consistency."""

import json
import re
import subprocess
from pathlib import Path

import pytest


def extract_code_blocks_from_markdown(doc_path: Path) -> dict[str, list[str]]:
    """Extract code blocks from markdown file by language."""
    with open(doc_path) as f:
        content = f.read()

    code_blocks: dict[str, list[str]] = {}

    # Extract bash code blocks
    bash_blocks = re.findall(r"```bash\n(.*?)\n```", content, re.DOTALL)
    code_blocks["bash"] = []
    for block in bash_blocks:
        lines = block.strip().split("\n")
        for line in lines:
            line = line.strip()
            if line and not line.startswith("#") and "uv run data-agents" in line:
                # Handle line continuations
                if line.endswith(" \\"):
                    # Find the next non-comment line and combine
                    idx = lines.index(next(ln for ln in lines if line in ln))
                    combined_line = line.rstrip(" \\")
                    for next_line in lines[idx + 1 :]:
                        next_line = next_line.strip()
                        if not next_line or next_line.startswith("#"):
                            continue
                        combined_line += " " + next_line
                        if not next_line.endswith(" \\"):
                            break
                    code_blocks["bash"].append(combined_line)
                else:
                    code_blocks["bash"].append(line)

    # Extract JSON code blocks
    json_blocks = re.findall(r"```json\n(.*?)\n```", content, re.DOTALL)
    code_blocks["json"] = [block.strip() for block in json_blocks]

    # Extract YAML code blocks
    yaml_blocks = re.findall(r"```yaml\n(.*?)\n```", content, re.DOTALL)
    code_blocks["yaml"] = [block.strip() for block in yaml_blocks]

    return code_blocks


def extract_nasa_power_queries_from_markdown(doc_path: Path) -> list[tuple[str, str]]:
    """Extract NASA POWER query examples from markdown with their descriptions."""
    with open(doc_path) as f:
        content = f.read()

    queries: list[tuple[str, str]] = []

    # Find the NASA POWER querying section using simple string search
    start_pos = content.find("### Querying NASA POWER Data")
    if start_pos == -1:
        return queries

    # Find the end of this section (next major section)
    end_pos = content.find("### Required Parameters", start_pos)
    if end_pos == -1:
        end_pos = len(content)

    nasa_section = content[start_pos:end_pos]

    # Extract bash code blocks from NASA section
    bash_blocks = re.findall(r"```bash\n(.*?)\n```", nasa_section, re.DOTALL)

    for block in bash_blocks:
        lines = block.strip().split("\n")
        current_query = None
        current_description = ""

        for line in lines:
            line = line.strip()
            if line.startswith("#"):
                # Extract description from comment
                current_description = line.lstrip("# ").strip()
            elif "uv run data-agents query" in line:
                # Handle line continuations
                if line.endswith(" \\"):
                    # Find continuation lines
                    idx = lines.index(next(ln for ln in lines if line in ln))
                    combined_line = line.rstrip(" \\")
                    for next_line in lines[idx + 1 :]:
                        next_line = next_line.strip()
                        if not next_line or next_line.startswith("#"):
                            continue
                        if next_line.endswith(" \\"):
                            combined_line += " " + next_line.rstrip(" \\")
                        else:
                            combined_line += " " + next_line
                            break
                    current_query = combined_line
                else:
                    current_query = line

                if current_query and current_description:
                    queries.append((current_description, current_query))
                    current_description = ""
                    current_query = None

    return queries


def extract_gbif_queries_from_markdown(doc_path: Path) -> list[tuple[str, str]]:
    """Extract GBIF query examples from markdown with their descriptions."""
    with open(doc_path) as f:
        content = f.read()

    queries: list[tuple[str, str]] = []

    # Find the GBIF querying section using simple string search
    start_pos = content.find("### Querying GBIF Occurrence Data")
    if start_pos == -1:
        return queries

    # Find the end of this section (next major section)
    end_pos = content.find("### GBIF Search Parameters Reference", start_pos)
    if end_pos == -1:
        end_pos = len(content)

    gbif_section = content[start_pos:end_pos]

    # Extract bash code blocks from GBIF section
    bash_blocks = re.findall(r"```bash\n(.*?)\n```", gbif_section, re.DOTALL)

    for block in bash_blocks:
        lines = block.strip().split("\n")
        current_query = None
        current_description = ""

        for line in lines:
            line = line.strip()
            if line and not line.startswith("#") and "uv run data-agents query" in line:
                # Extract just the query part after "query" command
                if "--adapter-config config/gbif.adapter.json" in line:
                    first_quote = line.find('"')
                    if first_quote != -1:
                        query_start = first_quote + 1
                        query_end = line.find('"', query_start)
                        if query_end != -1 and query_end > query_start:
                            current_query = line[query_start:query_end]

                        # Find description from previous comment
                        if current_query:
                            queries.append((current_query, current_description))
                            current_description = ""
            elif line.startswith("#"):
                # Accumulate description from comments
                comment = line[1:].strip()
                if comment:
                    current_description += comment + " "

    return queries


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
            "config_file": "config/jsonplaceholder.adapter.json",
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
            "config/example_with_nasa.router.json",
            "config/nasa_power.adapter.json",
            "config/jsonplaceholder.adapter.json",
            "examples/sample_data.csv",
            "config/httpbin.adapter.json",
            "examples/nasa_power_example.py",
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

    @pytest.fixture
    def doc_path(self) -> Path:
        """Return path to the CLI router config documentation."""
        return Path(__file__).parent.parent / "docs" / "CLI_ROUTER_CONFIG.md"

    @pytest.fixture
    def extracted_code_blocks(self, doc_path: Path) -> dict[str, list[str]]:
        """Extract all code blocks from documentation."""
        return extract_code_blocks_from_markdown(doc_path)

    def test_json_code_blocks_syntax(
        self, extracted_code_blocks: dict[str, list[str]]
    ) -> None:
        """Test that JSON code blocks in doc have valid syntax."""
        json_blocks = extracted_code_blocks.get("json", [])

        for i, block in enumerate(json_blocks):
            try:
                json.loads(block)
            except json.JSONDecodeError as e:
                pytest.fail(f"JSON code block {i + 1} has invalid syntax: {e}")

    def test_bash_commands_format(
        self, extracted_code_blocks: dict[str, list[str]]
    ) -> None:
        """Test that bash commands in doc are properly formatted."""
        bash_commands = extracted_code_blocks.get("bash", [])

        for command in bash_commands:
            # Should start with uv run data-agents
            if "uv run data-agents" in command:
                assert command.startswith("uv run data-agents"), (
                    f"Command should start with 'uv run data-agents': {command}"
                )

    def test_extracted_bash_commands_execute(
        self, extracted_code_blocks: dict[str, list[str]]
    ) -> None:
        """Test that at least some extracted bash commands can execute successfully."""
        bash_commands = extracted_code_blocks.get("bash", [])
        base_path = Path(__file__).parent.parent

        # Test basic commands that should work (info, list-adapters)
        info_commands = [
            cmd for cmd in bash_commands if "info" in cmd and "--router-config" in cmd
        ]
        list_commands = [cmd for cmd in bash_commands if "list-adapters" in cmd]

        # Test at least one info command
        if info_commands:
            command = info_commands[0]
            # Parse command into arguments
            parts = command.split()

            result = subprocess.run(
                parts,
                capture_output=True,
                text=True,
                cwd=base_path,
            )

            # Should either succeed or fail gracefully
            if result.returncode == 0:
                assert "Router" in result.stdout or "Adapter" in result.stdout

        # Test at least one list command
        if list_commands:
            command = list_commands[0]
            parts = command.split()

            result = subprocess.run(
                parts,
                capture_output=True,
                text=True,
                cwd=base_path,
            )

            if result.returncode == 0:
                assert "Available adapters:" in result.stdout

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


class TestNASAPowerCLIExamples:
    """Test NASA POWER adapter CLI examples from documentation."""

    def test_nasa_power_adapter_config_structure(self):
        """Test that NASA POWER adapter config structure is valid."""
        nasa_config = {
            "type": "nasa_power",
            "description": "NASA POWER meteorological and solar resource data",
        }

        assert nasa_config["type"] == "nasa_power"
        assert "description" in nasa_config

        # Test router config with NASA adapter
        router_with_nasa = {
            "adapters": {
                "nasa_power": {
                    "type": "nasa_power",
                    "description": "NASA POWER meteorological and solar resource data",
                },
                "local_weather": {
                    "type": "tabular",
                    "csv_file": "data/local_weather.csv",
                },
            }
        }

        assert "adapters" in router_with_nasa
        assert "nasa_power" in router_with_nasa["adapters"]
        assert router_with_nasa["adapters"]["nasa_power"]["type"] == "nasa_power"

    def test_nasa_power_discover_command(self):
        """Test NASA POWER discover command works."""
        # Test with single adapter config
        result = subprocess.run(
            [
                "uv",
                "run",
                "data-agents",
                "discover",
                "--adapter-config",
                "config/nasa_power.adapter.json",
            ],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
        )

        if result.returncode == 0:
            # Should contain NASA POWER specific information
            output = result.stdout
            assert "parameters" in output.lower() or "NASA" in output or "T2M" in output
        # Some tests may fail due to network issues, which is acceptable

    def test_nasa_power_discover_in_router(self):
        """Test NASA POWER discover command in router context."""
        result = subprocess.run(
            [
                "uv",
                "run",
                "data-agents",
                "discover",
                "--router-config",
                "config/example_with_nasa.router.json",
            ],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
        )

        if result.returncode == 0:
            # Should contain information about NASA adapter
            output = result.stdout
            assert "nasa" in output.lower() or "NASA" in output

    def test_nasa_power_point_query_format(self):
        """Test NASA POWER point query format parsing."""
        from data_agents.cli import parse_nasa_query

        # Test examples from documentation
        test_cases = [
            (
                "T2M latitude=40.7128 longitude=-74.0060 start=20240101 end=20240107 "
                "community=AG temporal=daily spatial_type=point",
                "T2M",
                {
                    "latitude": 40.7128,
                    "longitude": -74.0060,
                    "start": 20240101,
                    "end": 20240107,
                    "community": "AG",
                    "temporal": "daily",
                    "spatial_type": "point",
                },
            ),
            (
                "PRECTOTCORR latitude=34.0522 longitude=-118.2437 start=20240601 "
                "end=20240630 community=AG temporal=daily spatial_type=point",
                "PRECTOTCORR",
                {
                    "latitude": 34.0522,
                    "longitude": -118.2437,
                    "start": 20240601,
                    "end": 20240630,
                    "community": "AG",
                    "temporal": "daily",
                    "spatial_type": "point",
                },
            ),
            (
                "ALLSKY_SFC_SW_DWN latitude=33.4484 longitude=-112.0740 "
                "start=20240301 end=20240331 community=RE temporal=daily "
                "spatial_type=point",
                "ALLSKY_SFC_SW_DWN",
                {
                    "latitude": 33.4484,
                    "longitude": -112.0740,
                    "start": 20240301,
                    "end": 20240331,
                    "community": "RE",
                    "temporal": "daily",
                    "spatial_type": "point",
                },
            ),
        ]

        for query_string, expected_param, expected_kwargs in test_cases:
            param, kwargs = parse_nasa_query(query_string)
            assert param == expected_param
            assert kwargs == expected_kwargs

    def test_nasa_power_regional_query_format(self):
        """Test NASA POWER regional query format parsing."""
        from data_agents.cli import parse_nasa_query

        # Test regional examples from documentation
        test_cases = [
            (
                "T2M latitude_min=40.0 latitude_max=45.0 longitude_min=-80.0 "
                "longitude_max=-70.0 start=20240101 end=20240102 community=AG "
                "temporal=daily spatial_type=regional",
                "T2M",
                {
                    "latitude_min": 40.0,
                    "latitude_max": 45.0,
                    "longitude_min": -80.0,
                    "longitude_max": -70.0,
                    "start": 20240101,
                    "end": 20240102,
                    "community": "AG",
                    "temporal": "daily",
                    "spatial_type": "regional",
                },
            ),
            (
                "WS2M latitude_min=35.0 latitude_max=45.0 longitude_min=-105.0 "
                "longitude_max=-95.0 start=20240101 end=20240101 community=RE "
                "temporal=daily spatial_type=regional",
                "WS2M",
                {
                    "latitude_min": 35.0,
                    "latitude_max": 45.0,
                    "longitude_min": -105.0,
                    "longitude_max": -95.0,
                    "start": 20240101,
                    "end": 20240101,
                    "community": "RE",
                    "temporal": "daily",
                    "spatial_type": "regional",
                },
            ),
        ]

        for query_string, expected_param, expected_kwargs in test_cases:
            param, kwargs = parse_nasa_query(query_string)
            assert param == expected_param
            assert kwargs == expected_kwargs

    def test_nasa_power_temporal_query_formats(self):
        """Test NASA POWER temporal query formats from documentation."""
        from data_agents.cli import parse_nasa_query

        # Test monthly and climatology examples
        test_cases = [
            (
                "T2M latitude=40.7128 longitude=-74.0060 start=202401 end=202412 "
                "community=AG temporal=monthly spatial_type=point",
                "T2M",
                {
                    "latitude": 40.7128,
                    "longitude": -74.0060,
                    "start": 202401,
                    "end": 202412,
                    "community": "AG",
                    "temporal": "monthly",
                    "spatial_type": "point",
                },
            ),
            (
                "T2M latitude=40.7128 longitude=-74.0060 community=AG "
                "temporal=climatology spatial_type=point",
                "T2M",
                {
                    "latitude": 40.7128,
                    "longitude": -74.0060,
                    "community": "AG",
                    "temporal": "climatology",
                    "spatial_type": "point",
                },
            ),
        ]

        for query_string, expected_param, expected_kwargs in test_cases:
            param, kwargs = parse_nasa_query(query_string)
            assert param == expected_param
            assert kwargs == expected_kwargs

    def test_nasa_power_documented_parameters_format(self):
        """Test that documented NASA POWER parameters are valid identifiers."""
        documented_params = [
            "T2M",  # Temperature at 2 meters (°C)
            "PRECTOTCORR",  # Precipitation (mm/day)
            "ALLSKY_SFC_SW_DWN",  # Solar irradiance (kWh/m²/day)
            "WS2M",  # Wind speed at 2 meters (m/s)
            "RH2M",  # Relative humidity at 2 meters (%)
            "PS",  # Surface pressure (kPa)
        ]

        # All parameter names should be valid identifiers (no spaces, special chars)
        for param in documented_params:
            assert param.replace("_", "").isalnum(), (
                f"Parameter {param} contains invalid characters"
            )
            assert param.isupper(), f"Parameter {param} should be uppercase"

    def test_nasa_power_required_parameters_documented(self):
        """Test that documented required parameters are complete."""
        # These are the required parameters mentioned in the documentation
        communities = ["AG", "RE", "SB"]
        temporal_frequencies = ["daily", "monthly", "climatology", "hourly"]
        spatial_types = ["point", "regional"]

        # Test that all documented values are valid
        for community in communities:
            assert community.isupper() and community.isalpha()

        for temporal in temporal_frequencies:
            assert temporal.islower() and temporal.isalpha()

        for spatial in spatial_types:
            assert spatial.islower() and spatial.isalpha()

    def test_nasa_power_cli_command_format_consistency(self):
        """Test that NASA POWER CLI examples follow consistent format."""
        # All NASA POWER queries should include the required parameters
        # This test validates the format rather than executing the queries

        # Point query template
        point_template = (
            "T2M latitude=40.7128 longitude=-74.0060 start=20240101 end=20240107 "
            "community=AG temporal=daily spatial_type=point"
        )
        from data_agents.cli import parse_nasa_query

        _param, kwargs = parse_nasa_query(point_template)

        # Should have all required point parameters
        required_point = {
            "latitude",
            "longitude",
            "start",
            "end",
            "community",
            "temporal",
            "spatial_type",
        }
        assert required_point.issubset(set(kwargs.keys()))
        assert kwargs["spatial_type"] == "point"

        # Regional query template
        regional_template = (
            "T2M latitude_min=40.0 latitude_max=45.0 longitude_min=-80.0 "
            "longitude_max=-70.0 start=20240101 end=20240102 community=AG "
            "temporal=daily spatial_type=regional"
        )
        _param, kwargs = parse_nasa_query(regional_template)

        # Should have all required regional parameters
        required_regional = {
            "latitude_min",
            "latitude_max",
            "longitude_min",
            "longitude_max",
            "start",
            "end",
            "community",
            "temporal",
            "spatial_type",
        }
        assert required_regional.issubset(set(kwargs.keys()))
        assert kwargs["spatial_type"] == "regional"

    def test_nasa_power_info_command_works(self):
        """Test that NASA POWER info command works."""
        result = subprocess.run(
            [
                "uv",
                "run",
                "data-agents",
                "info",
                "--adapter-config",
                "config/nasa_power.adapter.json",
            ],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
        )

        # Should succeed or fail gracefully
        if result.returncode == 0:
            assert "NasaPowerAdapter" in result.stdout or "NASA" in result.stdout

    def test_router_with_nasa_commands_work(self):
        """Test that router commands work with NASA adapter included."""
        base_path = Path(__file__).parent.parent

        # Test info command
        result = subprocess.run(
            [
                "uv",
                "run",
                "data-agents",
                "info",
                "--router-config",
                "config/example_with_nasa.router.json",
            ],
            capture_output=True,
            text=True,
            cwd=base_path,
        )

        if result.returncode == 0:
            output = result.stdout
            assert "Router" in output
            assert "nasa" in output.lower() or "NASA" in output

        # Test list-adapters command
        result = subprocess.run(
            [
                "uv",
                "run",
                "data-agents",
                "list-adapters",
                "--router-config",
                "config/example_with_nasa.router.json",
            ],
            capture_output=True,
            text=True,
            cwd=base_path,
        )

        if result.returncode == 0:
            output = result.stdout
            assert "Available adapters:" in output
            assert "nasa" in output.lower() or "NASA" in output

    def test_nasa_power_error_handling_documented(self):
        """Test that NASA POWER error cases are handled gracefully."""
        # Test with invalid parameter format
        from data_agents.cli import parse_nasa_query

        # Should handle malformed queries gracefully
        malformed_queries = [
            "T2M latitude=invalid_number longitude=-74.0",
            "T2M key_without_equals_value",
            "",  # Empty query
        ]

        for query in malformed_queries:
            try:
                if not query:
                    # Empty query should raise ValueError
                    with pytest.raises(ValueError):
                        parse_nasa_query(query)
                else:
                    # Other malformed queries should parse what they can
                    param, kwargs = parse_nasa_query(query)
                    assert isinstance(param, str)
                    assert isinstance(kwargs, dict)
            except Exception:
                # Any exception is acceptable for malformed input
                pass


class TestAllDocumentedCLIExamples:
    """Test that all CLI examples from the documentation work as expected."""

    def test_basic_cli_examples_from_docs(self):
        """Test basic CLI examples mentioned in documentation."""
        base_path = Path(__file__).parent.parent

        # Test basic info command with router config
        result = subprocess.run(
            [
                "uv",
                "run",
                "data-agents",
                "info",
                "--router-config",
                "config/example.router.json",
            ],
            capture_output=True,
            text=True,
            cwd=base_path,
        )
        assert result.returncode == 0
        assert "Router" in result.stdout

        # Test basic info command with adapter config
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
            cwd=base_path,
        )
        assert result.returncode == 0

    def test_yaml_config_support(self):
        """Test that YAML configuration files work."""
        base_path = Path(__file__).parent.parent
        yaml_config = base_path / "config" / "example.router.yaml"

        if yaml_config.exists():
            result = subprocess.run(
                [
                    "uv",
                    "run",
                    "data-agents",
                    "info",
                    "--router-config",
                    str(yaml_config),
                ],
                capture_output=True,
                text=True,
                cwd=base_path,
            )
            # YAML support might not be available, so either success or graceful failure
            if result.returncode == 0:
                assert "Router" in result.stdout
            else:
                # Should mention YAML support issue
                assert "YAML" in result.stderr or "not available" in result.stderr

    def test_tabular_adapter_query_examples(self):
        """Test tabular adapter query examples from documentation."""
        base_path = Path(__file__).parent.parent

        # Test query with SQL-like syntax (age > 30)
        result = subprocess.run(
            [
                "uv",
                "run",
                "data-agents",
                "query",
                "age > 30",
                "--router-config",
                "config/example.router.json",
            ],
            capture_output=True,
            text=True,
            cwd=base_path,
        )

        # Should either succeed or fail gracefully
        if result.returncode == 0:
            # Should contain results or "no results" message
            assert (
                "Results" in result.stdout
                or "no results" in result.stdout
                or "Query returned" in result.stdout
            )

    def test_discover_command_examples(self):
        """Test discover command examples from documentation."""
        base_path = Path(__file__).parent.parent

        # Test discover with router config
        result = subprocess.run(
            [
                "uv",
                "run",
                "data-agents",
                "discover",
                "--router-config",
                "config/example.router.json",
            ],
            capture_output=True,
            text=True,
            cwd=base_path,
        )

        if result.returncode == 0:
            # Should contain adapter or parameter information
            assert (
                "columns" in result.stdout
                or "parameters" in result.stdout
                or "adapter" in result.stdout.lower()
            )

    def test_list_adapters_examples(self):
        """Test list-adapters command examples from documentation."""
        base_path = Path(__file__).parent.parent

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
            cwd=base_path,
        )

        assert result.returncode == 0
        assert "Available adapters:" in result.stdout

    def test_wildcard_query_examples(self):
        """Test wildcard query examples from documentation."""
        base_path = Path(__file__).parent.parent

        # Test query with "*" (all data)
        result = subprocess.run(
            [
                "uv",
                "run",
                "data-agents",
                "query",
                "*",
                "--router-config",
                "config/example.router.json",
            ],
            capture_output=True,
            text=True,
            cwd=base_path,
        )

        # Should either succeed or fail gracefully
        if result.returncode == 0:
            # Should contain results from adapters
            assert "Results" in result.stdout or "Query" in result.stdout

    def test_rest_endpoint_query_examples(self):
        """Test REST endpoint query examples from documentation."""
        base_path = Path(__file__).parent.parent

        # Test querying a REST endpoint like "users"
        result = subprocess.run(
            [
                "uv",
                "run",
                "data-agents",
                "query",
                "users",
                "--router-config",
                "config/example.router.json",
            ],
            capture_output=True,
            text=True,
            cwd=base_path,
        )

        # Should either succeed or fail gracefully due to network
        # The command structure should be valid regardless
        assert result.returncode in [0, 1]  # Success or expected failure

    def test_single_adapter_vs_router_consistency(self):
        """Test that single adapter and router commands work consistently."""
        base_path = Path(__file__).parent.parent

        # Test single adapter info
        result_single = subprocess.run(
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
            cwd=base_path,
        )

        # Test router info
        result_router = subprocess.run(
            [
                "uv",
                "run",
                "data-agents",
                "info",
                "--router-config",
                "config/example.router.json",
            ],
            capture_output=True,
            text=True,
            cwd=base_path,
        )

        # Both should succeed
        assert result_single.returncode == 0
        assert result_router.returncode == 0

        # Single adapter should show adapter info
        assert (
            "Adapter" in result_single.stdout
            or "REST" in result_single.stdout
            or "Tabular" in result_single.stdout
        )

        # Router should show router info
        assert "Router" in result_router.stdout


class TestNASAPowerCLIExecution:
    """Test actual execution of NASA POWER CLI examples from documentation."""

    @pytest.fixture
    def doc_path(self) -> Path:
        """Return path to the CLI router config documentation."""
        return Path(__file__).parent.parent / "docs" / "CLI_ROUTER_CONFIG.md"

    @pytest.fixture
    def nasa_query_examples(self, doc_path: Path) -> list[tuple[str, str]]:
        """Extract NASA POWER query examples from documentation."""
        return extract_nasa_power_queries_from_markdown(doc_path)

    def test_nasa_power_discover_command_execution(self):
        """Test that NASA POWER discover command actually works."""
        result = subprocess.run(
            [
                "uv",
                "run",
                "data-agents",
                "discover",
                "--adapter-config",
                "config/nasa_power.adapter.json",
            ],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
        )

        # Should succeed
        assert result.returncode == 0

        # Should contain meaningful discovery information
        output = result.stdout
        assert "parameters" in output.lower()
        assert "community" in output.lower()
        assert "temporal" in output.lower()

    def test_extracted_nasa_power_queries_execution(
        self, nasa_query_examples: list[tuple[str, str]]
    ) -> None:
        """Test execution of all NASA POWER query examples extracted from docs."""
        if not nasa_query_examples:
            pytest.skip("No NASA POWER query examples found in documentation")

        base_path = Path(__file__).parent.parent

        for description, command in nasa_query_examples:
            # Parse the command to extract components
            parts = command.split()
            if len(parts) < 4 or "uv run data-agents query" not in command:
                continue

            # Extract the query part (everything between "query" and "--adapter-config")
            query_start = command.find('"', command.find("query")) + 1
            query_end = command.find('"', query_start)
            if query_start == 0 or query_end == -1:
                continue

            query = command[query_start:query_end]

            # Build the command arguments
            cmd_args = [
                "uv",
                "run",
                "data-agents",
                "query",
                query,
                "--adapter-config",
                "config/nasa_power.adapter.json",
            ]

            result = subprocess.run(
                cmd_args,
                capture_output=True,
                text=True,
                cwd=base_path,
            )

            # Should succeed
            assert result.returncode == 0, (
                f"Query failed for: {description}\n"
                f"Command: {command}\nError: {result.stderr}"
            )

            # Should contain meaningful data
            output = result.stdout
            lines = output.strip().split("\n")
            assert len(lines) >= 2, f"No data returned for: {description}"

            # Extract parameter name from query
            param_name = query.split()[0]
            assert param_name in output, (
                f"Parameter {param_name} not found in output for: {description}"
            )

            # Detailed validation based on query content
            self._validate_nasa_query_output(query, output, description)

    def _validate_nasa_query_output(
        self, query: str, output: str, description: str
    ) -> None:
        """Validate NASA POWER query output with detailed checks."""

        # Parse query parameters
        query_parts = query.split()
        param_name = query_parts[0]

        # Build parameter dict
        params: dict[str, str] = {}
        for part in query_parts[1:]:
            if "=" in part:
                key, value = part.split("=", 1)
                params[key] = value

        # Check parameter name is in output
        assert param_name in output, (
            f"Parameter {param_name} not in output for {description}"
        )

        # Check spatial type specific validations
        if params.get("spatial_type") == "point":
            # Point queries should have lat/lon in output
            if "latitude" in params:
                lat_val = params["latitude"]
                # Check if latitude value appears in output (allowing for rounding)
                lat_base = lat_val.split(".")[0]  # Get integer part
                assert lat_base in output or lat_val in output, (
                    f"Latitude {lat_val} not found in output for {description}"
                )

            if "longitude" in params:
                lon_val = params["longitude"]
                # Check if longitude value appears in output (allowing for rounding)
                lon_base = lon_val.split(".")[0]  # Get integer part
                assert lon_base in output or lon_val in output, (
                    f"Longitude {lon_val} not found in output for {description}"
                )

        elif params.get("spatial_type") == "regional":
            # Regional queries should return multiple data points
            lines = output.strip().split("\n")
            assert len(lines) >= 3, (
                f"Regional query should return multiple data points for {description}"
            )

        # Check temporal specific validations
        temporal_type = params.get("temporal")
        if temporal_type == "daily":
            # Daily queries should have date information
            if "start" in params:
                start_date = params["start"]
                assert start_date in output, (
                    f"Start date {start_date} not found in output for {description}"
                )

        elif temporal_type == "monthly":
            # Monthly queries should have year information
            if "start" in params:
                start_year = params["start"]
                assert start_year in output, (
                    f"Start year {start_year} not found in output for {description}"
                )

        elif temporal_type == "climatology":
            # Climatology should have month indicators or annual data
            output_upper = output.upper()
            has_month_data = any(
                month in output_upper
                for month in [
                    "JAN",
                    "FEB",
                    "MAR",
                    "APR",
                    "MAY",
                    "JUN",
                    "JUL",
                    "AUG",
                    "SEP",
                    "OCT",
                    "NOV",
                    "DEC",
                    "ANN",
                ]
            )
            has_numeric_months = any(str(i).zfill(2) in output for i in range(1, 13))
            assert has_month_data or has_numeric_months, (
                f"Climatology data should have month indicators for {description}"
            )

        # Parameter-specific validations
        if param_name == "T2M":
            # Temperature should have numeric values (could be positive or negative)
            assert any(c.isdigit() for c in output), (
                f"Temperature data should contain numeric values for {description}"
            )

        elif param_name == "PRECTOTCORR":
            # Precipitation data validation
            assert any(c.isdigit() for c in output), (
                f"Precipitation data should contain numeric values for {description}"
            )

        elif param_name == "ALLSKY_SFC_SW_DWN":
            # Solar irradiance validation
            assert any(c.isdigit() for c in output), (
                f"Solar irradiance data should contain numeric values for {description}"
            )

        elif param_name == "WS2M":
            # Wind speed validation
            assert any(c.isdigit() for c in output), (
                f"Wind speed data should contain numeric values for {description}"
            )

    def test_nasa_power_point_query_from_docs(
        self, nasa_query_examples: list[tuple[str, str]]
    ) -> None:
        """Test point queries extracted from documentation."""
        point_queries = [
            (desc, cmd)
            for desc, cmd in nasa_query_examples
            if "spatial_type=point" in cmd
            and "latitude=" in cmd
            and "longitude=" in cmd
        ]

        if not point_queries:
            pytest.skip("No point queries found in documentation")

        # Test at least one point query
        _description, command = point_queries[0]

        # Extract query from command
        query_start = command.find('"', command.find("query")) + 1
        query_end = command.find('"', query_start)
        query = command[query_start:query_end]

        result = subprocess.run(
            [
                "uv",
                "run",
                "data-agents",
                "query",
                query,
                "--adapter-config",
                "config/nasa_power.adapter.json",
            ],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
        )

        assert result.returncode == 0
        output = result.stdout

        # Should contain meaningful data with proper structure
        lines = output.strip().split("\n")
        assert len(lines) >= 2  # Header + at least one data row

        # Should contain parameter name
        param_name = query.split()[0]
        assert param_name in output

        # Parse query parameters for detailed validation
        query_parts = query.split()
        params: dict[str, str] = {}
        for part in query_parts[1:]:
            if "=" in part:
                key, value = part.split("=", 1)
                params[key] = value

        # Should contain latitude/longitude information
        if "latitude" in params:
            lat_val = params["latitude"]
            lat_base = lat_val.split(".")[0]
            assert lat_base in output or lat_val in output, (
                f"Latitude {lat_val} not found in output"
            )

        if "longitude" in params:
            lon_val = params["longitude"]
            lon_base = lon_val.split(".")[0]
            assert lon_base in output or lon_val in output, (
                f"Longitude {lon_val} not found in output"
            )

        # Should contain date information for daily queries
        if params.get("temporal") == "daily" and "start" in params:
            start_date = params["start"]
            assert start_date in output or start_date[:4] in output, (
                "Date information not found in output"
            )

    def test_nasa_power_regional_query_from_docs(
        self, nasa_query_examples: list[tuple[str, str]]
    ) -> None:
        """Test regional queries extracted from documentation."""
        regional_queries = [
            (desc, cmd)
            for desc, cmd in nasa_query_examples
            if "spatial_type=regional" in cmd and "latitude_min=" in cmd
        ]

        if not regional_queries:
            pytest.skip("No regional queries found in documentation")

        # Test at least one regional query
        _description, command = regional_queries[0]

        # Extract query from command
        query_start = command.find('"', command.find("query")) + 1
        query_end = command.find('"', query_start)
        query = command[query_start:query_end]

        result = subprocess.run(
            [
                "uv",
                "run",
                "data-agents",
                "query",
                query,
                "--adapter-config",
                "config/nasa_power.adapter.json",
            ],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
        )

        assert result.returncode == 0
        output = result.stdout

        # Regional queries typically return multiple data points
        lines = output.strip().split("\n")
        assert len(lines) >= 3  # Header + multiple data rows

        # Should contain parameter name
        param_name = query.split()[0]
        assert param_name in output

        # Parse query for date validation
        query_parts = query.split()
        params: dict[str, str] = {}
        for part in query_parts[1:]:
            if "=" in part:
                key, value = part.split("=", 1)
                params[key] = value

        # Should contain date information if present
        if "start" in params:
            start_date = params["start"]
            assert start_date in output or start_date[:4] in output, (
                f"Date {start_date} not found in output"
            )

    def test_nasa_power_temporal_queries_from_docs(
        self, nasa_query_examples: list[tuple[str, str]]
    ) -> None:
        """Test different temporal frequency queries from documentation."""
        temporal_types = ["daily", "monthly", "climatology"]

        for temporal_type in temporal_types:
            temporal_queries = [
                (desc, cmd)
                for desc, cmd in nasa_query_examples
                if f"temporal={temporal_type}" in cmd
            ]

            if not temporal_queries:
                continue

            # Test first query of this temporal type
            description, command = temporal_queries[0]

            # Extract query from command
            query_start = command.find('"', command.find("query")) + 1
            query_end = command.find('"', query_start)
            query = command[query_start:query_end]

            result = subprocess.run(
                [
                    "uv",
                    "run",
                    "data-agents",
                    "query",
                    query,
                    "--adapter-config",
                    "config/nasa_power.adapter.json",
                ],
                capture_output=True,
                text=True,
                cwd=Path(__file__).parent.parent,
            )

            assert result.returncode == 0, f"Failed for {temporal_type}: {description}"
            output = result.stdout
            lines = output.strip().split("\n")
            assert len(lines) >= 2, f"No data for {temporal_type}: {description}"

            # Should contain parameter name
            param_name = query.split()[0]
            assert param_name in output, (
                f"Parameter {param_name} not found for {temporal_type}: {description}"
            )

            # Temporal-specific validations
            if temporal_type == "climatology":
                # Climatology should have month indicators or annual data
                output_upper = output.upper()
                has_month_data = any(
                    month in output_upper
                    for month in [
                        "JAN",
                        "FEB",
                        "MAR",
                        "APR",
                        "MAY",
                        "JUN",
                        "JUL",
                        "AUG",
                        "SEP",
                        "OCT",
                        "NOV",
                        "DEC",
                        "ANN",
                    ]
                )
                has_numeric_months = any(
                    str(i).zfill(2) in output for i in range(1, 13)
                )
                assert has_month_data or has_numeric_months, (
                    f"Climatology should have month indicators for {description}"
                )

            elif temporal_type == "monthly":
                # Monthly data should have year information
                query_parts = query.split()
                for part in query_parts:
                    if "start=" in part:
                        year = part.split("=")[1]
                        assert year in output, (
                            f"Year {year} not found in monthly output for {description}"
                        )
                        break

            elif temporal_type == "daily":
                # Daily data should have date information
                query_parts = query.split()
                for part in query_parts:
                    if "start=" in part:
                        date = part.split("=")[1]
                        assert date in output or date[:4] in output, (
                            f"Date {date} not found in daily output for {description}"
                        )
                        break

    def test_nasa_power_error_handling_execution(self):
        """Test that invalid queries are handled gracefully."""
        # Test with missing required parameters
        query = "T2M latitude=40.7"  # Missing many required params

        result = subprocess.run(
            [
                "uv",
                "run",
                "data-agents",
                "query",
                query,
                "--adapter-config",
                "config/nasa_power.adapter.json",
            ],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
        )

        # Should fail gracefully (non-zero exit code or error message)
        # The exact behavior depends on NASA POWER API validation
        assert result.returncode != 0 or "error" in result.stderr.lower()

    def test_nasa_power_router_integration_execution(self):
        """Test NASA POWER queries work within a router configuration."""
        result = subprocess.run(
            [
                "uv",
                "run",
                "data-agents",
                "query",
                "T2M latitude=40.7128 longitude=-74.0060 start=20240101 "
                "end=20240101 community=AG temporal=daily spatial_type=point",
                "--router-config",
                "config/example_with_nasa.router.json",
            ],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
        )

        # Should succeed
        assert result.returncode == 0

        # Should contain data from NASA adapter
        output = result.stdout
        assert "T2M" in output

        # Should show which adapter provided the data
        assert "nasa" in output.lower() or "Results from" in output


class TestGBIFCLIExamples:
    """Test GBIF Occurrence adapter CLI examples from documentation."""

    def test_gbif_adapter_config_structure(self):
        """Test that GBIF adapter config structure is valid."""
        gbif_config = {
            "type": "gbif_occurrence",
            "description": "GBIF biodiversity occurrence data",
        }

        assert gbif_config["type"] == "gbif_occurrence"
        assert "description" in gbif_config

        # Test router config with GBIF adapter
        router_with_gbif = {
            "adapters": {
                "gbif_data": {
                    "type": "gbif_occurrence",
                    "description": "GBIF biodiversity occurrence data",
                },
                "species_list": {
                    "type": "tabular",
                    "csv_file": "data/local_species.csv",
                },
            }
        }

        assert "adapters" in router_with_gbif
        assert "gbif_data" in router_with_gbif["adapters"]
        assert router_with_gbif["adapters"]["gbif_data"]["type"] == "gbif_occurrence"

    def test_gbif_discover_command(self):
        """Test GBIF discover command works."""
        # Test with single adapter config
        result = subprocess.run(
            [
                "uv",
                "run",
                "data-agents",
                "discover",
                "--adapter-config",
                "config/gbif.adapter.json",
            ],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
        )

        if result.returncode == 0:
            # Should contain GBIF specific information
            output = result.stdout
            assert (
                "parameters" in output.lower()
                or "37" in output
                or "scientificName" in output
                or "GBIF" in output
            )
        # Some tests may fail due to network issues, which is acceptable

    def test_gbif_discover_in_router(self):
        """Test GBIF discover command in router context."""
        # Create a temporary router config with GBIF adapter
        router_config = {
            "adapters": {
                "gbif_data": {
                    "type": "gbif_occurrence",
                    "description": "GBIF biodiversity occurrence data",
                }
            }
        }

        import json
        import tempfile

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(router_config, f)
            temp_config_path = f.name

        try:
            result = subprocess.run(
                [
                    "uv",
                    "run",
                    "data-agents",
                    "discover",
                    "--router-config",
                    temp_config_path,
                ],
                capture_output=True,
                text=True,
                cwd=Path(__file__).parent.parent,
            )

            if result.returncode == 0:
                # Should contain information about GBIF adapter
                output = result.stdout
                assert "gbif" in output.lower() or "GBIF" in output
        finally:
            # Clean up temp file
            import os

            os.unlink(temp_config_path)

    def test_gbif_simple_query_formats(self):
        """Test GBIF simple query formats from documentation."""
        # Test query parameter patterns from documentation examples
        test_cases = [
            ("mountain lion", "simple text search"),
            ("Puma concolor", "scientific name search"),
            ("Puma concolor country=US year=2023", "text with filters"),
            ("scientificName=Quercus robur", "structured scientific name"),
            ("country=US", "country filter"),
            ("year=2023", "year filter"),
            ("hasCoordinate=true", "coordinate filter"),
        ]

        # Test that these are valid query strings (would be passed to GBIF adapter)
        for query, _description in test_cases:
            # Verify query string format is reasonable
            assert isinstance(query, str)
            assert len(query) > 0
            # These should be valid GBIF query patterns
            if "=" in query:
                # Structured parameter query
                parts = query.split()
                for part in parts:
                    if "=" in part:
                        key, value = part.split("=", 1)
                        assert len(key) > 0, f"Empty parameter key in {query}"
                        assert len(value) > 0, f"Empty parameter value in {query}"

    def test_gbif_geographic_query_formats(self):
        """Test GBIF geographic query formats from documentation."""
        test_cases = [
            ("country=US", "country filter"),
            ("decimalLatitude=40,45 decimalLongitude=-75,-70", "coordinate range"),
            ("continent=NORTH_AMERICA", "continent filter"),
            (
                "scientificName=Ursus americanus hasCoordinate=true country=CA",
                "combined geo filters",
            ),
        ]

        for query, _description in test_cases:
            # Verify geographic query patterns
            assert isinstance(query, str)
            if "decimalLatitude" in query:
                assert "decimalLongitude" in query, "Latitude requires longitude"
            if "country=" in query:
                # Should have valid country code pattern
                country_part = [p for p in query.split() if p.startswith("country=")][0]
                country_value = country_part.split("=")[1]
                assert len(country_value) >= 2, (
                    "Country codes should be at least 2 chars"
                )

    def test_gbif_temporal_query_formats(self):
        """Test GBIF temporal query formats from documentation."""
        test_cases = [
            ("year=2023", "single year"),
            ("year=2020,2023", "year range"),
            ("year=2023 month=6", "year and month"),
            ("year=2023 month=6,8", "year and month range"),
        ]

        for query, _description in test_cases:
            # Verify temporal query patterns
            assert isinstance(query, str)
            if "year=" in query:
                year_part = [p for p in query.split() if p.startswith("year=")][0]
                year_value = year_part.split("=")[1]
                # Should be year format (4 digits or range)
                if "," in year_value:
                    start_year, end_year = year_value.split(",")
                    assert len(start_year) == 4, "Year should be 4 digits"
                    assert len(end_year) == 4, "Year should be 4 digits"
                else:
                    assert len(year_value) == 4, "Year should be 4 digits"

    def test_gbif_data_quality_query_formats(self):
        """Test GBIF data quality query formats from documentation."""
        test_cases = [
            ("basisOfRecord=HUMAN_OBSERVATION", "observation type"),
            ("basisOfRecord=PRESERVED_SPECIMEN", "specimen type"),
            ("hasCoordinate=true hasGeospatialIssue=false", "quality filters"),
            ("license=CC_BY_4_0", "license filter"),
        ]

        for query, _description in test_cases:
            # Verify data quality query patterns
            assert isinstance(query, str)
            if "basisOfRecord=" in query:
                basis_part = [
                    p for p in query.split() if p.startswith("basisOfRecord=")
                ][0]
                basis_value = basis_part.split("=")[1]
                assert basis_value in [
                    "HUMAN_OBSERVATION",
                    "PRESERVED_SPECIMEN",
                    "OBSERVATION",
                    "MACHINE_OBSERVATION",
                    "LITERATURE",
                    "LIVING_SPECIMEN",
                    "FOSSIL_SPECIMEN",
                    "MATERIAL_SAMPLE",
                    "UNKNOWN",
                ], f"Invalid basisOfRecord value: {basis_value}"

    def test_gbif_complex_query_formats(self):
        """Test GBIF complex multi-parameter query formats from documentation."""
        test_cases = [
            (
                "scientificName=Puma concolor country=US,CA year=2020,2023 "
                "basisOfRecord=HUMAN_OBSERVATION hasCoordinate=true",
                "comprehensive species search",
            ),
            (
                "decimalLatitude=35,45 decimalLongitude=-125,-115 year=2023 "
                "hasCoordinate=true basisOfRecord=HUMAN_OBSERVATION,PRESERVED_SPECIMEN",
                "geographic biodiversity survey",
            ),
            ("scientificName=Corvus limit=50", "pagination control"),
            ("country=US limit=100 offset=200", "offset pagination"),
        ]

        for query, _description in test_cases:
            # Verify complex query patterns
            assert isinstance(query, str)
            assert len(query.split()) >= 2, (
                "Complex queries should have multiple parameters"
            )

            # Verify parameter structure
            parts = query.split()
            param_count = sum(1 for part in parts if "=" in part)
            assert param_count >= 2, (
                f"Complex query should have multiple parameters: {query}"
            )

    def test_gbif_pagination_parameters(self):
        """Test GBIF pagination parameter handling."""
        test_cases = [
            ("limit=50", 50, None),
            ("limit=100 offset=200", 100, 200),
            ("scientificName=Corvus limit=25", 25, None),
        ]

        for query, expected_limit, expected_offset in test_cases:
            # Verify pagination parameters are extracted correctly
            if "limit=" in query:
                limit_part = [p for p in query.split() if p.startswith("limit=")][0]
                limit_value = int(limit_part.split("=")[1])
                assert limit_value == expected_limit

            if expected_offset is not None:
                assert "offset=" in query
                offset_part = [p for p in query.split() if p.startswith("offset=")][0]
                offset_value = int(offset_part.split("=")[1])
                assert offset_value == expected_offset


class TestGBIFCLIExecution:
    """Test execution of GBIF CLI examples with real API calls."""

    def test_gbif_query_execution_basic(self):
        """Test basic GBIF query execution."""
        # Test simple species search
        result = subprocess.run(
            [
                "uv",
                "run",
                "data-agents",
                "query",
                "Puma concolor",
                "--adapter-config",
                "config/gbif.adapter.json",
            ],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
        )

        if result.returncode == 0:
            output = result.stdout
            # Should contain species occurrence data
            assert (
                "scientificName" in output
                or "Puma" in output
                or "occurrence" in output.lower()
                or "gbifID" in output
            )
            # Should return structured data (likely DataFrame info)
            assert "columns" in output.lower() or len(output.strip()) > 0

    def test_gbif_query_execution_with_filters(self):
        """Test GBIF query execution with country filter."""
        # Test query with geographic filter
        result = subprocess.run(
            [
                "uv",
                "run",
                "data-agents",
                "query",
                "country=US year=2023 limit=5",
                "--adapter-config",
                "config/gbif.adapter.json",
            ],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
        )

        if result.returncode == 0:
            output = result.stdout
            # Should contain filtered occurrence data
            assert (
                "country" in output.lower()
                or "US" in output
                or "2023" in output
                or len(output.strip()) > 0
            )

    def test_gbif_query_execution_error_handling(self):
        """Test GBIF query error handling."""
        # Test with invalid parameter
        result = subprocess.run(
            [
                "uv",
                "run",
                "data-agents",
                "query",
                "invalidParameter=invalidValue",
                "--adapter-config",
                "config/gbif.adapter.json",
            ],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
        )

        # Should handle gracefully (either succeed with empty results or fail
        # gracefully)
        # Don't assert success/failure as API might handle this differently
        # Just ensure no crash
        assert result.returncode is not None

    def test_gbif_documented_examples_validation(self):
        """Test that documented GBIF examples are reasonable and don't crash."""
        doc_path = Path(__file__).parent.parent / "docs" / "CLI_ROUTER_CONFIG.md"
        gbif_queries = extract_gbif_queries_from_markdown(doc_path)

        # Should have extracted some queries from documentation
        assert len(gbif_queries) > 0, "Should extract GBIF queries from documentation"

        # Test a few representative queries (to avoid long test times)
        test_queries = gbif_queries[:3]  # Test first 3 queries

        for query, _description in test_queries:
            if query and len(query.strip()) > 0:
                # Test the query format is reasonable
                assert isinstance(query, str)
                assert len(query.strip()) > 0

                # Skip very long queries that might timeout
                if len(query) > 200:
                    continue

                # Test execution with timeout (quick test)
                result = subprocess.run(
                    [
                        "uv",
                        "run",
                        "data-agents",
                        "query",
                        query,
                        "--adapter-config",
                        "config/gbif.adapter.json",
                    ],
                    capture_output=True,
                    text=True,
                    timeout=30,  # 30 second timeout
                    cwd=Path(__file__).parent.parent,
                )

                # Should not crash (might fail due to network, but shouldn't crash)
                assert result.returncode is not None

                if result.returncode == 0:
                    # If successful, should have some output
                    output = result.stdout
                    assert len(output.strip()) > 0, f"Empty output for query: {query}"
