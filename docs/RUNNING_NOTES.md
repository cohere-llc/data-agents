# Running Notes from Analysis of Env-Agents Data Sources

## 9 Oct 2025
### General Approach To Analysis
- Use the RESTAdapter to explore API of data sources used in [env-agents](https://github.com/aparkin/env-agents)
- Create custom adapter to allow querying of same datasets as in env-agents
  - Do not attempt to standardize queries or output data, as done in env-agents
- For each data provider:
  - Identify all available datasets (not just what is used in env-agents)
  - Assess options for autmoatic discovery of API (openapi, etc)
  - Document considerations relevant to KBase project

### NASA POWER
- Desciption of API: https://power.larc.nasa.gov/api/pages/

| Data Product                       | OpenAPI spec URL                                                  |
|------------------------------------|-------------------------------------------------------------------|
| Hourly                             | https://power.larc.nasa.gov/api/temporal/hourly/openapi.json      |
| Daily                              | https://power.larc.nasa.gov/api/temporal/daily/openapi.json       |
| Monthly/Annual                     | https://power.larc.nasa.gov/api/temporal/monthly/openapi.json     |
| Climatology                        | https://power.larc.nasa.gov/api/temporal/climatology/openapi.json |
| Wind Rose                          | https://power.larc.nasa.gov/api/application/windrose/openapi.json |
| Thermal and Thermal Moisture Zones | https://power.larc.nasa.gov/api/application/zones/openapi.json    |
| Climate Projections                | https://power.larc.nasa.gov/api/projection/daily/openapi.json     |

| Utility                                         | OpenAPI spec URL                                              |
|-------------------------------------------------|---------------------------------------------------------------|
| Toolkit (visualization)                         | https://power.larc.nasa.gov/api/toolkit/openapi.json          |
| Manager (configuration data for all POWER APIs) | https://power.larc.nasa.gov/api/system/manager/openapi.json   |
| Resources (not sure exactly what this is)       | https://power.larc.nasa.gov/api/system/resources/openapi.json |
| PaRameter Uncertainty ViEwer (PRUVE)            | https://power.larc.nasa.gov/api/pruve/openapi.json            |

- env-agents only uses the daily data products
- the API is a little difficult to discover (e.g., parameter names are not included as enum values in the individual data product OpenAPI specs, instead they are accessible via the Manager API)

#### NASA POWER Considerations
- The APIs seem to be geared towards querying for small data sets (individual parameters over spatiotemporal ranges). Not sure how large the underlying datasets are.
- Underlying data likely updated regularly. (daily?)
- Seems like there could be quite a bit of metadata related to data collection, calibrations, attribution, etc. that does not seem to be available through the API, but may be important for research use (not sure though)
- NASA already has an interactive way to query these data (https://power.larc.nasa.gov/data-access-viewer/)  

