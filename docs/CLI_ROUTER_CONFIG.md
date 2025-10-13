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

### GBIF Occurrence Adapter

For GBIF Occurrence adapters, specify:
- `type`: Must be "gbif_occurrence"
- `base_url`: Optional base URL for the GBIF API (defaults to "https://api.gbif.org/v1")
- `description`: Optional description of the adapter

The GBIF Occurrence adapter provides access to biodiversity occurrence data from the Global Biodiversity Information Facility (GBIF). It supports searching for species occurrence records using various filters including taxonomic names, geographic locations, temporal criteria, and data quality filters.

Example GBIF Occurrence adapter configuration:
```json
{
  "type": "gbif_occurrence",
  "description": "GBIF biodiversity occurrence data",
  "base_url": "https://api.gbif.org/v1"
}
```

### OpenAQ Adapter

For OpenAQ adapters, specify:
- `type`: Must be "openaq"
- `api_key`: API key for OpenAQ API access (can use environment variable ${OPENAQ_API_KEY})
- `base_url`: Optional base URL for the OpenAQ API (defaults to "https://api.openaq.org/v3")
- `description`: Optional description of the adapter

The OpenAQ adapter provides access to air quality measurement data from the OpenAQ platform. It supports geographic filtering, parameter-based querying, and temporal filtering for comprehensive air quality data analysis.

Example OpenAQ adapter configuration:
```json
{
  "type": "openaq",
  "api_key": "${OPENAQ_API_KEY}",
  "base_url": "https://api.openaq.org/v3",
  "description": "OpenAQ air quality measurement data"
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

## GBIF Occurrence Adapter Usage

The GBIF Occurrence adapter provides access to biodiversity occurrence data from the Global Biodiversity Information Facility (GBIF). It supports searching for species occurrence records using 37 different search parameters including taxonomic names, geographic locations, temporal criteria, and data quality filters.

### GBIF Occurrence Configuration

Create a GBIF Occurrence adapter configuration file:

```json
{
  "type": "gbif_occurrence",
  "description": "GBIF biodiversity occurrence data"
}
```

Or include it in a router configuration:

```json
{
  "adapters": {
    "gbif_data": {
      "type": "gbif_occurrence",
      "description": "GBIF biodiversity occurrence data"
    },
    "species_list": {
      "type": "tabular",
      "csv_file": "data/local_species.csv"
    }
  }
}
```

### Discovering GBIF Parameters

```bash
# Discover all available GBIF search parameters
uv run data-agents discover --adapter-config config/gbif.adapter.json

# Or discover parameters in a router with GBIF adapter
uv run data-agents discover --router-config config/biodiversity_router.json
```

This will show all 37 available search parameters including:
- Taxonomic filters (scientificName, taxonKey, kingdomKey, etc.)
- Geographic filters (country, decimalLatitude, decimalLongitude, geometry, etc.)
- Temporal filters (year, month, day, eventDate, etc.)
- Data quality filters (basisOfRecord, hasCoordinate, hasGeospatialIssue, etc.)
- Dataset filters (datasetKey, publishingOrg, institutionCode, etc.)

### Querying GBIF Occurrence Data

GBIF queries support simple text searches or structured parameter queries. All parameters can be combined for complex searches.

#### Simple Text Search

```bash
# Search for mountain lions using common name
uv run data-agents query "mountain lion" --adapter-config config/gbif.adapter.json

# Search for scientific name
uv run data-agents query "Puma concolor" --adapter-config config/gbif.adapter.json

# Search with additional filters
uv run data-agents query "Puma concolor country=US year=2023" --adapter-config config/gbif.adapter.json
```

#### Scientific Name Searches

```bash
# Search by exact scientific name
uv run data-agents query "scientificName=Quercus robur" --adapter-config config/gbif.adapter.json

# Search for multiple species
uv run data-agents query "scientificName=Quercus robur,Quercus alba" --adapter-config config/gbif.adapter.json

# Search by genus
uv run data-agents query "scientificName=Quercus" --adapter-config config/gbif.adapter.json
```

#### Geographic Searches

```bash
# Search by country (ISO country codes)
uv run data-agents query "country=US" --adapter-config config/gbif.adapter.json

# Search by coordinate range (decimal degrees)
uv run data-agents query "decimalLatitude=40,45 decimalLongitude=-75,-70" --adapter-config config/gbif.adapter.json

# Search with coordinate requirement
uv run data-agents query "scientificName=Ursus americanus hasCoordinate=true country=CA" --adapter-config config/gbif.adapter.json

