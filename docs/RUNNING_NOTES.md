# Notes as they happen
Potentially useful information from this doc will be included in the CUMULATIVE_NOTES.md file after some clean up.

## 6 Nov 2025
Looking at [BASIN-3D](https://github.com/BASIN-3D/basin3d)
In general:
- Seems like it is intended to fill a similar need as ENV-AGENTS
- Also, similar adapter-pattern structure to ENV-AGENTS

Comments/Concerns:
- Seems quite bottom-up in terms of design, so the querying syntax should be evaluated carefully for applicability to new data sets and use-of-use
- It will likely have similar costs in terms of integration and maintenance of new data sources as ENV-AGENTS
- They seem to have started with just USGS and then extended it to EQA-WQX and ESS-DIVE data sets
  - It would be interesting to hear how this went and how much the original structure needed to be adapted
- Seems like possibly a custom data schema (although I'm not familiar enough with what is commonly used to be sure). At least, doesn't seem to be GeoJSON (used by NASA and Google)

Initial Recommendations
- Would not recommend pursuing, unless collaboration with the BASIN-3D stakeholders is important
- If it is, would recommend drafting use-case example to evaluate API and querying limitations

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