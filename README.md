# Data Agents
[![License](https://img.shields.io/github/license/cohere-llc/data-agents.svg)](https://github.com/cohere-llc/data-agents/blob/main/LICENSE)
[![macOS](https://github.com/cohere-llc/data-agents/actions/workflows/mac.yml/badge.svg)](https://github.com/cohere-llc/data-agents/actions/workflows/mac.yml)
[![ubuntu](https://github.com/cohere-llc/data-agents/actions/workflows/ubuntu.yml/badge.svg)](https://github.com/cohere-llc/data-agents/actions/workflows/ubuntu.yml)
[![windows](https://github.com/cohere-llc/data-agents/actions/workflows/windows.yml/badge.svg)](https://github.com/cohere-llc/data-agents/actions/workflows/windows.yml)
[![codecov](https://codecov.io/gh/cohere-llc/data-agents/branch/main/graph/badge.svg)](https://codecov.io/gh/cohere-llc/data-agents)

A prototype for general data discovery and harmonization following the env-agents structure (https://github.com/aparkin/env-agents).

__This is an exploratory project with many missing/incomplete features.
The code will change rapidly, and the project will likely be archived after the exporatory phase is completed.__

## Installation

### From source

```bash
# Clone the repository
git clone https://github.com/cohere-llc/data-agents.git
cd data-agents

# Install with uv (recommended)
uv sync

# Or install with pip
pip install -e .
```

### Development installation

```bash
# Install with development dependencies using uv (recommended)
uv sync --group dev

# Or install with pip
pip install -e ".[dev]"
```

## Usage

### Command Line Interface

The package provides a `data-agents` command-line tool:

```bash
# Get usage information
uv run data-agents --help

# Get the data-agents version
uv run data-agents --version

# Run a demonstration of the Router/Adapter functionality
uv run data-agents demo

# Get router information (including adapters)
uv run data-agents info --router-config config.router.json

# List all adapters in a router
uv run data-agents list-adapters --router-config config.router.json

# Discover queryable parameters with type information for all adapters in a router
uv run data-agents discover --router-config config.router.json

# Query data through all adapters in a router
uv run data-agents query "query-string" --router-config config.router.json

# Get adapter information
uv run data-agents info --adapter-config config.adapter.json

# Discover queryable parameter with type information for a single adapter
uv run data-agents discover --adapter-config config.adapter.json

# Query a single adapter
uv run data-agents query "query-string" --adapter-config config.adapter.json
```

### Python API

#### Basic Usage

```python
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

# Get information about the router
info = router.to_dict()
print(info)

# Discover capabilities of all adapters
discoveries = router.discover_all()
```

#### Router/Adapter Architecture

The system uses a **Router/Adapter** pattern:

- **`Router`**: Manages a collection of adapters and routes queries to them
- **`Adapter`**: Base class for accessing different types of data sources
- **`TabularAdapter`**: Default implementation for pandas DataFrame data

#### Creating Custom Adapters

```python
from data_agents import Adapter
import pandas as pd

class CustomAPIAdapter(Adapter):
    """Custom adapter for REST API data."""
    
    def __init__(self, api_url: str, config=None):
        super().__init__(config)
        self.api_url = api_url
    
    def query(self, query: str, **kwargs) -> pd.DataFrame:
        # Implement your custom query logic here
        # This could make HTTP requests, parse responses, etc.
        # Return data as a pandas DataFrame
        return pd.DataFrame()
    
    def discover(self) -> dict:
        # Return discovery information for your data source
        return {
            "adapter_type": "custom_api", 
            "base_url": self.api_url,
            "capabilities": {"supports_query": True}
        }

# Use your custom adapter
router = Router()
api_adapter = CustomAPIAdapter("https://api.example.com")
router["my-api"] = api_adapter
```

#### Working with Multiple Data Sources

```python
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
recent_orders = router["orders"].query("date >= '2023-01-01'")

# Query all adapters with the same query
all_results = router.query_all("*")
for adapter_name, data in all_results.items():
    print(f"{adapter_name}: {len(data)} records")

# Get discovery information for all adapters
discoveries = router.discover_all()
```

### Configuration

You can configure routers and adapters using JSON or YAML files:

#### Router Configuration

The CLI supports creating routers with pre-configured adapters:

```json
{
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
```

#### REST Adapter Configuration

For REST adapters, you can specify additional configuration:

```json
{
  "headers": {
    "User-Agent": "DataAgents/1.0"
  },
  "timeout": 10,
  "endpoints": ["users", "posts", "comments"],
  "pagination_param": "_limit",
  "pagination_limit": 10
}
```

#### Using Configuration Files

```bash
# Get router information
uv run data-agents info --router-config router_config.json

# Query all adapters in a router
uv run data-agents query "users" --router-config router_config.json
```

## Development

### Running tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=data_agents

# Run specific test file
uv run pytest tests/test_cli.py
```

### Code formatting and linting

```bash
# Format code with ruff
uv run ruff format .

# Lint code
uv run ruff check .

# Type checking with mypy
uv run mypy src/
```
