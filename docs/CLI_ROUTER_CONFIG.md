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

### NASA POWER Adapter

For NASA POWER adapters, specify:
- `type`: Must be "nasa_power"
- `description`: Optional description of the adapter

The NASA POWER adapter provides access to NASA's POWER (Prediction of Worldwide Energy Resources) meteorological and solar resource data. Each parameter (like temperature, precipitation, solar irradiance) is treated as a discoverable record type.

Example NASA POWER adapter configuration:
```json
{
  "type": "nasa_power",
  "description": "NASA POWER meteorological and solar resource data"
}
```

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

## NASA POWER Adapter Usage

The NASA POWER adapter provides access to meteorological and solar resource data from NASA's POWER API. Each parameter (like temperature, precipitation, solar irradiance) is treated as a discoverable record type.

### NASA POWER Configuration

Create a NASA POWER adapter configuration file:

```json
{
  "type": "nasa_power",
  "description": "NASA POWER meteorological and solar resource data"
}
```

Or include it in a router configuration:

```json
{
  "adapters": {
    "nasa_power": {
      "type": "nasa_power",
      "description": "NASA POWER meteorological and solar resource data"
    },
    "local_weather": {
      "type": "tabular",
      "csv_file": "data/local_weather.csv"
    }
  }
}
```

### Discovering NASA POWER Parameters

```bash
# Discover all available NASA POWER parameters
uv run data-agents discover --adapter-config config/nasa_power.adapter.json

# Or discover parameters in a router with NASA POWER adapter
uv run data-agents discover --router-config config/example_with_nasa.router.json
```

This will show:
- Total number of available parameters
- Available communities (AG=Agriculture, RE=Renewable Energy, SB=Sustainable Buildings)
- Temporal frequencies (daily, monthly, climatology, hourly)
- Spatial types (point, regional)
- Detailed information for each parameter including units, definitions, and availability

### Querying NASA POWER Data

NASA POWER queries use parameter names (like 'T2M' for temperature, 'PRECTOTCORR' for precipitation) followed by additional parameters as key=value pairs in the query string.

**Query Format**: `"PARAMETER_NAME key=value key2=value2 ..."`

#### Point Data Queries

Query data for a specific location (latitude/longitude):

```bash
# Temperature data for New York City
uv run data-agents query "T2M latitude=40.7128 longitude=-74.0060 start=20240101 end=20240107 community=AG temporal=daily spatial_type=point" \
  --adapter-config config/nasa_power.adapter.json

# Precipitation data for Los Angeles
uv run data-agents query "PRECTOTCORR latitude=34.0522 longitude=-118.2437 start=20240601 end=20240630 community=AG temporal=daily spatial_type=point" \
  --adapter-config config/nasa_power.adapter.json

# Solar irradiance for Phoenix
uv run data-agents query "ALLSKY_SFC_SW_DWN latitude=33.4484 longitude=-112.0740 start=20240301 end=20240331 community=RE temporal=daily spatial_type=point" \
  --adapter-config config/nasa_power.adapter.json
```

#### Regional Data Queries

Query data for a geographic region (requires minimum region size):

```bash
# Temperature data for Northeast US region (2-degree minimum region)
uv run data-agents query "T2M latitude_min=40.0 latitude_max=42.0 longitude_min=-76.0 longitude_max=-74.0 start=20240101 end=20240102 community=AG temporal=daily spatial_type=regional" \
  --adapter-config config/nasa_power.adapter.json

# Wind speed for Great Plains region
uv run data-agents query "WS2M latitude_min=35.0 latitude_max=45.0 longitude_min=-105.0 longitude_max=-95.0 start=20240101 end=20240101 community=RE temporal=daily spatial_type=regional" \
  --adapter-config config/nasa_power.adapter.json
```

#### Monthly and Climatology Data

```bash
# Monthly temperature averages (requires YYYY format for start/end)
uv run data-agents query "T2M latitude=40.7128 longitude=-74.0060 start=2024 end=2024 community=AG temporal=monthly spatial_type=point" \
  --adapter-config config/nasa_power.adapter.json

# Long-term climatology data (start/end are optional, defaults to 2001-2020)
uv run data-agents query "T2M latitude=40.7128 longitude=-74.0060 community=AG temporal=climatology spatial_type=point" \
  --adapter-config config/nasa_power.adapter.json

# Climatology data with custom year range
uv run data-agents query "T2M latitude=40.7128 longitude=-74.0060 start=2010 end=2020 community=AG temporal=climatology spatial_type=point" \
  --adapter-config config/nasa_power.adapter.json
```

### Required Parameters

All NASA POWER queries require:
- **Parameter name**: The NASA POWER parameter code (e.g., 'T2M', 'PRECTOTCORR')
- **community**: One of 'AG' (Agriculture), 'RE' (Renewable Energy), 'SB' (Sustainable Buildings)
- **temporal**: One of 'daily', 'monthly', 'climatology', 'hourly'
- **spatial_type**: Either 'point' or 'regional'

For temporal frequencies:
- **daily/hourly**: Require start and end dates in YYYYMMDD format
- **monthly**: Require start and end years in YYYY format
- **climatology**: Start and end years are optional (YYYY format, defaults to 2001-2020)

### Spatial Parameters

**For point queries:**
- **latitude**: Latitude coordinate (-90 to 90)
- **longitude**: Longitude coordinate (-180 to 180)

**For regional queries:**
- **latitude_min**: Minimum latitude
- **latitude_max**: Maximum latitude  
- **longitude_min**: Minimum longitude
- **longitude_max**: Maximum longitude

### Optional Parameters

You can also include optional parameters:
- **format**: Output format
- **units**: Unit system
- **time_standard**: Time standard
- **site_elevation**: Site elevation
- **wind_elevation**: Wind measurement elevation
- **wind_surface**: Wind surface type

### Common NASA POWER Parameters

Some frequently used parameters:
- **T2M**: Temperature at 2 meters (°C)
- **PRECTOTCORR**: Precipitation (mm/day)
- **ALLSKY_SFC_SW_DWN**: Solar irradiance (kWh/m²/day)
- **WS2M**: Wind speed at 2 meters (m/s)
- **RH2M**: Relative humidity at 2 meters (%)
- **PS**: Surface pressure (kPa)

Use the discover command to see all available parameters with their descriptions, units, and availability by community and temporal frequency.

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
- `config/example_with_nasa.router.json` - Router configuration with NASA POWER adapter
- `config/nasa_power.adapter.json` - NASA POWER adapter configuration
- `config/jsonplaceholder.adapter.json` - Single adapter configuration example
- `examples/sample_data.csv` - Sample CSV file for testing
- `config/httpbin.adapter.json` - Another REST adapter configuration example
- `examples/nasa_power_example.py` - Python example showing NASA POWER adapter usage