# Search by continent
uv run data-agents query "continent=NORTH_AMERICA" --adapter-config config/gbif.adapter.json
```

#### Temporal Searches

```bash
# Search by year
uv run data-agents query "year=2023" --adapter-config config/gbif.adapter.json

# Search by year range
uv run data-agents query "year=2020,2023" --adapter-config config/gbif.adapter.json

# Search by specific month and year
uv run data-agents query "year=2023 month=6" --adapter-config config/gbif.adapter.json

# Search by date range
uv run data-agents query "year=2023 month=6,8" --adapter-config config/gbif.adapter.json
```

#### Taxonomic Hierarchy Searches

```bash
# Search by taxon key (GBIF backbone taxonomy)
uv run data-agents query "taxonKey=2435099" --adapter-config config/gbif.adapter.json

# Search by family
uv run data-agents query "familyKey=9703" --adapter-config config/gbif.adapter.json

# Search by order (all mammals)
uv run data-agents query "orderKey=732" --adapter-config config/gbif.adapter.json

# Search by kingdom (all animals)
uv run data-agents query "kingdomKey=1" --adapter-config config/gbif.adapter.json
```

#### Data Quality and Type Searches

```bash
# Search for human observations only
uv run data-agents query "basisOfRecord=HUMAN_OBSERVATION" --adapter-config config/gbif.adapter.json

# Search for preserved specimens
uv run data-agents query "basisOfRecord=PRESERVED_SPECIMEN" --adapter-config config/gbif.adapter.json

# Search for records with coordinates and no spatial issues
uv run data-agents query "hasCoordinate=true hasGeospatialIssue=false" --adapter-config config/gbif.adapter.json

# Search by license type
uv run data-agents query "license=CC_BY_4_0" --adapter-config config/gbif.adapter.json
```

#### Complex Multi-Parameter Searches

```bash
# Comprehensive species search with quality filters
uv run data-agents query "scientificName=Puma concolor country=US,CA year=2020,2023 basisOfRecord=HUMAN_OBSERVATION hasCoordinate=true" \
  --adapter-config config/gbif.adapter.json

# Geographic and temporal biodiversity survey
uv run data-agents query "decimalLatitude=35,45 decimalLongitude=-125,-115 year=2023 hasCoordinate=true basisOfRecord=HUMAN_OBSERVATION,PRESERVED_SPECIMEN" \
  --adapter-config config/gbif.adapter.json

# Dataset-specific search
uv run data-agents query "datasetKey=50c9509d-22c7-4a22-a47d-8c48425ef4a7 year=2023" \
  --adapter-config config/gbif.adapter.json
```

#### Pagination Control

```bash
# Limit results (default is 20, maximum is 300)
uv run data-agents query "scientificName=Corvus limit=50" --adapter-config config/gbif.adapter.json

# Use offset for pagination
uv run data-agents query "country=US limit=100 offset=200" --adapter-config config/gbif.adapter.json
```

### GBIF Search Parameters Reference

**Taxonomic Parameters:**
- `q`: Full-text search across all fields
- `scientificName`: Scientific name(s) from GBIF backbone
- `taxonKey`: GBIF taxon key(s)
- `kingdomKey`, `phylumKey`, `classKey`, `orderKey`, `familyKey`, `genusKey`, `speciesKey`: Taxonomic hierarchy keys

**Geographic Parameters:**
- `country`: ISO country code(s) (e.g., "US", "CA", "DE")
- `continent`: Continent name(s) (e.g., "NORTH_AMERICA", "EUROPE")
- `decimalLatitude`, `decimalLongitude`: Coordinate ranges (e.g., "40,45" for range)
- `geometry`: Well-Known Text (WKT) polygon
- `geoDistance`: Point and radius search (e.g., "40.7,-74.0,10km")
- `hasCoordinate`: Filter for records with/without coordinates (true/false)
- `hasGeospatialIssue`: Include/exclude records with spatial issues (true/false)

**Temporal Parameters:**
- `year`: Year(s) or year range (e.g., "2023" or "2020,2023")
- `month`: Month(s) or month range (1-12)
- `day`: Day(s) or day range (1-31)
- `eventDate`: ISO date or date range

**Data Quality Parameters:**
- `basisOfRecord`: Type of record (e.g., "HUMAN_OBSERVATION", "PRESERVED_SPECIMEN")
- `occurrenceStatus`: Occurrence status (e.g., "PRESENT", "ABSENT")
- `issue`: Data quality issues to include/exclude
- `license`: License type for the data

**Dataset Parameters:**
- `datasetKey`: GBIF dataset identifier
- `publishingOrg`: Publishing organization identifier
- `institutionCode`: Institution code
- `collectionCode`: Collection code

**Pagination Parameters:**
- `limit`: Number of results to return (default: 20, max: 300)
- `offset`: Starting offset for pagination (default: 0)

### Response Data

GBIF queries return occurrence records with rich metadata including:
- Taxonomic information (scientific names, taxonomic hierarchy)
- Geographic data (coordinates, country, locality information)
- Temporal data (collection dates, event dates)
- Dataset information (data source, institution, collection)
- Data quality indicators (issues, basis of record)
- Additional metadata (collector, license, protocols)

### Common Use Cases

**Species Distribution Analysis:**
```bash
# Get all recent observations of a species in a region
uv run data-agents query "scientificName=Panthera leo country=ZA,BW,ZM year=2020,2023 hasCoordinate=true" \
  --adapter-config config/gbif.adapter.json
