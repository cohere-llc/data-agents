# Data Agents CLI - Router Configuration

The Data Agents CLI supports working with routers configured from JSON or YAML configuration files. You can get information about routers, list their adapters, discover queryable parameters, and query data through all adapters in a router.

## Configuration Format

### Router Configuration

The router configuration file should contain an `adapters` section that defines the adapters to be created and added to the router.

#### JSON Format Example

```json
{
  "adapters": {
    "api_data": {
      "type": "rest",
      "base_url": "https://api.example.com",
      "headers": {
        "User-Agent": "DataAgents-test/1.0"
      },
      "endpoints": ["foo", "bar"]
    },
    "csv_data": {
      "type": "tabular",
      "csv_file": "path/to/data.csv"
    }
  }
}
```

#### YAML Format Example

```yaml
adapters:
  api_data:
    type: rest
    base_url: https://api.example.com
    config_file: path/to/rest_config.json
    
  csv_data:
    type: tabular
    csv_file: path/to/data.csv
```

### Single Adapter Configuration

You can also create configuration files for individual adapters:

#### REST Adapter Configuration

```json
{
  "type": "rest",
  "base_url": "https://jsonplaceholder.typicode.com",
  "config_file": "config/jsonplaceholder.adapter.json"
}
```

#### Tabular Adapter Configuration

```json
{
  "type": "tabular",
  "csv_file": "examples/sample_data.csv"
}
```

## Adapter Types

### REST Adapter

For REST adapters, specify:
- `type`: Must be "rest"
- `base_url`: The base URL for the REST API (required)
- `config_file`: Path to a JSON/YAML file containing REST adapter configuration (optional)

The REST adapter configuration file can contain settings like:
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

### Tabular Adapter

For tabular adapters, specify:
- `type`: Must be "tabular"
- `csv_file`: Path to a valid CSV file (required)

## Usage Examples

### Get router information

```bash
# Get complete router information with all adapters
uv run data-agents info --router-config config/router.json

# Using YAML configuration
uv run data-agents info --router-config config/router.yaml
```

### List available adapters in a router

```bash
uv run data-agents list-adapters --router-config config/router.json
```

### Discover queryable parameters for all adapters

```bash
uv run data-agents discover --router-config config/router.json
```

### Query data through all adapters in the router

```bash
# Query all adapters with the same query string
uv run data-agents query "*" --router-config config/router.json

# Query for specific data (tabular adapters support SQL-like syntax)
uv run data-agents query "age > 30" --router-config config/router.json

# Query REST endpoints
uv run data-agents query "users" --router-config config/router.json
```

### Working with single adapters

You can also work with individual adapter configuration files:

```bash
# Get information about a single adapter
uv run data-agents info --adapter-config config/my_adapter.json

# Discover parameters for a single adapter
uv run data-agents discover --adapter-config config/my_adapter.json

# Query a single adapter
uv run data-agents query "users" --adapter-config config/my_adapter.json
```

## Error Handling

The CLI provides helpful error messages for common issues:

- Missing required fields (base_url, csv_file)
- File not found errors for configuration files or CSV files
- Invalid adapter types
- JSON/YAML parsing errors

## Example Files

See the following example files in the repository:
- `config/example.router.json` - Complete JSON router configuration example
- `config/example.router.yaml` - Complete YAML router configuration example
- `config/jsonplaceholder.adapter.json` - Single adapter configuration example
- `examples/sample_data.csv` - Sample CSV file for testing
- `config/jsonplaceholder.adapter.json` - Example REST adapter configuration
- `config/httpbin.adapter.json` - Another REST adapter configuration example