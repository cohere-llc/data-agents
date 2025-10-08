mattldawson: Describe the overall workflow for running aquire_environmental_data with `--phase 0`, sppecifically how the NASA POWER API is used and any data trasformations involved with NASA POWER data

GitHub Copilot:
## Overall Workflow for Phase 0 with NASA POWER

Here's the complete workflow when running `acquire_environmental_data.py --phase 0`:

### 1. **Initialization & Data Loading**
````bash
python scripts/acquire_environmental_data.py --phase 0 --clusters clusters.csv --samples samples.tsv
````

- Loads spatial clusters (4,789 clusters with center coordinates and bounding boxes)
- Loads genome samples with collection metadata
- Sets up SQLite database with tracking tables
- Initializes NASA POWER adapter (cached for reuse across clusters)

### 2. **NASA POWER Service Configuration**
````python
"NASA_POWER": {
    "rate_limit": 0.5,  # 2 requests per second (polite to NASA servers)
    "timeout": 60,      # 60 second timeout per request
    "time_range": ("2021-01-01", "2021-12-31")  # Full year 2021
}
````

### 3. **Cluster Processing Loop**

For each of the 4,789 spatial clusters:

#### **a) Geometry Preparation**
- Retrieves cluster center coordinates and bounding box from database
- For single-point clusters: adds 500m buffer (±0.005°)
- For multi-point clusters: uses actual DBSCAN-derived extent
- Creates `Geometry` object with bbox coordinates

#### **b) Request Specification**
````python
spec = RequestSpec(
    geometry=bbox_geometry,  # Cluster bounding box
    time_range=("2021-01-01", "2021-12-31"),
    variables=None,  # NASA POWER adapter determines available variables
    extra={"timeout": 60}
)
````

#### **c) NASA POWER API Call**
The NASA POWER adapter (`NASAPowerAdapter`) makes calls to NASA's POWER API:

**API Endpoint Pattern:**
````
https://power.larc.nasa.gov/api/temporal/daily/point
https://power.larc.nasa.gov/api/temporal/daily/regional
````

**Key Parameters Sent:**
- **Geometry**: Either point (lat,lon) or regional bbox
- **Date range**: 2021-01-01 to 2021-12-31  
- **Parameters**: All available meteorological variables (T2M, PRECTOTCORR, WS2M, etc.)
- **Format**: JSON
- **Community**: Agroclimatology (AG) - provides comprehensive variable set

### 4. **NASA POWER Data Transformations**

#### **a) Variable Name Mapping**
Raw NASA POWER parameter codes are mapped to canonical variables:
````python
# From rules_enhanced.py CANONICAL_MAP
"T2M" → "atm:air_temperature_2m"
"PRECTOTCORR" → "atm:precipitation_corrected" 
"WS2M" → "atm:wind_speed_2m"
"RH2M" → "atm:relative_humidity_2m"
# ... 30+ more mappings
````

#### **b) Unit Standardization** 
Units are normalized using `UNIT_ALIASES`:
````python
"C" → "degC"
"mm/day" → "mm/d"  
"m/s" → "meters_per_second"
"%" → "percent"
````

#### **c) Temporal Data Processing**
- NASA POWER returns daily time series for 2021 (365 days)
- Each day becomes a separate observation record
- Time stamps are standardized to ISO format
- Missing values are handled (NASA POWER uses -99 for missing data)

#### **d) Spatial Coordinate Assignment**
- For point queries: uses exact lat/lon from NASA POWER response
- For regional queries: may return grid points within the bbox
- Each observation gets precise coordinates for downstream spatial analysis

### 5. **Data Storage Format**

Each transformed observation is stored in the `env_observations` table:
````sql
INSERT INTO env_observations (
    obs_id,           -- Computed unique ID
    cluster_id,       -- Links to spatial cluster
    service_name,     -- "NASA_POWER"
    variable,         -- Canonical name (e.g., "atm:air_temperature_2m")
    value,            -- Numeric value
    unit,             -- Standardized unit
    time_stamp,       -- ISO date string
    lat, lon          -- Precise coordinates
)
````

### 6. **Example Data Flow**

**Input Cluster:**
- Cluster ID: 1247
- Center: 40.7128°N, 74.0060°W (New York City)
- Bbox: [40.707, -74.011, 40.718, -74.001]

**NASA POWER API Request:**
````
GET https://power.larc.nasa.gov/api/temporal/daily/regional
?parameters=T2M,T2M_MAX,T2M_MIN,PRECTOTCORR,WS2M,RH2M,...
&community=AG
&longitude-min=-74.011&longitude-max=-74.001
&latitude-min=40.707&latitude-max=40.718
&start=20210101&end=20211231&format=JSON
````

**Raw NASA Response (sample):**
````json
{
  "properties": {
    "parameter": {
      "T2M": {
        "20210101": 2.5,
        "20210102": 1.8,
        ...
      },
      "PRECTOTCORR": {
        "20210101": 0.0,
        "20210102": 2.3,
        ...
      }
    }
  },
  "geometry": {"coordinates": [-74.006, 40.712]}
}
````

**Transformed Output (sample records):**
````
obs_id=NASA_POWER_1247_20210101_T2M, cluster_id=1247, service_name=NASA_POWER,
variable=atm:air_temperature_2m, value=2.5, unit=degC, time_stamp=2021-01-01,
lat=40.712, lon=-74.006

obs_id=NASA_POWER_1247_20210102_PRECTOTCORR, cluster_id=1247, service_name=NASA_POWER,
variable=atm:precipitation_corrected, value=2.3, unit=mm/d, time_stamp=2021-01-02,
lat=40.712, lon=-74.006
````

### 7. **Progress Tracking & Resume Capability**

- Each cluster's processing status is tracked in `cluster_processing` table
- Failed clusters can be retried automatically
- Rate limiting (0.5s between requests) ensures NASA server politeness
- Progress bar shows real-time success/failure counts

**Expected Output for Phase 0:**
- ~1.75M observations from NASA POWER (4,789 clusters × 365 days × ~1 variable per day average)
- Processing time: ~40 minutes (4,789 clusters × 0.5s rate limit)
- Data provides comprehensive meteorological context for each genome sampling location

This creates a rich environmental dataset linking each microbial genome sample to detailed meteorological conditions at its collection site during 2021.