# NASA POWER Use Case Demo

This folder contains an example Python script that uses a hypothetical pacakge to
query and process geographical datasets.

The example is based on a real-world use case using the NASA POWER web service and a
CSV file. The querying and processing of the data are done via the R script included
in this folder.

The proposed Python package API consists of similar top-level functions as the
Google Earth Engine JavaScript/Python API, but is intended to pull data from
various sources (web services, databases, local files, etc.) instead of just
GEE datasets. The data and computation are local, not in the Google cloud
environment.

Primary references:
- https://developers.google.com/earth-engine/apidocs/ee-featurecollection
- https://developers.google.com/earth-engine/guides/joins_spatial
- https://developers.google.com/earth-engine/guides/feature_collection_reducing
- https://developers.google.com/earth-engine/apidocs/ee-featurecollection-reducecolumns
