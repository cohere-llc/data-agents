# Running Notes from Analysis of Env-Agents Data Sources

## Overall Observations

- It's not too hard to vibe-code your way to getting data from these APIs (definitely not for production, but potentially useful for one-off research applications).
- The APIs are geared towards facilitating fine-grained searches, not doing "bulk" data transfers.
- Several of these sources are already compilations of disparate datasets that have gone through some standardization processes. 

## Potential User Personas

After looking through several of the APIs and thinking about ways to facilitate use of these data by researchers,
it seemed potentially useful to think through options by way of personas (still thinking through this, though).

| Persona | Data Access Method | User Skills   | Throughput | Data Location | Development Effort to Facilitate |
|---------|--------------------|---------------|------------|---------------|----------------------------------|
| A       | Native website     | Chrome, Excel | Low        | Source        | None                             |
| B       | Native API         | Python, VS Code, Copilot | Moderate | Source | Low (example Jupyter Notebooks) |
| C       | KBase              | KBase User    | High       | Source or LakeHouse | High (data transfer/transformation; custom APIs)

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
- License: public domain (https://www.nasa.gov/organizations/disclaimer/)
- Size: 8.5 TB (https://www.earthdata.nasa.gov/news/feature-articles/power-earth-science-data#:~:text=The%20POWER%20team%20soon%20will,Amazon%20Sustainability%20Data%20Initiative%20(ASDI))
- Updated: daily

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

### GBIF Ecology
- Description of API: https://techdocs.gbif.org/en/openapi/
- License: Various (Public Domain, Create Commons 4.0, Unspecified)
- Size: ~2B occurrence records (from 81K datasets)
- The API is split up, but there appears to be only one data product (occurrence). The remaining API sections seem to be tools for visualization, registering/managing data sources, and querying metadata (I think)

| Data Product | OpenAPI spec URL                                  |
|--------------|---------------------------------------------------|
| Occurrence   | https://techdocs.gbif.org/openapi/occurrence.json |

| Utility                                                                | OpenAPI spec URL                                                        |
|------------------------------------------------------------------------|-------------------------------------------------------------------------|
| Registry (Datasets, Installations, Organizations, Nodes, and Networks) | https://techdocs.gbif.org/openapi/registry-principal-methods.json       |
| Species (taxonomically groups datasets)                                | https://techdocs.gbif.org/openapi/checklistbank.json                    |
| Occurrence Image (cute animal pics)                                    | none. access instructions : https://techdocs.gbif.org/en/openapi/images |
| Maps (geographical visualization of data)                              | https://techdocs.gbif.org/openapi/v2-maps.json                          |
| Literature (papers citing GBIF data)                                   | https://techdocs.gbif.org/openapi/literature.json                       |
| Validator (not sure what this is)                                      | https://techdocs.gbif.org/openapi/validator.json                        |
| Vocabulary (registry of controlled vocabulary - not sure what this means) | https://techdocs.gbif.org/openapi/vocabulary.json                    |

- env-agents only queries against the `occurrence/search` endpoint
- the OpenAPI spec seems pretty comprehensive. No issues using it to discover API for searching

## 10 Oct 2025
### OpenAQ

- Description of API: https://api.openaq.org/openapi.json
- License: Licenses for specific measurement data are queryable through the API
- Size: uncertain
- The API has many endpoints, but seems generally centered around "measurements", which can be located by
geographical location, type, instrument, source, etc. (all described in one OpenAPI spec)
- Seems to include detailed information about source, manner of collection

| Data Product    | OpenAPI spec URL                    |
|-----------------|-------------------------------------|
| AQ Measurements | https://api.openaq.org/openapi.json |

- env-agents searches by location and "parameter" (NO2, NO, PM2.5, etc.)