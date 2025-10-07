# Data Agents CLI - Router Configuration

The Data Agents CLI now supports creating routers with adapters pre-configured from JSON or YAML configuration files.

## Configuration Format

The configuration file should contain an `adapters` section that defines the adapters to be created and added to the router.

### JSON Format Example

```json
{
  "adapters": {
    "api_data": {
      "type": "rest",
      "base_url": "https://api.example.com",
      "config_file": "path/to/rest_config.json"
    },
    "csv_data": {
      "type": "tabular",
      "csv_file": "path/to/data.csv"
    }
  }
}
```

### YAML Format Example

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

### Create a router with adapters

```bash
# Using JSON configuration
uv run data-agents create my-router --config config/router.json

# Using YAML configuration
uv run data-agents create my-router --config config/router.yaml
```

### Query data through the router

```bash
# Query all data from a tabular adapter
uv run data-agents query my-router csv_data "*" --config config/router.json

# Query a specific column
uv run data-agents query my-router csv_data "name" --config config/router.json

# Query a REST endpoint
uv run data-agents query my-router api_data "users" --config config/router.json
```

### List available adapters

```bash
uv run data-agents list-adapters my-router --config config/router.json
```

## Error Handling

The CLI provides helpful error messages for common issues:

- Missing required fields (base_url, csv_file)
- File not found errors for configuration files or CSV files
- Invalid adapter types
- JSON/YAML parsing errors

## Example Files

See the following example files in the repository:
- `config/router_example.json` - Complete JSON configuration example
- `config/router_example.yaml` - Complete YAML configuration example
- `examples/sample_data.csv` - Sample CSV file for testing
- `config/httpbin.rest.adapter.json` - Example REST adapter configuration