```

**Biodiversity Surveys:**
```bash
# Get all species observations in a protected area
uv run data-agents query "decimalLatitude=44.2,44.6 decimalLongitude=-110.7,-110.4 year=2023 basisOfRecord=HUMAN_OBSERVATION" \
  --adapter-config config/gbif.adapter.json
```

**Collection Data:**
```bash
# Get museum specimens from a specific institution
uv run data-agents query "institutionCode=NMNH basisOfRecord=PRESERVED_SPECIMEN" \
  --adapter-config config/gbif.adapter.json
```

**Data Quality Assessment:**
```bash
# Get high-quality coordinate data for analysis
uv run data-agents query "hasCoordinate=true hasGeospatialIssue=false basisOfRecord=HUMAN_OBSERVATION year=2023" \
  --adapter-config config/gbif.adapter.json
```

## OpenAQ Adapter Usage

The OpenAQ adapter provides access to air quality measurement data from the OpenAQ platform. It supports geographic filtering by bounding box or center point with radius, parameter-based querying for specific pollutants, and temporal filtering for comprehensive air quality data analysis.

### OpenAQ Configuration

Create an OpenAQ adapter configuration file:

```json
{
  "type": "openaq",
  "api_key": "${OPENAQ_API_KEY}",
  "base_url": "https://api.openaq.org/v3",
  "description": "OpenAQ air quality measurement data"
}
```

Or include it in a router configuration:

```json
{
  "adapters": {
    "air_quality": {
      "type": "openaq",
      "api_key": "${OPENAQ_API_KEY}",
      "description": "OpenAQ air quality measurement data"
    },
    "weather_data": {
      "type": "nasa_power",
      "description": "NASA POWER meteorological data"
    }
  }
}
```

### API Key Setup

To use the OpenAQ adapter, you need an API key:

1. Sign up for an API key at https://openaq.org
2. Set the environment variable: `export OPENAQ_API_KEY="your_key_here"`
3. The adapter will automatically use the key for authenticated requests

### Discovering OpenAQ Parameters

```bash
# Discover available OpenAQ query methods and capabilities
uv run data-agents discover --adapter-config config/openaq_custom.adapter.json

# Or discover parameters in a router with OpenAQ adapter
uv run data-agents discover --router-config config/air_quality_router.json
```

This will show:
- Available query methods (query_measurements_by_region, query_measurements_by_parameter)
- Supported air quality parameters (PM2.5, PM10, NO2, O3, SO2, CO, etc.)
- Geographic filtering capabilities
- Temporal filtering options

### Querying OpenAQ Air Quality Data

The OpenAQ adapter supports two main query methods for retrieving air quality measurements with various filtering options.

#### Method 1: Geographic Region Queries (query_measurements_by_region)

Query air quality data for specific geographic regions using bounding boxes or center point with radius.

**Bounding Box Queries:**

```bash
# PM2.5 measurements in New York City area
uv run data-agents query "query_measurements_by_region bbox=40.6,-74.2,40.9,-73.7 parameters=pm25 limit=50" \
  --adapter-config config/openaq_custom.adapter.json

# Multiple parameters in Los Angeles area
uv run data-agents query "query_measurements_by_region bbox=33.7,-118.7,34.3,-117.9 parameters=pm25,no2,o3 limit=100" \
  --adapter-config config/openaq_custom.adapter.json

