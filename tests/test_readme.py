"""Tests to verify that README examples are up-to-date and working."""

import re
import subprocess
import tempfile
from pathlib import Path
from typing import List

import pandas as pd
import pytest

from data_agents import Adapter, RESTAdapter, Router, TabularAdapter


class TestREADMEExamples:
    """Test cases to ensure README examples work correctly."""

    def test_imports_available(self):
        """Test that all imports mentioned in README are available."""
        # Test the main imports from the basic usage example
        from data_agents import Router, TabularAdapter, RESTAdapter
        
        # Verify they are the correct types
        assert issubclass(Router, object)
        assert issubclass(TabularAdapter, Adapter)
        assert issubclass(RESTAdapter, Adapter)

    def test_basic_usage_example(self):
        """Test the basic usage example from README."""
        # This tests the code from the "Basic Usage" section
        from data_agents import Router, TabularAdapter, RESTAdapter
        import pandas as pd

        # Create a router
        router = Router()

        # Create sample data
        customers_data = pd.DataFrame({
            'id': [1, 2, 3],
            'name': ['Alice', 'Bob', 'Charlie'],
            'age': [25, 30, 35]
        })

        # Create adapters for the data
        customers_adapter = TabularAdapter(customers_data)
        api_adapter = RESTAdapter("https://api.example.com")

        # Add adapters to the router
        router["customers"] = customers_adapter
        router["api"] = api_adapter

        # Query the data
        all_customers = customers_adapter.query("*")
        older_customers = customers_adapter.query("age >= 30")

        # Verify results
        assert len(all_customers) == 3
        assert len(older_customers) == 2  # Bob and Charlie

        # Get information about the router
        info = router.to_dict()
        assert info["type"] == "Router"
        assert info["adapter_count"] == 2

        # Discover capabilities of all adapters
        discoveries = router.discover_all()
        assert "customers" in discoveries
        assert "api" in discoveries

    def test_custom_adapter_example(self):
        """Test the custom adapter example from README."""
        from data_agents import Adapter
        import pandas as pd

        class CustomAPIAdapter(Adapter):
            """Custom adapter for REST API data."""
            
            def __init__(self, api_url: str, config=None):
                super().__init__(config)
                self.api_url = api_url
            
            def query(self, query: str, **kwargs) -> pd.DataFrame:
                # Return sample data for testing
                return pd.DataFrame({"test": [1, 2, 3]})
            
            def discover(self) -> dict:
                return {
                    "adapter_type": "custom_api", 
                    "base_url": self.api_url,
                    "capabilities": {"supports_query": True}
                }

        # Use the custom adapter
        router = Router()
        api_adapter = CustomAPIAdapter("https://api.example.com")
        router["my-api"] = api_adapter

        # Test functionality
        result = router["my-api"].query("test")
        assert len(result) == 3
        
        discovery = router["my-api"].discover()
        assert discovery["adapter_type"] == "custom_api"
        assert discovery["base_url"] == "https://api.example.com"

    def test_multiple_data_sources_example(self):
        """Test the multiple data sources example from README."""
        # Create test data
        customers_df = pd.DataFrame({
            'id': [1, 2, 3],
            'name': ['Alice', 'Bob', 'Charlie']
        })
        orders_df = pd.DataFrame({
            'order_id': [101, 102, 103],
            'customer_id': [1, 2, 3],
            'date': ['2023-01-01', '2023-02-01', '2023-03-01']
        })
        products_df = pd.DataFrame({
            'product_id': [1, 2, 3],
            'name': ['Widget A', 'Widget B', 'Widget C']
        })

        # Create multiple adapters for different data sources
        customers_adapter = TabularAdapter(customers_df)
        orders_adapter = TabularAdapter(orders_df)
        products_adapter = TabularAdapter(products_df)

        # Create a router and add all adapters
        router = Router()
        router["customers"] = customers_adapter
        router["orders"] = orders_adapter
        router["products"] = products_adapter

        # Query specific adapters
        customer_data = router["customers"].query("*")
        
        # Query all adapters with the same query
        all_results = router.query_all("*")
        
        # Verify results
        assert len(customer_data) == 3
        assert len(all_results) == 3
        assert "customers" in all_results
        assert "orders" in all_results
        assert "products" in all_results
        
        # Get discovery information for all adapters
        discoveries = router.discover_all()
        assert len(discoveries) == 3

    def test_cli_commands_exist(self):
        """Test that CLI commands mentioned in README actually exist."""
        # Test that the data-agents command exists and has expected subcommands
        result = subprocess.run(
            ["uv", "run", "data-agents", "--help"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent
        )
        
        assert result.returncode == 0
        help_output = result.stdout
        
        # Check that mentioned commands exist
        expected_commands = ["create", "demo", "query", "list-adapters", "info"]
        for command in expected_commands:
            assert command in help_output

    def test_configuration_example_structure(self):
        """Test that configuration file examples have correct structure."""
        # Test the router configuration structure from README
        config_example = {
            "adapters": {
                "my_api": {
                    "type": "rest",
                    "base_url": "https://api.example.com",
                    "config_file": "path/to/rest_config.json"
                },
                "my_data": {
                    "type": "tabular",
                    "csv_file": "path/to/data.csv"
                }
            }
        }
        
        # Verify structure
        assert "adapters" in config_example
        assert "my_api" in config_example["adapters"]
        assert "my_data" in config_example["adapters"]
        assert config_example["adapters"]["my_api"]["type"] == "rest"
        assert config_example["adapters"]["my_data"]["type"] == "tabular"

    def test_rest_adapter_config_structure(self):
        """Test that REST adapter configuration example has correct structure."""
        rest_config_example = {
            "headers": {
                "User-Agent": "DataAgents/1.0"
            },
            "timeout": 10,
            "endpoints": ["users", "posts", "comments"],
            "pagination_param": "_limit",
            "pagination_limit": 10
        }
        
        # Test that this config can be used with RESTAdapter
        adapter = RESTAdapter("https://api.example.com", rest_config_example)
        assert adapter.headers["User-Agent"] == "DataAgents/1.0"
        assert adapter.timeout == 10
        assert adapter.endpoints == ["users", "posts", "comments"]
        assert adapter.pagination_param == "_limit"
        assert adapter.pagination_limit == 10


class TestREADMECodeExtraction:
    """Tests that extract and validate code blocks from README."""

    @staticmethod
    def extract_python_code_blocks(readme_path: Path) -> List[str]:
        """Extract Python code blocks from README."""
        with open(readme_path) as f:
            content = f.read()
        
        # Find all Python code blocks
        pattern = r'```python\n(.*?)\n```'
        matches = re.findall(pattern, content, re.DOTALL)
        return matches

    @staticmethod
    def extract_bash_code_blocks(readme_path: Path) -> List[str]:
        """Extract bash code blocks from README."""
        with open(readme_path) as f:
            content = f.read()
        
        # Find all bash code blocks
        pattern = r'```bash\n(.*?)\n```'
        matches = re.findall(pattern, content, re.DOTALL)
        return matches

    def test_python_code_blocks_syntax(self):
        """Test that all Python code blocks in README have valid syntax."""
        readme_path = Path(__file__).parent.parent / "README.md"
        code_blocks = self.extract_python_code_blocks(readme_path)
        
        for i, code_block in enumerate(code_blocks):
            try:
                compile(code_block, f"<README_block_{i}>", "exec")
            except SyntaxError as e:
                pytest.fail(f"Syntax error in README Python code block {i}: {e}\nCode:\n{code_block}")

    def test_bash_commands_format(self):
        """Test that bash commands in README follow expected format."""
        readme_path = Path(__file__).parent.parent / "README.md"
        bash_blocks = self.extract_bash_code_blocks(readme_path)
        
        # Check for common issues
        for i, bash_block in enumerate(bash_blocks):
            lines = bash_block.strip().split('\n')
            for line_num, line in enumerate(lines):
                line = line.strip()
                if line.startswith('#'):
                    continue  # Skip comments
                if not line:
                    continue  # Skip empty lines
                    
                # Check that data-agents CLI commands use 'uv run'
                if 'data-agents' in line and not line.startswith('uv run'):
                    # Allow exceptions for non-command contexts
                    if not any(skip in line for skip in ['git clone', 'cd ', 'pip install']):
                        pytest.fail(
                            f"README bash block {i}, line {line_num + 1}: "
                            f"CLI commands should use 'uv run data-agents' not bare 'data-agents'\n"
                            f"Found: {line}"
                        )

    def test_imports_in_readme_are_available(self):
        """Test that all imports shown in README are actually available."""
        readme_path = Path(__file__).parent.parent / "README.md"
        code_blocks = self.extract_python_code_blocks(readme_path)
        
        # Extract import statements
        import_lines = []
        for code_block in code_blocks:
            for line in code_block.split('\n'):
                line = line.strip()
                if line.startswith('from data_agents import') or line.startswith('import data_agents'):
                    import_lines.append(line)
        
        # Test each import
        for import_line in import_lines:
            try:
                exec(import_line)
            except ImportError as e:
                pytest.fail(f"Import from README failed: {import_line}\nError: {e}")


class TestREADMEConsistency:
    """Tests to ensure README content is consistent with codebase."""

    def test_version_consistency(self):
        """Test that version in README matches version in code."""
        # Read version from pyproject.toml
        pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
        with open(pyproject_path) as f:
            pyproject_content = f.read()
        
        version_match = re.search(r'version = "([^"]+)"', pyproject_content)
        assert version_match, "Could not find version in pyproject.toml"
        pyproject_version = version_match.group(1)
        
        # Read version from __init__.py
        from data_agents import __version__
        
        assert __version__ == pyproject_version, f"Version mismatch: __init__.py has {__version__}, pyproject.toml has {pyproject_version}"

    def test_available_adapters_documented(self):
        """Test that all available adapters are documented in README."""
        readme_path = Path(__file__).parent.parent / "README.md"
        with open(readme_path) as f:
            readme_content = f.read()
        
        # Check that both TabularAdapter and RESTAdapter are mentioned
        assert "TabularAdapter" in readme_content
        assert "RESTAdapter" in readme_content
        
        # Check that they can actually be imported
        from data_agents import TabularAdapter, RESTAdapter
        assert TabularAdapter is not None
        assert RESTAdapter is not None

    def test_cli_help_matches_readme(self):
        """Test that CLI help output matches what's documented in README."""
        # Get CLI help
        result = subprocess.run(
            ["uv", "run", "data-agents", "--help"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent
        )
        
        assert result.returncode == 0
        cli_help = result.stdout
        
        # Read README
        readme_path = Path(__file__).parent.parent / "README.md"
        with open(readme_path) as f:
            readme_content = f.read()
        
        # Extract commands from CLI help
        help_commands = re.findall(r'^\s+([\w-]+)\s+', cli_help, re.MULTILINE)
        
        # Check that commands mentioned in README exist in CLI help
        readme_commands = re.findall(r'uv run data-agents ([\w-]+)', readme_content)
        for cmd in set(readme_commands):
            assert cmd in help_commands, f"Command '{cmd}' mentioned in README but not found in CLI help"