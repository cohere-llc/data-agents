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
# Create a new agent
data-agents create my-agent

# Process data with an agent
data-agents process my-agent "some data to process"

# Get agent information
data-agents info my-agent

# Use with configuration file
data-agents create my-agent --config config.json
```

### Python API

```python
from data_agents import DataAgent

# Create an agent
agent = DataAgent("my-agent")

# Process some data
result = agent.process("input data")
print(result)

# Get agent information
info = agent.get_info()
print(info)
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

### Project structure

```
data-agents/
├── src/
│   └── data_agents/
│       ├── __init__.py
│       ├── core.py          # Core DataAgent functionality
│       └── cli.py           # Command-line interface
├── tests/
│   ├── __init__.py
│   └── test_data_agents.py  # Test suite
├── pyproject.toml           # Project configuration
├── README.md                # This file
└── uv.lock                  # Dependency lock file
```

## License

Apache 2.0