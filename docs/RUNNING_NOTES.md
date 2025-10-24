# Notes as they happen
Potentially useful information from this doc will be included in the CUMULATIVE_NOTES.md file after some clean up.

## 24 Oct 2025
It looks like the Google Earty Engine Python and JS packages are public (https://github.com/google/earthengine-api)
- They seems to primarily be a wrapper for the GEE backend API server, but might be useful as a pattern
- 

There are packages with APIs similar to Google Earth Engine that work with other data sources
- DataCube
  - https://github.com/opendatacube/datacube-core
  - https://opendatacube.readthedocs.io/en/latest/index.html
  - Specific to geographical data
  - Does not seem to allow the complex types of queries of GEE
  - API seems less well designed
- IBM Geospatial Analytics (formerly IBM PAIRS)
  - https://github.com/IBM/Environmental-Intelligence-Suite
  - https://www.ibm.com/docs/en/environmental-intel-suite?topic=components-geospatial-analytics
  - Python API involves writing a lot of complex json data
  - Seems more complex and less elegant than GEE API
- Pangeo-Forge
  - https://pangeo-forge.org
  - https://pangeo-forge.readthedocs.io/en/latest/
  - Seems to have been decommissioned

Projects that use Google Earth Engine Python/JS APIs
- Geo Agentic Starter Kit
  - https://github.com/GeoRetina/geo_agentic_starter_kit
- SEPAL
  - https://github.com/openforis/sepal
  - > SEPAL is a cloud computing platform for geographical data processing. It enables users to quickly process large amount of data without high network bandwidth requirements or need to invest in high-performance computing infrastructure.