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
uv pip install -e .

# Or install with pip
pip install -e .
```

### Development installation

```bash
# Install with development dependencies
uv pip install -e ".[dev]"

# Or with pip
pip install -e ".[dev]"
```

## Usage

### Command Line Interface

The package provides a `data-agents` command-line tool:

```bash
# Run a demonstration of the Router/Adapter functionality
data-agents demo

# Create a new agent
data-agents create my-agent

# Get agent information (including router and adapters)
data-agents info my-agent

# List all adapters in an agent
data-agents list-adapters my-agent

# Query data through an adapter
data-agents query my-agent adapter-name "query-string"

# Use with configuration file
data-agents create my-agent --config config.json
```

### Python API

#### Basic Usage

```python
from data_agents import DataAgent, TabularAdapter
import pandas as pd

# Create an agent
agent = DataAgent("my-agent")

# Create sample data
customers_data = pd.DataFrame({
    'id': [1, 2, 3],
    'name': ['Alice', 'Bob', 'Charlie'],
    'age': [25, 30, 35]
})

# Create an adapter for the data
customers_adapter = TabularAdapter("customers", customers_data)

# Add adapter to the agent
agent.add_adapter(customers_adapter)

# Query the data
all_customers = agent.query("customers", "*")
older_customers = agent.query("customers", "age > 30")

# Get information about available adapters
info = agent.get_info()
print(info)
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
    
    def __init__(self, name: str, api_url: str, config=None):
        super().__init__(name, config)
        self.api_url = api_url
    
    def query(self, query: str, **kwargs) -> pd.DataFrame:
        # Implement your custom query logic here
        # This could make HTTP requests, parse responses, etc.
        pass
    
    def get_schema(self) -> dict:
        # Return schema information for your data source
        return {"type": "api", "url": self.api_url}

# Use your custom adapter
api_adapter = CustomAPIAdapter("my-api", "https://api.example.com")
agent.add_adapter(api_adapter)
```

#### Working with Multiple Data Sources

```python
# Create multiple adapters for different data sources
customers_adapter = TabularAdapter("customers", customers_df)
orders_adapter = TabularAdapter("orders", orders_df)
products_adapter = TabularAdapter("products", products_df)

# Add all adapters to the agent
agent.add_adapter(customers_adapter)
agent.add_adapter(orders_adapter)
agent.add_adapter(products_adapter)

# Query specific adapters
customer_data = agent.query("customers", "*")
recent_orders = agent.query("orders", "date > '2023-01-01'")

# Query all adapters with the same query
all_results = agent.query_all("*")
for adapter_name, data in all_results.items():
    print(f"{adapter_name}: {len(data)} records")

# Get schema information for all adapters
schemas = agent.router.get_all_schemas()
```

### Configuration

You can provide configuration via JSON files:

```json
{
    "setting1": "value1",
    "setting2": 42,
    "nested": {
        "key": "value"
    }
}
```

## Development

### Running tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=data_agents

# Run specific test file
pytest tests/test_data_agents.py
```

### Code formatting and linting

```bash
# Format code with ruff
ruff format .

# Lint code
ruff check .

# Type checking with mypy
mypy src/
```