# All parameters in London area with date range
uv run data-agents query "query_measurements_by_region bbox=51.3,-0.5,51.7,0.2 date_from=2024-01-01 date_to=2024-01-07 limit=200" \
  --adapter-config config/openaq_custom.adapter.json
```

**Center Point and Radius Queries:**

```bash
# Air quality within 25km of San Francisco
uv run data-agents query "query_measurements_by_region center_lat=37.7749 center_lon=-122.4194 radius=25 parameters=pm25 limit=50" \
  --adapter-config config/openaq_custom.adapter.json

# Multiple parameters within 50km of Berlin
uv run data-agents query "query_measurements_by_region center_lat=52.5200 center_lon=13.4050 radius=50 parameters=pm25,pm10,no2 limit=100" \
  --adapter-config config/openaq_custom.adapter.json

# Recent measurements within 10km of Tokyo
uv run data-agents query "query_measurements_by_region center_lat=35.6762 center_lon=139.6503 radius=10 date_from=2024-10-01 limit=75" \
  --adapter-config config/openaq_custom.adapter.json
```

#### Method 2: Parameter-Based Queries (query_measurements_by_parameter)

Query measurements for specific air quality parameters with optional geographic and temporal filtering.

**Parameter-Specific Queries:**

```bash
# Global PM2.5 measurements (latest)
uv run data-agents query "query_measurements_by_parameter parameter=pm25 limit=100" \
  --adapter-config config/openaq_custom.adapter.json

# NO2 measurements in the United States
uv run data-agents query "query_measurements_by_parameter parameter=no2 country=US limit=150" \
  --adapter-config config/openaq_custom.adapter.json

# Ozone measurements in specific region
uv run data-agents query "query_measurements_by_parameter parameter=o3 bbox=40.0,-125.0,45.0,-120.0 limit=75" \
  --adapter-config config/openaq_custom.adapter.json
```

**Temporal Filtering:**

```bash
# PM10 measurements from the last week
uv run data-agents query "query_measurements_by_parameter parameter=pm10 date_from=2024-10-01 date_to=2024-10-07 limit=200" \
  --adapter-config config/openaq_custom.adapter.json

# SO2 measurements from specific month in Europe
uv run data-agents query "query_measurements_by_parameter parameter=so2 bbox=35.0,-10.0,70.0,40.0 date_from=2024-06-01 date_to=2024-06-30 limit=100" \
  --adapter-config config/openaq_custom.adapter.json
```

#### Combined Geographic and Parameter Queries

```bash
# PM2.5 in California with temporal filter
uv run data-agents query "query_measurements_by_parameter parameter=pm25 bbox=32.5,-124.4,42.0,-114.1 date_from=2024-09-01 date_to=2024-09-07 limit=200" \
  --adapter-config config/openaq_custom.adapter.json

# Multiple parameters around major cities
uv run data-agents query "query_measurements_by_region center_lat=40.7128 center_lon=-74.0060 radius=100 parameters=pm25,pm10,no2,o3 date_from=2024-10-01 limit=300" \
  --adapter-config config/openaq_custom.adapter.json
```

### Query Parameters Reference

#### Geographic Parameters

**For Bounding Box queries:**
- `bbox`: Comma-separated values as "south,west,north,east" (e.g., "40.6,-74.2,40.9,-73.7")

**For Center/Radius queries:**
- `center_lat`: Center latitude (-90 to 90)
- `center_lon`: Center longitude (-180 to 180)  
- `radius`: Radius in kilometers from center point

**For Parameter-based queries:**
- `country`: ISO country code (e.g., "US", "GB", "DE")
- `bbox`: Optional bounding box for geographic filtering

#### Air Quality Parameters

Common parameters available:
- `pm25`: PM2.5 (Particulate Matter ≤ 2.5 μm)
- `pm10`: PM10 (Particulate Matter ≤ 10 μm)
- `no2`: Nitrogen Dioxide
- `o3`: Ozone
- `so2`: Sulfur Dioxide
- `co`: Carbon Monoxide
- `bc`: Black Carbon

#### Temporal Parameters

- `date_from`: Start date in YYYY-MM-DD format
- `date_to`: End date in YYYY-MM-DD format

#### Control Parameters

- `limit`: Maximum number of results to return (default varies by method)
- `parameters`: Comma-separated list of parameters for region queries

### Response Data Structure

OpenAQ queries return detailed measurement data including:
- **Measurement Values**: Pollutant concentrations with units
- **Location Information**: Station names, coordinates, addresses
- **Temporal Data**: Measurement timestamps and collection dates
- **Data Quality**: Quality flags and validation status
- **Source Information**: Data provider and sensor details
- **Geographic Context**: Country, region, and locality information

### Common Use Cases

**Urban Air Quality Monitoring:**
```bash
# Monitor air quality in major metropolitan areas
uv run data-agents query "query_measurements_by_region center_lat=34.0522 center_lon=-118.2437 radius=50 parameters=pm25,no2,o3 date_from=2024-10-01 date_to=2024-10-07" \
  --adapter-config config/openaq_custom.adapter.json
