# Status Update&mdash;21 October 2025

__Task:__ Investigate data sources used by  [ENV-AGENTS](https://github.com/aparkin/env-agents/tree/main)

__Overall Goal:__ Facilitate use of ENV-AGENTS (and similar) source data for research applications __(in Python)__

## Status

- Investigated all Phase 0-2 data sources from ENV-AGENTS
- Looked into OpenAPI Python packages and Google Earth Engine Python package

## Summary of Data Sources

| Data Product     | Source              | OpenAPI spec | Python Package |
|------------------|---------------------|--------------|----------------|
| NASA POWER       | NASA                | yes          | -              |
| GBIF Ecology     | GBIF                | yes          | pygbif         |
| OpenAQ           | OpenAQ              | yes          | -              |
| USGS WDFN        | USGS                | yes          | -              |
| WQP              | WQP                 | no           | -              |
| SSURGO           | USDA                | no           | -              |
| OMP Overpass API | OpenStreetMap       | no           | -              |
| Soilgrids        | Soilgrids           | yes          | -              |
| SRTM             | Google Earth Engine | no           | ee             |
| MODIS            | Google Earth Engine | no           | ee             |
| WORLDCLIM_BIO    | Google Earth Engine | no           | ee             |
| TERRACLIMATE     | Google Earth Engine | no           | ee             |
| GPM              | Google Earth Engine | no           | ee             |



## OpenAPI-based Python Packages

### What
Several python packages exist that consume OpenAPI specs to facilitate (to varying degrees)
in-code interactions with the REST APIs described.

- `openapi-core`
  - https://github.com/python-openapi/openapi-core
  - Still pre-1.0, but seems actively maintained, 60 contributors, 350 Stars
  - No code-generation
  - Provides ability to validate and unmarshall request and response data
- `openapi-generator`
  - https://github.com/OpenAPITools/openapi-generator
  - On v7.16, 3300 contributors, 25K Stars
  - Code generator (for many languages)
  - Creates client libraries, server stubs, docs

### Why
- Could use existing packages to facilitate interactions with generic services based on their published specs
- Would be somewhere between having users use native APIs to access data and providing a Python package with standardized queryies and output data
- Could build upon the OpenAPI-backed wrappers with custom implementations of specific query types (location, time, species, etc.) for services that support those type of searches, gradually standardizing query syntax but always leaving native search capabilities in place
- Custom transformations to standardize output data could also gradually be introduced. This would gradually move us closer to a fully standardized Python package

### Notes
- I tried out `openapi-core` with the NASA POWER OpenAPI spec, see [here](https://github.com/cohere-llc/data-agents/blob/f842d148667db6befadee680238635e12144d62f/tests/adapters/test_openapi_adapter.py#L53-L88)
  - The package is simple and fairly straigh-forward to use
- I haven't tried `openapi-generator` yet. Seems like a bigger lift to use for the first time.
- The biggest potential problem I see is the quality of the OpenAPI specs themselves
  - NASA POWER input schema needed to be modified slightly to work (syntax issues)
  - NASA POWER output schema was inconsistent with the actual output, but modifying the schema to be less strict for some data allowed it to work
- If we do go this route, it would be good to set up the package to be consistent with how KBase users interact with other datasetes in Python (ie. genomics data)

## Google Earth Engine

Google Earth Engine seems to be doing something similar to what we need to do. They provide a cloud-based service to query and processes geographical data from a variety of sources in a standardized way. We may benefit from investigating how they have structured their APIs (JS and Python).

### Structure

- Data are organized into __Images__ (raster data; e.g., satellite images) and __Features__ (Geometry-based data; roads, borders, point measurements)
- __ImageCollection__ and __FeatureCollection__ are labelled collections that can be queried
- __Geometry__ is a point, line, shape, etc. in [GeoJSON](https://datatracker.ietf.org/doc/html/rfc7946#autoid-1) format
- __Reducer__ aggregates data algorithmically
- __Join__ allows SQL-like linking of datasets for complex queries

### Some potentially relevant examples
- From the Earth Enginge [Getting Started Guide](https://developers.google.com/earth-engine/guides/getstarted). (code samples are licensed under Apache 2.0)
  - public [Python/JS client libraries](https://github.com/google/earthengine-api) (Apache 2.0)
- Loading a dataset and filtering with standard and dataset-specific attributes:
```js
var filteredCollection = ee.ImageCollection('LANDSAT/LC08/C02/T1_TOA')
  .filterBounds(point)
  .filterDate(start, finish)
  .sort('CLOUD_COVER', true);
```
- Processing filtered data algorithmically:
```js
// Load and display a Landsat TOA image.
var image = ee.Image('LANDSAT/LC08/C02/T1_TOA/LC08_044034_20140318');
Map.addLayer(image, {bands: ['B4', 'B3', 'B2'], max: 0.3});

// Create an arbitrary rectangle as a region and display it.
var region = ee.Geometry.Rectangle(-122.2806, 37.1209, -122.0554, 37.2413);
Map.addLayer(region);

// Get a dictionary of means in the region.  Keys are bandnames.
var mean = image.reduceRegion({
  reducer: ee.Reducer.mean(),
  geometry: region,
  scale: 30
});
```
- Joining datasets:
```js
// Load a Landsat 8 image collection at a point of interest.
var collection = ee.ImageCollection('LANDSAT/LC08/C02/T1_TOA')
    .filterBounds(ee.Geometry.Point(-122.09, 37.42));

// Define start and end dates with which to filter the collections.
var april = '2014-04-01';
var may = '2014-05-01';
var june = '2014-06-01';
var july = '2014-07-01';

// The primary collection is Landsat images from April to June.
var primary = collection.filterDate(april, june);

// The secondary collection is Landsat images from May to July.
var secondary = collection.filterDate(may, july);

// Use an equals filter to define how the collections match.
var filter = ee.Filter.equals({
  leftField: 'system:index',
  rightField: 'system:index'
});

// Create the join.
var simpleJoin = ee.Join.simple();

// Apply the join.
var simpleJoined = simpleJoin.apply(primary, secondary, filter);

// Display the result.
print('Simple join: ', simpleJoined);
```
