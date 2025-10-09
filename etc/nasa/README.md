# NASA POWER Parameter Fetcher

This directory contains scripts to query the NASA POWER System Manager API and work with parameter metadata.

## Scripts

### `fetch_parameters.py`
Main script that queries the NASA POWER System Manager API to retrieve all available parameters with their metadata for different communities and temporal frequencies.

### `example_usage.py`
Example script showing how to work with the fetched parameter data, including filtering and analysis functions.

### `get_param_codes.py`
Utility script to extract parameter abbreviations from fetched data for easy copy-paste into API queries.

## Features

- Fetches parameters for all NASA POWER communities (AG, RE, SB)
- Supports all temporal frequencies (daily, monthly, climatology, hourly)  
- Provides structured JSON output with parameter metadata
- Includes summary statistics
- Can filter by specific community or temporal frequency

## Usage

### Basic Usage

```bash
# Fetch all parameters for all communities and temporal frequencies
python fetch_parameters.py --summary --pretty

# Fetch parameters for specific community
python fetch_parameters.py --community AG --summary --pretty

# Fetch parameters for specific temporal frequency
python fetch_parameters.py --temporal daily --summary --pretty

# Fetch specific combination and save to file
python fetch_parameters.py --community AG --temporal daily --output ag_daily.json --pretty
```

### Getting Parameter Codes for API Queries

```bash
# Get meteorology parameter codes for AG daily data
python get_param_codes.py ag_daily.json --community AG --temporal daily --type METEOROLOGY --max 10

# Get all parameter codes as a list
python get_param_codes.py ag_daily.json --community AG --temporal daily --format list
```

### Command Line Options

**fetch_parameters.py:**
- `--community {AG,RE,SB}`: Fetch only for specific community
- `--temporal {daily,monthly,climatology,hourly}`: Fetch only for specific temporal frequency
- `--output FILE`: Save output to JSON file (default: stdout)
- `--summary`: Include summary statistics
- `--pretty`: Pretty-print JSON output
- `--help`: Show help message

**get_param_codes.py:**
- `--community {AG,RE,SB}`: Required community
- `--temporal {daily,monthly,climatology,hourly}`: Required temporal frequency  
- `--type TYPE`: Filter by parameter type (METEOROLOGY, RADIATION, etc.)
- `--max N`: Maximum number of parameters (default: 20)
- `--format {comma,list}`: Output format (default: comma-separated)

## Output Structure

```json
{
  "metadata": {
    "source": "NASA POWER System Manager API",
    "base_url": "https://power.larc.nasa.gov",
    "fetched_communities": ["AG", "RE", "SB"],
    "fetched_temporal_frequencies": ["daily", "monthly", "climatology", "hourly"]
  },
  "parameters": {
    "AG": {
      "daily": {
        "T2M": {
          "abbreviation": "T2M",
          "name": "Temperature at 2 Meters",
          "definition": "The average air (dry bulb) temperature at 2 meters above the surface of the earth.",
          "units": "C",
          "type": "METEOROLOGY",
          "temporal": "DAILY",
          "source": "SOURCE",
          "community": "AG",
          "calculated": false,
          "inputs": null
        }
      }
    }
  },
  "summary": {
    "total_unique_parameters": 200,
    "total_communities": 3,
    "communities": {...},
    "parameter_types": {...},
    "temporal_frequencies": {...},
    "unique_parameters": [...]
  }
}
```

## Parameter Metadata Fields

Each parameter includes:

- `abbreviation`: Short parameter code used in API queries
- `name`: Full descriptive name
- `definition`: Detailed parameter definition
- `units`: Measurement units (°C, mm/day, m/s, etc.)
- `type`: Parameter category (METEOROLOGY, RADIATION, HYDROLOGY, etc.)
- `temporal`: Temporal frequency (DAILY, MONTHLY, etc.)
- `source`: Data source (POWER, SOURCE)
- `community`: Target community (AG, RE, SB)
- `calculated`: Whether parameter is calculated from other parameters
- `inputs`: Input parameters used for calculated parameters

## Communities

- **AG** (Agriculture): Agricultural meteorology parameters
- **RE** (Renewable Energy): Solar and wind energy parameters
- **SB** (Sustainable Buildings): Building energy parameters

## Temporal Frequencies

- **daily**: Daily time series data
- **monthly**: Monthly time series data  
- **climatology**: Long-term climatological averages
- **hourly**: Hourly time series data (limited availability)

## Examples

### Get all AG parameters
```bash
python fetch_parameters.py --community AG --summary --output ag_all_parameters.json --pretty
```

### Get daily parameters for all communities
```bash
python fetch_parameters.py --temporal daily --summary --output daily_parameters.json --pretty
```

### Quick parameter count check
```bash
python fetch_parameters.py --summary | grep "Total unique parameters"
```

## API Reference

The script uses the NASA POWER System Manager API endpoint:
```
https://power.larc.nasa.gov/api/system/manager/parameters?community={COMMUNITY}&temporal={TEMPORAL}
```

## Dependencies

- Python 3.6+
- requests
- Standard library: json, argparse, pathlib