```

**Regional Pollution Assessment:**
```bash
# Assess pollution levels across a state or province
uv run data-agents query "query_measurements_by_region bbox=32.0,-107.0,37.0,-103.0 parameters=pm25,pm10,o3 date_from=2024-09-01 date_to=2024-09-30" \
  --adapter-config config/openaq_custom.adapter.json
```

**Parameter-Specific Analysis:**
```bash
# Focus on specific pollutant across multiple regions
uv run data-agents query "query_measurements_by_parameter parameter=pm25 country=US date_from=2024-10-01 date_to=2024-10-07 limit=500" \
  --adapter-config config/openaq_custom.adapter.json
```

**Comparative Studies:**
```bash
# Compare air quality between different cities
uv run data-agents query "query_measurements_by_region center_lat=51.5074 center_lon=-0.1278 radius=25 parameters=pm25,no2 date_from=2024-10-01 limit=100" \
  --adapter-config config/openaq_custom.adapter.json
```

**Environmental Health Research:**
```bash
# Gather comprehensive air quality data for health studies
uv run data-agents query "query_measurements_by_region bbox=40.4774,-74.2591,40.9176,-73.7004 parameters=pm25,pm10,no2,o3,so2 date_from=2024-08-01 date_to=2024-08-31" \
  --adapter-config config/openaq_custom.adapter.json
```

### Rate Limiting and Best Practices

The OpenAQ API has rate limits to ensure fair usage:
- The adapter automatically handles rate limiting with appropriate warnings
- For large data requests, consider breaking them into smaller geographic or temporal chunks
- Use specific parameters and date ranges to optimize query performance
- The adapter will retry failed requests and provide meaningful error messages

### Data Quality Considerations

- OpenAQ aggregates data from multiple sources with varying quality levels
- Some sensors may have gaps in data or quality issues
- The adapter includes location enrichment to provide geographic context
- Consider filtering by specific data providers or sensor types for consistency

## Testing and Validation

All adapter configurations and CLI examples in this documentation are validated through comprehensive tests:

### Automated Testing

The data-agents project includes extensive tests for all adapters and CLI functionality:

```bash
# Test all adapters including OpenAQ
pytest tests/adapters/ -v

# Test CLI integration with all adapter types
pytest tests/test_*integration.py -v

# Test router configurations
pytest tests/test_cli_router*.py -v

# Test specific adapter
pytest tests/adapters/test_openaq_adapter.py -v
```

### Example Validation

All configuration examples and CLI commands in this documentation are:
- ✅ **Syntax Validated**: JSON/YAML format correctness
- ✅ **Parameter Validated**: Geographic coordinates, date formats, parameter names
- ✅ **CLI Tested**: Command structure and argument validation
- ✅ **Integration Tested**: Adapter creation and router configuration
- ✅ **Error Handling Tested**: Invalid configurations and network issues

### Configuration File Testing

Each adapter configuration file is tested for:
- Required field presence and format
- Environment variable substitution
- API endpoint accessibility
- Parameter validation
- Error message clarity

### Query Example Testing

All query examples are validated for:
- Parameter format correctness
- Geographic coordinate validity
- Date range format compliance
- Parameter name accuracy
- Limit and pagination settings

This ensures that all examples in this documentation work correctly and provide reliable starting points for users.

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
- `config/gbif.adapter.json` - GBIF Occurrence adapter configuration
- `config/openaq_custom.adapter.json` - OpenAQ adapter configuration
- `config/jsonplaceholder.adapter.json` - Single adapter configuration example
- `examples/sample_data.csv` - Sample CSV file for testing
- `config/httpbin.adapter.json` - Another REST adapter configuration example
- `examples/nasa_power_example.py` - Python example showing NASA POWER adapter usage
- `examples/openaq_example.py` - Python example demonstrating OpenAQ adapter usage