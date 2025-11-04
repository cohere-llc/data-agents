# Status Report&mdash;4 November 2025

__Task:__ Investigate data sources used by  [ENV-AGENTS](https://github.com/aparkin/env-agents/tree/main)

__Overall Goal:__ Facilitate use of ENV-AGENTS (and similar) source data for research applications __(in Python)__

## Status
- Investigated structure of Google Earth Engine Python API
- Began development of prototype Python package to support NASA POWER use case
  - Use to explore design options, estimate costs, allow user assessment of API
  - Can try it out by clicking Binder badge on [prototype repo](https://github.com/cohere-llc/data-agents?tab=readme-ov-file#data-agents) or just click [here](https://mybinder.org/v2/gh/cohere-llc/data-agents/HEAD?filepath=examples/simple.ipynb)
  

## Options For External Data Sources
- Bulk data transfer
  - Beginning to look into bulk data transfer options for external data sources
  - Likely the lowest-cost option, if available
- Python package backed by native web services
  - ENV-AGENTS-like structure
![ENV-AGENTS-like design](env-agents-structure.png)
    - custom adapters for each service with unified query syntax
    - data staged in local Jupyter environment
    - interactions via native REST APIs or Python packages
    - high-cost option
      - custom integration per-adapter
      - high maintenance costs as APIs/Python packages evolve

  - Google Earth Engine-like structure
![GEE-like design](gee-structure.png)
    - backend server supporting python package
    - data staged on server
    - interactions via native REST APIs or bulk protocols
    - medium-high cost option
      - custom integration per-adapter
      - high maintenance costs as APIs evolve
      - allows mixed use with lower-cost bulk-transfer when available

## Bulk Data Options

| Data Product     | Source              | Bulk source  | URL                                       |
|------------------|---------------------|--------------|-------------------------------------------|
| NASA POWER       | NASA                | AWS (S3)     | https://registry.opendata.aws/nasa-power/ |
| GBIF Ecology     | GBIF                | AWS (S3)     | [link](https://aws.amazon.com/marketplace/pp/prodview-dvyemtksskta2?sr=0-1&ref_=beagle&applicationId=AWSMPContessa#usage)               |
| OpenAQ           | OpenAQ              | AWS (S3)     | [link](https://aws.amazon.com/marketplace/pp/prodview-rvesvhymasphs?sr=0-1&ref_=beagle&applicationId=AWSMPContessa#resources)               |
| USGS WDFN        | USGS                |              |                |
| WQP              | WQP                 |              |                |
| SSURGO           | USDA                |              |                |
| OMP Overpass API | OpenStreetMap       | AWS (S3)     | [link](https://aws.amazon.com/marketplace/pp/prodview-3lemxt4oqpqsw?sr=0-4&ref_=beagle&applicationId=AWSMPContessa)               |
| Soilgrids        | Soilgrids           |              |                |
| SRTM             | Google Earth Engine | AWS (S3)*    | [link](https://aws.amazon.com/marketplace/pp/prodview-sfsm7hqeqw2wg?sr=0-2&ref_=beagle&applicationId=AWSMPContessa#resources)               |
| MODIS            | Google Earth Engine | AWS (S3)**   | [Veg Ind 16d 250m](https://aws.amazon.com/marketplace/pp/prodview-4tjmrk43eec6s?sr=0-1&ref_=beagle&applicationId=AWSMPContessa)               |
| WORLDCLIM_BIO    | Google Earth Engine |              |                |
| TERRACLIMATE     | Google Earth Engine |              |                |
| GPM              | Google Earth Engine | AWS (S3)***  | [Final 1month 0.1x0.1 v07](https://registry.opendata.aws/nasa-gpm3imergm/)               |

\* This is for NASA GEDI, which seems to be an alternative elevation dataset to SRTM

\*\* It's not clear if all the MODIS products available on Google Earth Engine are also available on AWS, but many are

\*\*\* There are several GPM precipitation products available as well