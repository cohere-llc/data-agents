# Data Agents
[![License](https://img.shields.io/github/license/cohere-llc/data-agents.svg)](https://github.com/cohere-llc/data-agents/blob/main/LICENSE)
[![macOS](https://github.com/cohere-llc/data-agents/actions/workflows/mac.yml/badge.svg)](https://github.com/cohere-llc/data-agents/actions/workflows/mac.yml)
[![ubuntu](https://github.com/cohere-llc/data-agents/actions/workflows/ubuntu.yml/badge.svg)](https://github.com/cohere-llc/data-agents/actions/workflows/ubuntu.yml)
[![windows](https://github.com/cohere-llc/data-agents/actions/workflows/windows.yml/badge.svg)](https://github.com/cohere-llc/data-agents/actions/workflows/windows.yml)
[![codecov](https://codecov.io/gh/cohere-llc/data-agents/branch/main/graph/badge.svg)](https://codecov.io/gh/cohere-llc/data-agents)
[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/cohere-llc/data-agents/HEAD?filepath=examples)

A prototype for interaction with services used in [env-agents](https://github.com/aparkin/env-agents),
based on the [Google Earth Engine Python API](https://github.com/google/earthengine-api) and [GeoJSON](https://datatracker.ietf.org/doc/html/rfc7946) format.

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

### Python API

#### Basic Usage

```python
import data_agents as da

# Authenticate user with external services
da.Authenticate()
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
