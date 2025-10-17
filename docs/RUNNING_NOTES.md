# Running Notes from Analysis of Env-Agents Data Sources

__Task:__ Investigate data sources used by  [ENV-AGENTS](https://github.com/aparkin/env-agents/tree/main)

__Overall Goal:__ Facilitate use of ENV-AGENTS (and similar) source data for research applications

## Methodology
- Use Copilot to wrap source data APIs
  - Use "adapter" approach as in ENV-AGENTS
  - Do not attempt to standardize queries or output data (as done in ENV-AGENTS)
- For each data provider:
  - Identify all available datasets (not just what is used in env-agents)
  - Assess options for automatic discovery of API (openapi, etc)
  - Document considerations relevant to KBase project
- Why this approach?
  - Don't want to write a lot of code by hand that will probably never be used again
  - Allows assessment of how useful AI agents might be for researchers attempting to use native data source APIs

## General Observations
- Many APIs seem stable and well-documented (OpenAPI specs available).
  - NASA POWER, GBIF, OpenAQ
- Some are not well documented and require extra effort to understand.
  - USGS NWIS (no OpenAPI spec, but being ported to new service with somewhat rough OpenAPI spec), WQP (no OpenAPI specs)
- All have web portals available, with most being easy to use.
- Of the two data sources I could find estimates for (NASA POWER, GBIF), the underlying data is (very roughly) ~5-10 TB.
- It's not too hard to vibe-code your way to getting data from these APIs (definitely not for production, but potentially useful for one-off research applications).
- APIs are geared towards facilitating fine-grained searches, not doing "bulk" data transfers.
- Several of these sources are already compilations of disparate datasets that have gone through some standardization processes.
- The lowest-cost, lowest-risk, most straightforward and actionable way to use these data are through the web portals already developed by the maintainers of the datasets.
  - The value-add of any proposed development should be measured against this approach
- Bulk data transfer may require contacting the admins of the various data sources. I couldn't find anything by searching for this.

## My Rough Understanding of Potential Options (or Roadmap)

| Data Access Method                                            | User Skills                      | Throughput  | Dev Cost                                                        | User Costs                                                                                                                  | Pros                                                                                                       | Cons                                                                                                                                                                       |
|---------------------------------------------------------------|----------------------------------|-------------|-----------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Native Web Portal (__NOT PURSUING__) | Browser; Excel; multiple portals | Low         | Very Low (docs)                                                 | Medium (learning to use different portals; time spent on individual searches; translation between platform concepts/naming) | Low dev cost; currently available                                                                          | Low throughput                                                                                                                                                             |
| Jupyter Notebook (Native APIs)                                | Python; AI Agent                 | Medium      | Low-Medium (tutorials; examples, user forums, workshops)        | Medium-High (learning APIs with AI assist; translation between platform concepts/naming)                                    | Low dev cost; high throughput; users gain transferable skills                                              | High spin-up time for users w/ limited coding experience; uncertain usefulness of AI agents                                                                                |
| Jupyter Notebook (custom Python pkg using native APIs)        | Python                           | Medium-High | Medium-High (pkg using multiple APIs, docs, user forums)        | Low-Medium (integrating output with various schemas/naming)                                                                 | High throughput; only one portal for users to learn                                                        | High dev cost; volatile APIs; non-transferable user skills                                                                                                                 |
| Jupyter Notebook (bulk data ingestion; standardized querying) | Python                           | High        | High (custom portal and API; data ingestion; docs; user forums) | Low (standardized query; more consistent results schemas/naming)                                                            | High throughput; only one portal for users to learn; standardized data sets; single back-end API           | High dev cost; loss of information through standardizing data; volatile source data schemas; volatile bulk transfer APIs (if even available); non-transferable user skills |

## Possible Paths Forward

### OpenAPI-based Python Packages

If the plan includes both options 2 and 3, we could consider initially developing a Python package that uses existing OpenAPI Python packages to facilitate interactions with generic services based on their published specs (sort of midway between options 2 and 3). We could then build upon the OpenAPI-backed wrappers with custom implementations of specific query types (location, time, species, etc.) for services that support those type of searches, gradually standardizing query syntax but always leaving native search capabilities in place. Custom transformations to standardize output data could also gradually be introduced. This would gradually move us closer to option 3. (This work might result in useful information for option 4, but wouldn't directly contribute to it.)

#### OpenAPI Python Packages
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

#### Notes
- I tried out `openapi-core` with the NASA POWER OpenAPI spec, see [here](https://github.com/cohere-llc/data-agents/blob/f842d148667db6befadee680238635e12144d62f/tests/adapters/test_openapi_adapter.py#L53-L88)
  - The package is simple and fairly straigh-forward to use
- I haven't tried `openapi-generator` yet. Seems like a bigger lift to use for the first time.
- The biggest potential problem I see is the quality of the OpenAPI specs themselves
  - NASA POWER input schema needed to be modified slightly to work (syntax issues)
  - NASA POWER output schema was inconsistent with the actual output, but modifying the schema to be less strict for some data allowed it to work
- If we do go this route, it would be good to set up the package to be consistent with how KBase users interact with other datasetes in Python (ie. genomics data)

# Notes on Specific Data Sources

## NASA POWER
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

### NASA POWER Query Example

#### Point data

##### Request

```bash
curl -X 'GET' \
  'https://power.larc.nasa.gov/api/temporal/daily/point?start=20210801&end=20210805&latitude=33.8&longitude=-116.5&community=ag&parameters=T2M&format=json&units=metric&header=true&time-standard=utc&site-elevation=200' \
  -H 'accept: application/json'
```

##### Response

<div>
<details>
<summary>Click to expand</summary>

```json
{
  "type": "Feature",
  "geometry": {
    "type": "Point",
    "coordinates": [
      -116.5,
      33.8,
      923.95
    ]
  },
  "properties": {
    "parameter": {
      "T2M": {
        "20210801": 29.38,
        "20210802": 31.57,
        "20210803": 32.71,
        "20210804": 34.07,
        "20210805": 34.71
      },
      "PSC": {
        "20210801": 99.01,
        "20210802": 98.93,
        "20210803": 98.72,
        "20210804": 98.46,
        "20210805": 98.41
      }
    }
  },
  "header": {
    "title": "NASA/POWER Source Native Resolution Daily Data",
    "api": {
      "version": "v2.8.0",
      "name": "POWER Daily API"
    },
    "sources": [
      "POWER",
      "MERRA2"
    ],
    "fill_value": -999,
    "time_standard": "UTC",
    "start": "20210801",
    "end": "20210805"
  },
  "messages": [],
  "parameters": {
    "T2M": {
      "units": "C",
      "longname": "Temperature at 2 Meters"
    },
    "PSC": {
      "units": "kPa",
      "longname": "Corrected Atmospheric Pressure (Adjusted For Site Elevation)"
    }
  },
  "times": {
    "data": 0.718,
    "process": 0.03
  }
}
```
</details>
</div>

- Coordinates are: longitude (deg), latitude (deg), elevation (m?)

#### Regional Data

##### Request

```bash
curl -X 'GET' \
  'https://power.larc.nasa.gov/api/temporal/daily/regional?start=20210801&end=20210805&latitude-min=32.0&latitude-max=34.0&longitude-min=-117.0&longitude-max=-115.0&community=ag&parameters=T2M&format=json&units=metric&header=true&time-standard=utc' \
  -H 'accept: application/json'
```

##### Response


<div>
<details>
<summary>Click to expand</summary>

```json
{
  "features": [
    {
      "type": "Feature",
      "geometry": {
        "type": "Point",
        "coordinates": [
          -116.875,
          32,
          220.39
        ]
      },
      "properties": {
        "parameter": {
          "T2M": {
            "20210801": 24.43,
            "20210802": 25.02,
            "20210803": 25.32,
            "20210804": 24.32,
            "20210805": 23.43
          }
        }
      }
    },
    {
      "type": "Feature",
      "geometry": {
        "type": "Point",
        "coordinates": [
          -116.25,
          32,
          980.98
        ]
      },
      "properties": {
        "parameter": {
          "T2M": {
            "20210801": 27.69,
            "20210802": 28.54,
            "20210803": 29.85,
            "20210804": 30.24,
            "20210805": 30.56
          }
        }
      }
    },
    ...
    {
      "type": "Feature",
      "geometry": {
        "type": "Point",
        "coordinates": [
          -115,
          34,
          349.92
        ]
      },
      "properties": {
        "parameter": {
          "T2M": {
            "20210801": 35.17,
            "20210802": 37.43,
            "20210803": 38.77,
            "20210804": 39.68,
            "20210805": 39.43
          }
        }
      }
    }
  ],
  "header": {
    "title": "NASA/POWER Source Native Resolution Daily Data",
    "api": {
      "version": "v2.8.0",
      "name": "POWER Daily API"
    },
    "sources": [
      "MERRA2"
    ],
    "fill_value": -999,
    "time_standard": "UTC",
    "start": "20210801",
    "end": "20210805"
  },
  "messages": [],
  "parameters": {
    "T2M": {
      "units": "C",
      "longname": "Temperature at 2 Meters"
    }
  },
  "times": {
    "data": 0.882,
    "process": 0.07
  },
  "type": "FeatureCollection"
}
```
</details>
</div>

- Coordinates are: longitude (deg), latitude (deg), elevation (m?)
- Results generally are grouped as time series by location

### NASA POWER Considerations
- Output data schemas available in OpenAPI specs
- The APIs seem to be geared towards querying for small data sets (individual parameters over spatiotemporal ranges). Not sure how large the underlying datasets are.
- Underlying data likely updated regularly. (daily?)
- Seems like there could be quite a bit of metadata related to data collection, calibrations, attribution, etc. that does not seem to be available through the API, but may be important for research use (not sure though)
- NASA already has an interactive way to query these data (https://power.larc.nasa.gov/data-access-viewer/)

## GBIF Ecology
- Description of API: https://techdocs.gbif.org/en/openapi/v1/registry-principal-methods
- License: Various (Public Domain, Create Commons 4.0, Unspecified)
- Size: ~2B occurrence records (from 81K datasets) @ ~1.5KB/record = ~3TB
- The API is split up, but there appears to be only one data product (occurrence). The remaining API sections seem to be tools for visualization, registering/managing data sources, and querying metadata (I think)
- They are in the process of migrating to [Version 2 of the REST API](https://techdocs.gbif.org/en/openapi/#roadmap-to-v2)
- Python package available for querying data: [pygbif](https://techdocs.gbif.org/en/data-use/pygbif)

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
- there are an incredible number of search parameters for many of the endpoints and simple searches return huge amounts of data

### GBIF Query Example

#### Species

##### Request

```bash
curl -X 'GET' \
  'https://api.gbif.org/v1/species/search?datasetKey=d7dddbf4-2cf0-4f39-9b2a-bb099caae36c&habitat=TERRESTRIAL&nameType=SCIENTIFIC&q=pomeranian' \
  -H 'accept: application/json'
```

##### Response

<div>
<details>
<summary>Click to expand</summary>

```json
{
  "offset": 0,
  "limit": 20,
  "endOfRecords": true,
  "count": 10,
  "results": [
    {
      "key": 2075001,
      "nameKey": 63249343,
      "datasetKey": "d7dddbf4-2cf0-4f39-9b2a-bb099caae36c",
      "constituentKey": "7ddf754f-d193-4cc9-b351-99906754a03b",
      "nubKey": 2075001,
      "parentKey": 2074940,
      "parent": "Macrosiphoniella",
      "basionymKey": 4485221,
      "basionym": "Metopeurum medvedevi Bozhko, 1957",
      "kingdom": "Animalia",
      "phylum": "Arthropoda",
      "order": "Hemiptera",
      "family": "Aphididae",
      "genus": "Macrosiphoniella",
      "species": "Macrosiphoniella medvedevi",
      "kingdomKey": 1,
      "phylumKey": 54,
      "classKey": 216,
      "orderKey": 809,
      "familyKey": 3042,
      "genusKey": 2074940,
      "speciesKey": 2075001,
      "scientificName": "Macrosiphoniella medvedevi (Bozhko, 1950)",
      "canonicalName": "Macrosiphoniella medvedevi",
      "authorship": "(Bozhko, 1950) ",
      "publishedIn": "Bozhko, M.P. (1950) The aphid fauna of Kharkiv and Sumy regions. 14-15, 173–191.",
      "nameType": "SCIENTIFIC",
      "taxonomicStatus": "ACCEPTED",
      "rank": "SPECIES",
      "origin": "SOURCE",
      "numDescendants": 0,
      "numOccurrences": 0,
      "taxonID": "gbif:2075001",
      "extinct": false,
      "habitats": [
        "TERRESTRIAL"
      ],
      "nomenclaturalStatus": [],
      "threatStatuses": [],
      "descriptions": [
        {
          "description": "Terrestrial."
        },
        {
          "description": "Terrestrial."
        },
        {
          "description": "Material. Syntype: Macrosiphoniella (Ramitrichophorus) medvedevi (Bozhko, 1950) — 2 apterous viviparous female, „ Russia [mistake, right — Ukraine], Helichrysum arenarium, Smiev, 3. viii. 1947, Leg. Bozhko, Ramitrichophorus medvedevi Bozhko, Det. Bozhko ” (from collections of NHM); Paratypes: Macrosiphoniella (Ramitrichophorus) nasti Szelegiewicz, 1958 — 4 apterous viviparous female, „ Polonia, Bydgoszcz, 30. vii. 1956, Helichrysum arenarium, leg. Szelegiewicz, Paratypus, Macrosiphoniella (Ramitrichophorus) nasti sp. n., det. Szelegiewicz, 1957 ” (from collections of MNHN and NHM). Additional materials: 2 apterous viviparous females, 03. vii. 1947, Ukraine, Helichrysum arenarium (from collections of MNHN); 4 apterous viviparous females, 06. viii. 1957, Poland, Kuyavian-Pomeranian Voivodeship, Bydgoszcz, Helichrysum arenarium (from collections of MNHN); 1 apterous viviparous female, 1 male and 16 oviparous female, 20. ix. 1962, Poland, Kuyavian-Pomeranian Voivodeship, Bydgoszcz, Helichrysum arenarium (from collections of IE BC CAS); 3 apterous viviparous females, 25. vii. 1965, Poland, Mazovian Voivodeship, Otwock County, Otwock, Helichrysum arenarium (from collections of IE BC CAS); 37 apterous viviparous females and 16 alate viviparous female, 26. vii. 1969, Russia, Moscow Province, Serpukhovsky District, Luzhki Vill., Helichrysum arenarium (from collections of IE BC CAS). Also used data from Bozhko (1950, 1957, 1976), and Szelegiewicz (1958)."
        },
        {
          "description": "Etymology. The species was named in honor of the famous Soviet Ukrainian entomologist Sergei Ivanovich Medvedev."
        },
        {
          "description": "Distribution. Germany (Mecklenburg-Vorpommern) (Müller 1969), Poland (West Pomeranian Voivodeship, Świnoujście and Kamień County, Międzyzdroje; Warmian-Masurian Voivodeship, Olsztyn; Kuyavian-Pomeranian Voivodeship, Bydgoszcz; Greater Poland Voivodeship, Poznań; Mazovian Voivodeship, Otwock County, Otwock; Podlasie Voivodeship, Mońki County, near Dolistowo Stare Vill.; Pomeranian Voivodeship, Nowy Dwór Gdański County, Krynica Morska) (Szelegiewicz 1958 a, 1958 b, 1967, 1968, 1974, 1975, 1978; Huculak 1965; Achremowicz 1967, 1975; Czylok et al. 1982; Nast et al. 1990; Węgierek & Wojciechowski 2004; Osiadacz & Hałaj 2010), Russia (Moscow Province, Serpukhovsky District, Luzhki Vill.), Ukraine (Kharkiv Province, Chuhuiv District, near Zmiiv) (Bozhko 1950, 1963, 1976), Kazakhstan (?) (Aktobe Region, near Aktobe and in Temir District, near Kalmakkyrgan railway station) (Smailova 1980), Iran (Rezwani et al. 1994). Smailova (1980) indicates that two samples of M. (R.) medvedevi were collected from stems and pedicels of Helichrysum arenarium in Kazakhstan (Aktobe Region: near Aktobe and in Temir District, near Kalmakkyrgan railway station). Aphid colonies consisted of apterous viviparous females and immatures of 2 – 3 instars. However, Kadyrbekov in his summary on the fauna of aphids of Kazakhstan (2017) does not give this species for this territory, indicating that only two species have been found in Kazakhstan — M. (R.) janckei and M. (R.) hillerislambersi. Thus, the presence of M. (R.) medvedevi in Kazakhstan remains doubtful."
        },
        {
          "description": "Description. Apterous viviparous female. Body elongate elliptical, 1.6 – 2.0 times as long as wide. The living specimens reddish yellow, with a large black patch on dorsum of abdomen (this patch is absent in macerated specimens), with dark head, antennae, legs (except bases of femora), siphunculi and cauda; with distinct waxy pulverulence, in this case, the aphids are gray with brown-red streaks. Cleared specimens with dark brown front, antennae (except base of 3 rd antennal segment), distal half of the rostrum, legs (except base of femora) and siphunculi, with brown head (except front), sclerites at the base of the coxae, peritremes, anal plate and cauda, with light-brown bands and scleroites on thorax and abdomen and subgenital plate. Thorax with more or less wide bands on pro- and mesonotum and row of sclerites on metanotum; abdomen with rows of spinal sclerites, with small marginal sclerites and peritrems on I – VII segments, with antesiphuncular sclerites and with band on VIII tergite; sclerites on the thorax and abdomen are often small, pale and rare; sclerites on VII tergite often and on metanotum sometimes fused to form a short band. Surface of head, thoracic dorsum and abdominal tergites I – V smooth, sometimes weakly wrinkled, on VI – VII abdominal tergites with rows of small pointed spinules, which on VIII abdominal tergite partially fuse to form scales; thoracic venter smooth, ventral abdomen with long rows of small hardly visible spinules, sometimes forming strongly elongate cells. Setae on head, thorax and dorsum long, finely pointed, often bifurcating at the apices, in this case, each of the teeth of the fork is finely pointed. Third antennal segment with 11 – 30 secondary rhinaria, fourth segment with 0 – 4, fifth with 0 rhinaria. Rhinaria with internal diameter 6 – 23 μm, with external diameter 2.7 – 5.5 times as long as high of rhinaria. Setae on antennae blunt, pointed or rarely very weakly capitate. Rostrum is often very long, reaching abdominal segment III – V. Ultimate rostral segment 5.1 – 8.2 times as long as its basal width. Setae on legs pointed or finely pointed. Peritremes on abdominal segments I and II separated by a distance equal to or less than diameter of peritreme. Siphunculi with polygonal reticulation on distal 0.33 – 0.53 of length (largest transverse row in reticulate part of siphunculi consisting of 4 – 7 cells). Subgenital and anal plates with finely pointed setae. Cauda nearly triangular, with some constriction in the middle, which divides it into broad base and conical and rounded on apex distal part; setae on cauda long and finely pointed. Alate viviparous female. Body elongate elliptical, 2.1 – 2.5 times as long as wide. The living specimens with dark head and thorax. Cleared specimens with dark brown thorax; abdomen with distinct brown marginal sclerites on segments I – VII, spinal sclerites on abdominal tergites I – VI very small, light-brown or often absent, antesiphuncular sclerites hardly visible. Third antennal segment with 22 – 32 secondary rhinaria, fourth segment with 2 – 11, fifth with 0 – 1 rhinaria. Rostrum is often very long, reaching abdominal segment II – V. Peritremes on abdominal segments I and II separated by a distance less than diameter of peritreme or fused. Siphunculi with polygonal reticulation on distal 0.48 – 0.60 of length. Male. Body elongate elliptical, 2.0 times as long as wide. Colour of living specimens unknown. Tibiae of all legs dark brown only on the apices and brown in the middle. Marginal sclerites on I – VII segments distinct and sometimes relatively large. Third antennal segment with 33 – 37 secondary rhinaria, 4 th segment with 9 – 11 and 5 th segment with 4 – 5 secondary rhinaria. Siphunculi with polygonal reticulation on distal 0.35 – 0.46 of length. Cauda escuteon-shaped (misshapen specimen?). Hind tibiae with 1 – 3 round or oval pheromone plates. Oviparous female. Body 1.7 – 2.1 times as long as wide. Colour of living specimens unknown. Tibiae of all legs dark brown only on the apices and brown or light-brown in the middle. Marginal sclerites on abdomen absent, spinal sclerites on abdominal tergites I – VI often small or also absent. Third antennal segment with 8 – 23 secondary rhinaria, fourth and fifth segments with 0 rhinaria. Rostrum reaching abdominal segment III – IV. Siphunculi with polygonal reticulation on distal 0.34 – 0.48 of length (largest transverse row in reticulate part of siphunculi consisting of 4 – 6 cells). Cauda nearly triangular, sometimes with very weak constriction in the middle. Hind tibiae more or less distinctly swollen on basal half, with 27 – 55 round or oval pheromone plates, more of them located on basal half. Systematic relationships. The species is very close to Macrosiphoniella (Ramitrichophorus) janckei Börner, 1939. The differences between them are given in the keys."
        },
        {
          "description": "(Figs. 3, 42 – 63, Tabl. 4 – 5)"
        },
        {
          "description": "Biology. The species lives on stems, inflorescences and the lower surface of leaves of Helichrysum arenarium (L.) Moench, always attended by ants (Szelegiewicz 1958 a, 1958 b, 1967; Huculak 1965; Czylok et al. 1982), including Formica cinerea Mayr. (Szelegiewicz 1958 a). Apterous male and oviparous females of M. (R.) medvedevi were found in Poland (Kuyavian-Pomeranian Voivodeship, Bydgoszcz) by Szelegiewicz on 20. ix. 1962. Previously, another species — Macrosiphoniella nikolajevi Kadyrbekov, 1999 — was included in the subgenus Macrosiphoniella."
        }
      ],
      "vernacularNames": [],
      "higherClassificationMap": {
        "1": "Animalia",
        "54": "Arthropoda",
        "216": "Insecta",
        "809": "Hemiptera",
        "3042": "Aphididae",
        "2074940": "Macrosiphoniella"
      },
      "synonym": false,
      "class": "Insecta"
    },
    {
      "key": 4486873,
      "nameKey": 4594857,
      "datasetKey": "d7dddbf4-2cf0-4f39-9b2a-bb099caae36c",
      "constituentKey": "7ddf754f-d193-4cc9-b351-99906754a03b",
      "nubKey": 4486873,
      "parentKey": 2008323,
      "parent": "Gampsocoris",
      "kingdom": "Animalia",
      "phylum": "Arthropoda",
      "order": "Hemiptera",
      "family": "Berytidae",
      "genus": "Gampsocoris",
      "species": "Gampsocoris culicinus",
      "kingdomKey": 1,
      "phylumKey": 54,
      "classKey": 216,
      "orderKey": 809,
      "familyKey": 4306,
      "genusKey": 2008323,
      "speciesKey": 4486873,
      "scientificName": "Gampsocoris culicinus Seidenstücker, 1948",
      "canonicalName": "Gampsocoris culicinus",
      "authorship": "Seidenstücker, 1948",
      "publishedIn": "Seidenstücker, G. (1948) Eine neue europäische Heteropteren-Art: Gampsocoris culicinus n. sp. (Insecta, Hemiptera). Senckenbergiana., 29(1-6), 109–114.",
      "nameType": "SCIENTIFIC",
      "taxonomicStatus": "ACCEPTED",
      "rank": "SPECIES",
      "origin": "SOURCE",
      "numDescendants": 3,
      "numOccurrences": 0,
      "taxonID": "gbif:4486873",
      "extinct": false,
      "habitats": [
        "TERRESTRIAL"
      ],
      "nomenclaturalStatus": [],
      "threatStatuses": [],
      "descriptions": [
        {
          "description": "Terrestrial."
        },
        {
          "description": "Eastern Beskidy Mts: Przemyśl [FA 21], Spława n. Bircza [FA 10] – Smreczyński 1908. Eastern Sudetes Mts: Kłodzko [XR 18] – Smreczyński 1954. Lower Silesia: Wrocław, Leśnica [XS 36] – Scholtz 1847, Scholz 1931, Assmann 1854. Pomeranian Lake District: Szczecin [VV 71] – Schmidt 1928. Western Beskidy Mts: Niedźwiedź [DV 39] – Smreczyński 1906 a, Smreczyński 1910. „ Galicja ”: Nowicki 1864. Metatropini Henry, 1997"
        },
        {
          "description": "New records. the Eastern Beskid Mountains (Beskidy Wschodnie): EA 10: Libusza, geographical coordinates: 49 º 40 ' 43 \" N, 21 º 15 ' 54 \" E. A single individual, ♂ was captured 08 Aug 2013 at the edge of not mowed, overgrowing meadow, using sweep-net."
        },
        {
          "description": "Gampsocoris culicinus is adapted to habitats with various humidity and temperature. Observations indicate that it prefers shady and moist sites, such as the edges of forests and glades. However, reports from Ukraine and France suggest its recognition as a xerophilic species preferring dry and sunny slopes. This species can occur on many species of plants belonging to the families as diverse as: Lamiaceae, Boraginaceae, Scrophulariaceae, Fabaceae, Rosaceae, Caryophyllaceae and Asteraceae, most of which have glandular hairs (Péricart 1984). In Germany most often it has been found on Stachys sylvatica L."
        }
      ],
      "vernacularNames": [],
      "higherClassificationMap": {
        "1": "Animalia",
        "54": "Arthropoda",
        "216": "Insecta",
        "809": "Hemiptera",
        "4306": "Berytidae",
        "2008323": "Gampsocoris"
      },
      "synonym": false,
      "class": "Insecta"
    },
    {
      "key": 8777451,
      "nameKey": 12144785,
      "datasetKey": "d7dddbf4-2cf0-4f39-9b2a-bb099caae36c",
      "constituentKey": "7ddf754f-d193-4cc9-b351-99906754a03b",
      "nubKey": 8777451,
      "parentKey": 2074940,
      "parent": "Macrosiphoniella",
      "kingdom": "Animalia",
      "phylum": "Arthropoda",
      "order": "Hemiptera",
      "family": "Aphididae",
      "genus": "Macrosiphoniella",
      "species": "Macrosiphoniella janckei",
      "kingdomKey": 1,
      "phylumKey": 54,
      "classKey": 216,
      "orderKey": 809,
      "familyKey": 3042,
      "genusKey": 2074940,
      "speciesKey": 8777451,
      "scientificName": "Macrosiphoniella janckei Börner, 1939",
      "canonicalName": "Macrosiphoniella janckei",
      "authorship": "Börner, 1939",
      "publishedIn": "Börner, C. (1939) Neue Gattungen und Arten der mitteleuropäischen Aphidenfauna. 6(1), 75–83.",
      "nameType": "SCIENTIFIC",
      "taxonomicStatus": "ACCEPTED",
      "rank": "SPECIES",
      "origin": "SOURCE",
      "numDescendants": 0,
      "numOccurrences": 0,
      "taxonID": "gbif:8777451",
      "extinct": false,
      "habitats": [
        "TERRESTRIAL"
      ],
      "nomenclaturalStatus": [],
      "threatStatuses": [],
      "descriptions": [
        {
          "description": "Terrestrial."
        },
        {
          "description": "Material. Syntype: Macrosiphoniella (Ramitrichophorus) janckei Börner, 1939 — 3 apterous viviparous female, „ Helichrysum arenarium, Kolberg, Allemagne, Jancke leg., Macrosiphoniella janckei ” (from collections of MNHN and NHM). Additional materials: 3 apterous viviparous females, without date, Poland, West Pomeranian Voivodeship, Kołobrzeg County, Kołobrzeg (Kolberg), Helichrysum arenarium (from collections of IE BC CAS); 2 apterous viviparous females, 8. vi. 1954, Russia, Stavropol Krai, Stepnovsky District, Irgakly, Helichrysum sp., (from collections of NHM); 4 apterous viviparous females, 29. vi. 1960, Germany, Hesse, Darmstadt, Frankfurt am Main, Helichrysum arenarium (from collections of NHM); 3 apterous viviparous females, 10. viii. 1965, Poland, West Pomeranian Voivodeship, Kamień County, Międzyzdroje, Helichrysum arenarium (from collections of IE BC CAS); 15 apterous viviparous females, 03. vi. 1979, Moldova, Autonomous Territorial Unit of Gagauzia, Vill. Bugeac, Helichrysum arenarium (from collections of MNHN); 15 apterous viviparous females, 07. vii. 2004, Lithuania, Klaipėda County, Neringa, Vill. Pervalka, Helichrysum arenarium (from collections of IE BC CAS and ZIN RAS), 1 apterous viviparous female, 08. vii. 2004, Lithuania, Klaipėda County, Neringa, Nida, Helichrysum arenarium (from collections of IE BC CAS); 1 apterous viviparous female, 17. vii. 1996, Russia, Pskov Province, Nevel` District, near Dubokray Vill., Helichrysum arenarium (from collections of BSU); 1 apterous viviparous female, 14. vii. 2014, Belarus, Minsk Region, Maladzyechna District, near Udranka Vill., Helichrysum arenarium (from collections of BSU); 38 apterous viviparous females, 1 alate viviparous female, 16. vii. 2015, Belarus, Vitebsk Province, Gorodock District, near Zadrach`e Vill., Helichrysum arenarium (from collections of BSU); 57 apterous viviparous females, 1 oviparous female, 28. viii. 2016, Russia, Pskov Province, Nevel` District, near Dubokray Vill., Helichrysum arenarium (from collections of BSU); 18 apterous viviparous females, 30. viii. 2016, Russia, Pskov Province, Nevel` District, near Dubokray Vill., Helichrysum arenarium (from collections of BSU). Also used data from Börner (1939), Bozhko (1976), and Heie (1975)."
        },
        {
          "description": "Etymology. The species was named in honor of the famous German biologist Oldwig Jancke, who first collected the apterous viviparous females of this species."
        },
        {
          "description": "Distribution. Germany (Hesse, Darmstadt, Frankfurt am Main; Mecklenburg-Vorpommern: Mecklenburgische Seenplatte and Rostock, Laage) (Müller 1964, 1975; Szelegiewicz 1968), Poland (West Pomeranian Voivodeship: Kołobrzeg County, Kołobrzeg [Kolberg] and Kamień County, Międzyzdroje; Kuyavian-Pomeranian Voivodeship, Bydgoszcz) (Börner 1939, 1952; Szelegiewicz 1968, 1978; Nast et al. 1990; Węgierek & Wojciechowski 2004; Wrzesińska & Sawilska 2009; Osiadacz & Hałaj 2010), Lithuania (Klaipėda County, Neringa, Vill. Pervalka and Neringa, Nida) (Rakauskas et al. 2008, as Macrosiphoniella (Ramitrichophorus) janckei and M. (R.) hillerislambersi), Belarus (Minsk Region, Maladzyechna District, near Udranka Vill. (Buga & Stekolshchikov 2012), Moldova (Autonomous Territorial Unit of Gagauzia, Vill. Bugeac) (Vereshchagin et al. 1985; Andreev & Vereshchagin 1993 as Macrosiphoniella medvedevi), Ukraine (forest-steppe and steppe zones) (Bozhko 1963, 1976), Russia (Pskov Province, Nevel` District, near Dubokray Vill.; Stavropol Krai, Stepnovsky District, Irgakly), Kazakhstan (West Kazakhstan Region, Terekti District, east of Uralsk; Atyrau Region, Makhambet District, near Makhambet Vill. and Isatay District, near Isatai Vill.; Aktobe Region, Shalkar District, near Shalkar; Akmola Region, Birzhan sal District, east of Stepnyak; Karaganda Region, Ulytau District, south-west of Ulytau Vill.; Almaty Region, right bank of the river Ili) (Kadyrbekov 2003, 2017). Ivanovskaya (1977) records this species from the Altai Republic (Russia) on the basis of nine immature of the third instar collected on an unknown Asteraceae. On the basis of these data, many researchers in their later publications indicate Western Siberia as part of the area of this species. However, any reliable identification based on such material seems very doubtful and, therefore, there are no reliable data on the finding of this species in Western Siberia and Altai (see Stekolshchikov & Novgorodova 2015)."
        },
        {
          "description": "Description. Apterous viviparous female. Body elliptical or elongate elliptical, 1.5 – 2.0 times as long as wide. The living specimens from pale gray-olive to reddish brown or black, with green spots at siphuncular bases; waxpowdered except in the middle of the abdominal dorsum and along body margins, in wax-powder pale ash gray. Cleared specimens with dark brown antennae (except base of 3 rd antennal segment), distal half of the rostrum, legs (except base of femora) and siphunculi, with brown head, base of 3 rd antennal segment, sclerites at the base of the coxae, peritremes, anal and subgenital plates and cauda, with light-brown or rarely brown bands and scleroites on thorax and abdomen. Thorax with more or less wide bands on pro- and mesonotum and row of sclerites on metanotum; abdomen with rows of spinal sclerites, with small marginal sclerites and peritrems on I – VI segments, with antesiphuncular sclerites and with bands on VII – VIII tergites; sclerites on the thorax and abdomen are often small, pale and rare or, especially marginal sclerites, absent; sclerites on VII tergite almost always fused to form a short band. Surface of head, thoracic dorsum and abdominal tergites I – V smooth, sometimes weakly wrinkled, on VI – VII abdominal tergites with rows of small pointed spinules, which on VIII abdominal tergite partially fuse to form scales; thoracic venter smooth, ventral abdomen with long rows of small hardly visible spinules, sometimes forming strongly elongate cells. Setae on head, dorsal side of thorax and abdomen relatively long, with bifurcate or flabellate apices, on ventral side finely pointed. Third antennal segment with 10 – 30 secondary rhinaria, fourth segment with 0 – 4, fifth with 0 – 1 rhinaria. Rhinaria with internal diameter 6 – 30 μm, with external diameter 1.7 – 8.2 times as long as high of rhinaria. Setae on antennae blunt, bifurcate or apically flabellate. Rostrum is often very long, reaching abdominal segment III – V. Ultimate rostral segment 4.6 – 6.7 times as long as its basal width. Setae on legs blunt or bifurcate, rarely pointed, finely pointed or apically flabellate. Peritremes on abdominal segments I and II separated by a distance equal to or less than diameter of peritreme. Siphunculi with polygonal reticulation on distal 0.33 – 0.55 of length (largest transverse row in reticulate part of siphunculi consisting of 4 – 8 cells), distinctly imbricated, with short rows of pointed spinules at the base that fused into large scales in front of the reticular part. Subgenital and anal plate with finely pointed, bifurcate or weakly flabellate apically setae. Cauda nearly triangular, with some constriction in the middle, which weakly divides it into broad base and conical and rounded on apex distal part; setae on cauda long, finely pointed, bifurcate or weakly flabellate apically. Alate viviparous female. Body elongate elliptical, 2.2 times as long as wide. Colour of living specimen unknown. Cleared specimens with dark brown thorax; abdomen with distinct brown marginal sclerites on segments I – VII, spinal sclerites on abdominal tergites I – VI and antesiphuncular sclerites absent. Third antennal segment with 29 secondary rhinaria, 4 th segment with 7 – 8 and 5 th segment with 1 secondary rhinaria. Rostrum reaching abdominal segment I. Peritremes on abdominal segments I and II separated by a distance less than diameter of peritreme or fused. Male. Apterous (Müller 1975). Oviparous female. Body 1.8 times as long as wide. Colour of living specimen unknown. Tibiae of all legs dark brown only on the apices and brown or light-brown in the middle. Spinal sclerites on abdominal tergites I – VI, marginal sclerites on all abdominal segments, antesiphuncular sclerites, and band on abdominal tergite VII absent. Setae on head, dorsal side of thorax and abdomen not only with bifurcate or flabellate, but also with blunt or weakly capitate apices; setae on abdominal tergite VIII with blunt, bifurcate or weakly capitate apices. Third antennal segment with 11 – 12 secondary rhinaria, fourth and fifth segments with 0 rhinaria. Setae on legs blunt, pointed or finely pointed. Subgenital and anal plate with finely pointed or bifurcate setae. Cauda triangular, without constriction in the middle. Hind tibiae weakly swollen on basal half, with 23 – 27 round or oval pheromone plates, more of them located on basal half. Systematic relationships. The species is very close to Macrosiphoniella (Ramitrichophorus) medvedevi (Bozhko, 1950). The differences between them are given in the keys."
        },
        {
          "description": "(Figs. 2, 25 – 41, Tabl. 3)"
        },
        {
          "description": "Biology. The species lives on stems, inflorescences and the lower surface of leaves of Helichrysum arenarium (L.) Moench, actively attended by ants (Szelegiewicz 1968, Bozhko 1976, Kadyrbekov 2003, Buga & Stekolshchikov 2012). This species has never been observed on other species of the genus Helichrysum or plants of other genera. Colonies of these aphids in Belarus and the Pskov Province of Russia were always collected from beneath the inflorescences and from stems of H. arenarium. All these colonies were attended by ants Formica cinerea Mayr. Apterous males and oviparous females of M. (R.) janckei were found in Germany (Rostock, Laage) by Müller (1975) on 28. ix. 1970, and a single oviparous female only was found together with apterous viviparous females in Russia (Pskov Province, Nevel` District, near Dubokray Vill.) in August 2016."
        }
      ],
      "vernacularNames": [],
      "higherClassificationMap": {
        "1": "Animalia",
        "54": "Arthropoda",
        "216": "Insecta",
        "809": "Hemiptera",
        "3042": "Aphididae",
        "2074940": "Macrosiphoniella"
      },
      "synonym": false,
      "class": "Insecta"
    },
    {
      "key": 4452387,
      "nameKey": 2617891,
      "datasetKey": "d7dddbf4-2cf0-4f39-9b2a-bb099caae36c",
      "constituentKey": "2d59e5db-57ad-41ff-97d6-11f5fb264527",
      "nubKey": 4452387,
      "parentKey": 8851168,
      "parent": "Clitostethus",
      "basionymKey": 6993436,
      "basionym": "Coccinella arcuata Rossi, 1794",
      "kingdom": "Animalia",
      "phylum": "Arthropoda",
      "order": "Coleoptera",
      "family": "Coccinellidae",
      "genus": "Clitostethus",
      "species": "Clitostethus arcuatus",
      "kingdomKey": 1,
      "phylumKey": 54,
      "classKey": 216,
      "orderKey": 1470,
      "familyKey": 7782,
      "genusKey": 8851168,
      "speciesKey": 4452387,
      "scientificName": "Clitostethus arcuatus (Rossi, 1794)",
      "canonicalName": "Clitostethus arcuatus",
      "authorship": "(Rossi, 1794) ",
      "nameType": "SCIENTIFIC",
      "taxonomicStatus": "ACCEPTED",
      "rank": "SPECIES",
      "origin": "SOURCE",
      "numDescendants": 14,
      "numOccurrences": 0,
      "taxonID": "gbif:4452387",
      "extinct": false,
      "habitats": [
        "TERRESTRIAL"
      ],
      "nomenclaturalStatus": [],
      "threatStatuses": [
        "NOT_EVALUATED",
        "NOT_EVALUATED"
      ],
      "descriptions": [
        {
          "description": "Material examined. Total of 25 specimens collected mostly from Punica granatum, N. oleander and Bougainvillea sp. at 7 localities: Barranco de las Penitas (05. VIII. 2017), Betancuria (25. III. 2017), Caleta de Fuste (13. II. 2017), Costa Calma (09. II. 2017, 21. III. 2017, 27. III. 2017), El Pinar (25. III. 2017), Pajara (12. VIII. 2017) and Vega de Rio Palmas (25. III. 2017). Distribution. Widely distributed in the Palearctic region (Kovář 2007). New to Fuerteventura. Previously re- ported from Tenerife, Gomera and La Palma (Eizaguirre 2007)."
        },
        {
          "description": "Materials examined. Asir: Ahd Rifidh, 18 ° 06.33 ' N, 42 ° 53.82 ' E, 16. I. 2013, BS, Al Ansi, A., 1 ex."
        },
        {
          "description": "World distribution. Asia: IN, IQ, SY, and TR; Europe: AL, AR, AU, AZ, BH, CR, CZ, FR, GB, GE, GG, GR, HU, IT, NL, RO, SK, ST, SZ, UK, and YU; North Africa: CI, and MR; AFR and NAR (Kovar 2007); new record for SA."
        },
        {
          "description": "Local distribution. This is a newly recorded genus from Saudi Arabia; it was collected from Asir province."
        },
        {
          "description": "Diagnosis. Body is dark brown to black, covered with rather long, whitish hairs; head is black; pronotum is whitish, at its middle with several black spots; elytra black or brown, with two arched concentric horseshoe-shaped lines, crossing the suture with their posterior part."
        },
        {
          "description": "Material: Gdańsk Przymorze, Ronald Reagan Park (CF 43), 1 ex. shaken down from bird cherry (Prunus padus), 29 Apr 2016, leg. JR."
        },
        {
          "description": "This south European species was reported more than a century ago from Legnica in Lower Silesia (Letzner 1874) and Ojców in Kraków-Wieluń Upland (Eichler 1914), and recently from Upper Silesia (Królik 2006, Greń et al. 2013), Wielkopolska- Kujawy Lowland (Ruta et al. 2009), Pomeranian Lake District (Ceryngier et al. 2016 b) and Mazovian Lowland (Bodzon & Ceryngier 2016, Ceryngier et al. 2016 c). Its current range expansion and increase in numbers can probably be attributed to climate change."
        }
      ],
      "vernacularNames": [
        {
          "vernacularName": "Ladybird beetle",
          "language": "eng"
        },
        {
          "vernacularName": "Omegamariehøne",
          "language": "dan"
        },
        {
          "vernacularName": "Boogvlekkapoentje",
          "language": "nld"
        },
        {
          "vernacularName": "eføymarihøne",
          "language": "nob"
        }
      ],
      "higherClassificationMap": {
        "1": "Animalia",
        "54": "Arthropoda",
        "216": "Insecta",
        "1470": "Coleoptera",
        "7782": "Coccinellidae",
        "8851168": "Clitostethus"
      },
      "synonym": false,
      "class": "Insecta"
    },
    {
      "key": 4486878,
      "nameKey": 6944321,
      "datasetKey": "d7dddbf4-2cf0-4f39-9b2a-bb099caae36c",
      "constituentKey": "7ddf754f-d193-4cc9-b351-99906754a03b",
      "nubKey": 4486878,
      "parentKey": 4486877,
      "parent": "Metatropis",
      "basionymKey": 4486879,
      "basionym": "Berytus rufescens Herrich-Schaeffer, 1835",
      "kingdom": "Animalia",
      "phylum": "Arthropoda",
      "order": "Hemiptera",
      "family": "Berytidae",
      "genus": "Metatropis",
      "species": "Metatropis rufescens",
      "kingdomKey": 1,
      "phylumKey": 54,
      "classKey": 216,
      "orderKey": 809,
      "familyKey": 4306,
      "genusKey": 4486877,
      "speciesKey": 4486878,
      "scientificName": "Metatropis rufescens (Herrich-Schaeffer, 1835)",
      "canonicalName": "Metatropis rufescens",
      "authorship": "(Herrich-Schaeffer, 1835) ",
      "publishedIn": "Herrich-Schaeffer, G.H.W. (1835) Nomenclator entomologicus--Verzeichniss der Europaishen Insecten: zur erleichterung des Tausch-verkehrs mit Preisen versehen. I. Lepidoptera & Hemiptera. Nomenclator entomologicus--Verzeichniss der Europaishen Insecten: zur erleichterung des Tausch-verkehrs mit Preisen versehen. I. Lepidoptera & Hemiptera. Regensburg: Friedrich Pustet.",
      "nameType": "SCIENTIFIC",
      "taxonomicStatus": "ACCEPTED",
      "rank": "SPECIES",
      "origin": "SOURCE",
      "numDescendants": 1,
      "numOccurrences": 0,
      "taxonID": "gbif:4486878",
      "extinct": false,
      "habitats": [
        "TERRESTRIAL"
      ],
      "nomenclaturalStatus": [],
      "threatStatuses": [
        "NOT_EVALUATED",
        "LEAST_CONCERN"
      ],
      "descriptions": [
        {
          "description": "Beskid Zachodni: Brenna [CA 50]: 9.08.2020, leg. RŻ, det. GG; Wyżyna Krakowsko- Wieluńska: Przybysławice [DA 26]: 11.10.2020, leg. PŁ."
        },
        {
          "description": "univoltine"
        },
        {
          "description": "oligophagous"
        },
        {
          "description": "oligophagous"
        },
        {
          "description": "herbivore"
        },
        {
          "description": "herbivore"
        },
        {
          "description": "1"
        },
        {
          "description": "1"
        },
        {
          "description": "0"
        },
        {
          "description": "0"
        },
        {
          "description": "0"
        },
        {
          "description": "0"
        },
        {
          "description": "0"
        },
        {
          "description": "0"
        },
        {
          "description": "0"
        },
        {
          "description": "0"
        },
        {
          "description": "0"
        },
        {
          "description": "Terrestrial."
        },
        {
          "description": "Bionomics: Hygrophilous; skiophilous; oligophagous (Circaea spp., Linnaea borealis); one generation a year. Remarks: Formerly considered a rare species in Poland (Hebda 1998, Gorczyca 2004), however in recent years, this species is regularly recorded in our country, as well as throughout Central Europe (Špryňar & Kment, Taszakowski & Gorczyca 2018). In Orzechowski & Wasielewski 2016 the UTM square was incorrectly specified (correct is WT 28). Distribution in Poland (Fig. 10): Baltic Coast: * Szklana Huta [XA 87] – 1 ex., 26 Aug 2008, leg. M. W. Kozłowski. Białowieża Forest: Białowieski NP [FD 94] – Strawiński 1956 b, Hebda 2011; Białowieża [FD 94] – Smreczyński 1954. Eastern Beskidy Mts: Bednarka [EA 20, EV 29] – Taszakowski & Gorczyca 2018; upper Ropa River val. [EV 17] – Taszakowski 2012; Lisów [EA 21] – Taszakowski & Gorczyca 2018. Eastern Sudetes Mts: Rozumice [YR 14] – Hebda & Kocorek 2012. Krakowsko- Wieluńska Upland: Chełmowa Mt. [DA 16] – Chłond & Gorczyca 2009. Lower Silesia: general – Lancke & Polentz 1942; Górażdże [BB 80] – Hohol-Kilinkiewicz & Czaja 2006; * Oława [XS 64] – 22 May 2014, 1 ex., leg. W. T. Szczepański (DZUS). Lubelska Upland: Bachus Res. [FB 68] – Cmoluchowa & Lechowski 1990, Dziedzic & Łętowski 2002; Sawin [FB 68] – Cmoluchowa & Lechowski 1992. Małopolska Upland: * Łódź, Łagiewniki forest [CC 94] – 23 May 1997, 1 ex., leg. R. Dobosz (USMB). Pomeranian Lake District: Bielinek over Odra River Res. [VU 46] – Lis B. 2010; Słupsk [XA 33] – Karl 1935. Roztocze Upland: Jarugi Res. [FB 41] – Cmoluchowa & Lechowski 1994; Frampol [FB 11] – Lechowski & Smardzewska-Gruszczak 1996; Nart Res. [FB 40], Stokowa Mt. [FB 40], Tarnawa [FB 13] – Cmoluchowa & Lechowski 1994; Paary [FA 68] – Strawiński 1959 c; Bukowa Góra Res. [FB 30] – Cmoluchowa & Lechowski 1994, Strawiński 1964; Susiec [FA 58] – Strawiński 1959 a. Świętokrzyskie Mts: Łysa Góra Mt. [EB 03] – Strawiński 1962. Upper Silesia: Segiecki forest [CA 48] – Hebda 1998; * Segiet Res. [CA 48] – 11 May 2009, 2 exx., 23 May 2010, 1 ex., leg. R. Dobosz (USMB), 11 Jul 2002, 7 exx., 1 Aug 2002, 5 exx., 21 Aug 2002, 1 ex., 1 Sep 2002, 1 ex., 11 Sep 2002, 1 ex., leg. A. Nosol (DBUO); * Zabrze [CA 37] – 12 Jul 2012, 1 ex., leg. M. Obrzut (DZUS). Western Beskidy Mts: * Cieszyn [CA 21] – 22 Aug 2006, 1 ex., leg. J. Spandel (DBUO); Stary Groń Mts. [CA 50] – Matuszczyk & Taszakowski 2017. Wielkopolsko- Kujawska Lowland: * Gościm, Solecko lake [WU 54] – 1 ex, 3 Jun 2014, leg. R. Orzechowski; * Gryżyna, ad Gryżyńskie lake [WT 18] – 1 ex., 2 – 4 Jun 2016, leg. M. Bunalski; * Krępa [WT 36] – 1 ex., 16 Sep 2016, leg. R. Orzechowski; * Łęgi Słubickie [VT 79] – 1 ex., 6 Sep 2016, 1 ex., 24 Oct 2016, leg. M. Adamski; * Mniszki [WU 61] – 1 ex., 8 Sep 2016, leg. R. Orzechowski; Węgrzynice [WT 28] – Orzechowski & Wasielewski 2016. „ Pomerania ”: Stichel 1926."
        }
      ],
      "vernacularNames": [
        {
          "vernacularName": "Steffensurttæge",
          "language": "dan"
        },
        {
          "vernacularName": "Heksenkruidsteltwants",
          "language": "nld"
        },
        {
          "vernacularName": "Hexenkraut-Wanze",
          "language": "deu"
        },
        {
          "vernacularName": "skogstyltetege",
          "language": "nno"
        },
        {
          "vernacularName": "skogstyltetege",
          "language": "nob"
        },
        {
          "vernacularName": "vanamolude",
          "language": "fin"
        }
      ],
      "higherClassificationMap": {
        "1": "Animalia",
        "54": "Arthropoda",
        "216": "Insecta",
        "809": "Hemiptera",
        "4306": "Berytidae",
        "4486877": "Metatropis"
      },
      "synonym": false,
      "class": "Insecta"
    },
    {
      "key": 11128959,
      "nameKey": 62196491,
      "datasetKey": "d7dddbf4-2cf0-4f39-9b2a-bb099caae36c",
      "constituentKey": "7ddf754f-d193-4cc9-b351-99906754a03b",
      "nubKey": 11128959,
      "parentKey": 1031505,
      "parent": "Liposcelis",
      "kingdom": "Animalia",
      "phylum": "Arthropoda",
      "order": "Psocodea",
      "family": "Liposcelididae",
      "genus": "Liposcelis",
      "species": "Liposcelis aleksandrowiczi",
      "kingdomKey": 1,
      "phylumKey": 54,
      "classKey": 216,
      "orderKey": 7612838,
      "familyKey": 4379,
      "genusKey": 1031505,
      "speciesKey": 11128959,
      "scientificName": "Liposcelis aleksandrowiczi Georgiev, Ostrovsky & Lienhard, 2020",
      "canonicalName": "Liposcelis aleksandrowiczi",
      "authorship": "Georgiev, Ostrovsky & Lienhard, 2020",
      "publishedIn": "Georgiev, D., Ostrovsky, A. & Lienhard, C. (2020) A population growth model for Liposcelis entomophila (Enderlein) (Psocoptera: Liposcelididae). 29, 41–46.",
      "nameType": "SCIENTIFIC",
      "taxonomicStatus": "ACCEPTED",
      "rank": "SPECIES",
      "origin": "SOURCE",
      "numDescendants": 0,
      "numOccurrences": 0,
      "taxonID": "gbif:11128959",
      "extinct": false,
      "habitats": [
        "TERRESTRIAL"
      ],
      "nomenclaturalStatus": [],
      "threatStatuses": [],
      "descriptions": [
        {
          "description": "Material examined: Holotype 1 ♀, slide- mounted (MHNG): BELARUS, Gomel area, Gomel district, roadside of the railway embankment East of the horticultural partnership “ Lisichki ”, in the nest of Formica pratensis Retz., in sparse growth dominated by Populus tremula, Betula pendula and Quercus robur, 52 ° 22 ' 41 \" N, 31 ° 04 ' 22 \" E, 128 m a. s. l., 13.10.2019, leg. A. Ostrovsky. Paratypes, same data as holotype: 31 ♀, 7 ♂, one of them allotype mounted on same slide as holotype (MHNG), 5 ♀, 2 ♂ (coll. A. Ostrovsky), 3 ♀, 1 ♂ (coll. D. Georgiev)."
        },
        {
          "description": "Etymology: The species is named in honor of Prof. Dr. Hab. Oleg Aleksandrowicz, Institute of Biology and Earth Sciences, Pomeranian University in Słupsk, Poland."
        },
        {
          "description": "Diagnosis (based on females): Very similar to Liposcelis ornata Mockford in body color and general morphology (see Mockford, 1978). Differing from L. ornata by the presence of a brown patch laterally on tg 6 (tg 6 unpigmented in L. ornata) and by the often almost completely brown tg 7 and tg 8 (only laterally brown in L. ornata). Large brown transversal band in anterior half of abdomen covering posterior half of tg 3 and most of tg 4 in the new species, covering most of tg 3 and tg 4 in L. ornata. The latter having always 3 long PNS (each of them at least 2 / 3 length of SI, Fig. 3 E), while the 2 - 3 PNS in the new species are much shorter (at most 1 / 2 length of SI, Fig. 3 CD). Pilosity on vertex less dense in the new species than in L. ornata, in which the hairs are 1 - 2 x as long as the distance between their alveoli, Fig. 3 F)."
        },
        {
          "description": "Description: Female. Coloration. Body whitish to light yellowish-brown with a complex reddish-brown color pattern (Fig. 2 A): postclypeus medium brown, vertex with Y-shaped brown marking with stem along the middle line; lateral lobe of pronotum brown, synthorax brown laterally, pale in the middle; abdomen with an irregular transverse brown pigmentation on posterior half of tg 3 (tergite 3) and on tg 4, extending laterally into anterior half of tg 5; tg 6 with brown patches laterally; tg 7 and tg 8 often almost completely brown, usually somewhat paler in the middle; tg 9 and tg 10 with a small brown patch laterally, pale in the middle. Morphology. Belonging to section I, group A (see Lienhard 1990, 1998): Abdominal tg 3 and tg 4 lacking posterior delimitation by intersegmental membrane; lateral lobe of pronotum, in addition to the long humeral seta (SI), with a row of 2 - 3 apically truncated pronotal setae (PNS) situated towards anterior margin. PNS relatively short, at most 1 / 2 length of SI (Fig. 3 CD). Compound eye with 8 ommatidia (Fig. 3 A). Vertex not densely pilose (hairs in average only about half as long as distance between their alveoli, Figs 2 B, 3 B), its surface sculpture with more or less spindle-shaped transverse areoles bearing small tubercles, the latter smaller than the alveoli of the hairs (Fig. 2 B). 5 - 6 long apically truncated setae in anterior half of prosternum and 8 - 10 such setae along anterior margin of mesosternum. Abdominal marginal setae M 8, Md 9, Mv 9, Md 10, Mv 10 and discal setae D of tg 10 well differentiated; Md 10, Mv 10 and Mv 9 of about same length, but Md 9 somewhat shorter; epiproctal setae Se straight, apically truncated, not longer than abdominal marginal setae. Abdominal tergites not densely pilose, with distinct tubercles but lacking well defined areoles (Fig. 2 C). Male. Much smaller than female, but body pigmentation, general pilosity, surface sculpture and chaetotaxy essentially as in female. Compound eye with 5 ommatidia. 4 prosternal setae, 7 mesosternal setae. Phallosome typical for the genus (Lienhard, 1990, 1998). Measurements: Body length (slide-mounted): female holotype 1.3 mm; male allotype 0.9 mm."
        }
      ],
      "vernacularNames": [],
      "higherClassificationMap": {
        "1": "Animalia",
        "54": "Arthropoda",
        "216": "Insecta",
        "4379": "Liposcelididae",
        "1031505": "Liposcelis",
        "7612838": "Psocodea"
      },
      "synonym": false,
      "class": "Insecta"
    },
    {
      "key": 2008320,
      "nameKey": 1446040,
      "datasetKey": "d7dddbf4-2cf0-4f39-9b2a-bb099caae36c",
      "constituentKey": "7ddf754f-d193-4cc9-b351-99906754a03b",
      "nubKey": 2008320,
      "parentKey": 2008319,
      "parent": "Berytinus",
      "basionymKey": 2008321,
      "basionym": "Cimex clavipes Fabricius, 1775",
      "kingdom": "Animalia",
      "phylum": "Arthropoda",
      "order": "Hemiptera",
      "family": "Berytidae",
      "genus": "Berytinus",
      "species": "Berytinus clavipes",
      "kingdomKey": 1,
      "phylumKey": 54,
      "classKey": 216,
      "orderKey": 809,
      "familyKey": 4306,
      "genusKey": 2008319,
      "speciesKey": 2008320,
      "scientificName": "Berytinus clavipes (Fabricius, 1775)",
      "canonicalName": "Berytinus clavipes",
      "authorship": "(Fabricius, 1775) ",
      "publishedIn": "Fabricius, J.C. (1775) Systema entomologiae, sistens insectorum classes, ordines, genera, species, adjectis synonymis, locis, descriptionibus, observationibus. Systema entomologiae. Flensburgi et Lipsiae: Korte, xxvii + 832 pp. Available from http://www.biodiversitylibrary.org/page/25552081",
      "nameType": "SCIENTIFIC",
      "taxonomicStatus": "ACCEPTED",
      "rank": "SPECIES",
      "origin": "SOURCE",
      "numDescendants": 2,
      "numOccurrences": 0,
      "taxonID": "gbif:2008320",
      "extinct": false,
      "habitats": [
        "TERRESTRIAL"
      ],
      "nomenclaturalStatus": [],
      "threatStatuses": [
        "NOT_EVALUATED",
        "VULNERABLE",
        "LEAST_CONCERN"
      ],
      "descriptions": [
        {
          "description": "MATERIAL. 7.5 km W of Kolyvan village, Loktevka river basin, H = 417 m, 1. VI. 2020, 3 ♀; Vicinity of Sentelek village, 5 km SW of Mashenka village, Charysh river basin, H = 625 m, 30. V. 2020, 1 ♂."
        },
        {
          "description": "DISTRIBUTION. Trans-Euroasian. Recorded from Altai Krai [Kanukova, Vinokurov, 2009 a; Knyshov, Namyatova, 2010]."
        },
        {
          "description": "Beskid Zachodni: Dubne [DV 96]: 4.05.2001, leg. AM; Stryszawa, Opaczne [CA 90]: 16.05.2020, leg. GG."
        },
        {
          "description": "Material examined. Golestan Province: Golestan National Park: Ghareh-Ghashli (1825 m), 1 Ƥ, 1 ♂, September 2006. New record for Iran. General distribution. Euro-Siberian, known from Transcaucasia."
        },
        {
          "description": "Kras, 14 Aug 2007, 1 ex.; 18 Aug 2008, 1 ex. Marcelowy Ravine, 22 Jun 2008, 1 ex. Kotłowy Stream, 15 Jun 2006, 1 ex.; 15 Aug 2006, 1 ex. Podłaźce Clearing, 27 Jun 2007, 1 ex.; 17 Jun 2006, 1 ex.; 19 Aug 2006, 1 ex."
        },
        {
          "description": "МатериаΛ. Разнотравный сухоΑоΛьный Λуг, 30.08.1980 — 2 экз. (Т. Стенченко); разнотравный сухоΑоΛьный Λуг, 03.07.1981 — 1 экз. (Т. Стенченко); поΛяна березово-еΛового Λеса на берегу р. ÀуΑка, 21 – 28.07.2017 — 1 экз., 24.06 – 01.07.2011 — 1 экз."
        },
        {
          "description": "Распространение. ТранспаΛеарктический виΑ."
        },
        {
          "description": "univoltine"
        },
        {
          "description": "oligophagous"
        },
        {
          "description": "oligophagous"
        },
        {
          "description": "herbivore"
        },
        {
          "description": "herbivore"
        },
        {
          "description": "1"
        },
        {
          "description": "1"
        },
        {
          "description": "0"
        },
        {
          "description": "0"
        },
        {
          "description": "0"
        },
        {
          "description": "0"
        },
        {
          "description": "0"
        },
        {
          "description": "0"
        },
        {
          "description": "0"
        },
        {
          "description": "0"
        },
        {
          "description": "0"
        },
        {
          "description": "Terrestrial."
        },
        {
          "description": "Biono mics: Mesophilous; oligophagous, mainly on Ononis spp.; one generation (possible two) a year. R e m a r k s: Common and widely distributed in Poland. D i s t r i b u t i o n i n P o l a n d (Fig. 2). Baltic Coast: * Czajcze n. Mielno [WA 71] – 18 Aug 1996, 2 exx., leg. B. & J. A. Lis (DBUO); Słowiński NP [XA 46] – Korcz 2003. Białowieża Forest: Białowieża [FD 94] – Strawiński 1956 b. Eastern Beskidy Mts: Bednarka [EA 20, EV 29], Blechnarka [EV 17], Dobrynia [EV 39], Gładyszów [EV 18], Jaśliska [EV 57], Krempna [EV 38] – Taszakowski & Gorczyca 2018; Krościenko [FV 28] – Smreczyński 1906 b; Libusza [EA 10], Lipinki [EA 20] – Taszakowski & Gorczyca 2018; Przemyśl [FA 21] – Kotula 1890; Wysowa- Zdrój [EV 17] – Taszakowski & Gorczyca 2018. Eastern Sudetes Mts: * Gipsowa Góra Res. [YR 14] – 8 Sep 1932, 10 exx., leg. H. Nowotny (USMB). Krakowsko- Wieluńska Upland: Kraków, Błonia [DA 24] – Stobiecki 1886; Kraków, Dębniki [DA 14] – Stobiecki 1886; Kraków, Krzemionki [DA 14] – Smreczyński 1906 b; Kraków, Panieńskie Skały [DA 14] – Stobiecki 1886; Kraków, Sikornik [DA 14] – Stobiecki 1886; * Olsztyn [CA 98] – 1 Aug 1999, 2 exx, 26 Jan 1999, 1 ex., leg. A. Pańczyk (DBUO); Zabierzów [DA 15] – Stobiecki 1886. Lower Silesia: Kopalina [XS 84] – Scholz 1931; Śliwice [XR 59] – Assmann 1854; Wrocław, Karłowice [XS 46] – Scholtz 1847, Assmann 1854, Scholz 1931; Wrocław, Popowice [XS 36] – Assmann 1854, Scholz 1931; Wrocław, Rędzin [XS 37] – Scholz 1931; Wrocław, Swojczyce [XS 46] – Scholtz 1847, Assmann 1854. Lubelska Upland: Gródek [GB 03] – Strawiński 1959 b; Janów Lubelski [EB 91] – Piasecka 1960; Michałówka [EB 69] – Strawiński 1957 b; Bagno Serebryskie Res. [FB 77] – Lechowski & Smardzewska-Gruszczak 2004; Brzeźno Res. [FB 87] – Smardzewska-Gruszczak & Lechowski 2006; Zawadówka Res. [FB 66] – Smardzewska-Gruszczak & Lechowski 2000; Ruda Czechowska [EB 69] – Strawiński 1963; Wólka Gołębska [EC 60] – Strawiński 1963. Małopolska Upland: Sielec [DA 39] – Fedorko 1959. Mazurian Lake District: Olsztyn, Posorty [DE 65] – Mikołajski 1962 c, 1962 d. Pieniny Mts: Biała Skała [DV 57] – Hebda & Ścibior 2016; Kras [DV 67] – Taszakowski & Pasińska 2017; Krościenko by the Dunajec River [DV 57] – Smreczyński 1954; Pieniny, general [DV 57] – Smreczyński 1954, Taszakowski & Pasińska 2017. Pomeranian Lake District: Szczecin [VV 71] – Dohrn 1860. Roztocze Upland: Biała Góra n. Tomaszów Lubelski [FA 79] – Cmoluchowa & Lechowski 1994; Kosobudy [FB 41] – Strawiński 1956 a; Łabunie [FB 61] – Strawiński 1960; Tartaczna Góra Res. [FB 30], Strawiński 1966 b; Susiec [FA 58] – Strawiński 1959 a; Wólka Łosiniecka [FA 68] – Strawiński 1959 a; Zwierzyniec [FB 30] – Strawiński 1956 a. Sandomierska Lowland: Szklarnia Res. [FB 01] – Lechowski & Smardzewska-Gruszczak 1998. Tatry Mts: Kościeliska val. [DV 15] – Smreczyński 1954, Lis B. et al. 2004; Strążyska val. [DV 25] – Smreczyński 1954. Trzebnickie Hills: Oborniki Śląskie [XS 38] – Polentz 1943. Upper Silesia: * Będzin [CA 67] – 25 Jun 2008, 1 ex., leg. A. Kulis (DZUS); Bycina [CA 28] – Stobiecki 1886, Lis J. A. 1989, Lis J. A. & Lis B. 1998; Chełmek [CA 75] – Stobiecki 1886, Lis J. A. 1989, Lis J. A. & Lis B. 1998; Dąb [CA 75] – Stobiecki 1886, Lis J. A. 1989, Lis J. A. & Lis B. 1998; Lipowiec [CA 84] – Stobiecki 1886, Lis J. A. 1989, Lis J. A. & Lis B. 1998; * Piekary Śląskie [CA 58] – 23 May 2008, 1 ex., leg. M. Sikora (DZUS); Regulice [CA 94] – Smreczyński 1954; * Ruda Śląska [CA 46] – 9 Aug 2008, 1 ex., leg. L. Jezuit (DZUS); * Tychy [CA 55] – 26 Mar 2007, 2 exx., leg. D. Nawara (DZUS); Żarki [CA 84] – Stobiecki 1886, Lis J. A. 1989, Lis J. A. & Lis B. 1998. Western Beskidy Mts: Babia Góra Mt. [CV 99] – Lis B. et al. 2002, Celary 2003; Bieńkowice [DA 32] – Smreczyński 1906 b; Chełm n. Myślenice [DA 21] – Smreczyński 1954; * Cieszyn [CA 21] – 1 ex. (DZUS); Krzyszkowice [DA 22] – Smreczyński 1906 b; Łomnica [DV 87] – Smreczyński 1954; Niedźwiedź [DV 39] – Smreczyński 1910; Wieliczka [DA 33] – Stobiecki 1886. Wielkopolsko- Kujawska Lowland: Duninów [CD 92] – Strawiński 1965. “ Prussia ” – Siebold 1839. “ Silesia ” – Gravenhorts 1836, Schummel 1836. “ Western Galicja ” – Łomnicki 1882."
        }
      ],
      "vernacularNames": [
        {
          "vernacularName": "Stalkruidsteltwants",
          "language": "nld"
        },
        {
          "vernacularName": "engstyltetege",
          "language": "nno"
        },
        {
          "vernacularName": "engstyltetege",
          "language": "nob"
        },
        {
          "vernacularName": "vaaleatikkulude",
          "language": "fin"
        }
      ],
      "higherClassificationMap": {
        "1": "Animalia",
        "54": "Arthropoda",
        "216": "Insecta",
        "809": "Hemiptera",
        "4306": "Berytidae",
        "2008319": "Berytinus"
      },
      "synonym": false,
      "class": "Insecta"
    },
    {
      "key": 4486851,
      "nameKey": 1446067,
      "datasetKey": "d7dddbf4-2cf0-4f39-9b2a-bb099caae36c",
      "constituentKey": "7ddf754f-d193-4cc9-b351-99906754a03b",
      "nubKey": 4486851,
      "parentKey": 2008319,
      "parent": "Berytinus",
      "basionymKey": 4486852,
      "basionym": "Berytus crassipes Herrich-Schaeffer, 1835",
      "kingdom": "Animalia",
      "phylum": "Arthropoda",
      "order": "Hemiptera",
      "family": "Berytidae",
      "genus": "Berytinus",
      "species": "Berytinus crassipes",
      "kingdomKey": 1,
      "phylumKey": 54,
      "classKey": 216,
      "orderKey": 809,
      "familyKey": 4306,
      "genusKey": 2008319,
      "speciesKey": 4486851,
      "scientificName": "Berytinus crassipes (Herrich-Schaeffer, 1835)",
      "canonicalName": "Berytinus crassipes",
      "authorship": "(Herrich-Schaeffer, 1835) ",
      "publishedIn": "Herrich-Schaeffer, G.H.W. (1835) Nomenclator entomologicus--Verzeichniss der Europaishen Insecten: zur erleichterung des Tausch-verkehrs mit Preisen versehen. I. Lepidoptera & Hemiptera. Nomenclator entomologicus--Verzeichniss der Europaishen Insecten: zur erleichterung des Tausch-verkehrs mit Preisen versehen. I. Lepidoptera & Hemiptera. Regensburg: Friedrich Pustet.",
      "nameType": "SCIENTIFIC",
      "taxonomicStatus": "ACCEPTED",
      "rank": "SPECIES",
      "origin": "SOURCE",
      "numDescendants": 1,
      "numOccurrences": 0,
      "taxonID": "gbif:4486851",
      "extinct": false,
      "habitats": [
        "TERRESTRIAL"
      ],
      "nomenclaturalStatus": [],
      "threatStatuses": [
        "NOT_EVALUATED",
        "ENDANGERED",
        "LEAST_CONCERN"
      ],
      "descriptions": [
        {
          "description": "Podłaźce Clearing, 1 Jul 2007, 1 ex."
        },
        {
          "description": "МатериаΛ. МаΛиново-кипрейно-вейниковое сообщество, 14.06.2017 — 2 экз."
        },
        {
          "description": "Распространение. Европейско-сибирский виΑ."
        },
        {
          "description": "univoltine"
        },
        {
          "description": "oligophagous"
        },
        {
          "description": "oligophagous"
        },
        {
          "description": "herbivore"
        },
        {
          "description": "herbivore"
        },
        {
          "description": "1"
        },
        {
          "description": "1"
        },
        {
          "description": "0"
        },
        {
          "description": "0"
        },
        {
          "description": "0"
        },
        {
          "description": "0"
        },
        {
          "description": "0"
        },
        {
          "description": "0"
        },
        {
          "description": "0"
        },
        {
          "description": "0"
        },
        {
          "description": "0"
        },
        {
          "description": "Terrestrial."
        },
        {
          "description": "Bionomics: Mesophilous; oligophagous (mainly Caryophyllaceae); one generation a year. Remarks: Common and probably widely distributed in Poland. Distribution in Poland (Fig. 5): Baltic Coast: Chłapowo [CF 37] – Smreczyński 1954; Gdynia [CF 44] – Lis B. & Kowalczyk 2017. Eastern Beskidy Mts: Prałkowce [FA 21] – Kotula 1890; Wysowa- Zdrój [EV 17] – Taszakowski & Gorczyca 2018. Krakowsko- Wieluńska Upland: Błędowska Desert [CA 97] – Lis J. A. 1989, Lis J. A. & Lis B. 1998; Kraków, Krzemionki [DA 14] – Smreczyński 1954; Kraków, Mydlniki [DA 24] – Stobiecki 1915, Smreczyński 1954. * Olsztyn [CA 98] – 19 Jul 1999, 1 ex., leg. A. Pańczyk (DBUO). Lower Silesia: Kopalina [XS 84] – Scholz 1931. Lubelska Upland: Lublin, Botanical Garden [FB 08] – Cmoluchowa 1960; Bagno Serebryskie Res. [FB 77] – Lechowski & Smardzewska-Gruszczak 2004; Zawadówka Res. [FB 66] – Smardzewska-Gruszczak & Lechowski 2000; Turka [FB 18] – Lechowski 1984; Wandzin [FB 19] – Fedorko 1957; Wrotków [FB 07] – Cmoluchowa 1958; Zemborzyce [FB 07] – Cmoluchowa 1958. Małopolska Upland: * Krzyżanowice Dolne [DA 68] – 16 Sep 1954, 1 ex., 17 Sep 1954, 1 ex., leg. S. Nowakowski (ZMPA); * Młodzawy [DA 68] – 13 Aug 1954, 1 ex., leg. S. Nowakowski (ZMPA). Masurian Lake District: Ełk [EE 86] – Smreczyński 1954. Pieniny Mts: general [DV 57] – Smreczyński 1954, Taszakowski & Pasińska 2017. Pomeranian lake District: Szczecin [VV 71] – Schmidt 1928. Roztocze Upland: Bukowa Góra Res. [FB 30] – Lechowski & Cmoluchowa 1993, Cmoluchowa & Lechowski 1994; Zwierzyniec [FB 30] – Strawiński 1956 a. Sandomierska Lowland: Lipie [EA 69] – Stobiecki 1915; Zaleszany [EB 61] – Stobiecki 1915. Upper Silesia: Balin [CA 85] – Stobiecki 1915, Lis J. A. 1989, Lis J. A. & Lis B. 1998; * Będzin [CA 67] – 25 Jun 2008, 1 ex., leg. A. Kulis (DZUS); Bytom [CA 58] – Lis J. A. 1989, Lis J. A. & Lis B. 1998; * Bytom, Stolarzowice [CA 48] – 3 Nov 1931, 1 ex., leg. H. Nowotny (USMB); * Bytom [CA 58] – 1 Apr 1932, 1 ex. leg. H. Nowotny (USMB), 4 Aug 1934, 1 ex., leg. F. Kirsch (USMB); Chełmek [CA 75] – Stobiecki 1886; Lis J. A. 1989, Lis J. A. & Lis B. 1998; Dąb [CA 75] – Stobiecki 1886, Lis J. A. 1989, Lis J. A. & Lis B. 1998; Segiecki forest [CA 48] – Lis J. A. 1989, Lis J. A. & Lis B. 1998; * Ligota Dolna [CB 05] – 17 Oct 1938, 3 exx., leg. H. Nowotny (USMB); St. Anne Mt. LP [BA 99] – Lis J. A. 1989, Lis J. A. & Lis B. 1998, Lis B. & Danielczok-Demska 2001; Kamienna Góra Res. [BA 99] – Polentz 1943, Lis B. 1994, Lis J. A. 1989, Lis J. A. & Lis B. 1998, Lis B. & Danielczok-Demska 2001; * Tychy [CA 55] – 13 Mar 2007, 1 ex., 26 Mar 2007, 1 ex., 2 Apr 2007, 1 ex., leg. D. Nawara (DZUS); Zbrosławice [CA 38] – Lis J. A. 1989, Lis J. A. & Lis B. 1998. Western Beskidy Mts: Gruszów [DA 42] – Stobiecki 1915; Łomnica [DV 87] – Smreczyński 1954; Masyw Czantorii Wielkiej Mts. [CA 40] – Kędzior et al. 2012; Młodów [DV 77] – Stobiecki 1915; Niedźwiedź [DV 39] – Smreczyński 1910; Piwniczna [DV 77] – Smreczyński 1954; Słupia [DA 41] – Stobiecki 1915. Western Sudetes Mts: Cieplice Śląskie Zdrój [WS 43] – Scholtz 1847, Assmann 1854, Scholz 1931; Jedlina Zdrój [WS 92] – Assmann 1854, Scholz 1931; Staniszów [WS 53] – Assmann 1854; Szczawno Zdrój [WS 82] – Scholtz 1847, Assmann 1854, Scholz 1931. Wielkopolsko- Kujawska Lowland: * Sycyn Dolny [XU 03] – 2 exx., 16 Jul 2011, 1 ex., 7 Aug 2012, leg. M. Bunalski; Wełna [XU 24] – Schumacher 1913; Wybranowo [XU 64] – Schumacher 1913."
        },
        {
          "description": "B i o n o m i c s: Xerothermophilous; oligophagous (mainly Fabaceae); one generation a year. R e m a r k s: Rare in Poland. D i s t r i b u t i o n i n P o l a n d (Fig. 6): Eastern Beskidy Mts: Łuczyce [FA 31] – Kotula 1890; Przemyśl [FA 21] – Smreczyński 1908; Przemyśl, Wzniesienie [FA 21] – Kotula 1890. Eastern Sudetes Mts: * Gipsowa Góra Res. [YR 14] – 8 Sep 1932, 5 exx., leg. H. Nowotny (USMB). Krakowsko- Wieluńska Upland: Kraków, Borek Fałęcki [DA 24] – Smreczyński 1954; Kraków, Mydlniki [DA 24] – Smreczyński 1954. Lubelska Upland: Bagno Serebryskie Res. [FB 77] – Lechowski & Smardzewska-Gruszczak 2006 a; Polesie Wołyńskie – Lechowski & Smardzewska-Gruszczak 2006 b. Pieniny Mts: Kras [DV 67] – Taszakowski & Pasińska 2017; Krościenko nad Dunajcem [DV 57] – Smreczyński 1954. Roztocze Upland: Łabunie [FB 61] – Strawiński 1960. Tatry Mts: Strążyska val. [DV 25] – Smreczyński 1954. Upper Silesia: Bytom [CA 58] – Lis J. A. 1989, Lis J. A. & Lis B. 1998, * Bytom, Dąbrowa Miejska [CA 58] – 28 Nov 1930, 1 ex., 24 Apr 1931, 1 ex., leg. H. Nowotny (USMB); * Bytom, Stolarzowice [CA 48] – 3 Nov 1931, 1 ex., leg. H. Nowotny (USMB); Regulice [CA 94] – Smreczyński 1954. Western Beskidy Mts: Niedźwiedź [DV 39] – Smreczyński 1910; Stary Sącz [DV 79] – Smreczyński 1954. Gampsocorinae Southwood & Leston, 1959 Gampsocorini Southwood & Leston, 1959"
        }
      ],
      "vernacularNames": [
        {
          "vernacularName": "Lille styltetæge",
          "language": "dan"
        },
        {
          "vernacularName": "Hoornbloemsteltwants",
          "language": "nld"
        },
        {
          "vernacularName": "bakkestyltetege",
          "language": "nno"
        },
        {
          "vernacularName": "bakkestyltetege",
          "language": "nob"
        },
        {
          "vernacularName": "nystytikkulude",
          "language": "fin"
        }
      ],
      "higherClassificationMap": {
        "1": "Animalia",
        "54": "Arthropoda",
        "216": "Insecta",
        "809": "Hemiptera",
        "4306": "Berytidae",
        "2008319": "Berytinus"
      },
      "synonym": false,
      "class": "Insecta"
    },
    {
      "key": 4486860,
      "nameKey": 16849277,
      "datasetKey": "d7dddbf4-2cf0-4f39-9b2a-bb099caae36c",
      "constituentKey": "7ddf754f-d193-4cc9-b351-99906754a03b",
      "nubKey": 4486860,
      "parentKey": 2008322,
      "parent": "Berytinus minor",
      "kingdom": "Animalia",
      "phylum": "Arthropoda",
      "order": "Hemiptera",
      "family": "Berytidae",
      "genus": "Berytinus",
      "species": "Berytinus minor",
      "kingdomKey": 1,
      "phylumKey": 54,
      "classKey": 216,
      "orderKey": 809,
      "familyKey": 4306,
      "genusKey": 2008319,
      "speciesKey": 2008322,
      "scientificName": "Berytinus minor minor",
      "canonicalName": "Berytinus minor minor",
      "authorship": "(Herrich-Schaeffer, 1835) ",
      "publishedIn": "Herrich-Schaeffer, G.H.W. (1835) Nomenclator entomologicus--Verzeichniss der Europaishen Insecten: zur erleichterung des Tausch-verkehrs mit Preisen versehen. I. Lepidoptera & Hemiptera. Nomenclator entomologicus--Verzeichniss der Europaishen Insecten: zur erleichterung des Tausch-verkehrs mit Preisen versehen. I. Lepidoptera & Hemiptera. Regensburg: Friedrich Pustet.",
      "nameType": "SCIENTIFIC",
      "taxonomicStatus": "ACCEPTED",
      "rank": "SUBSPECIES",
      "origin": "SOURCE",
      "numDescendants": 0,
      "numOccurrences": 0,
      "taxonID": "gbif:4486860",
      "extinct": false,
      "habitats": [
        "TERRESTRIAL"
      ],
      "nomenclaturalStatus": [],
      "threatStatuses": [],
      "descriptions": [
        {
          "description": "Beskid Zachodni: Przyborów, Moczarki [CV 89]: 28.03. 2020, leg. GG."
        },
        {
          "description": "Terrestrial."
        },
        {
          "description": "Biono mics: Mesophilous; mainly Trifolium spp.; one (possible two) generation a year. Remarks: Common and widely distributed in Poland. Distribution in P o l a n d (Fig. 4): Bieszczady Mts: Stuposiany [FV 24] – Cmoluchowa & Lechowski 1977. Eastern Beskidy Mts: Bednarka [EA 20, EV 29], Dobrynia [EV 39] – Taszakowski & Gorczyca 2018; upper Ropa River val. [EV 17] – Taszakowski 2012; Hureczko [FA 31] – Kotula 1890; Iwonicz [EV 59] – Strawiński 1953; Libusza [EA 10], Lipinki [EA 20] – Taszakowski & Gorczyca 2018; Prałkowce [FA 21] – Kotula 1890; Przemyśl, Lipowica [FA 21] – Kotula 1890. Eastern Sudetes Mts: * Gipsowa Góra Res. [YR 14] – 8 Sep 1932, 2 exx., leg. H. Nowotny (USMB); * Masyw Śnieżnika Mts. [XR 46] – 24 Aug 2006, 1 ex., KNB (DBUO). Krakowsko- Wieluńska Upland: Kraków, Bielany [DA 14] – Smreczyński 1906 b; Kraków, Przylasek Rusiecki [DA 34], Modlniczka [DA 15] – Stobiecki 1915; Sąspowska val. [DA 16] – Chłond & Gorczyca 2009. Lower Silesia: * Kwietno [XS 06] – 8 May 1944, 5 exx., 27 May 1944, 1 ex., leg. A. Lanzke (ZMPA); * Leszczyna n. Legnica [WS 65] – 14 May 1932, 1 ex. (DBUO); * Szymanów [XS 25] – 29 Jul 1943, 1 ex., leg. A. Lanzke (ZMPA); * Ujazd Dolny [XS 06] – 18 Aug 1944, 1 ex., leg. A. Lanzke (ZMPA); Wrocław [XS 46] – Scholtz 1847, Assmann 1854, Scholz 1931. Małopolska Upland: * Krzyżanowice Dolne [DA 68] – 16 Sep 1954, 1 ex., 19 Sep 1954, 1 ex., leg. S. Nowakowski (ZMPA). Lubelska Upland: Bystrzyca [FB 18] – Lechowski 1984; Dratów [FB 39] – Cmoluchowa & Lechowski 1988; Kaniwola [FB 49] – Cmoluchowa & Lechowski 1988; Lublin, Botanical Garden [FB 08] – Cmoluchowa 1960; Łuszczów [FB 28] – Lechowski 1984; Podgórz [EB 68] – Cmoluchowa 1964; Brzeźno Res. [FB 87] – Smardzewska-Gruszczak & Lechowski 2006; Zawadówka Res. [FB 66] – Smardzewska-Gruszczak & Lechowski 2000; Rudnik [FB 18] – Lechowski 1984; Turka [FB 18] – Lechowski 1984; Wandzin [FB 19] – Strawiński 1956 c; Wrotków [FB 07] – Cmoluchowa 1958; Zemborzyce [FB 07] – Cmoluchowa 1958. Mazowiecka Lowland: Chylice [EC 06] – Lechowski 1989; Klembów [ED 20] – Lechowski 1989; Warszawa [EC 08] – Hałka- Wojciechowicz 1996. Pieniny Mts: general [DV 57] – Taszakowski & Pasińska 2017. Pomeranian Lake District: Gwda Wielka [XV 15] – Burdajewicz & Nowacka 1995; * Piła n. Gostycyn [XV 82] – 11 Aug 2004, 1 ex., leg. B. & J. A. Lis (DBUO); Słupsk [XA 33] – Karl 1935; * Szczecin [WT 82] – 26 May 1915, 1 ex., leg. P. Noack (ZMPA). Roztocze Upland: Łabunie [FB 61] – Strawiński 1960; Nart Res. [FB 40] – Tenenbaum 1921; Ulów [FA 69] – Tenenbaum 1921; Zwierzyniec [FB 30] – Strawiński 1966 a. Sandomierska Lowland: Lipie [EA 69] – Stobiecki 1915. Świętokrzyskie Mts: Łysa Góra [EB 03] – Strawiński 1962; Trzcianka [EB 03] – Strawiński 1962. Tatry Mts: general [DV 25] – Nowicki 1870, Smreczyński 1954. Upper Silesia: * Bażany [CB 04] – 20 Sep 1936, 1 ex. leg. H. Nowotny (USMB); Bytom [CA 58] – Lis J. A. 1989, Lis J. A. & Lis B. 1998; * Bytom [CA 58] – 27 Nov 1931, 1 ex., 4 Aug 1934, 1 ex., 13 Jul 1937, 2 exx., leg. F. Kirsch (USMB); 3 Mar 1934, 4 exx., 5 Oct 1936, 3 exx., 6 Sep 1937, 4 exx., leg. H. Nowotny (USMB); 22 Sep 1934, 1 ex., (ZMPA); * Bytom, Dąbrowa Miejska [CA 58] – 14 Nov 1930, 1 ex., 28 Nov 1930, 10 exx., 24 Apr 1931, 10 exx., 16 Sep 1937, 1 ex., leg. H. Nowotny (USMB); Bytom, Stolarzowice [CA 48] – Lis J. A. 1989, Lis J. A. & Lis B. 1998; Chełmek [CA 75] – Stobiecki 1915, Lis J. A. 1989, Lis J. A. & Lis B. 1998; Gliwice [CA 37] – Lis J. A. 1989, Lis J. A. & Lis B. 1998; * Katowice, Podlesie [CA 56] – 25 Aug 2009, 1 ex., leg. A. Kempny (DZUS); Segiecki forest [CA 48] – Lis J. A. 1989, Lis J. A. & Lis B. 1998; * Ligota Dolna [CB 05] – 21 Sep 1937, 1 ex., 17 Oct 1938, 1 ex., leg. H. Nowotny (USMB); Mikołów, Jamna [CA 55] – Lis J. A. 1989, Lis J. A. & Lis B. 1998; * Mysłowice, Brzezinka [CA 66] – 23 May 2009, 1 ex., leg. K. Rydzoń (DZUS); Piekary Śląskie [CA 58] – Bugaj-Nawrocka & Gorczyca 2013; Kamienna Góra Res. [BA 99] – Lis B. 1994, Lis J. A. 1989, Lis J. A. & Lis B. 1998, Lis B. & Danielczok-Demska 2001; * Łężczok Res. [CA 05] – 25 Aug 2006, 3 exx., leg. T. Masarczyk (DZUS), 31 Oct 1937, 3 exx., leg. H. Nowotny (USMB); Szymiszów [CA 09] – Lis J. A. 1989, Lis J. A. & Lis B. 1998; * Tworóg [CB 30] – 23 Oct 1928, 1 ex. leg. H. Nowotny (USMB); * Tychy [CA 55] – 13 Mar 2007, 2 exx., 24.03.2007, 4 exx., 26 Mar 2007, 5 exx., 29 Mar 2007, 6 exx., 2 Apr 2007, 7 exx., leg. D. Nawara (DZUS); Zbrosławice [CA 38] – Lis J. A. 1989, Lis J. A. & Lis B. 1998. Western Beskidy Mts: Babia Góra Mt. [CV 99] – Lis B. et al. 2002, Celary 2003, * 6 Sep 1957, 2 exx., leg. S. Nowakowski (ZMPA); Bieńkowice [DA 32] – Smreczyński 1906 b; Buczkowice [CA 51] – Lis B. & Dubiel 2013; Dobczyce [DA 32] – Smreczyński 1906 b; Gruszów [DA 42] – Stobiecki 1915; Krzyszkowice [DA 22] – Smreczyński 1906 b; Niedźwiedź [DV 39] – Smreczyński 1910; Słupia [DA 41] – Stobiecki 1915; * Sól [CV 58] – 6 Aug 2003, 1 ex., leg. J. Ćwikła (DZUS). Western Sudetes Mts: * Łężyce [WR 98] – 22 Jul 2000, 1 ex., leg. M. Widziszewska (DBUO); Nowa Ruda [XS 00] – Assmann 1854, Scholz 1931. Wielkopolsko- Kujawska Lowland: Brudzyń [XU 65] – Szulczewski 1913; * Dolina Samy val. [XU 03] – 1 ex., 8 – 10 May 2009 leg. M. Bunalski; Duninów [CD 92] – Strawiński 1965; * Głuszyna [XT 39] – 1 ex., 20 Jun 1974, leg. A. Korcz; Zawisze [WT 27] – 1 ex., 10 Apr 2015, leg. R. Orzechowski."
        }
      ],
      "vernacularNames": [],
      "higherClassificationMap": {
        "1": "Animalia",
        "54": "Arthropoda",
        "216": "Insecta",
        "809": "Hemiptera",
        "4306": "Berytidae",
        "2008319": "Berytinus",
        "2008322": "Berytinus minor"
      },
      "synonym": false,
      "class": "Insecta"
    },
    {
      "key": 2008315,
      "nameKey": 7398480,
      "datasetKey": "d7dddbf4-2cf0-4f39-9b2a-bb099caae36c",
      "constituentKey": "7ddf754f-d193-4cc9-b351-99906754a03b",
      "nubKey": 2008315,
      "parentKey": 2008314,
      "parent": "Neides",
      "basionymKey": 2008318,
      "basionym": "Cimex tipularius Linnaeus, 1758",
      "kingdom": "Animalia",
      "phylum": "Arthropoda",
      "order": "Hemiptera",
      "family": "Berytidae",
      "genus": "Neides",
      "species": "Neides tipularius",
      "kingdomKey": 1,
      "phylumKey": 54,
      "classKey": 216,
      "orderKey": 809,
      "familyKey": 4306,
      "genusKey": 2008314,
      "speciesKey": 2008315,
      "scientificName": "Neides tipularius (Linnaeus, 1758)",
      "canonicalName": "Neides tipularius",
      "authorship": "(Linnaeus, 1758) ",
      "publishedIn": "Linnaeus, C. (1758) Systema Naturae. Regnum Animale. Editio Decima. Systema Naturae. Regnum Animale. Editio Decima. Holmiae: Laurentii Salvii, 1, 1–824.",
      "nameType": "SCIENTIFIC",
      "taxonomicStatus": "ACCEPTED",
      "rank": "SPECIES",
      "origin": "SOURCE",
      "numDescendants": 1,
      "numOccurrences": 0,
      "taxonID": "gbif:2008315",
      "extinct": false,
      "habitats": [
        "TERRESTRIAL"
      ],
      "nomenclaturalStatus": [],
      "threatStatuses": [
        "NOT_EVALUATED",
        "VULNERABLE",
        "LEAST_CONCERN"
      ],
      "descriptions": [
        {
          "description": "Nizina Mazowiecka: rez. Jedlnia [EB 29]: 20.08.2022, leg. MM, det. GG; Nizina Wielkopolsko-Kujawska: Kalisz [CC 03]: 20.07.2022, leg. TR, det. GG; Pojezierze Pomorskie: Jonki [XV 57]: 1.08.2022, leg. GG; Śląsk Górny: Ryczów [CA 93]: 24.07.2022, leg. JR, det. GG; Wyżyna Krakowsko- Wieluńska: Ryczów [DA 08]: 24.07.2022, leg. JR, det. GG; Żelazko [CA 98]: 9.10. 2021, leg. JR, det. GG; Wyżyna Małopolska: Bosowice [DA 99]: 3.05.2022, leg. GK; Staniowice [DB 61]: 10.05.2022, leg. GK; Szaniec [DA 79]: 17.06.2022, leg. GK."
        },
        {
          "description": "Distribution in Iran. East Azarbaijan, West Azarbaijan (Gharaat et al. 2009), Guilan (Linnavuori 2007). General distribution. West Palearctic, Near East and North Africa."
        },
        {
          "description": "Comment. On Asteraceae and Poaceae (Linnavuori 2007)."
        },
        {
          "description": "Gampsocorinae Southwood & Leston, 1959"
        },
        {
          "description": "univoltine"
        },
        {
          "description": "polyphagous"
        },
        {
          "description": "polyphagous"
        },
        {
          "description": "omnivore"
        },
        {
          "description": "herbivore"
        },
        {
          "description": "1"
        },
        {
          "description": "1"
        },
        {
          "description": "1"
        },
        {
          "description": "1"
        },
        {
          "description": "1"
        },
        {
          "description": "0"
        },
        {
          "description": "0"
        },
        {
          "description": "0"
        },
        {
          "description": "0"
        },
        {
          "description": "0"
        },
        {
          "description": "0"
        },
        {
          "description": "Terrestrial."
        },
        {
          "description": "B io no mic s: Mesophilous / xerothermophilous; polyphagous (mainly Caryophyllaceae, Geraniaceae, Asteraceae, Scrophulariaceae and Poaceae); one generation a year. R e m a r k s: Common and widely distributed in Poland. D i s t r i b u t i o n i n P o l a n d (Fig. 1): Baltic Coast: Chłapowo [CF 37] – Smreczyński 1954; Gdynia [CF 44] – Lis B. & Kowalczyk 2017; Karpinka [VV 88] – Schmidt 1928; * Smołdzino [XA 46] – 1 Aug 2002, 1 ex., leg. B. & J. A. Lis (DBUO); Białowieża Forest: Czerlonka [FD 84] – Strawiński 1956 b; general [FD 94] – Trojan et al. 1994. Eastern Beskidy Mts: Bednarka [EA 20, EV 29] – Taszakowski & Gorczyca 2018; * Bednarka, Cieklinka Mt. [EV 29] – 6 Aug 2015, 1 ex., leg. R. Dobosz (USMB); Ciężkowice [DA 91] – Smreczyński 1954; Libusza [EA 10] – Taszakowski & Gorczyca 2018; Przemyśl, Lipowica [FA 21] – Kotula 1890; Przemyśl, Wzniesienie [FA 21] – Kotula 1890; Zarzecze [FA 13] – Krasucki 1919. Eastern Sudetes Mts: * Gipsowa Góra Res. [YR 14] – 8 Sep 1932, 4 exx., leg. H. Nowotny (USMB). Krakowsko- Wieluńska Upland: Błędowska Desert [CA 97] – Lis J. A. 1989, Lis J. A. & Lis B. 1998; Czatkowice [DA 05] – Smreczyński 1906 b; Czyżówki [DA 16] – Chłond & 1886, Smreczyński 1906 b; Kraków, Błonia [DA 24] – Stobiecki 1886; Kraków, Borek Fałęcki [DA 24] – Smreczyński 1906 b, Stobiecki 1915; Kraków, Dębniki [DA 14] – Stobiecki 1886; Kraków, Krzemionki [DA 14] – Stobiecki 1886, Smreczyński 1906 b, Stobiecki 1915; Kraków, Mydlniki [DA 24] – Stobiecki 1915; Kraków, Olsza [DA 24] – Smreczyński 1906 b; Kraków, Panieńskie Skały [DA 14] – Stobiecki 1886; Kraków, Podgórki [DA 14] – Smreczyński 1954; Kraków, Podgórze [DA 24] – Stobiecki 1886; Kraków, Przegorzały [DA 14] – Stobiecki 1915; Kraków, Sikornik [DA 14] – Stobiecki 1886; * Mirów [DB 00] – 21 Jul 1999, 1 ex., leg. A. Pańczyk (DBUO); * Podlesice, n. Zborów Mt. [CB 90] – 11 Jul 2006, 5 exx., leg. D. Kolbe (DZUS); Przedmość [CB 16, CB 26] – Noga & Lis B. 2015; Rudawa [DA 05] – Stobiecki 1915; Rząska [DA 15] – Smreczyński 1906 b; Wierzchowie [DA 15] – Smreczyński 1954; Zabierzów [DA 15] – Stobiecki 1886, Smreczyński 1906 b. Lower Silesia: * Bardo [XR 29] – 25 May 1932, 1 ex. leg. F. Kirsch (USMB); * Brzeg [XS 73] – 1 ex., 26 Feb 2011, leg. J. Regner; Gogolin [BA 89] – Lis J. A. 1989, Hebda 2006; * 12 Sep 1928, 2 exx., 16 Oct 1930, 2 exx., leg. H. Nowotny (USMB); Górażdże [BB 80] – Hohol-Kilinkiewicz & Czaja 2006; * Ochodze [XS 91] – 6 Sep 2004, 1 ex., leg. E. Fąferko (DBUO); Kamień Śląski [BB 90] – Hebda 2006; * Ligota Wielka [XS 22] – 20 Apr 1930, 1 ex., leg. E. Drescher (USMB); * Lipowa [XS 82] – 31 Jul 2004, 2 exx., 20 Aug 2004, 1 ex., 19 Sep 2004, 2 exx., leg. E. Fąferko (DBUO); * Raszowa n. Lubin [WS 88] – 4 Aug 1928, 2 exx. (DBUO); Winnica [WS 76] – Assmann 1854; Wrocław [XS 46] – Assmann 1854; Wrocław, Karłowice [XS 46] – Assmann 1854; * Ząbkowice Śląskie [XS 20] – 9 Feb 1938, 1 ex. leg. H. Nowotny (USMB). Lubelska Upland: Bochotnica [EB 68] – Cmoluchowa 1964; Felin [FB 17] – Ziarkiewicz 1962; Gołąb [EC 60] – Cmoluchowa 1971; Gródek [GB 03] – Strawiński 1959 b; Kazimierz Dolny [EB 68] – Cmoluchowa 1964; Lublin [FB 07] – Ziarkiewicz 1957; Michałówka [EB 69] – Strawiński 1957 b; Opoka [EB 63] – Cmoluchowa 1971; Podgórz [EB 68] – Cmoluchowa 1964; Bagno Serebryskie Res. [FB 77] – Lechowski & Smardzewska-Gruszczak 2004; Brzeźno Res. [FB 87] – Smardzewska-Gruszczak & Lechowski 2006; Ruda Czechowska [EB 69] – Strawiński 1963; Wandzin [FB 19] – Strawiński 1956 c, Strawiński 1957 a, Ziarkiewicz 1958; Wolica [EC 80] – Smreczyński 1954; Wólka Gołębska [EC 60] – Strawiński 1963; Zaklików [EB 72] – Cmoluchowa 1971; Zawadówka Res. [FB 66] – Smardzewska-Gruszczak & Lechowski 2000; Zemborzyce [FB 07] – Cmoluchowa 1958. Małopolska Upland: * Bogucice [DA 79] – 3 Aug 1999, 4 exx., 7 Aug 1999, 1 ex., 10 Aug 1999, 2 exx., leg. B. & J. A. Lis (DBUO); * Grabowiec Res. n. Pińczów [DA 57] – 17 Jul 1954, 1 ex., leg. S. Nowakowski (ZMPA); Kruszewiec [DB 59] – Strawiński 1936; * Krzyżanowice Dolne [DA 68] – 16 Sep 1954, 5 exx., leg. S. Nowakowski (ZMPA), 6 Aug 2000, 1 ex., leg. B. & J. A. Lis (DBUO); Leszczyny [DB 87] – Strawiński 1936; Sielec [DA 39] – Fedorko 1959; * Polana Polichno Res. [DA 69] – 28 May 1959, 1 ex., leg. W. Bazyluk (ZMPA); * Pińczów [DA 69] – 5 Aug 1998, 1 ex., KNB (DBUO); * Skorocice [DA 78], 10 Aug 1999, 1 ex. leg. B. & J. A. Lis (DBUO); Winiary [DA 78] – 26 Aug 1954, 1 ex., leg. S. Nowakowski (ZMPA). Mazowiecka Lowland: Dziekanów Leśny [DC 99] – Bilewicz-Pawińska 1965; * Gaj Policzko [DB 25] – 1 Aug 2007, 1 ex. leg. W. Żyła (USMB); Jadwisin [ED 41] – Bilewicz-Pawińska 1965; * Łomna [DD 80] – 17 Oct 1980, 1 ex., 26 Apr 1982, 1 ex., leg. A. Kędziorek (ZMPA); Otwock [EC 27] – Smreczyński 1954; Puszcza Biała forest [ED 54] – Cmoluchowa & Lechowski 1993; Radom [EB 19] – Tomasik 2014; * Romanów [DC 02] – 18 Aug 2011, 1 ex., leg. J. Kalisiak; * Rogów [DC 24] – 3 exx., 6 Sep 2014, leg. M. Bunalski; Skierniewice [DC 45] – Strawiński 1936; Szymanów [DC 57] – Smreczyński 1954; Warszawa, Młociny [DC 99] – Bilewicz-Pawińska 1961, Bilewicz- Pawińska 1965; Zbroszki [DD 93] – Lechowski 1989. Mazurian Lake District: general – Mikołajski 1962 b; Klewki [DE 75] – Mikołajski 1961; Kujawy [CD 67] – Smreczyński 1954; Olsztyn, Posorty [DE 65] – Mikołajski 1962 d; Redykajny Res. [DE 66] – Mikołajski 1962 a; Tomaszkowo [DE 65] – Mikołajski 1961. Pieniny Mts: Kras [DV 67] – Taszakowski & Pasińska 2017. Podlasie Lowland: Dawidowizna [FE 12] – Lis J. A. et al. 1995; Downary Plac [FE 12] – Lis J. A. et al. 1995; Goniądz [FE 12] – Lis J. A. et al. 1995; Osowiec [FE 02] – Lis J. A. et al. 1995; Osowiec, Twierdza [FE 02] – Lis J. A. et al. 1995; Czerwone Bagno Res. [FE 13] – Lis J. A. et al. 1995; Układek [FE 13] – Lis J. A. et al. 1995; Wólka Piaseczna [FE 13] – Lis J. A. et al. 1995; Wroceń [FE 23] – Lis J. A. et al. 1995. Pomeranian Lake District: Bielinek over the Odra River Res. [VU 46] – Engel & Hedicke 1934, Engel 1938; Bory Tucholskie forest [CE 05] – Kuhlgatz 1901, Cmoluchowa & Lechowski 1993; Cisiny [CE 13] – Kosicki 1958; Dobrcz [CE 00] – Wrzesińska et al. 2013; Goleniów [VV 83] – Wagner 1941; * Gołąbek n. Tuchola [XV 64] – 19 Aug 2004, 1 ex., leg. B. & J. A. Lis (DBUO); * Gostycyn [XV 82] – 17 Aug 2004, leg. B. & J. A. Lis (DBUO); Recz [WV 30] – Karl 1935; * Piła n. Gostycyn [XV 82] – 11 Aug 2004, 2 exx., 17 Aug 2004, 3 exx., leg. B. & J. A. Lis (DBUO); * Płazowo [XV 93] – 9 Aug 2004, 2 exx., leg. B. & J. A. Lis (DBUO); Szczecin [VV 71] – Schmidt 1928; Wierzchlas Res. [CE 03] – Kosicki 1958; Zakrzewska Osada [XV 61] – Tarnawski 2013; * Zamrzenica [XV 82] – 8 Aug 2004, 7 exx., 12 Aug 2004, 2 exx., leg. B. & J. A. Lis (DBUO); Roztocze Upland: Górecko Stare [FA 49] – Cmoluchowa & Lechowski 1994; Kosobudy [FB 41] – Strawiński 1956 a; Łabunie [FB 61] – Strawiński 1960; Paary [FA 68] – Strawiński 1956 a; Bukowa Góra Res. [FB 30] – Strawiński 1956 a, Strawiński 1964, Lechowski & Cmoluchowa 1993, Cmoluchowa & Lechowski 1994; Nart Res. [FB 40] – Strawiński 1956 a; Tartaczna Góra Res. [FB 30] – Strawiński 1966 b; Susiec [FA 58] – Strawiński 1959 a; Turzyniec [FB 31] – Strawiński 1956 a; Wólka Łosiniecka [FA 68] – Strawiński 1959 a; Zwierzyniec [FB 30] – Strawiński 1956 a, Strawiński 1966 a. Sandomierska Lowland: Kłaj [DA 53] – Stobiecki 1915; Łańcut [EA 84] – Nowicki 1868; Tarnów [DA 93] – Smreczyński 1954. Świętokrzyskie Mts: Psarska Mt. [DB 94] – Strawiński 1962. Trzebnickie Hills: Kuraszków [XS 38], Maczów [XS 38] – Bugaj-Nawrocka et al. 2018; Oborniki Śląskie [XS 38] – Polentz 1943, Bugaj-Nawrocka et al. 2018; Ose [XS 89] – Lanzke & Polentz 1942; Rościsławice [XS 28] – Bugaj-Nawrocka et al. 2018. Upper Silesia: * Bażany [CB 04] – 20 Sep 1936, 1 ex. leg. H. Nowotny (USMB); Bobrek [CA 74] – Stobiecki 1886, Lis J. A. 1989, Lis J. A. & Lis B. 1998; Bukowno, Pustynia Starczynowska [CA 87] – Lis J. A. 1989, Lis J. A. & Lis B. 1998; Bytom [CA 58] – Lis J. A. 1989, Lis J. A. & Lis B. 1998; Chełmek [CA 75] – Stobiecki 1886, Stobiecki 1915, Lis J. A. 1989, Lis J. A. & Lis B. 1998; Dąb [CA 75] – Stobiecki 1886, Lis J. A. 1989, Lis J. A. & Lis B. 1998; Dolina Żabnika Res. [CA 86] – Chłond et al. 2005; Gliwice [CA 37] – Lis J. A. 1989, Lis J. A. & Lis B. 1998; Jemielnica [CB 10] – Lis J. A. 1989, Lis J. A. & Lis B. 1998, 19 Oct 1936, 2 exx., leg. H. Nowotny (USMB); Libiąż [CA 75] – Stobiecki 1886, Lis J. A. 1989, Lis J. A. & Lis B. 1998; Lipowiec [CA 84] – Stobiecki 1886, Lis J. A. 1989, Lis J. A. & Lis B. 1998; Łabędy [CA 37] – Lis J. A. 1989; * Łężczok Res. [CA 05] – 24 Jul 2006, 1 ex., 1 Sep 2006, 1 ex., 11 Sep 2006, 1 ex., 16 Sep 2006, 1 ex., leg. T. Masarczyk (DZUS); * Pławy [CA 68] – 20 Jul 2008, 1 ex., leg. K. Rydzoń; St. Anne Mt. LP [BA 99] – Lis J. A. 1989, Lis J. A. & Lis B. 1998, Lis B. & Danielczok-Demska 2001; Potępa [CB 30] – Lis J. A. 1989, Lis J. A. & Lis B. 1998; * Ruda Śląska [CA 46] – 09 Aug 2008, 1 ex., 15 Aug 2008, 1 ex., 20 Aug 2008, 3 exx., 17 Oct 2008, 1 ex., leg. L. Jezuit (DZUS); * Rudziniec [CA 18] – 8 Jul 2015, 1 ex., at light, leg. R. Dobosz (USMB); * Strzelce Opolskie [CA 09] – 17 Jul 2005, 1 ex., leg. M. Hamal (DBUO); Szymiszów [CA 09] – Lis J. A. 1989, Lis J. A. & Lis B. 1998; * Wojciechów [CB 14] – 10 Aug 1938, 1 ex., leg. H. Nowotny (USMB); Zbrosławice [CA 38] – Lis J. A. 1989, Lis J. A. & Lis B. 1998; Żabie Doły Res. [CA 57] – Musik 2010; Żarki [CA 84] – Stobiecki 1886, Lis J. A. 1989, Lis J. A. & Lis B. 1998. Western Beskidy Mts: Bieńkowice [DA 32] – Smreczyński 1906 b; * Cieszyn [CA 21] – 12 Aug 2006, 1 ex., leg J. Spandel (DBUO), 3 exx. (USMB); Kasina Wielka [DA 30] – Smreczyński 1910; Krzyszkowice [DA 22] – Smreczyński 1906 b; Melsztyn [DA 62] – Smreczyński 1906 a, Smreczyński 1954; Piwniczna [DV 77] – Smreczyński 1954; Wieliczka [DA 33] – Stobiecki 1886. Western Sudetes Mts: Cieplice Śląskie Zdrój [WS 43] – Assmann 1854; Sołtys Mt. [WS 62] – Assmann 1854. Wielkopolsko- Kujawska Lowland: Brudzyń [XU 65] – Szulczewski 1913; Czarnowska Górka ad Czarnów [VU 82] – Hebda & Rutkowski 2015; * Dolina Samy val. [XU 03] – 1 ex., 16 May 2009, 2 exx., 11 Aug 2010, 1 ex., 10 Jul 2011, leg. M. Bunalski; Duninów [CD 92] – Strawiński 1965; * Dziekanowice [XU 62] – 1 ex., 9 May 2010, leg. M. Bunalski; Janowiec Wielkopolski [XU 64] – Szulczewski 1908; * Jaryszewo, valley of the Warta river [XU 13] – 1 ex., 27 Jul 2014, 1 ex., 20 Jul 2015, leg. M. Bunalski; * Jezioro Sycyńskie lake [XU 03] – 1 ex., 11 Aug 2015, leg. M. Bunalski; Kromolin [CC 52] – Strawiński 1936; Milsko [WT 55] – 1 ex., 9 Sep 2017, leg. R. Orzechowski; Papowo Toruńskie [CD 48] – Cmoluch 1960; Puszcza Zielonka forest [XU 42] – Skórka 1994; Suponin [CE 10] – Wrzesińska et al. 2013; * Sycyn Dolny [XU 03] – 2 exx., 27 – 30 Apr 2009, 5 exx., 20 Jun 2009, 1 ex., 17 Jun 2009, 1 ex., 10 Aug 2009, 10 exx., 19 Jul 2010, 6 exx., 25 Jul 2010, 3 exx., 29 Apr 2011, 2 exx., 20 May 2011, 2 exx., 17 Jul 2011, 1 ex., 16 Jul 2011, 1 ex., 3 Aug 2011, 2 exx., 3 Aug 2011, 1 ex., 7 Jul 2012, 2 exx., 7 Aug 2012, 1 ex., 7 Jul 2012, 2 exx., 28 Aug 2012, 3 exx., 29 Aug 2012, 1 ex., 1 May 2013, 1 ex., 23 Aug 2013, 1 ex., 7 Sep 2013, leg. M. Bunalski; * Sycyn Dolny [XU 13] – 1 ex., 4 Jun 2010, 3 exx., 2 Aug 2012, 1 ex., 11 Aug 2013, leg. M. Bunalski; Toruń [CD 37] – Smreczyński 1954; Turew [XT 27] – Trojan 1989; * Uroczysko Maruszka [XU 41] – 1 ex., 12 Aug 2009, leg. M. Bunalski; * Wschowa [WT 93] – 1 ex., 4 Mar 2014, leg. R. Matuszczak; Zielona Góra [WT 35] – Gruhl 1929; 1 ex., 6 May 2014, leg. R. Orzechowski. Berytinini Southwood & Leston, 1959"
        }
      ],
      "vernacularNames": [
        {
          "vernacularName": "Styltetæge",
          "language": "dan"
        },
        {
          "vernacularName": "Stor styltetæge",
          "language": "dan"
        },
        {
          "vernacularName": "Lange steltwants",
          "language": "nld"
        },
        {
          "vernacularName": "Schnakerich",
          "language": "deu"
        },
        {
          "vernacularName": "kyststyltetege",
          "language": "nno"
        },
        {
          "vernacularName": "kyststyltetege",
          "language": "nob"
        },
        {
          "vernacularName": "koipeloinen",
          "language": "fin"
        }
      ],
      "higherClassificationMap": {
        "1": "Animalia",
        "54": "Arthropoda",
        "216": "Insecta",
        "809": "Hemiptera",
        "4306": "Berytidae",
        "2008314": "Neides"
      },
      "synonym": false,
      "class": "Insecta"
    }
  ],
  "facets": []
}
```
</details>
</div>

#### Occurance

- I couldn't easily figure out a set of search parameters that would return huge amounts of data, but below is the example output for responses from such a search

##### Output Example

<div>
<details>
<summary>Click to expand</summary>

```json
{
  "endOfRecords": true,
  "count": 0,
  "results": [
    {
      "key": 0,
      "datasetKey": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
      "publishingOrgKey": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
      "networkKeys": [
        "3fa85f64-5717-4562-b3fc-2c963f66afa6"
      ],
      "installationKey": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
      "hostingOrganizationKey": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
      "publishingCountry": "AF",
      "protocol": "EML",
      "lastCrawled": "2025-10-15T20:18:04.120Z",
      "lastParsed": "2025-10-15T20:18:04.120Z",
      "crawlId": 0,
      "projectId": "string",
      "programmeAcronym": "string",
      "extensions": {
        "additionalProp1": [
          {
            "additionalProp1": "string",
            "additionalProp2": "string",
            "additionalProp3": "string"
          }
        ],
        "additionalProp2": [
          {
            "additionalProp1": "string",
            "additionalProp2": "string",
            "additionalProp3": "string"
          }
        ],
        "additionalProp3": [
          {
            "additionalProp1": "string",
            "additionalProp2": "string",
            "additionalProp3": "string"
          }
        ]
      },
      "basisOfRecord": "PRESERVED_SPECIMEN",
      "individualCount": 0,
      "occurrenceStatus": "PRESENT",
      "sex": "string",
      "lifeStage": "string",
      "establishmentMeans": "string",
      "degreeOfEstablishment": "string",
      "pathway": "string",
      "classifications": {
        "additionalProp1": {
          "usage": {
            "key": "string",
            "name": "string",
            "rank": "string",
            "code": "string",
            "authorship": "string",
            "genericName": "string",
            "infragenericEpithet": "string",
            "specificEpithet": "string",
            "infraspecificEpithet": "string",
            "formattedName": "string"
          },
          "acceptedUsage": {
            "key": "string",
            "name": "string",
            "rank": "string",
            "code": "string",
            "authorship": "string",
            "genericName": "string",
            "infragenericEpithet": "string",
            "specificEpithet": "string",
            "infraspecificEpithet": "string",
            "formattedName": "string"
          },
          "taxonomicStatus": "string",
          "classification": [
            {
              "key": "string",
              "name": "string",
              "rank": "string",
              "authorship": "string"
            }
          ],
          "iucnRedListCategoryCode": "string",
          "issues": [
            "string"
          ]
        },
        "additionalProp2": {
          "usage": {
            "key": "string",
            "name": "string",
            "rank": "string",
            "code": "string",
            "authorship": "string",
            "genericName": "string",
            "infragenericEpithet": "string",
            "specificEpithet": "string",
            "infraspecificEpithet": "string",
            "formattedName": "string"
          },
          "acceptedUsage": {
            "key": "string",
            "name": "string",
            "rank": "string",
            "code": "string",
            "authorship": "string",
            "genericName": "string",
            "infragenericEpithet": "string",
            "specificEpithet": "string",
            "infraspecificEpithet": "string",
            "formattedName": "string"
          },
          "taxonomicStatus": "string",
          "classification": [
            {
              "key": "string",
              "name": "string",
              "rank": "string",
              "authorship": "string"
            }
          ],
          "iucnRedListCategoryCode": "string",
          "issues": [
            "string"
          ]
        },
        "additionalProp3": {
          "usage": {
            "key": "string",
            "name": "string",
            "rank": "string",
            "code": "string",
            "authorship": "string",
            "genericName": "string",
            "infragenericEpithet": "string",
            "specificEpithet": "string",
            "infraspecificEpithet": "string",
            "formattedName": "string"
          },
          "acceptedUsage": {
            "key": "string",
            "name": "string",
            "rank": "string",
            "code": "string",
            "authorship": "string",
            "genericName": "string",
            "infragenericEpithet": "string",
            "specificEpithet": "string",
            "infraspecificEpithet": "string",
            "formattedName": "string"
          },
          "taxonomicStatus": "string",
          "classification": [
            {
              "key": "string",
              "name": "string",
              "rank": "string",
              "authorship": "string"
            }
          ],
          "iucnRedListCategoryCode": "string",
          "issues": [
            "string"
          ]
        }
      },
      "scientificName": "string",
      "scientificNameAuthorship": "string",
      "acceptedScientificName": "string",
      "kingdom": "string",
      "phylum": "string",
      "order": "string",
      "family": "string",
      "genus": "string",
      "subgenus": "string",
      "species": "string",
      "genericName": "string",
      "specificEpithet": "string",
      "infraspecificEpithet": "string",
      "taxonRank": "DOMAIN",
      "taxonomicStatus": "ACCEPTED",
      "iucnRedListCategory": "string",
      "dateIdentified": "2025-10-15T20:18:04.120Z",
      "decimalLatitude": 0,
      "decimalLongitude": 0,
      "coordinatePrecision": 0,
      "coordinateUncertaintyInMeters": 0,
      "elevation": 0,
      "elevationAccuracy": 0,
      "depth": 0,
      "depthAccuracy": 0,
      "continent": "AFRICA",
      "stateProvince": "string",
      "gadm": {
        "level0": {
          "gid": "string",
          "name": "string"
        },
        "level1": {
          "gid": "string",
          "name": "string"
        },
        "level2": {
          "gid": "string",
          "name": "string"
        },
        "level3": {
          "gid": "string",
          "name": "string"
        }
      },
      "waterBody": "string",
      "distanceFromCentroidInMeters": 0,
      "higherGeography": "string",
      "georeferencedBy": "string",
      "year": 0,
      "month": 0,
      "day": 0,
      "eventDate": {
        "from": {},
        "to": {}
      },
      "startDayOfYear": 0,
      "endDayOfYear": 0,
      "typeStatus": "string",
      "typifiedName": "string",
      "issues": [
        "ZERO_COORDINATE"
      ],
      "modified": "2025-10-15T20:18:04.120Z",
      "lastInterpreted": "2025-10-15T20:18:04.120Z",
      "references": "string",
      "license": "CC0_1_0",
      "organismQuantity": 0,
      "organismQuantityType": "string",
      "sampleSizeUnit": "string",
      "sampleSizeValue": 0,
      "relativeOrganismQuantity": 0,
      "isSequenced": true,
      "associatedSequences": "string",
      "identifiers": [
        {
          "identifier": "string",
          "title": "string",
          "type": "URL",
          "identifierLink": "string"
        }
      ],
      "media": [
        {
          "type": "StillImage",
          "format": "string",
          "references": "string",
          "title": "string",
          "description": "string",
          "source": "string",
          "audience": "string",
          "created": "2025-10-15T20:18:04.120Z",
          "creator": "string",
          "contributor": "string",
          "publisher": "string",
          "license": "string",
          "rightsHolder": "string",
          "identifier": "string"
        }
      ],
      "facts": [
        {
          "id": "string",
          "type": "string",
          "value": "string",
          "unit": "string",
          "accuracy": "string",
          "method": "string",
          "determinedBy": "string",
          "determinedDate": "string",
          "remarks": "string"
        }
      ],
      "relations": [
        {
          "id": "string",
          "occurrenceId": 0,
          "relatedOccurrenceId": 0,
          "type": "string",
          "accordingTo": "string",
          "establishedDate": "string",
          "remarks": "string"
        }
      ],
      "institutionKey": "string",
      "collectionKey": "string",
      "isInCluster": true,
      "datasetID": "string",
      "datasetName": "string",
      "otherCatalogNumbers": "string",
      "earliestEonOrLowestEonothem": "string",
      "latestEonOrHighestEonothem": "string",
      "earliestEraOrLowestErathem": "string",
      "latestEraOrHighestErathem": "string",
      "earliestPeriodOrLowestSystem": "string",
      "latestPeriodOrHighestSystem": "string",
      "earliestEpochOrLowestSeries": "string",
      "latestEpochOrHighestSeries": "string",
      "earliestAgeOrLowestStage": "string",
      "latestAgeOrHighestStage": "string",
      "lowestBiostratigraphicZone": "string",
      "highestBiostratigraphicZone": "string",
      "group": "string",
      "formation": "string",
      "member": "string",
      "bed": "string",
      "recordedBy": "string",
      "identifiedBy": "string",
      "preparations": "string",
      "samplingProtocol": "string",
      "dnaSequenceID": [
        "string"
      ],
      "geodeticDatum": "string",
      "class": "string",
      "countryCode": "AF",
      "recordedByIDs": [
        {
          "type": "ORCID",
          "value": "string"
        }
      ],
      "identifiedByIDs": [
        {
          "type": "ORCID",
          "value": "string"
        }
      ],
      "gbifRegion": "AFRICA",
      "country": "string",
      "publishedByGbifRegion": "AFRICA"
    }
  ],
  "facets": [
    {
      "field": "string",
      "counts": [
        {
          "name": "string",
          "count": 0
        }
      ]
    }
  ]
}
```
</details>
</div>

## OpenAQ

- Description of API: https://api.openaq.org/docs
- License: Licenses for specific measurement data are queryable through the API
- Size: uncertain
- The API has many endpoints, but seems generally centered around "measurements", which can be located by
geographical location, type, instrument, source, etc. (all described in one OpenAPI spec)
- Seems to include detailed information about source, manner of collection

| Data Product    | OpenAPI spec URL                    |
|-----------------|-------------------------------------|
| AQ Measurements | https://api.openaq.org/openapi.json |

- env-agents searches by location and "parameter" (NO2, NO, PM2.5, etc.)

### OpenAQ Query Example

#### Location

##### Request

```bash
curl -X 'GET' \
  'https://api.openaq.org/v3/locations?coordinates=33.8%2C-116.5&radius=10000&limit=100&page=1&order_by=id&sort_order=asc' \
  -H 'accept: application/json' \
  -H "X-API-Key: ${OPENAQ_API_KEY}"
```
##### Response

<div>
<details>
<summary>Click to expand</summary>

```json
{
  "meta": {
    "name": "openaq-api",
    "website": "/",
    "page": 1,
    "limit": 100,
    "found": 4
  },
  "results": [
    {
      "id": 1011,
      "name": "Palm Springs - Fire",
      "locality": null,
      "timezone": "America/Los_Angeles",
      "country": {
        "id": 155,
        "code": "US",
        "name": "United States"
      },
      "owner": {
        "id": 4,
        "name": "Unknown Governmental Organization"
      },
      "provider": {
        "id": 119,
        "name": "AirNow"
      },
      "isMobile": false,
      "isMonitor": true,
      "instruments": [
        {
          "id": 2,
          "name": "Government Monitor"
        }
      ],
      "sensors": [
        {
          "id": 1820,
          "name": "o3 ppm",
          "parameter": {
            "id": 10,
            "name": "o3",
            "units": "ppm",
            "displayName": "O₃"
          }
        },
        {
          "id": 1822,
          "name": "pm10 µg/m³",
          "parameter": {
            "id": 1,
            "name": "pm10",
            "units": "µg/m³",
            "displayName": "PM10"
          }
        }
      ],
      "coordinates": {
        "latitude": 33.8497,
        "longitude": -116.54
      },
      "licenses": [
        {
          "id": 33,
          "name": "US Public Domain",
          "attribution": {
            "name": "Unknown Governmental Organization",
            "url": null
          },
          "dateFrom": "2016-01-30",
          "dateTo": null
        }
      ],
      "bounds": [
        -116.54,
        33.8497,
        -116.54,
        33.8497
      ],
      "distance": 6640.90375304,
      "datetimeFirst": {
        "utc": "2016-03-06T20:00:00Z",
        "local": "2016-03-06T12:00:00-08:00"
      },
      "datetimeLast": {
        "utc": "2016-11-09T21:00:00Z",
        "local": "2016-11-09T13:00:00-08:00"
      }
    },
    {
      "id": 7974,
      "name": "Palm Springs - Fire",
      "locality": "Riverside-San Bernardino-Ontario",
      "timezone": "America/Los_Angeles",
      "country": {
        "id": 155,
        "code": "US",
        "name": "United States"
      },
      "owner": {
        "id": 4,
        "name": "Unknown Governmental Organization"
      },
      "provider": {
        "id": 119,
        "name": "AirNow"
      },
      "isMobile": false,
      "isMonitor": true,
      "instruments": [
        {
          "id": 2,
          "name": "Government Monitor"
        }
      ],
      "sensors": [
        {
          "id": 25461,
          "name": "co ppm",
          "parameter": {
            "id": 8,
            "name": "co",
            "units": "ppm",
            "displayName": "CO"
          }
        },
        {
          "id": 4272341,
          "name": "no ppm",
          "parameter": {
            "id": 35,
            "name": "no",
            "units": "ppm",
            "displayName": "NO"
          }
        },
        {
          "id": 25462,
          "name": "no2 ppm",
          "parameter": {
            "id": 7,
            "name": "no2",
            "units": "ppm",
            "displayName": "NO₂"
          }
        },
        {
          "id": 4272473,
          "name": "nox ppm",
          "parameter": {
            "id": 19840,
            "name": "nox",
            "units": "ppm",
            "displayName": "NOx"
          }
        },
        {
          "id": 25463,
          "name": "o3 ppm",
          "parameter": {
            "id": 10,
            "name": "o3",
            "units": "ppm",
            "displayName": "O₃"
          }
        },
        {
          "id": 23102,
          "name": "pm10 µg/m³",
          "parameter": {
            "id": 1,
            "name": "pm10",
            "units": "µg/m³",
            "displayName": "PM10"
          }
        }
      ],
      "coordinates": {
        "latitude": 33.85260499999999,
        "longitude": -116.54096500000001
      },
      "licenses": [
        {
          "id": 33,
          "name": "US Public Domain",
          "attribution": {
            "name": "Unknown Governmental Organization",
            "url": null
          },
          "dateFrom": "2016-01-30",
          "dateTo": null
        }
      ],
      "bounds": [
        -116.54096500000001,
        33.85260499999999,
        -116.54096500000001,
        33.85260499999999
      ],
      "distance": 6958.96089894,
      "datetimeFirst": {
        "utc": "2016-11-14T18:00:00Z",
        "local": "2016-11-14T10:00:00-08:00"
      },
      "datetimeLast": {
        "utc": "2025-10-15T19:00:00Z",
        "local": "2025-10-15T12:00:00-07:00"
      }
    },
    {
      "id": 3069196,
      "name": "EBAM-9",
      "locality": "SC0",
      "timezone": "America/Los_Angeles",
      "country": {
        "id": 155,
        "code": "US",
        "name": "United States"
      },
      "owner": {
        "id": 4,
        "name": "Unknown Governmental Organization"
      },
      "provider": {
        "id": 119,
        "name": "AirNow"
      },
      "isMobile": false,
      "isMonitor": true,
      "instruments": [
        {
          "id": 2,
          "name": "Government Monitor"
        }
      ],
      "sensors": [
        {
          "id": 10658798,
          "name": "pm10 µg/m³",
          "parameter": {
            "id": 1,
            "name": "pm10",
            "units": "µg/m³",
            "displayName": "PM10"
          }
        }
      ],
      "coordinates": {
        "latitude": 33.85273,
        "longitude": -116.48087
      },
      "licenses": [
        {
          "id": 33,
          "name": "US Public Domain",
          "attribution": {
            "name": "Unknown Governmental Organization",
            "url": null
          },
          "dateFrom": "2016-01-30",
          "dateTo": null
        }
      ],
      "bounds": [
        -116.48087,
        33.85273,
        -116.48087,
        33.85273
      ],
      "distance": 6110.99452348,
      "datetimeFirst": {
        "utc": "2024-09-17T20:00:00Z",
        "local": "2024-09-17T13:00:00-07:00"
      },
      "datetimeLast": {
        "utc": "2024-09-18T19:00:00Z",
        "local": "2024-09-18T12:00:00-07:00"
      }
    },
    {
      "id": 3069197,
      "name": "EBAM-9",
      "locality": "SC0",
      "timezone": "America/Los_Angeles",
      "country": {
        "id": 155,
        "code": "US",
        "name": "United States"
      },
      "owner": {
        "id": 4,
        "name": "Unknown Governmental Organization"
      },
      "provider": {
        "id": 119,
        "name": "AirNow"
      },
      "isMobile": false,
      "isMonitor": true,
      "instruments": [
        {
          "id": 2,
          "name": "Government Monitor"
        }
      ],
      "sensors": [
        {
          "id": 10659114,
          "name": "pm10 µg/m³",
          "parameter": {
            "id": 1,
            "name": "pm10",
            "units": "µg/m³",
            "displayName": "PM10"
          }
        }
      ],
      "coordinates": {
        "latitude": 33.85273,
        "longitude": -116.48087
      },
      "licenses": [
        {
          "id": 33,
          "name": "US Public Domain",
          "attribution": {
            "name": "Unknown Governmental Organization",
            "url": null
          },
          "dateFrom": "2016-01-30",
          "dateTo": null
        }
      ],
      "bounds": [
        -116.48087,
        33.85273,
        -116.48087,
        33.85273
      ],
      "distance": 6110.99452348,
      "datetimeFirst": {
        "utc": "2024-09-17T20:00:00Z",
        "local": "2024-09-17T13:00:00-07:00"
      },
      "datetimeLast": {
        "utc": "2025-10-15T19:00:00Z",
        "local": "2025-10-15T12:00:00-07:00"
      }
    }
  ]
}
```
</details>
</div>

#### Sensor by location

##### Request

```bash
curl -X 'GET' \
  'https://api.openaq.org/v3/locations/1011/sensors' \
  -H 'accept: application/json' \
  -H "X-API-key: ${OPENAQ_API_KEY}"
```

#### Response

<div>
<details>
<summary>Click to expand</summary>

```json
{
  "meta": {
    "name": "openaq-api",
    "website": "/",
    "page": 1,
    "limit": 100,
    "found": 2
  },
  "results": [
    {
      "id": 1820,
      "name": "o3 ppm",
      "parameter": {
        "id": 10,
        "name": "o3",
        "units": "ppm",
        "displayName": "O₃"
      },
      "datetimeFirst": {
        "utc": "2016-03-06T20:00:00Z",
        "local": "2016-03-06T12:00:00-08:00"
      },
      "datetimeLast": {
        "utc": "2016-11-09T17:00:00Z",
        "local": "2016-11-09T09:00:00-08:00"
      },
      "coverage": {
        "expectedCount": 1,
        "expectedInterval": "01:00:00",
        "observedCount": 4929,
        "observedInterval": "4929:00:00",
        "percentComplete": 492900.0,
        "percentCoverage": 492900.0,
        "datetimeFrom": {
          "utc": "2016-03-06T20:00:00Z",
          "local": "2016-03-06T12:00:00-08:00"
        },
        "datetimeTo": {
          "utc": "2016-11-09T17:00:00Z",
          "local": "2016-11-09T09:00:00-08:00"
        }
      },
      "latest": {
        "datetime": {
          "utc": "2016-11-09T17:00:00Z",
          "local": "2016-11-09T09:00:00-08:00"
        },
        "value": 0.027,
        "coordinates": {
          "latitude": 33.8497,
          "longitude": -116.54
        }
      },
      "summary": {
        "min": 0.0,
        "q02": null,
        "q25": null,
        "median": null,
        "q75": null,
        "q98": null,
        "max": 0.104,
        "avg": 0.04798316088456065,
        "sd": null
      }
    },
    {
      "id": 1822,
      "name": "pm10 µg/m³",
      "parameter": {
        "id": 1,
        "name": "pm10",
        "units": "µg/m³",
        "displayName": "PM10"
      },
      "datetimeFirst": {
        "utc": "2016-03-06T20:00:00Z",
        "local": "2016-03-06T12:00:00-08:00"
      },
      "datetimeLast": {
        "utc": "2016-11-09T21:00:00Z",
        "local": "2016-11-09T13:00:00-08:00"
      },
      "coverage": {
        "expectedCount": 1,
        "expectedInterval": "01:00:00",
        "observedCount": 4742,
        "observedInterval": "4742:00:00",
        "percentComplete": 474200.0,
        "percentCoverage": 474200.0,
        "datetimeFrom": {
          "utc": "2016-03-06T20:00:00Z",
          "local": "2016-03-06T12:00:00-08:00"
        },
        "datetimeTo": {
          "utc": "2016-11-09T21:00:00Z",
          "local": "2016-11-09T13:00:00-08:00"
        }
      },
      "latest": {
        "datetime": {
          "utc": "2016-11-09T21:00:00Z",
          "local": "2016-11-09T13:00:00-08:00"
        },
        "value": 5.0,
        "coordinates": {
          "latitude": 33.8497,
          "longitude": -116.54
        }
      },
      "summary": {
        "min": 0.0,
        "q02": null,
        "q25": null,
        "median": null,
        "q75": null,
        "q98": null,
        "max": 856.0,
        "avg": 26.36714466469844,
        "sd": null
      }
    }
  ]
}
```
</details>
</div>

#### Measurements by Sensor

##### Resquest

```bash
curl -X 'GET' \
  'https://api.openaq.org/v3/sensors/1820/hours/daily?datetime_to=2016-10-17&datetime_from=2016-10-14&limit=100&page=1' \
  -H 'accept: application/json' \
  -H "X-API-Key: ${OPENAQ_API_KEY}"
```
##### Response

<div>
<details>
<summary> Click to expand</summary>

```json
{
  "meta": {
    "name": "openaq-api",
    "website": "/",
    "page": 1,
    "limit": 100,
    "found": 3
  },
  "results": [
    {
      "value": 0.0461,
      "flagInfo": {
        "hasFlags": false
      },
      "parameter": {
        "id": 10,
        "name": "o3",
        "units": "ppm",
        "displayName": null
      },
      "period": {
        "label": "1 day",
        "interval": "24:00:00",
        "datetimeFrom": {
          "utc": "2016-10-14T07:00:00Z",
          "local": "2016-10-14T00:00:00-07:00"
        },
        "datetimeTo": {
          "utc": "2016-10-15T07:00:00Z",
          "local": "2016-10-15T00:00:00-07:00"
        }
      },
      "coordinates": null,
      "summary": {
        "min": 0.012,
        "q02": 0.01384,
        "q25": 0.03475,
        "median": 0.0445,
        "q75": 0.059000000000000004,
        "q98": 0.07315999999999999,
        "max": 0.075,
        "avg": 0.04612500000000002,
        "sd": 0.017845502417184533
      },
      "coverage": {
        "expectedCount": 24,
        "expectedInterval": "24:00:00",
        "observedCount": 24,
        "observedInterval": "24:00:00",
        "percentComplete": 100.0,
        "percentCoverage": 100.0,
        "datetimeFrom": {
          "utc": "2016-10-14T07:00:00Z",
          "local": "2016-10-14T00:00:00-07:00"
        },
        "datetimeTo": {
          "utc": "2016-10-15T07:00:00Z",
          "local": "2016-10-15T00:00:00-07:00"
        }
      }
    },
    {
      "value": 0.0415,
      "flagInfo": {
        "hasFlags": false
      },
      "parameter": {
        "id": 10,
        "name": "o3",
        "units": "ppm",
        "displayName": null
      },
      "period": {
        "label": "1 day",
        "interval": "24:00:00",
        "datetimeFrom": {
          "utc": "2016-10-15T07:00:00Z",
          "local": "2016-10-15T00:00:00-07:00"
        },
        "datetimeTo": {
          "utc": "2016-10-16T07:00:00Z",
          "local": "2016-10-16T00:00:00-07:00"
        }
      },
      "coordinates": null,
      "summary": {
        "min": 0.027,
        "q02": 0.027,
        "q25": 0.0295,
        "median": 0.038,
        "q75": 0.053000000000000005,
        "q98": 0.06628,
        "max": 0.067,
        "avg": 0.04152631578947369,
        "sd": 0.0143850555981339
      },
      "coverage": {
        "expectedCount": 24,
        "expectedInterval": "24:00:00",
        "observedCount": 19,
        "observedInterval": "19:00:00",
        "percentComplete": 79.0,
        "percentCoverage": 79.0,
        "datetimeFrom": {
          "utc": "2016-10-15T07:00:00Z",
          "local": "2016-10-15T00:00:00-07:00"
        },
        "datetimeTo": {
          "utc": "2016-10-16T07:00:00Z",
          "local": "2016-10-16T00:00:00-07:00"
        }
      }
    },
    {
      "value": 0.0324,
      "flagInfo": {
        "hasFlags": false
      },
      "parameter": {
        "id": 10,
        "name": "o3",
        "units": "ppm",
        "displayName": null
      },
      "period": {
        "label": "1 day",
        "interval": "24:00:00",
        "datetimeFrom": {
          "utc": "2016-10-16T07:00:00Z",
          "local": "2016-10-16T00:00:00-07:00"
        },
        "datetimeTo": {
          "utc": "2016-10-17T07:00:00Z",
          "local": "2016-10-17T00:00:00-07:00"
        }
      },
      "coordinates": null,
      "summary": {
        "min": 0.016,
        "q02": 0.01784,
        "q25": 0.024,
        "median": 0.035,
        "q75": 0.04025,
        "q98": 0.043539999999999995,
        "max": 0.044,
        "avg": 0.03241666666666668,
        "sd": 0.00861200712184254
      },
      "coverage": {
        "expectedCount": 24,
        "expectedInterval": "24:00:00",
        "observedCount": 24,
        "observedInterval": "24:00:00",
        "percentComplete": 100.0,
        "percentCoverage": 100.0,
        "datetimeFrom": {
          "utc": "2016-10-16T07:00:00Z",
          "local": "2016-10-16T00:00:00-07:00"
        },
        "datetimeTo": {
          "utc": "2016-10-17T07:00:00Z",
          "local": "2016-10-17T00:00:00-07:00"
        }
      }
    }
  ]
}
```
</details>
</div>

## USGS NWIS

- USGS National Water Information System
- There is a note on the [USGS Surface Water Daily Data page](https://waterdata.usgs.gov/nwis/dv?referred_module=sw) that says it (NWIS) is being decommisioned "in the future" and suggests using "WDFN" (maybe "Water Data for the Nation"?)
- Adam's code seems to use the original service, which doesn't appear to have an OpenAPI spec
  - My guess is that env-agents used more investigative methods to discover the API of NWIS
- There does appear to be a documented API for WDFN data here: https://api.waterdata.usgs.gov/ogcapi/v0/openapi?f=html with OpenAPI specs
  - It includes daily data, which is what env-agents seems to have been using
- The information here is for WDFN

| Data Product    | OpenAPI spec URL                                          |
|-----------------|-----------------------------------------------------------|
| all water data  | https://api.waterdata.usgs.gov/ogcapi/v0/openapi?f=html#/ |

- there are many documented endpoints, but `daily` and `latest-continuous` may be the most relevant
- it's not clear what the difference between `daily` and `latest-daily` endpoints are
- there are endpoints that look like they contain metadata for measurements (e.g., `time-series-metadata`, `monitoring-locations`, etc.)

### USGS WDFN Query Example

#### Feature

##### Request

```bash
curl -X 'GET' \
  'https://api.waterdata.usgs.gov/ogcapi/v0/collections/daily/items?f=json&lang=en-US&limit=10&properties=id,time_series_id,monitoring_location_id,parameter_code,statistic_id,time,value,unit_of_measure,approval_status,qualifier,last_modified&skipGeometry=false&offset=0&datetime=2018-02-12T00%3A00%3A00Z%2F2018-03-05T12%3A31%3A12Z' \
  -H 'accept: application/geo+json'
```

##### Response

<div>
<details>
<summary>Click to expand</summary>

```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "properties": {
        "value": "114",
        "unit_of_measure": "uS/cm",
        "parameter_code": "00095",
        "statistic_id": "00001",
        "monitoring_location_id": "USGS-02081094",
        "time_series_id": "f4770ab8aee64721914b0c46a0e1493b",
        "time": "2018-02-23",
        "approval_status": "Approved",
        "qualifier": null,
        "last_modified": "2025-06-06T16:31:58.944425+00:00"
      },
      "id": "0000093d-9535-4bdd-8530-12b9b8d47411",
      "geometry": {
        "type": "Point",
        "coordinates": [
          -76.8927777777778,
          35.8130555555556
        ]
      }
    },
    {
      "type": "Feature",
      "properties": {
        "value": "0.46",
        "unit_of_measure": "ft",
        "parameter_code": "00065",
        "statistic_id": "00001",
        "monitoring_location_id": "USGS-08080700",
        "time_series_id": "57efa232a7ce44b1844596de75104b74",
        "time": "2018-03-01",
        "approval_status": "Approved",
        "qualifier": null,
        "last_modified": "2025-07-04T19:03:40.447175+00:00"
      },
      "id": "00005171-76fe-434a-b31c-b30e1c7f9b26",
      "geometry": {
        "type": "Point",
        "coordinates": [
          -101.7026747676,
          34.1789604828062
        ]
      }
    },
    {
      "type": "Feature",
      "properties": {
        "value": "13.1",
        "unit_of_measure": "degC",
        "parameter_code": "00010",
        "statistic_id": "00002",
        "monitoring_location_id": "USGS-08065350",
        "time_series_id": "57038b647e2c4c4aa698643b197aa44d",
        "time": "2018-02-22",
        "approval_status": "Approved",
        "qualifier": null,
        "last_modified": "2025-07-04T19:53:41.553856+00:00"
      },
      "id": "00006381-0a7b-42ee-95e5-5126e05ffde0",
      "geometry": {
        "type": "Point",
        "coordinates": [
          -95.6563406910259,
          31.3385131853307
        ]
      }
    },
    {
      "type": "Feature",
      "properties": {
        "value": "14.0",
        "unit_of_measure": "degC",
        "parameter_code": "00010",
        "statistic_id": "00002",
        "monitoring_location_id": "USGS-02110770",
        "time_series_id": "236ab8e84b9140babea1871e2cd763f1",
        "time": "2018-02-12",
        "approval_status": "Approved",
        "qualifier": null,
        "last_modified": "2025-03-11T18:32:15.616937+00:00"
      },
      "id": "00007ea3-51f6-4ad5-8549-3e2895bb718d",
      "geometry": {
        "type": "Point",
        "coordinates": [
          -78.7186287074082,
          33.8212834688731
        ]
      }
    },
    {
      "type": "Feature",
      "properties": {
        "value": "420.69",
        "unit_of_measure": "ft",
        "parameter_code": "72019",
        "statistic_id": "00002",
        "monitoring_location_id": "USGS-345758106364003",
        "time_series_id": "2a940062364e463096cbf61169981f2d",
        "time": "2018-02-18",
        "approval_status": "Approved",
        "qualifier": null,
        "last_modified": "2025-07-05T14:26:40.752284+00:00"
      },
      "id": "0000b50b-4dbd-453c-b584-dfce6470dc06",
      "geometry": {
        "type": "Point",
        "coordinates": [
          -106.61168611111111,
          34.966258333333336
        ]
      }
    },
    {
      "type": "Feature",
      "properties": {
        "value": "2.59",
        "unit_of_measure": "ft",
        "parameter_code": "00065",
        "statistic_id": "00003",
        "monitoring_location_id": "USGS-08130500",
        "time_series_id": "792266f983804ac4aa851587e91ccfb7",
        "time": "2018-02-16",
        "approval_status": "Approved",
        "qualifier": null,
        "last_modified": "2025-03-11T20:33:01.030490+00:00"
      },
      "id": "0000cb9b-b3d2-40f6-827d-ddd1c73a2068",
      "geometry": {
        "type": "Point",
        "coordinates": [
          -100.630931765048,
          31.2740546472882
        ]
      }
    },
    {
      "type": "Feature",
      "properties": {
        "value": "0.00",
        "unit_of_measure": "ft^3/s",
        "parameter_code": "00060",
        "statistic_id": "00003",
        "monitoring_location_id": "USGS-09424150",
        "time_series_id": "497e78c0c1a84eecbfb4b173add9923a",
        "time": "2018-02-21",
        "approval_status": "Approved",
        "qualifier": null,
        "last_modified": "2025-07-05T00:14:52.573320+00:00"
      },
      "id": "0000cf23-e607-4857-8c23-3056f34fdd48",
      "geometry": {
        "type": "Point",
        "coordinates": [
          -114.157170161686,
          34.3161256441171
        ]
      }
    },
    {
      "type": "Feature",
      "properties": {
        "value": "52.0",
        "unit_of_measure": "ft^3/s",
        "parameter_code": "00060",
        "statistic_id": "00003",
        "monitoring_location_id": "USGS-11427760",
        "time_series_id": "c82d9f6ce66f4587b18397be292c0cd6",
        "time": "2018-02-22",
        "approval_status": "Approved",
        "qualifier": null,
        "last_modified": "2025-07-05T06:24:04.000595+00:00"
      },
      "id": "0000cf9a-7c33-4e18-b326-b5303d4950ea",
      "geometry": {
        "type": "Point",
        "coordinates": [
          -120.595481215948,
          39.0251806326975
        ]
      }
    },
    {
      "type": "Feature",
      "properties": {
        "value": "0.13",
        "unit_of_measure": "in",
        "parameter_code": "00045",
        "statistic_id": "00006",
        "monitoring_location_id": "USGS-03051000",
        "time_series_id": "5011abe2876c413a9c452a625ae6b763",
        "time": "2018-03-02",
        "approval_status": "Approved",
        "qualifier": null,
        "last_modified": "2025-03-11T22:14:38.129449+00:00"
      },
      "id": "0000e1d8-29f7-4937-9ecf-47a10e14f4b1",
      "geometry": {
        "type": "Point",
        "coordinates": [
          -79.9359079923468,
          39.0292694107684
        ]
      }
    },
    {
      "type": "Feature",
      "properties": {
        "value": "6.61",
        "unit_of_measure": "ft",
        "parameter_code": "00065",
        "statistic_id": "00003",
        "monitoring_location_id": "USGS-02234400",
        "time_series_id": "853144f5015144bbb5fcd223eb69da2c",
        "time": "2018-03-04",
        "approval_status": "Approved",
        "qualifier": null,
        "last_modified": "2025-07-04T02:21:58.643447+00:00"
      },
      "id": "0000e937-1c3f-4976-b507-91ecd493f642",
      "geometry": {
        "type": "Point",
        "coordinates": [
          -81.2906221110044,
          28.7041629070688
        ]
      }
    }
  ],
  "numberReturned": 10,
  "links": [
    {
      "rel": "next",
      "href": "https://api.waterdata.usgs.gov/ogcapi/v0/collections/daily/items?cursor=MDAwMGU5MzctMWMzZi00OTc2LWI1MDctOTFlY2Q0OTNmNjQy&lang=en-US&limit=10&properties=id,time_series_id,monitoring_location_id,parameter_code,statistic_id,time,value,unit_of_measure,approval_status,qualifier,last_modified&skipGeometry=false&datetime=2018-02-12T00%3A00%3A00Z%2F2018-03-05T12%3A31%3A12Z",
      "type": "application/geo+json",
      "title": "Items (next)"
    },
    {
      "type": "application/geo+json",
      "rel": "self",
      "title": "This document as GeoJSON",
      "href": "https://api.waterdata.usgs.gov/ogcapi/v0/collections/daily/items?f=json&lang=en-US&limit=10&properties=id,time_series_id,monitoring_location_id,parameter_code,statistic_id,time,value,unit_of_measure,approval_status,qualifier,last_modified&skipGeometry=false&datetime=2018-02-12T00%3A00%3A00Z%2F2018-03-05T12%3A31%3A12Z"
    },
    {
      "rel": "alternate",
      "type": "application/ld+json",
      "title": "This document as RDF (JSON-LD)",
      "href": "https://api.waterdata.usgs.gov/ogcapi/v0/collections/daily/items?f=jsonld&lang=en-US&limit=10&properties=id,time_series_id,monitoring_location_id,parameter_code,statistic_id,time,value,unit_of_measure,approval_status,qualifier,last_modified&skipGeometry=false&datetime=2018-02-12T00%3A00%3A00Z%2F2018-03-05T12%3A31%3A12Z"
    },
    {
      "type": "text/html",
      "rel": "alternate",
      "title": "This document as HTML",
      "href": "https://api.waterdata.usgs.gov/ogcapi/v0/collections/daily/items?f=html&lang=en-US&limit=10&properties=id,time_series_id,monitoring_location_id,parameter_code,statistic_id,time,value,unit_of_measure,approval_status,qualifier,last_modified&skipGeometry=false&datetime=2018-02-12T00%3A00%3A00Z%2F2018-03-05T12%3A31%3A12Z"
    },
    {
      "type": "application/json",
      "title": "Daily values",
      "rel": "collection",
      "href": "https://api.waterdata.usgs.gov/ogcapi/v0/collections/daily"
    }
  ],
  "timeStamp": "2025-10-15T22:02:04.134794Z"
}
```
</details>
</div>

#### Parameter

- Parameter search doesn't return a `json` response. You can choose from html or csv

##### Request

```bash
curl -X 'GET' \
  'https://help.waterdata.usgs.gov/code/parameter_cd_nm_query?parm_nm_cd=00095&fmt=rdb&inline=true'
```

##### Response

(buried in html)

```
# National Water Information System
# 2025/10/15
#
#
# Date Retrieved: USGS Water Data for the Nation Help System
#
parameter_cd    group   parm_nm epa_equivalence result_statistical_basis        result_time_basis       result_weight_basis     result_particle_size_basis      result_sample_fraction  result_temperature_basis        CASRN   SRSName parm_unit
5s      8s      90s     5s      0s      0s      0s      0s      5s      8s      1s      20s     10s
00095   Physical        Specific conductance, water, unfiltered, microsiemens per centimeter at 25 degrees Celsius      Agree                                   Total   25 deg C                Specific conductance    uS/cm @25C
```

## WQP

- "The Water Quality Portal (WQP) is the premiere source of discrete water-quality data in the United States and beyond. This cooperative service integrates publicly available water-quality data from the United States Geological Survey (USGS), the Environmental Protection Agency (EPA), and over 400 state, federal, tribal, and local agencies"
- Does not appear to have an OpenAPI spec
- Allows you to interactively build up a query and shows the request as a string (https://www.waterqualitydata.us/#advanced=true)

### WQP Query Example

#### Sample Results (biological metadata)

##### Request

```bash
curl -X POST --header 'Content-Type: application/json' --header 'Accept: application/zip' -d '{"within":"50","lat":"33.8","long":"-116.5","startDateLo":"08-01-2023","startDateHi":"08-10-2023","dataProfile":"biological","providers":["NWIS","STORET"]}' 'https://www.waterqualitydata.us/data/Result/search?mimeType=csv&zip=yes' --output wqp.data.csv.zip
```

##### Response

(after unzipping)

<div>
<details>
<summary>Click to expand</summary>

```csv
OrganizationIdentifier,OrganizationFormalName,ActivityIdentifier,ActivityTypeCode,ActivityMediaName,ActivityMediaSubdivisionName,ActivityStartDate,ActivityStartTime/Time,ActivityStartTime/TimeZoneCode,ActivityEndDate,ActivityEndTime/Time,ActivityEndTime/TimeZoneCode,ActivityRelativeDepthName,ActivityDepthHeightMeasure/MeasureValue,ActivityDepthHeightMeasure/MeasureUnitCode,ActivityDepthAltitudeReferencePointText,ActivityTopDepthHeightMeasure/MeasureValue,ActivityTopDepthHeightMeasure/MeasureUnitCode,ActivityBottomDepthHeightMeasure/MeasureValue,ActivityBottomDepthHeightMeasure/MeasureUnitCode,ProjectIdentifier,ActivityConductingOrganizationText,MonitoringLocationIdentifier,ActivityCommentText,SampleAquifer,HydrologicCondition,HydrologicEvent,ActivityLocation/LatitudeMeasure,ActivityLocation/LongitudeMeasure,ActivityLocation/SourceMapScaleNumeric,ActivityLocation/HorizontalAccuracyMeasure/MeasureValue,ActivityLocation/HorizontalAccuracyMeasure/MeasureUnitCode,ActivityLocation/HorizontalCollectionMethodName,ActivityLocation/HorizontalCoordinateReferenceSystemDatumName,AssemblageSampledName,CollectionDuration/MeasureValue,CollectionDuration/MeasureUnitCode,SamplingComponentName,SamplingComponentPlaceInSeriesNumeric,ReachLengthMeasure/MeasureValue,ReachLengthMeasure/MeasureUnitCode,ReachWidthMeasure/MeasureValue,ReachWidthMeasure/MeasureUnitCode,PassCount,NetTypeName,NetSurfaceAreaMeasure/MeasureValue,NetSurfaceAreaMeasure/MeasureUnitCode,NetMeshSizeMeasure/MeasureValue,NetMeshSizeMeasure/MeasureUnitCode,BoatSpeedMeasure/MeasureValue,BoatSpeedMeasure/MeasureUnitCode,CurrentSpeedMeasure/MeasureValue,CurrentSpeedMeasure/MeasureUnitCode,ToxicityTestType,SampleCollectionMethod/MethodIdentifier,SampleCollectionMethod/MethodIdentifierContext,SampleCollectionMethod/MethodName,SampleCollectionMethod/MethodQualifierTypeName,SampleCollectionMethod/MethodDescriptionText,SampleCollectionEquipmentName,SampleCollectionMethod/SampleCollectionEquipmentCommentText,SamplePreparationMethod/MethodIdentifier,SamplePreparationMethod/MethodIdentifierContext,SamplePreparationMethod/MethodName,SamplePreparationMethod/MethodQualifierTypeName,SamplePreparationMethod/MethodDescriptionText,SampleContainerTypeName,SampleContainerColorName,ChemicalPreservativeUsedName,ThermalPreservativeUsedName,SampleTransportStorageDescription,DataLoggerLine,ResultDetectionConditionText,MethodSpecificationName,CharacteristicName,ResultSampleFractionText,ResultMeasureValue,ResultMeasure/MeasureUnitCode,MeasureQualifierCode,ResultStatusIdentifier,StatisticalBaseCode,ResultValueTypeName,ResultWeightBasisText,ResultTimeBasisText,ResultTemperatureBasisText,ResultParticleSizeBasisText,PrecisionValue,DataQuality/BiasValue,ConfidenceIntervalValue,UpperConfidenceLimitValue,LowerConfidenceLimitValue,ResultCommentText,USGSPCode,ResultDepthHeightMeasure/MeasureValue,ResultDepthHeightMeasure/MeasureUnitCode,ResultDepthAltitudeReferencePointText,ResultSamplingPointName,BiologicalIntentName,BiologicalIndividualIdentifier,SubjectTaxonomicName,UnidentifiedSpeciesIdentifier,SampleTissueAnatomyName,GroupSummaryCountWeight/MeasureValue,GroupSummaryCountWeight/MeasureUnitCode,CellFormName,CellShapeName,HabitName,VoltismName,TaxonomicPollutionTolerance,TaxonomicPollutionToleranceScaleText,TrophicLevelName,FunctionalFeedingGroupName,TaxonomicDetailsCitation/ResourceTitleName,TaxonomicDetailsCitation/ResourceCreatorName,TaxonomicDetailsCitation/ResourceSubjectText,TaxonomicDetailsCitation/ResourcePublisherName,TaxonomicDetailsCitation/ResourceDate,TaxonomicDetailsCitation/ResourceIdentifier,FrequencyClassDescriptorCode,FrequencyClassDescriptorUnitCode,LowerClassBoundValue,UpperClassBoundValue,ResultAnalyticalMethod/MethodIdentifier,ResultAnalyticalMethod/MethodIdentifierContext,ResultAnalyticalMethod/MethodName,ResultAnalyticalMethod/MethodQualifierTypeName,MethodDescriptionText,LaboratoryName,AnalysisStartDate,AnalysisStartTime/Time,AnalysisStartTime/TimeZoneCode,AnalysisEndDate,AnalysisEndTime/Time,AnalysisEndTime/TimeZoneCode,ResultLaboratoryCommentCode,ResultLaboratoryCommentText,DetectionQuantitationLimitTypeName,DetectionQuantitationLimitMeasure/MeasureValue,DetectionQuantitationLimitMeasure/MeasureUnitCode,LaboratoryAccreditationIndicator,LaboratoryAccreditationAuthorityName,TaxonomistAccreditationIndicator,TaxonomistAccreditationAuthorityName,LabSamplePreparationMethod/MethodIdentifier,LabSamplePreparationMethod/MethodIdentifierContext,LabSamplePreparationMethod/MethodName,LabSamplePreparationMethod/MethodQualifierTypeName,LabSamplePreparationMethod/MethodDescriptionText,PreparationStartDate,PreparationStartTime/Time,PreparationStartTime/TimeZoneCode,PreparationEndDate,PreparationEndTime/Time,PreparationEndTime/TimeZoneCode,SubstitutionDilutionFactorNumeric,ProviderName
PECHANGA_WQX,"Pechanga Band of Luiseno Mission Indians of the Pechanga Reservation, California (Tribal)",PECHANGA_WQX-ST 2:20230802:0928:SR:,Sample-Routine,Water,,2023-08-02,09:28:00,PDT,,,,,,,,,,,,PED Monitoring,,PECHANGA_WQX-ST 2,,,,,33.4365000000,-117.0448000000,,,,,,,,,,,,,,,,,,,,,,,,,,SASMN,PECHANGA_WQX,SASMN,PECHANGA_WQX,Sample Collection Method for Pechanga Tribe according to their QAPP,Water Bottle,,,,,,,,,,,,,,,Enterococcus,,270,cfu/100mL,,Final,,Actual,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,9230-C,APHA,"9230 C ~ Fecal Streptococcus and Enterococcus Groups, Membrane Filter Techniques",,,,2023-08-02,,,,,,,,Lower Reporting Limit,1,cfu/100mL,,,,,,,,,,,,,,,,,STORET
MORONGO1_WQX,Morongo Band of Mission Indians,MORONGO1_WQX-SPS080823,Field Msr/Obs,Water,,2023-08-08,15:12:00,PDT,,,,,,,,,,,,SWQM,,MORONGO1_WQX-SPS,,,,,33.9539700000,-116.7984000000,,,,,,,,,,,,,,,,,,,,,,,,,,MBMI_QAPP,MORONGO1_WQX,Standard Method,,,Probe/Sensor,,,,,,,,,,,,,,,"Temperature, water",,75,deg F,,Final,,Actual,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,STORET
MORONGO1_WQX,Morongo Band of Mission Indians,MORONGO1_WQX-BC1080823,Field Msr/Obs,Water,,2023-08-08,09:03:00,PDT,,,,,,,,,,,,SWQM,,MORONGO1_WQX-BC1,,,,,33.9681900000,-116.8631000000,,,,,,,,,,,,,,,,,,,,,,,,,,MBMI_QAPP,MORONGO1_WQX,Standard Method,,,Probe/Sensor,,,,,,,,,,,,,,,pH,,8.54,None,,Final,,Actual,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,STORET
MORONGO1_WQX,Morongo Band of Mission Indians,MORONGO1_WQX-WC1080823,Field Msr/Obs,Water,,2023-08-08,10:22:00,PDT,,,,,,,,,,,,SWQM,,MORONGO1_WQX-WC1,,,,,34.0143000000,-116.8205000000,,,,,,,,,,,,,,,,,,,,,,,,,,MBMI_QAPP,MORONGO1_WQX,Standard Method,,,Probe/Sensor,,,,,,,,,,,,,,,pH,,7.83,None,,Final,,Actual,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,STORET
PECHANGA_WQX,"Pechanga Band of Luiseno Mission Indians of the Pechanga Reservation, California (Tribal)",PECHANGA_WQX-ST 3:20230802:0843:SR:,Sample-Routine,Water,,2023-08-02,08:43:00,PDT,,,,,,,,,,,,PED Monitoring,,PECHANGA_WQX-ST 3,,,,,33.4533100000,-117.1189000000,,,,,,,,,,,,,,,,,,,,,,,,,,SASMN,PECHANGA_WQX,SASMN,PECHANGA_WQX,Sample Collection Method for Pechanga Tribe according to their QAPP,Water Bottle,,,,,,,,,,,,,,as NO3,Nitrate,Dissolved,1.8,mg/L,,Final,,Actual,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,10206,HACH,"Nitrate, Dimethylphenol Method",,,,2023-08-02,,,,,,,,Lower Reporting Limit,0.5,mg/L,,,,,,,,,,,,,,,,,STORET
MORONGO1_WQX,Morongo Band of Mission Indians,MORONGO1_WQX-BC1080823,Field Msr/Obs,Water,,2023-08-08,09:03:00,PDT,,,,,,,,,,,,SWQM,,MORONGO1_WQX-BC1,,,,,33.9681900000,-116.8631000000,,,,,,,,,,,,,,,,,,,,,,,,,,MBMI_QAPP,MORONGO1_WQX,Standard Method,,,Probe/Sensor,,,,,,,,,,,,,,,"Temperature, water",,61.9,deg F,,Final,,Actual,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,STORET
MORONGO1_WQX,Morongo Band of Mission Indians,MORONGO1_WQX-BOG080823,Field Msr/Obs,Water,,2023-08-08,10:59:00,PDT,,,,,,,,,,,,SWQM,,MORONGO1_WQX-BOG,,,,,33.9925700000,-116.8436000000,,,,,,,,,,,,,,,,,,,,,,,,,,MBMI_QAPP,MORONGO1_WQX,Standard Method,,,Probe/Sensor,,,,,,,,,,,,,,,pH,,7.44,None,,Final,,Actual,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,STORET
PECHANGA_WQX,"Pechanga Band of Luiseno Mission Indians of the Pechanga Reservation, California (Tribal)",PECHANGA_WQX-ST 4:20230802:1038:SR:,Sample-Routine,Water,,2023-08-02,10:38:00,PDT,,,,,,,,,,,,PED Monitoring,,PECHANGA_WQX-ST 4,,,,,33.4405900000,-117.0320000000,,,,,,,,,,,,,,,,,,,,,,,,,,SASMN,PECHANGA_WQX,SASMN,PECHANGA_WQX,Sample Collection Method for Pechanga Tribe according to their QAPP,Water Bottle,,,,,,,,,,,,,,as P,"Total Phosphorus, mixed forms",Total,0.26,mg/L,,Final,,Actual,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,365.2,USEPA,Phosphorus by Single Reagent Colorimetry,,https://www.nemi.gov/methods/method_summary/5254/,,2023-08-02,,,,,,,,Lower Reporting Limit,0.05,mg/L,,,,,,,,,,,,,,,,,STORET
MORONGO1_WQX,Morongo Band of Mission Indians,MORONGO1_WQX-HE1080823,Field Msr/Obs,Water,,2023-08-08,09:36:00,PDT,,,,,,,,,,,,SWQM,,MORONGO1_WQX-HE1,,,,,33.9743400000,-116.8605000000,,,,,,,,,,,,,,,,,,,,,,,,,,MBMI_QAPP,MORONGO1_WQX,Standard Method,,,Probe/Sensor,,,,,,,,,,,,,,,Turbidity,,7.22,NTU,,Final,,Actual,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,STORET
SOBOBA_WQX,"Soboba Band of Luiseno Indians, California (Tribal)",SOBOBA_WQX-ICHS:20230802100000:FM:.05,Field Msr/Obs,Water,,2023-08-02,10:00:00,PST,,,,,.05,ft,,,,,,Soboba_WQM,,SOBOBA_WQX-ICHS,,,,,33.4631100000,-116.5059000000,,,,,,,,,,,,,,,,,,,,,,,,,,SOBOBA_QAPP,SOBOBA_WQX,SOBOBA_QAPP,,,Probe/Sensor,MP25T,,,,,,,,,,,,,,Specific conductance,,0.258,mS/cm,,Final,,Actual,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,STORET
ABCI_WQX,Augustine Band of Cahuilla Indians (Tribal),ABCI_WQX-MW_4:20230802:0000:FM:PS:,Field Msr/Obs,Water,,2023-08-02,,,,,,,,,,,,,,ABCIFY20-25,,ABCI_WQX-MW_4,,,,,33.6548000000,-116.1975000000,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,Probe/Sensor,,,,,,,,,,,,,,,Turbidity,,3.1,NTU,,Final,,Actual,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,STORET
MORONGO1_WQX,Morongo Band of Mission Indians,MORONGO1_WQX-LM1080823,Field Msr/Obs,Water,,2023-08-08,11:18:00,PDT,,,,,,,,,,,,SWQM,,MORONGO1_WQX-LM1,,,,,33.9908000000,-116.8426000000,,,,,,,,,,,,,,,,,,,,,,,,,,MBMI_QAPP,MORONGO1_WQX,Standard Method,,,Probe/Sensor,,,,,,,,,,,,,,,Salinity,,0.17,PSS,,Final,,Actual,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,STORET
MORONGO1_WQX,Morongo Band of Mission Indians,MORONGO1_WQX-BC1080823,Field Msr/Obs,Water,,2023-08-08,09:03:00,PDT,,,,,,,,,,,,SWQM,,MORONGO1_WQX-BC1,,,,,33.9681900000,-116.8631000000,,,,,,,,,,,,,,,,,,,,,,,,,,MBMI_QAPP,MORONGO1_WQX,Standard Method,,,Probe/Sensor,,,,,,,,,,,,,,,Barometric pressure,,27.223,inHg,,Final,,Actual,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,STORET
MORONGO1_WQX,Morongo Band of Mission Indians,MORONGO1_WQX-BOG080823,Field Msr/Obs,Water,,2023-08-08,10:59:00,PDT,,,,,,,,,,,,SWQM,,MORONGO1_WQX-BOG,,,,,33.9925700000,-116.8436000000,,,,,,,,,,,,,,,,,,,,,,,,,,MBMI_QAPP,MORONGO1_WQX,Standard Method,,,Probe/Sensor,,,,,,,,,,,,,,,Specific conductance,,356.9,uS/cm,,Final,,Actual,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,STORET
MORONGO1_WQX,Morongo Band of Mission Indians,MORONGO1_WQX-H000080823,Field Msr/Obs,Water,,2023-08-08,09:12:00,PDT,,,,,,,,,,,,SWQM,,MORONGO1_WQX-H000,,,,,33.9682200000,-116.8630000000,,,,,,,,,,,,,,,,,,,,,,,,,,MBMI_QAPP,MORONGO1_WQX,Standard Method,,,Probe/Sensor,,,,,,,,,,,,,,,pH,,8.18,None,,Final,,Actual,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,STORET
PECHANGA_WQX,"Pechanga Band of Luiseno Mission Indians of the Pechanga Reservation, California (Tribal)",PECHANGA_WQX-ST 4:20230802:1038:FM:,Field Msr/Obs,Water,,2023-08-02,10:38:00,PDT,,,,,,,,,,,,PED Monitoring,,PECHANGA_WQX-ST 4,,,,,33.4405900000,-117.0320000000,,,,,,,,,,,,,,,,,,,,,,,,,,SASMN,PECHANGA_WQX,SASMN,PECHANGA_WQX,Sample Collection Method for Pechanga Tribe according to their QAPP,Probe/Sensor,,,,,,,,,,,,,,,"Temperature, water",,24.6,deg C,,Final,,Actual,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,STORET
ABCI_WQX,Augustine Band of Cahuilla Indians (Tribal),ABCI_WQX-MW_7:20230808:0000:FM:PS:,Field Msr/Obs,Water,,2023-08-08,,,,,,,,,,,,,,ABCIFY20-25,,ABCI_WQX-MW_7,,,,,33.6507000000,-116.1940000000,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,Probe/Sensor,,,,,,,,,,,,,,,Oxidation reduction potential (ORP),,159.5,mV,,Final,,Actual,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,STORET
MORONGO1_WQX,Morongo Band of Mission Indians,MORONGO1_WQX-WC1080823,Field Msr/Obs,Water,,2023-08-08,10:22:00,PDT,,,,,,,,,,,,SWQM,,MORONGO1_WQX-WC1,,,,,34.0143000000,-116.8205000000,,,,,,,,,,,,,,,,,,,,,,,,,,MBMI_QAPP,MORONGO1_WQX,Standard Method,,,Probe/Sensor,,,,,,,,,,,,,,,Turbidity,,0.09,NTU,,Final,,Actual,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,STORET
MORONGO1_WQX,Morongo Band of Mission Indians,MORONGO1_WQX-BC1080823,Field Msr/Obs,Water,,2023-08-08,09:03:00,PDT,,,,,,,,,,,,SWQM,,MORONGO1_WQX-BC1,,,,,33.9681900000,-116.8631000000,,,,,,,,,,,,,,,,,,,,,,,,,,MBMI_QAPP,MORONGO1_WQX,Standard Method,,,Probe/Sensor,,,,,,,,,,,,,,,Turbidity,,0.76,NTU,,Final,,Actual,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,STORET
MORONGO1_WQX,Morongo Band of Mission Indians,MORONGO1_WQX-BOG080823,Field Msr/Obs,Water,,2023-08-08,10:59:00,PDT,,,,,,,,,,,,SWQM,,MORONGO1_WQX-BOG,,,,,33.9925700000,-116.8436000000,,,,,,,,,,,,,,,,,,,,,,,,,,MBMI_QAPP,MORONGO1_WQX,Standard Method,,,Probe/Sensor,,,,,,,,,,,,,,,Salinity,,0.17,PSS,,Final,,Actual,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,STORET
MORONGO1_WQX,Morongo Band of Mission Indians,MORONGO1_WQX-LM1080823,Field Msr/Obs,Water,,2023-08-08,11:18:00,PDT,,,,,,,,,,,,SWQM,,MORONGO1_WQX-LM1,,,,,33.9908000000,-116.8426000000,,,,,,,,,,,,,,,,,,,,,,,,,,MBMI_QAPP,MORONGO1_WQX,Standard Method,,,Probe/Sensor,,,,,,,,,,,,,,,Turbidity,,20.4,NTU,,Final,,Actual,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,STORET
SOBOBA_WQX,"Soboba Band of Luiseno Indians, California (Tribal)",SOBOBA_WQX-IC2:20230802100000:FM:.05,Field Msr/Obs,Water,,2023-08-02,10:00:00,PST,,,,,.05,ft,,,,,,Soboba_WQM,,SOBOBA_WQX-IC2,,,,,33.4639700000,-116.5096000000,,,,,,,,,,,,,,,,,,,,,,,,,,SOBOBA_QAPP,SOBOBA_WQX,SOBOBA_QAPP,,,Probe/Sensor,MP25T,,,,,,,,,,,,,,Dissolved oxygen (DO),,8.33,mg/L,,Final,,Actual,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,STORET
PECHANGA_WQX,"Pechanga Band of Luiseno Mission Indians of the Pechanga Reservation, California (Tribal)",PECHANGA_WQX-ST 4:20230802:1038:FM:,Field Msr/Obs,Water,,2023-08-02,10:38:00,PDT,,,,,,,,,,,,PED Monitoring,,PECHANGA_WQX-ST 4,,,,,33.4405900000,-117.0320000000,,,,,,,,,,,,,,,,,,,,,,,,,,SASMN,PECHANGA_WQX,SASMN,PECHANGA_WQX,Sample Collection Method for Pechanga Tribe according to their QAPP,Probe/Sensor,,,,,,,,,,,,,,,Specific conductance,,0.6278,mS/cm,,Final,,Actual,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,STORET
PECHANGA_WQX,"Pechanga Band of Luiseno Mission Indians of the Pechanga Reservation, California (Tribal)",PECHANGA_WQX-ST 4:20230802:1038:FM:,Field Msr/Obs,Water,,2023-08-02,10:38:00,PDT,,,,,,,,,,,,PED Monitoring,,PECHANGA_WQX-ST 4,,,,,33.4405900000,-117.0320000000,,,,,,,,,,,,,,,,,,,,,,,,,,SASMN,PECHANGA_WQX,SASMN,PECHANGA_WQX,Sample Collection Method for Pechanga Tribe according to their QAPP,Probe/Sensor,,,,,,,,,,,,,,,Dissolved oxygen (DO),,114.2,%,,Final,,Actual,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,STORET
MORONGO1_WQX,Morongo Band of Mission Indians,MORONGO1_WQX-BC1080823,Field Msr/Obs,Water,,2023-08-08,09:03:00,PDT,,,,,,,,,,,,SWQM,,MORONGO1_WQX-BC1,,,,,33.9681900000,-116.8631000000,,,,,,,,,,,,,,,,,,,,,,,,,,MBMI_QAPP,MORONGO1_WQX,Standard Method,,,Probe/Sensor,,,,,,,,,,,,,,,Total dissolved solids,,342,mg/L,,Final,,Actual,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,STORET
ABCI_WQX,Augustine Band of Cahuilla Indians (Tribal),ABCI_WQX-MW_6:20230802:0000:FM:PS:,Field Msr/Obs,Water,,2023-08-02,,,,,,,,,,,,,,ABCIFY20-25,,ABCI_WQX-MW_6,,,,,33.6526000000,-116.1889000000,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,Probe/Sensor,,,,,,,,,,,,,,,pH,,8.67,None,,Final,,Actual,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,STORET
MORONGO1_WQX,Morongo Band of Mission Indians,MORONGO1_WQX-HW1080823,Field Msr/Obs,Water,,2023-08-08,09:27:00,PDT,,,,,,,,,,,,SWQM,,MORONGO1_WQX-HW1,,,,,33.9744700000,-116.8608000000,,,,,,,,,,,,,,,,,,,,,,,,,,MBMI_QAPP,MORONGO1_WQX,Standard Method,,,Probe/Sensor,,,,,,,,,,,,,,,"Temperature, water",,66.6,deg F,,Final,,Actual,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,STORET
ABCI_WQX,Augustine Band of Cahuilla Indians (Tribal),ABCI_WQX-MW_4:20230802:0000:FM:PS:,Field Msr/Obs,Water,,2023-08-02,,,,,,,,,,,,,,ABCIFY20-25,,ABCI_WQX-MW_4,,,,,33.6548000000,-116.1975000000,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,Probe/Sensor,,,,,,,,,,,,,,,pH,,8.33,None,,Final,,Actual,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,STORET
MORONGO1_WQX,Morongo Band of Mission Indians,MORONGO1_WQX-BC1080823,Field Msr/Obs,Water,,2023-08-08,09:03:00,PDT,,,,,,,,,,,,SWQM,,MORONGO1_WQX-BC1,,,,,33.9681900000,-116.8631000000,,,,,,,,,,,,,,,,,,,,,,,,,,MBMI_QAPP,MORONGO1_WQX,Standard Method,,,Probe/Sensor,,,,,,,,,,,,,,,Salinity,,0.26,PSS,,Final,,Actual,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,STORET
MORONGO1_WQX,Morongo Band of Mission Indians,MORONGO1_WQX-BC1080823,Field Msr/Obs,Water,,2023-08-08,09:03:00,PDT,,,,,,,,,,,,SWQM,,MORONGO1_WQX-BC1,,,,,33.9681900000,-116.8631000000,,,,,,,,,,,,,,,,,,,,,,,,,,MBMI_QAPP,MORONGO1_WQX,Standard Method,,,Probe/Sensor,,,,,,,,,,,,,,,Specific conductance,,526,uS/cm,,Final,,Actual,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,STORET
PECHANGA_WQX,"Pechanga Band of Luiseno Mission Indians of the Pechanga Reservation, California (Tribal)",PECHANGA_WQX-ST 4:20230802:1038:FM:,Field Msr/Obs,Water,,2023-08-02,10:38:00,PDT,,,,,,,,,,,,PED Monitoring,,PECHANGA_WQX-ST 4,,,,,33.4405900000,-117.0320000000,,,,,,,,,,,,,,,,,,,,,,,,,,SASMN,PECHANGA_WQX,SASMN,PECHANGA_WQX,Sample Collection Method for Pechanga Tribe according to their QAPP,Probe/Sensor,,,,,,,,,,,,,,,Dissolved oxygen (DO),,9.49,mg/L,,Final,,Actual,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,STORET
PECHANGA_WQX,"Pechanga Band of Luiseno Mission Indians of the Pechanga Reservation, California (Tribal)",PECHANGA_WQX-ST 4:20230802:1038:FM:,Field Msr/Obs,Water,,2023-08-02,10:38:00,PDT,,,,,,,,,,,,PED Monitoring,,PECHANGA_WQX-ST 4,,,,,33.4405900000,-117.0320000000,,,,,,,,,,,,,,,,,,,,,,,,,,SASMN,PECHANGA_WQX,SASMN,PECHANGA_WQX,Sample Collection Method for Pechanga Tribe according to their QAPP,Probe/Sensor,,,,,,,,,,,,,Not Reported,,Turbidity,,,,,Final,,Actual,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,STORET
MORONGO1_WQX,Morongo Band of Mission Indians,MORONGO1_WQX-BOG080823,Field Msr/Obs,Water,,2023-08-08,10:59:00,PDT,,,,,,,,,,,,SWQM,,MORONGO1_WQX-BOG,,,,,33.9925700000,-116.8436000000,,,,,,,,,,,,,,,,,,,,,,,,,,MBMI_QAPP,MORONGO1_WQX,Standard Method,,,Probe/Sensor,,,,,,,,,,,,,,,Barometric pressure,,26.437,inHg,,Final,,Actual,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,STORET
MORONGO1_WQX,Morongo Band of Mission Indians,MORONGO1_WQX-HE1080823,Field Msr/Obs,Water,,2023-08-08,09:36:00,PDT,,,,,,,,,,,,SWQM,,MORONGO1_WQX-HE1,,,,,33.9743400000,-116.8605000000,,,,,,,,,,,,,,,,,,,,,,,,,,MBMI_QAPP,MORONGO1_WQX,Standard Method,,,Probe/Sensor,,,,,,,,,,,,,,,Salinity,,0.14,PSS,,Final,,Actual,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,STORET
PECHANGA_WQX,"Pechanga Band of Luiseno Mission Indians of the Pechanga Reservation, California (Tribal)",PECHANGA_WQX-ST 4:20230802:1038:SR:,Sample-Routine,Water,,2023-08-02,10:38:00,PDT,,,,,,,,,,,,PED Monitoring,,PECHANGA_WQX-ST 4,,,,,33.4405900000,-117.0320000000,,,,,,,,,,,,,,,,,,,,,,,,,,SASMN,PECHANGA_WQX,SASMN,PECHANGA_WQX,Sample Collection Method for Pechanga Tribe according to their QAPP,Water Bottle,,,,,,,,,,,,,,as NH3,Ammonia,Dissolved,0.32,mg/L,,Final,,Actual,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,4500-NH3 B,APHA,4500 NH3 B ~ Ammonia by Titration,,https://www.nemi.gov/methods/method_summary/9696/,,2023-08-02,,,,,,,,Lower Reporting Limit,0.1,mg/L,,,,,,,,,,,,,,,,,STORET
MORONGO1_WQX,Morongo Band of Mission Indians,MORONGO1_WQX-M000080823,Field Msr/Obs,Water,,2023-08-08,15:52:00,PDT,,,,,,,,,,,,SWQM,,MORONGO1_WQX-M000,,,,,33.9873000000,-116.7861000000,,,,,,,,,,,,,,,,,,,,,,,,,,MBMI_QAPP,MORONGO1_WQX,Standard Method,,,Probe/Sensor,,,,,,,,,,,,,,,Total dissolved solids,,265,mg/L,,Final,,Actual,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,STORET
MORONGO1_WQX,Morongo Band of Mission Indians,MORONGO1_WQX-M000080823,Field Msr/Obs,Water,,2023-08-08,15:52:00,PDT,,,,,,,,,,,,SWQM,,MORONGO1_WQX-M000,,,,,33.9873000000,-116.7861000000,,,,,,,,,,,,,,,,,,,,,,,,,,MBMI_QAPP,MORONGO1_WQX,Standard Method,,,Probe/Sensor,,,,,,,,,,,,,,,Barometric pressure,,26.464,inHg,,Final,,Actual,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,STORET
PECHANGA_WQX,"Pechanga Band of Luiseno Mission Indians of the Pechanga Reservation, California (Tribal)",PECHANGA_WQX-ST 3:20230802:0843:SR:,Sample-Routine,Water,,2023-08-02,08:43:00,PDT,,,,,,,,,,,,PED Monitoring,,PECHANGA_WQX-ST 3,,,,,33.4533100000,-117.1189000000,,,,,,,,,,,,,,,,,,,,,,,,,,SASMN,PECHANGA_WQX,SASMN,PECHANGA_WQX,Sample Collection Method for Pechanga Tribe according to their QAPP,Water Bottle,,,,,,,,,,,,,,as P,"Total Phosphorus, mixed forms",Total,0.22,mg/L,,Final,,Actual,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,365.2,USEPA,Phosphorus by Single Reagent Colorimetry,,https://www.nemi.gov/methods/method_summary/5254/,,2023-08-02,,,,,,,,Lower Reporting Limit,0.05,mg/L,,,,,,,,,,,,,,,,,STORET
MORONGO1_WQX,Morongo Band of Mission Indians,MORONGO1_WQX-LMO080823,Field Msr/Obs,Water,,2023-08-08,11:30:00,PDT,,,,,,,,,,,,SWQM,,MORONGO1_WQX-LMO,,,,,33.9905500000,-116.8423000000,,,,,,,,,,,,,,,,,,,,,,,,,,MBMI_QAPP,MORONGO1_WQX,Standard Method,,,Probe/Sensor,,,,,,,,,,,,,,,Barometric pressure,,26.517,inHg,,Final,,Actual,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,STORET
MORONGO1_WQX,Morongo Band of Mission Indians,MORONGO1_WQX-HW1080823,Field Msr/Obs,Water,,2023-08-08,09:27:00,PDT,,,,,,,,,,,,SWQM,,MORONGO1_WQX-HW1,,,,,33.9744700000,-116.8608000000,,,,,,,,,,,,,,,,,,,,,,,,,,MBMI_QAPP,MORONGO1_WQX,Standard Method,,,Probe/Sensor,,,,,,,,,,,,,,,pH,,8.02,None,,Final,,Actual,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,STORET
MORONGO1_WQX,Morongo Band of Mission Indians,MORONGO1_WQX-HW1080823,Field Msr/Obs,Water,,2023-08-08,09:27:00,PDT,,,,,,,,,,,,SWQM,,MORONGO1_WQX-HW1,,,,,33.9744700000,-116.8608000000,,,,,,,,,,,,,,,,,,,,,,,,,,MBMI_QAPP,MORONGO1_WQX,Standard Method,,,Probe/Sensor,,,,,,,,,,,,,,,Specific conductance,,334.2,uS/cm,,Final,,Actual,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,STORET
MORONGO1_WQX,Morongo Band of Mission Indians,MORONGO1_WQX-HE1080823,Field Msr/Obs,Water,,2023-08-08,09:36:00,PDT,,,,,,,,,,,,SWQM,,MORONGO1_WQX-HE1,,,,,33.9743400000,-116.8605000000,,,,,,,,,,,,,,,,,,,,,,,,,,MBMI_QAPP,MORONGO1_WQX,Standard Method,,,Probe/Sensor,,,,,,,,,,,,,,,Barometric pressure,,27.043,inHg,,Final,,Actual,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,STORET
MORONGO1_WQX,Morongo Band of Mission Indians,MORONGO1_WQX-H000080823,Field Msr/Obs,Water,,2023-08-08,09:12:00,PDT,,,,,,,,,,,,SWQM,,MORONGO1_WQX-H000,,,,,33.9682200000,-116.8630000000,,,,,,,,,,,,,,,,,,,,,,,,,,MBMI_QAPP,MORONGO1_WQX,Standard Method,,,Probe/Sensor,,,,,,,,,,,,,,,Specific conductance,,367.6,uS/cm,,Final,,Actual,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,STORET
SOBOBA_WQX,"Soboba Band of Luiseno Indians, California (Tribal)",SOBOBA_WQX-IC2:20230802100000:FM:.05,Field Msr/Obs,Water,,2023-08-02,10:00:00,PST,,,,,.05,ft,,,,,,Soboba_WQM,,SOBOBA_WQX-IC2,,,,,33.4639700000,-116.5096000000,,,,,,,,,,,,,,,,,,,,,,,,,,SOBOBA_QAPP,SOBOBA_WQX,SOBOBA_QAPP,,,Probe/Sensor,MP25T,,,,,,,,,,,,,,Oxidation reduction potential (ORP),,149.7,mV,,Final,,Actual,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,STORET
MORONGO1_WQX,Morongo Band of Mission Indians,MORONGO1_WQX-LMO080823,Field Msr/Obs,Water,,2023-08-08,11:30:00,PDT,,,,,,,,,,,,SWQM,,MORONGO1_WQX-LMO,,,,,33.9905500000,-116.8423000000,,,,,,,,,,,,,,,,,,,,,,,,,,MBMI_QAPP,MORONGO1_WQX,Standard Method,,,Probe/Sensor,,,,,,,,,,,,,,,Salinity,,0.17,PSS,,Final,,Actual,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,STORET
MORONGO1_WQX,Morongo Band of Mission Indians,MORONGO1_WQX-LMO080823,Field Msr/Obs,Water,,2023-08-08,11:30:00,PDT,,,,,,,,,,,,SWQM,,MORONGO1_WQX-LMO,,,,,33.9905500000,-116.8423000000,,,,,,,,,,,,,,,,,,,,,,,,,,MBMI_QAPP,MORONGO1_WQX,Standard Method,,,Probe/Sensor,,,,,,,,,,,,,,,Total dissolved solids,,230,mg/L,,Final,,Actual,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,STORET
PECHANGA_WQX,"Pechanga Band of Luiseno Mission Indians of the Pechanga Reservation, California (Tribal)",PECHANGA_WQX-ST 4:20230802:1038:SR:,Sample-Routine,Water,,2023-08-02,10:38:00,PDT,,,,,,,,,,,,PED Monitoring,,PECHANGA_WQX-ST 4,,,,,33.4405900000,-117.0320000000,,,,,,,,,,,,,,,,,,,,,,,,,,SASMN,PECHANGA_WQX,SASMN,PECHANGA_WQX,Sample Collection Method for Pechanga Tribe according to their QAPP,Water Bottle,,,,,,,,,,,,,,,Total Coliform,,24,MPN/100mL,,Final,,Actual,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,9221-B,APHA,9221 B ~ Standard Total Coliform- Fermentation Technique,,,,2023-08-02,,,,,,,,Lower Reporting Limit,2,MPN/100mL,,,,,,,,,,,,,,,,,STORET
ABCI_WQX,Augustine Band of Cahuilla Indians (Tribal),ABCI_WQX-MW_6:20230802:0000:FM:PS:,Field Msr/Obs,Water,,2023-08-02,,,,,,,,,,,,,,ABCIFY20-25,,ABCI_WQX-MW_6,,,,,33.6526000000,-116.1889000000,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,Probe/Sensor,,,,,,,,,,,,,,,Oxidation reduction potential (ORP),,146.2,mV,,Final,,Actual,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,STORET
PECHANGA_WQX,"Pechanga Band of Luiseno Mission Indians of the Pechanga Reservation, California (Tribal)",PECHANGA_WQX-ST 3:20230802:0843:SR:,Sample-Routine,Water,,2023-08-02,08:43:00,PDT,,,,,,,,,,,,PED Monitoring,,PECHANGA_WQX-ST 3,,,,,33.4533100000,-117.1189000000,,,,,,,,,,,,,,,,,,,,,,,,,,SASMN,PECHANGA_WQX,SASMN,PECHANGA_WQX,Sample Collection Method for Pechanga Tribe according to their QAPP,Water Bottle,,,,,,,,,,,,,,,Total Coliform,,220,MPN/100mL,,Final,,Actual,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,9221-B,APHA,9221 B ~ Standard Total Coliform- Fermentation Technique,,,,2023-08-02,,,,,,,,Lower Reporting Limit,2,MPN/100mL,,,,,,,,,,,,,,,,,STORET
SOBOBA_WQX,"Soboba Band of Luiseno Indians, California (Tribal)",SOBOBA_WQX-ICHS:20230802100000:FM:.05,Field Msr/Obs,Water,,2023-08-02,10:00:00,PST,,,,,.05,ft,,,,,,Soboba_WQM,,SOBOBA_WQX-ICHS,,,,,33.4631100000,-116.5059000000,,,,,,,,,,,,,,,,,,,,,,,,,,SOBOBA_QAPP,SOBOBA_WQX,SOBOBA_QAPP,,,Probe/Sensor,MP25T,,,,,,,,,,,,,,pH,,9.33,None,,Final,,Actual,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,STORET
MORONGO1_WQX,Morongo Band of Mission Indians,MORONGO1_WQX-H000080823,Field Msr/Obs,Water,,2023-08-08,09:12:00,PDT,,,,,,,,,,,,SWQM,,MORONGO1_WQX-H000,,,,,33.9682200000,-116.8630000000,,,,,,,,,,,,,,,,,,,,,,,,,,MBMI_QAPP,MORONGO1_WQX,Standard Method,,,Probe/Sensor,,,,,,,,,,,,,,,"Temperature, water",,64.1,deg F,,Final,,Actual,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,STORET
MORONGO1_WQX,Morongo Band of Mission Indians,MORONGO1_WQX-LMO080823,Field Msr/Obs,Water,,2023-08-08,11:30:00,PDT,,,,,,,,,,,,SWQM,,MORONGO1_WQX-LMO,,,,,33.9905500000,-116.8423000000,,,,,,,,,,,,,,,,,,,,,,,,,,MBMI_QAPP,MORONGO1_WQX,Standard Method,,,Probe/Sensor,,,,,,,,,,,,,,,"Temperature, water",,67.6,deg F,,Final,,Actual,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,STORET
PECHANGA_WQX,"Pechanga Band of Luiseno Mission Indians of the Pechanga Reservation, California (Tribal)",PECHANGA_WQX-ST 4:20230802:1038:SR:,Sample-Routine,Water,,2023-08-02,10:38:00,PDT,,,,,,,,,,,,PED Monitoring,,PECHANGA_WQX-ST 4,,,,,33.4405900000,-117.0320000000,,,,,,,,,,,,,,,,,,,,,,,,,,SASMN,PECHANGA_WQX,SASMN,PECHANGA_WQX,Sample Collection Method for Pechanga Tribe according to their QAPP,Water Bottle,,,,,,,,,,,,,,as NH4,Total Kjeldahl nitrogen,Total,0.34,mg/L,,Final,,Actual,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,351.2,USEPA,351.2 ~ EPA; Total Kjeldahl Nitrogen by Colorimetry,,https://www.nemi.gov/methods/method_summary/9626/,,2023-08-02,,,,,,,,Lower Reporting Limit,0.1,mg/L,,,,,,,,,,,,,,,,,STORET
SOBOBA_WQX,"Soboba Band of Luiseno Indians, California (Tribal)",SOBOBA_WQX-IC2:20230802100000:FM:.05,Field Msr/Obs,Water,,2023-08-02,10:00:00,PST,,,,,.05,ft,,,,,,Soboba_WQM,,SOBOBA_WQX-IC2,,,,,33.4639700000,-116.5096000000,,,,,,,,,,,,,,,,,,,,,,,,,,SOBOBA_QAPP,SOBOBA_WQX,SOBOBA_QAPP,,,Probe/Sensor,MP25T,,,,,,,,,,,,,,"Temperature, water",,23.18,deg C,,Final,,Actual,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,STORET
PECHANGA_WQX,"Pechanga Band of Luiseno Mission Indians of the Pechanga Reservation, California (Tribal)",PECHANGA_WQX-ST 2:20230802:0928:SR:,Sample-Routine,Water,,2023-08-02,09:28:00,PDT,,,,,,,,,,,,PED Monitoring,,PECHANGA_WQX-ST 2,,,,,33.4365000000,-117.0448000000,,,,,,,,,,,,,,,,,,,,,,,,,,SASMN,PECHANGA_WQX,SASMN,PECHANGA_WQX,Sample Collection Method for Pechanga Tribe according to their QAPP,Water Bottle,,,,,,,,,,,,,,as NO3,Nitrate,Dissolved,1.3,mg/L,,Final,,Actual,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,10206,HACH,"Nitrate, Dimethylphenol Method",,,,2023-08-02,,,,,,,,Lower Reporting Limit,0.5,mg/L,,,,,,,,,,,,,,,,,STORET
PECHANGA_WQX,"Pechanga Band of Luiseno Mission Indians of the Pechanga Reservation, California (Tribal)",PECHANGA_WQX-ST 2:20230802:0928:SR:,Sample-Routine,Water,,2023-08-02,09:28:00,PDT,,,,,,,,,,,,PED Monitoring,,PECHANGA_WQX-ST 2,,,,,33.4365000000,-117.0448000000,,,,,,,,,,,,,,,,,,,,,,,,,,SASMN,PECHANGA_WQX,SASMN,PECHANGA_WQX,Sample Collection Method for Pechanga Tribe according to their QAPP,Water Bottle,,,,,,,,,,,,,,,Total Coliform,,150,MPN/100mL,,Final,,Actual,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,9221-B,APHA,9221 B ~ Standard Total Coliform- Fermentation Technique,,,,2023-08-02,,,,,,,,Lower Reporting Limit,2,MPN/100mL,,,,,,,,,,,,,,,,,STORET
MORONGO1_WQX,Morongo Band of Mission Indians,MORONGO1_WQX-LMO080823,Field Msr/Obs,Water,,2023-08-08,11:30:00,PDT,,,,,,,,,,,,SWQM,,MORONGO1_WQX-LMO,,,,,33.9905500000,-116.8423000000,,,,,,,,,,,,,,,,,,,,,,,,,,MBMI_QAPP,MORONGO1_WQX,Standard Method,,,Probe/Sensor,,,,,,,,,,,,,,,pH,,8.39,None,,Final,,Actual,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,STORET
MORONGO1_WQX,Morongo Band of Mission Indians,MORONGO1_WQX-H000080823,Field Msr/Obs,Water,,2023-08-08,09:12:00,PDT,,,,,,,,,,,,SWQM,,MORONGO1_WQX-H000,,,,,33.9682200000,-116.8630000000,,,,,,,,,,,,,,,,,,,,,,,,,,MBMI_QAPP,MORONGO1_WQX,Standard Method,,,Probe/Sensor,,,,,,,,,,,,,,,Barometric pressure,,27.223,inHg,,Final,,Actual,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,STORET
SOBOBA_WQX,"Soboba Band of Luiseno Indians, California (Tribal)",SOBOBA_WQX-IC2:20230802100000:FM:.05,Field Msr/Obs,Water,,2023-08-02,10:00:00,PST,,,,,.05,ft,,,,,,Soboba_WQM,,SOBOBA_WQX-IC2,,,,,33.4639700000,-116.5096000000,,,,,,,,,,,,,,,,,,,,,,,,,,SOBOBA_QAPP,SOBOBA_WQX,SOBOBA_QAPP,,,Probe/Sensor,MP25T,,,,,,,,,,,,,,Turbidity,,0.81,NTU,,Final,,Actual,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,STORET
MORONGO1_WQX,Morongo Band of Mission Indians,MORONGO1_WQX-HE1080823,Field Msr/Obs,Water,,2023-08-08,09:36:00,PDT,,,,,,,,,,,,SWQM,,MORONGO1_WQX-HE1,,,,,33.9743400000,-116.8605000000,,,,,,,,,,,,,,,,,,,,,,,,,,MBMI_QAPP,MORONGO1_WQX,Standard Method,,,Probe/Sensor,,,,,,,,,,,,,,,Total dissolved solids,,189,mg/L,,Final,,Actual,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,STORET
MORONGO1_WQX,Morongo Band of Mission Indians,MORONGO1_WQX-LM1080823,Field Msr/Obs,Water,,2023-08-08,11:18:00,PDT,,,,,,,,,,,,SWQM,,MORONGO1_WQX-LM1,,,,,33.9908000000,-116.8426000000,,,,,,,,,,,,,,,,,,,,,,,,,,MBMI_QAPP,MORONGO1_WQX,Standard Method,,,Probe/Sensor,,,,,,,,,,,,,,,Specific conductance,,346,uS/cm,,Final,,Actual,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,STORET
MORONGO1_WQX,Morongo Band of Mission Indians,MORONGO1_WQX-WC1080823,Field Msr/Obs,Water,,2023-08-08,10:22:00,PDT,,,,,,,,,,,,SWQM,,MORONGO1_WQX-WC1,,,,,34.0143000000,-116.8205000000,,,,,,,,,,,,,,,,,,,,,,,,,,MBMI_QAPP,MORONGO1_WQX,Standard Method,,,Probe/Sensor,,,,,,,,,,,,,,,"Temperature, water",,53,deg F,,Final,,Actual,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,STORET
PECHANGA_WQX,"Pechanga Band of Luiseno Mission Indians of the Pechanga Reservation, California (Tribal)",PECHANGA_WQX-ST 4:20230802:1038:FM:,Field Msr/Obs,Water,,2023-08-02,10:38:00,PDT,,,,,,,,,,,,PED Monitoring,,PECHANGA_WQX-ST 4,,,,,33.4405900000,-117.0320000000,,,,,,,,,,,,,,,,,,,,,,,,,,SASMN,PECHANGA_WQX,SASMN,PECHANGA_WQX,Sample Collection Method for Pechanga Tribe according to their QAPP,Probe/Sensor,,,,,,,,,,,,,,,pH,,8.37,None,,Final,,Actual,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,STORET
MORONGO1_WQX,Morongo Band of Mission Indians,MORONGO1_WQX-SPS080823,Field Msr/Obs,Water,,2023-08-08,15:12:00,PDT,,,,,,,,,,,,SWQM,,MORONGO1_WQX-SPS,,,,,33.9539700000,-116.7984000000,,,,,,,,,,,,,,,,,,,,,,,,,,MBMI_QAPP,MORONGO1_WQX,Standard Method,,,Probe/Sensor,,,,,,,,,,,,,,,Salinity,,0.2,PSS,,Final,,Actual,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,STORET
MORONGO1_WQX,Morongo Band of Mission Indians,MORONGO1_WQX-M000080823,Field Msr/Obs,Water,,2023-08-08,15:52:00,PDT,,,,,,,,,,,,SWQM,,MORONGO1_WQX-M000,,,,,33.9873000000,-116.7861000000,,,,,,,,,,,,,,,,,,,,,,,,,,MBMI_QAPP,MORONGO1_WQX,Standard Method,,,Probe/Sensor,,,,,,,,,,,,,,,"Temperature, water",,63.8,deg F,,Final,,Actual,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,STORET
MORONGO1_WQX,Morongo Band of Mission Indians,MORONGO1_WQX-WC1080823,Field Msr/Obs,Water,,2023-08-08,10:22:00,PDT,,,,,,,,,,,,SWQM,,MORONGO1_WQX-WC1,,,,,34.0143000000,-116.8205000000,,,,,,,,,,,,,,,,,,,,,,,,,,MBMI_QAPP,MORONGO1_WQX,Standard Method,,,Probe/Sensor,,,,,,,,,,,,,,,Specific conductance,,352.3,uS/cm,,Final,,Actual,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,STORET
MORONGO1_WQX,Morongo Band of Mission Indians,MORONGO1_WQX-H000080823,Field Msr/Obs,Water,,2023-08-08,09:12:00,PDT,,,,,,,,,,,,SWQM,,MORONGO1_WQX-H000,,,,,33.9682200000,-116.8630000000,,,,,,,,,,,,,,,,,,,,,,,,,,MBMI_QAPP,MORONGO1_WQX,Standard Method,,,Probe/Sensor,,,,,,,,,,,,,,,Total dissolved solids,,239,mg/L,,Final,,Actual,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,STORET
SOBOBA_WQX,"Soboba Band of Luiseno Indians, California (Tribal)",SOBOBA_WQX-IC2:20230802100000:FM:.05,Field Msr/Obs,Water,,2023-08-02,10:00:00,PST,,,,,.05,ft,,,,,,Soboba_WQM,,SOBOBA_WQX-IC2,,,,,33.4639700000,-116.5096000000,,,,,,,,,,,,,,,,,,,,,,,,,,SOBOBA_QAPP,SOBOBA_WQX,SOBOBA_QAPP,,,Probe/Sensor,MP25T,,,,,,,,,,,,,,pH,,7.65,None,,Final,,Actual,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,STORET
MORONGO1_WQX,Morongo Band of Mission Indians,MORONGO1_WQX-M000080823,Field Msr/Obs,Water,,2023-08-08,15:52:00,PDT,,,,,,,,,,,,SWQM,,MORONGO1_WQX-M000,,,,,33.9873000000,-116.7861000000,,,,,,,,,,,,,,,,,,,,,,,,,,MBMI_QAPP,MORONGO1_WQX,Standard Method,,,Probe/Sensor,,,,,,,,,,,,,,,Specific conductance,,407,uS/cm,,Final,,Actual,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,STORET
MORONGO1_WQX,Morongo Band of Mission Indians,MORONGO1_WQX-WC1080823,Field Msr/Obs,Water,,2023-08-08,10:22:00,PDT,,,,,,,,,,,,SWQM,,MORONGO1_WQX-WC1,,,,,34.0143000000,-116.8205000000,,,,,,,,,,,,,,,,,,,,,,,,,,MBMI_QAPP,MORONGO1_WQX,Standard Method,,,Probe/Sensor,,,,,,,,,,,,,,,Salinity,,0.17,PSS,,Final,,Actual,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,STORET
SOBOBA_WQX,"Soboba Band of Luiseno Indians, California (Tribal)",SOBOBA_WQX-ICHS:20230802100000:FM:.05,Field Msr/Obs,Water,,2023-08-02,10:00:00,PST,,,,,.05,ft,,,,,,Soboba_WQM,,SOBOBA_WQX-ICHS,,,,,33.4631100000,-116.5059000000,,,,,,,,,,,,,,,,,,,,,,,,,,SOBOBA_QAPP,SOBOBA_WQX,SOBOBA_QAPP,,,Probe/Sensor,MP25T,,,,,,,,,,,,,,"Temperature, water",,35.29,deg C,,Final,,Actual,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,STORET
MORONGO1_WQX,Morongo Band of Mission Indians,MORONGO1_WQX-H000080823,Field Msr/Obs,Water,,2023-08-08,09:12:00,PDT,,,,,,,,,,,,SWQM,,MORONGO1_WQX-H000,,,,,33.9682200000,-116.8630000000,,,,,,,,,,,,,,,,,,,,,,,,,,MBMI_QAPP,MORONGO1_WQX,Standard Method,,,Probe/Sensor,,,,,,,,,,,,,,,Turbidity,,0.42,NTU,,Final,,Actual,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,STORET
MORONGO1_WQX,Morongo Band of Mission Indians,MORONGO1_WQX-LMO080823,Field Msr/Obs,Water,,2023-08-08,11:30:00,PDT,,,,,,,,,,,,SWQM,,MORONGO1_WQX-LMO,,,,,33.9905500000,-116.8423000000,,,,,,,,,,,,,,,,,,,,,,,,,,MBMI_QAPP,MORONGO1_WQX,Standard Method,,,Probe/Sensor,,,,,,,,,,,,,,,Turbidity,,9.34,NTU,,Final,,Actual,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,STORET
MORONGO1_WQX,Morongo Band of Mission Indians,MORONGO1_WQX-SPS080823,Field Msr/Obs,Water,,2023-08-08,15:12:00,PDT,,,,,,,,,,,,SWQM,,MORONGO1_WQX-SPS,,,,,33.9539700000,-116.7984000000,,,,,,,,,,,,,,,,,,,,,,,,,,MBMI_QAPP,MORONGO1_WQX,Standard Method,,,Probe/Sensor,,,,,,,,,,,,,,,Turbidity,,2.18,NTU,,Final,,Actual,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,STORET
MORONGO1_WQX,Morongo Band of Mission Indians,MORONGO1_WQX-BOG080823,Field Msr/Obs,Water,,2023-08-08,10:59:00,PDT,,,,,,,,,,,,SWQM,,MORONGO1_WQX-BOG,,,,,33.9925700000,-116.8436000000,,,,,,,,,,,,,,,,,,,,,,,,,,MBMI_QAPP,MORONGO1_WQX,Standard Method,,,Probe/Sensor,,,,,,,,,,,,,,,Turbidity,,22.8,NTU,,Final,,Actual,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,STORET
PECHANGA_WQX,"Pechanga Band of Luiseno Mission Indians of the Pechanga Reservation, California (Tribal)",PECHANGA_WQX-ST 4:20230802:1038:SR:,Sample-Routine,Water,,2023-08-02,10:38:00,PDT,,,,,,,,,,,,PED Monitoring,,PECHANGA_WQX-ST 4,,,,,33.4405900000,-117.0320000000,,,,,,,,,,,,,,,,,,,,,,,,,,SASMN,PECHANGA_WQX,SASMN,PECHANGA_WQX,Sample Collection Method for Pechanga Tribe according to their QAPP,Water Bottle,,,,,,,,,,,,,Not Detected,as NO2,Nitrite,Dissolved,,,,Final,,Actual,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,4500-NO2(B),APHA,4500 NO2 B ~ Nitrite in Water by Colorimetry,,https://www.nemi.gov/methods/method_summary/7415/,,2023-08-02,,,,,,,,Lower Reporting Limit,0.02,mg/L,,,,,,,,,,,,,,,,,STORET
MORONGO1_WQX,Morongo Band of Mission Indians,MORONGO1_WQX-HE1080823,Field Msr/Obs,Water,,2023-08-08,09:36:00,PDT,,,,,,,,,,,,SWQM,,MORONGO1_WQX-HE1,,,,,33.9743400000,-116.8605000000,,,,,,,,,,,,,,,,,,,,,,,,,,MBMI_QAPP,MORONGO1_WQX,Standard Method,,,Probe/Sensor,,,,,,,,,,,,,,,"Temperature, water",,65.7,deg F,,Final,,Actual,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,STORET
MORONGO1_WQX,Morongo Band of Mission Indians,MORONGO1_WQX-M000080823,Field Msr/Obs,Water,,2023-08-08,15:52:00,PDT,,,,,,,,,,,,SWQM,,MORONGO1_WQX-M000,,,,,33.9873000000,-116.7861000000,,,,,,,,,,,,,,,,,,,,,,,,,,MBMI_QAPP,MORONGO1_WQX,Standard Method,,,Probe/Sensor,,,,,,,,,,,,,,,pH,,7.87,None,,Final,,Actual,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,STORET
PECHANGA_WQX,"Pechanga Band of Luiseno Mission Indians of the Pechanga Reservation, California (Tribal)",PECHANGA_WQX-ST 2:20230802:0928:SR:,Sample-Routine,Water,,2023-08-02,09:28:00,PDT,,,,,,,,,,,,PED Monitoring,,PECHANGA_WQX-ST 2,,,,,33.4365000000,-117.0448000000,,,,,,,,,,,,,,,,,,,,,,,,,,SASMN,PECHANGA_WQX,SASMN,PECHANGA_WQX,Sample Collection Method for Pechanga Tribe according to their QAPP,Water Bottle,,,,,,,,,,,,,Present Below Quantification Limit,,Escherichia coli,,,,,Final,,Actual,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,9221-E,APHA,9221 E ~ Fecal Coliform Procedure- Multiple-Tube Procedure,,https://www.nemi.gov/methods/method_summary/5588/,,2023-08-02,,,,,,,,Lower Reporting Limit,2,MPN/100mL,,,,,,,,,,,,,,,,,STORET
ABCI_WQX,Augustine Band of Cahuilla Indians (Tribal),ABCI_WQX-MW_4:20230802:0000:FM:PS:,Field Msr/Obs,Water,,2023-08-02,,,,,,,,,,,,,,ABCIFY20-25,,ABCI_WQX-MW_4,,,,,33.6548000000,-116.1975000000,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,Probe/Sensor,,,,,,,,,,,,,,,Oxidation reduction potential (ORP),,135.4,mV,,Final,,Actual,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,STORET
MORONGO1_WQX,Morongo Band of Mission Indians,MORONGO1_WQX-SPS080823,Field Msr/Obs,Water,,2023-08-08,15:12:00,PDT,,,,,,,,,,,,SWQM,,MORONGO1_WQX-SPS,,,,,33.9539700000,-116.7984000000,,,,,,,,,,,,,,,,,,,,,,,,,,MBMI_QAPP,MORONGO1_WQX,Standard Method,,,Probe/Sensor,,,,,,,,,,,,,,,Total dissolved solids,,270,mg/L,,Final,,Actual,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,STORET
SOBOBA_WQX,"Soboba Band of Luiseno Indians, California (Tribal)",SOBOBA_WQX-IC2:20230802100000:FM:.05,Field Msr/Obs,Water,,2023-08-02,10:00:00,PST,,,,,.05,ft,,,,,,Soboba_WQM,,SOBOBA_WQX-IC2,,,,,33.4639700000,-116.5096000000,,,,,,,,,,,,,,,,,,,,,,,,,,SOBOBA_QAPP,SOBOBA_WQX,SOBOBA_QAPP,,,Probe/Sensor,MP25T,,,,,,,,,,,,,,Specific conductance,,0.241,mS/cm,,Final,,Actual,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,STORET
PECHANGA_WQX,"Pechanga Band of Luiseno Mission Indians of the Pechanga Reservation, California (Tribal)",PECHANGA_WQX-ST 4:20230802:1038:SR:,Sample-Routine,Water,,2023-08-02,10:38:00,PDT,,,,,,,,,,,,PED Monitoring,,PECHANGA_WQX-ST 4,,,,,33.4405900000,-117.0320000000,,,,,,,,,,,,,,,,,,,,,,,,,,SASMN,PECHANGA_WQX,SASMN,PECHANGA_WQX,Sample Collection Method for Pechanga Tribe according to their QAPP,Water Bottle,,,,,,,,,,,,,Present Below Quantification Limit,,Escherichia coli,,,,,Final,,Actual,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,9221-E,APHA,9221 E ~ Fecal Coliform Procedure- Multiple-Tube Procedure,,https://www.nemi.gov/methods/method_summary/5588/,,2023-08-02,,,,,,,,Lower Reporting Limit,2,MPN/100mL,,,,,,,,,,,,,,,,,STORET
SOBOBA_WQX,"Soboba Band of Luiseno Indians, California (Tribal)",SOBOBA_WQX-IC2:20230802100000:FM:.05,Field Msr/Obs,Water,,2023-08-02,10:00:00,PST,,,,,.05,ft,,,,,,Soboba_WQM,,SOBOBA_WQX-IC2,,,,,33.4639700000,-116.5096000000,,,,,,,,,,,,,,,,,,,,,,,,,,SOBOBA_QAPP,SOBOBA_WQX,SOBOBA_QAPP,,,Probe/Sensor,MP25T,,,,,,,,,,,,,,Flow,,0.111,m/sec,,Final,,Actual,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,STORET
MORONGO1_WQX,Morongo Band of Mission Indians,MORONGO1_WQX-SPS080823,Field Msr/Obs,Water,,2023-08-08,15:12:00,PDT,,,,,,,,,,,,SWQM,,MORONGO1_WQX-SPS,,,,,33.9539700000,-116.7984000000,,,,,,,,,,,,,,,,,,,,,,,,,,MBMI_QAPP,MORONGO1_WQX,Standard Method,,,Probe/Sensor,,,,,,,,,,,,,,,Barometric pressure,,27.326,inHg,,Final,,Actual,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,STORET
MORONGO1_WQX,Morongo Band of Mission Indians,MORONGO1_WQX-WC1080823,Field Msr/Obs,Water,,2023-08-08,10:22:00,PDT,,,,,,,,,,,,SWQM,,MORONGO1_WQX-WC1,,,,,34.0143000000,-116.8205000000,,,,,,,,,,,,,,,,,,,,,,,,,,MBMI_QAPP,MORONGO1_WQX,Standard Method,,,Probe/Sensor,,,,,,,,,,,,,,,Total dissolved solids,,229,mg/L,,Final,,Actual,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,STORET
PECHANGA_WQX,"Pechanga Band of Luiseno Mission Indians of the Pechanga Reservation, California (Tribal)",PECHANGA_WQX-ST 4:20230802:1038:SR:,Sample-Routine,Water,,2023-08-02,10:38:00,PDT,,,,,,,,,,,,PED Monitoring,,PECHANGA_WQX-ST 4,,,,,33.4405900000,-117.0320000000,,,,,,,,,,,,,,,,,,,,,,,,,,SASMN,PECHANGA_WQX,SASMN,PECHANGA_WQX,Sample Collection Method for Pechanga Tribe according to their QAPP,Water Bottle,,,,,,,,,,,,,,,Enterococcus,,6,cfu/100mL,,Final,,Actual,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,9230-C,APHA,"9230 C ~ Fecal Streptococcus and Enterococcus Groups, Membrane Filter Techniques",,,,2023-08-02,,,,,,,,Lower Reporting Limit,1,cfu/100mL,,,,,,,,,,,,,,,,,STORET
SOBOBA_WQX,"Soboba Band of Luiseno Indians, California (Tribal)",SOBOBA_WQX-ICHS:20230802100000:FM:.05,Field Msr/Obs,Water,,2023-08-02,10:00:00,PST,,,,,.05,ft,,,,,,Soboba_WQM,,SOBOBA_WQX-ICHS,,,,,33.4631100000,-116.5059000000,,,,,,,,,,,,,,,,,,,,,,,,,,SOBOBA_QAPP,SOBOBA_WQX,SOBOBA_QAPP,,,Probe/Sensor,MP25T,,,,,,,,,,,,,,Turbidity,,0.32,NTU,,Final,,Actual,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,STORET
ABCI_WQX,Augustine Band of Cahuilla Indians (Tribal),ABCI_WQX-MW_4:20230802:0000:FM:PS:,Field Msr/Obs,Water,,2023-08-02,,,,,,,,,,,,,,ABCIFY20-25,,ABCI_WQX-MW_4,,,,,33.6548000000,-116.1975000000,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,Probe/Sensor,,,,,,,,,,,,,,,Dissolved oxygen (DO),,4.94,mg/L,,Final,,Actual,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,STORET
MORONGO1_WQX,Morongo Band of Mission Indians,MORONGO1_WQX-WC1080823,Field Msr/Obs,Water,,2023-08-08,10:22:00,PDT,,,,,,,,,,,,SWQM,,MORONGO1_WQX-WC1,,,,,34.0143000000,-116.8205000000,,,,,,,,,,,,,,,,,,,,,,,,,,MBMI_QAPP,MORONGO1_WQX,Standard Method,,,Probe/Sensor,,,,,,,,,,,,,,,Barometric pressure,,25.212,inHg,,Final,,Actual,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,STORET
ABCI_WQX,Augustine Band of Cahuilla Indians (Tribal),ABCI_WQX-MW_6:20230802:0000:FM:PS:,Field Msr/Obs,Water,,2023-08-02,,,,,,,,,,,,,,ABCIFY20-25,,ABCI_WQX-MW_6,,,,,33.6526000000,-116.1889000000,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,Probe/Sensor,,,,,,,,,,,,,,,Dissolved oxygen (DO),,6.46,mg/L,,Final,,Actual,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,STORET
SOBOBA_WQX,"Soboba Band of Luiseno Indians, California (Tribal)",SOBOBA_WQX-ICHS:20230802100000:FM:.05,Field Msr/Obs,Water,,2023-08-02,10:00:00,PST,,,,,.05,ft,,,,,,Soboba_WQM,,SOBOBA_WQX-ICHS,,,,,33.4631100000,-116.5059000000,,,,,,,,,,,,,,,,,,,,,,,,,,SOBOBA_QAPP,SOBOBA_WQX,SOBOBA_QAPP,,,Probe/Sensor,MP25T,,,,,,,,,,,,,,Flow,,0.017,m/sec,,Final,,Actual,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,STORET
MORONGO1_WQX,Morongo Band of Mission Indians,MORONGO1_WQX-LM1080823,Field Msr/Obs,Water,,2023-08-08,11:18:00,PDT,,,,,,,,,,,,SWQM,,MORONGO1_WQX-LM1,,,,,33.9908000000,-116.8426000000,,,,,,,,,,,,,,,,,,,,,,,,,,MBMI_QAPP,MORONGO1_WQX,Standard Method,,,Probe/Sensor,,,,,,,,,,,,,,,pH,,8.52,None,,Final,,Actual,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,STORET
PECHANGA_WQX,"Pechanga Band of Luiseno Mission Indians of the Pechanga Reservation, California (Tribal)",PECHANGA_WQX-ST 2:20230802:0928:SR:,Sample-Routine,Water,,2023-08-02,09:28:00,PDT,,,,,,,,,,,,PED Monitoring,,PECHANGA_WQX-ST 2,,,,,33.4365000000,-117.0448000000,,,,,,,,,,,,,,,,,,,,,,,,,,SASMN,PECHANGA_WQX,SASMN,PECHANGA_WQX,Sample Collection Method for Pechanga Tribe according to their QAPP,Water Bottle,,,,,,,,,,,,,,as NH3,Ammonia,Dissolved,0.34,mg/L,,Final,,Actual,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,4500-NH3 B,APHA,4500 NH3 B ~ Ammonia by Titration,,https://www.nemi.gov/methods/method_summary/9696/,,2023-08-02,,,,,,,,Lower Reporting Limit,0.1,mg/L,,,,,,,,,,,,,,,,,STORET
MORONGO1_WQX,Morongo Band of Mission Indians,MORONGO1_WQX-HE1080823,Field Msr/Obs,Water,,2023-08-08,09:36:00,PDT,,,,,,,,,,,,SWQM,,MORONGO1_WQX-HE1,,,,,33.9743400000,-116.8605000000,,,,,,,,,,,,,,,,,,,,,,,,,,MBMI_QAPP,MORONGO1_WQX,Standard Method,,,Probe/Sensor,,,,,,,,,,,,,,,pH,,7.97,None,,Final,,Actual,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,STORET
MORONGO1_WQX,Morongo Band of Mission Indians,MORONGO1_WQX-M000080823,Field Msr/Obs,Water,,2023-08-08,15:52:00,PDT,,,,,,,,,,,,SWQM,,MORONGO1_WQX-M000,,,,,33.9873000000,-116.7861000000,,,,,,,,,,,,,,,,,,,,,,,,,,MBMI_QAPP,MORONGO1_WQX,Standard Method,,,Probe/Sensor,,,,,,,,,,,,,,,Salinity,,0.2,PSS,,Final,,Actual,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,STORET
MORONGO1_WQX,Morongo Band of Mission Indians,MORONGO1_WQX-M000080823,Field Msr/Obs,Water,,2023-08-08,15:52:00,PDT,,,,,,,,,,,,SWQM,,MORONGO1_WQX-M000,,,,,33.9873000000,-116.7861000000,,,,,,,,,,,,,,,,,,,,,,,,,,MBMI_QAPP,MORONGO1_WQX,Standard Method,,,Probe/Sensor,,,,,,,,,,,,,,,Turbidity,,0.7,NTU,,Final,,Actual,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,STORET
PECHANGA_WQX,"Pechanga Band of Luiseno Mission Indians of the Pechanga Reservation, California (Tribal)",PECHANGA_WQX-ST 3:20230802:0843:SR:,Sample-Routine,Water,,2023-08-02,08:43:00,PDT,,,,,,,,,,,,PED Monitoring,,PECHANGA_WQX-ST 3,,,,,33.4533100000,-117.1189000000,,,,,,,,,,,,,,,,,,,,,,,,,,SASMN,PECHANGA_WQX,SASMN,PECHANGA_WQX,Sample Collection Method for Pechanga Tribe according to their QAPP,Water Bottle,,,,,,,,,,,,,Not Detected,as NO2,Nitrite,Dissolved,,,,Final,,Actual,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,4500-NO2(B),APHA,4500 NO2 B ~ Nitrite in Water by Colorimetry,,https://www.nemi.gov/methods/method_summary/7415/,,2023-08-02,,,,,,,,Lower Reporting Limit,0.02,mg/L,,,,,,,,,,,,,,,,,STORET
ABCI_WQX,Augustine Band of Cahuilla Indians (Tribal),ABCI_WQX-MW_7:20230808:0000:FM:PS:,Field Msr/Obs,Water,,2023-08-08,,,,,,,,,,,,,,ABCIFY20-25,,ABCI_WQX-MW_7,,,,,33.6507000000,-116.1940000000,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,Probe/Sensor,,,,,,,,,,,,,,,Dissolved oxygen (DO),,7.14,mg/L,,Final,,Actual,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,STORET
MORONGO1_WQX,Morongo Band of Mission Indians,MORONGO1_WQX-HW1080823,Field Msr/Obs,Water,,2023-08-08,09:27:00,PDT,,,,,,,,,,,,SWQM,,MORONGO1_WQX-HW1,,,,,33.9744700000,-116.8608000000,,,,,,,,,,,,,,,,,,,,,,,,,,MBMI_QAPP,MORONGO1_WQX,Standard Method,,,Probe/Sensor,,,,,,,,,,,,,,,Turbidity,,4.89,NTU,,Final,,Actual,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,STORET
MORONGO1_WQX,Morongo Band of Mission Indians,MORONGO1_WQX-HW1080823,Field Msr/Obs,Water,,2023-08-08,09:27:00,PDT,,,,,,,,,,,,SWQM,,MORONGO1_WQX-HW1,,,,,33.9744700000,-116.8608000000,,,,,,,,,,,,,,,,,,,,,,,,,,MBMI_QAPP,MORONGO1_WQX,Standard Method,,,Probe/Sensor,,,,,,,,,,,,,,,Barometric pressure,,27.046,inHg,,Final,,Actual,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,STORET
SOBOBA_WQX,"Soboba Band of Luiseno Indians, California (Tribal)",SOBOBA_WQX-ICHS:20230802100000:FM:.05,Field Msr/Obs,Water,,2023-08-02,10:00:00,PST,,,,,.05,ft,,,,,,Soboba_WQM,,SOBOBA_WQX-ICHS,,,,,33.4631100000,-116.5059000000,,,,,,,,,,,,,,,,,,,,,,,,,,SOBOBA_QAPP,SOBOBA_WQX,SOBOBA_QAPP,,,Probe/Sensor,MP25T,,,,,,,,,,,,,,Oxidation reduction potential (ORP),,53.06,mV,,Final,,Actual,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,STORET
PECHANGA_WQX,"Pechanga Band of Luiseno Mission Indians of the Pechanga Reservation, California (Tribal)",PECHANGA_WQX-ST 4:20230802:1038:FM:,Field Msr/Obs,Water,,2023-08-02,10:38:00,PDT,,,,,,,,,,,,PED Monitoring,,PECHANGA_WQX-ST 4,,,,,33.4405900000,-117.0320000000,,,,,,,,,,,,,,,,,,,,,,,,,,SASMN,PECHANGA_WQX,SASMN,PECHANGA_WQX,Sample Collection Method for Pechanga Tribe according to their QAPP,Probe/Sensor,,,,,,,,,,,,,,,pH,,-180,mV,,Final,,Actual,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,STORET
PECHANGA_WQX,"Pechanga Band of Luiseno Mission Indians of the Pechanga Reservation, California (Tribal)",PECHANGA_WQX-ST 3:20230802:0843:SR:,Sample-Routine,Water,,2023-08-02,08:43:00,PDT,,,,,,,,,,,,PED Monitoring,,PECHANGA_WQX-ST 3,,,,,33.4533100000,-117.1189000000,,,,,,,,,,,,,,,,,,,,,,,,,,SASMN,PECHANGA_WQX,SASMN,PECHANGA_WQX,Sample Collection Method for Pechanga Tribe according to their QAPP,Water Bottle,,,,,,,,,,,,,,as NH3,Ammonia,Dissolved,0.29,mg/L,,Final,,Actual,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,4500-NH3 B,APHA,4500 NH3 B ~ Ammonia by Titration,,https://www.nemi.gov/methods/method_summary/9696/,,2023-08-02,,,,,,,,Lower Reporting Limit,0.1,mg/L,,,,,,,,,,,,,,,,,STORET
MORONGO1_WQX,Morongo Band of Mission Indians,MORONGO1_WQX-HE1080823,Field Msr/Obs,Water,,2023-08-08,09:36:00,PDT,,,,,,,,,,,,SWQM,,MORONGO1_WQX-HE1,,,,,33.9743400000,-116.8605000000,,,,,,,,,,,,,,,,,,,,,,,,,,MBMI_QAPP,MORONGO1_WQX,Standard Method,,,Probe/Sensor,,,,,,,,,,,,,,,Specific conductance,,291.4,uS/cm,,Final,,Actual,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,STORET
MORONGO1_WQX,Morongo Band of Mission Indians,MORONGO1_WQX-HW1080823,Field Msr/Obs,Water,,2023-08-08,09:27:00,PDT,,,,,,,,,,,,SWQM,,MORONGO1_WQX-HW1,,,,,33.9744700000,-116.8608000000,,,,,,,,,,,,,,,,,,,,,,,,,,MBMI_QAPP,MORONGO1_WQX,Standard Method,,,Probe/Sensor,,,,,,,,,,,,,,,Salinity,,0.16,PSS,,Final,,Actual,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,STORET
PECHANGA_WQX,"Pechanga Band of Luiseno Mission Indians of the Pechanga Reservation, California (Tribal)",PECHANGA_WQX-ST 2:20230802:0928:SR:,Sample-Routine,Water,,2023-08-02,09:28:00,PDT,,,,,,,,,,,,PED Monitoring,,PECHANGA_WQX-ST 2,,,,,33.4365000000,-117.0448000000,,,,,,,,,,,,,,,,,,,,,,,,,,SASMN,PECHANGA_WQX,SASMN,PECHANGA_WQX,Sample Collection Method for Pechanga Tribe according to their QAPP,Water Bottle,,,,,,,,,,,,,Not Detected,as P,"Total Phosphorus, mixed forms",Total,,,,Final,,Actual,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,365.2,USEPA,Phosphorus by Single Reagent Colorimetry,,https://www.nemi.gov/methods/method_summary/5254/,,2023-08-02,,,,,,,,Lower Reporting Limit,0.05,mg/L,,,,,,,,,,,,,,,,,STORET
MORONGO1_WQX,Morongo Band of Mission Indians,MORONGO1_WQX-SPS080823,Field Msr/Obs,Water,,2023-08-08,15:12:00,PDT,,,,,,,,,,,,SWQM,,MORONGO1_WQX-SPS,,,,,33.9539700000,-116.7984000000,,,,,,,,,,,,,,,,,,,,,,,,,,MBMI_QAPP,MORONGO1_WQX,Standard Method,,,Probe/Sensor,,,,,,,,,,,,,,,Specific conductance,,414.7,uS/cm,,Final,,Actual,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,STORET
PECHANGA_WQX,"Pechanga Band of Luiseno Mission Indians of the Pechanga Reservation, California (Tribal)",PECHANGA_WQX-ST 2:20230802:0928:SR:,Sample-Routine,Water,,2023-08-02,09:28:00,PDT,,,,,,,,,,,,PED Monitoring,,PECHANGA_WQX-ST 2,,,,,33.4365000000,-117.0448000000,,,,,,,,,,,,,,,,,,,,,,,,,,SASMN,PECHANGA_WQX,SASMN,PECHANGA_WQX,Sample Collection Method for Pechanga Tribe according to their QAPP,Water Bottle,,,,,,,,,,,,,Not Detected,as NO2,Nitrite,Dissolved,,,,Final,,Actual,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,4500-NO2(B),APHA,4500 NO2 B ~ Nitrite in Water by Colorimetry,,https://www.nemi.gov/methods/method_summary/7415/,,2023-08-02,,,,,,,,Lower Reporting Limit,0.02,mg/L,,,,,,,,,,,,,,,,,STORET
PECHANGA_WQX,"Pechanga Band of Luiseno Mission Indians of the Pechanga Reservation, California (Tribal)",PECHANGA_WQX-ST 2:20230802:0928:SR:,Sample-Routine,Water,,2023-08-02,09:28:00,PDT,,,,,,,,,,,,PED Monitoring,,PECHANGA_WQX-ST 2,,,,,33.4365000000,-117.0448000000,,,,,,,,,,,,,,,,,,,,,,,,,,SASMN,PECHANGA_WQX,SASMN,PECHANGA_WQX,Sample Collection Method for Pechanga Tribe according to their QAPP,Water Bottle,,,,,,,,,,,,,,as NH4,Total Kjeldahl nitrogen,Total,0.36,mg/L,,Final,,Actual,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,351.2,USEPA,351.2 ~ EPA; Total Kjeldahl Nitrogen by Colorimetry,,https://www.nemi.gov/methods/method_summary/9626/,,2023-08-02,,,,,,,,Lower Reporting Limit,0.1,mg/L,,,,,,,,,,,,,,,,,STORET
MORONGO1_WQX,Morongo Band of Mission Indians,MORONGO1_WQX-LMO080823,Field Msr/Obs,Water,,2023-08-08,11:30:00,PDT,,,,,,,,,,,,SWQM,,MORONGO1_WQX-LMO,,,,,33.9905500000,-116.8423000000,,,,,,,,,,,,,,,,,,,,,,,,,,MBMI_QAPP,MORONGO1_WQX,Standard Method,,,Probe/Sensor,,,,,,,,,,,,,,,Specific conductance,,354.3,uS/cm,,Final,,Actual,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,STORET
ABCI_WQX,Augustine Band of Cahuilla Indians (Tribal),ABCI_WQX-MW_4:20230802:0000:FM:PS:,Field Msr/Obs,Water,,2023-08-02,,,,,,,,,,,,,,ABCIFY20-25,,ABCI_WQX-MW_4,,,,,33.6548000000,-116.1975000000,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,Probe/Sensor,,,,,,,,,,,,,,,Conductivity,,619,uS/cm,,Final,,Actual,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,STORET
ABCI_WQX,Augustine Band of Cahuilla Indians (Tribal),ABCI_WQX-MW_7:20230808:0000:FM:PS:,Field Msr/Obs,Water,,2023-08-08,,,,,,,,,,,,,,ABCIFY20-25,,ABCI_WQX-MW_7,,,,,33.6507000000,-116.1940000000,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,Probe/Sensor,,,,,,,,,,,,,,,Conductivity,,426,uS/cm,,Final,,Actual,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,STORET
ABCI_WQX,Augustine Band of Cahuilla Indians (Tribal),ABCI_WQX-MW_6:20230802:0000:FM:PS:,Field Msr/Obs,Water,,2023-08-02,,,,,,,,,,,,,,ABCIFY20-25,,ABCI_WQX-MW_6,,,,,33.6526000000,-116.1889000000,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,Probe/Sensor,,,,,,,,,,,,,,,Conductivity,,238,uS/cm,,Final,,Actual,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,STORET
MORONGO1_WQX,Morongo Band of Mission Indians,MORONGO1_WQX-H000080823,Field Msr/Obs,Water,,2023-08-08,09:12:00,PDT,,,,,,,,,,,,SWQM,,MORONGO1_WQX-H000,,,,,33.9682200000,-116.8630000000,,,,,,,,,,,,,,,,,,,,,,,,,,MBMI_QAPP,MORONGO1_WQX,Standard Method,,,Probe/Sensor,,,,,,,,,,,,,,,Salinity,,0.18,PSS,,Final,,Actual,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,STORET
MORONGO1_WQX,Morongo Band of Mission Indians,MORONGO1_WQX-LM1080823,Field Msr/Obs,Water,,2023-08-08,11:18:00,PDT,,,,,,,,,,,,SWQM,,MORONGO1_WQX-LM1,,,,,33.9908000000,-116.8426000000,,,,,,,,,,,,,,,,,,,,,,,,,,MBMI_QAPP,MORONGO1_WQX,Standard Method,,,Probe/Sensor,,,,,,,,,,,,,,,"Temperature, water",,65.7,deg F,,Final,,Actual,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,STORET
PECHANGA_WQX,"Pechanga Band of Luiseno Mission Indians of the Pechanga Reservation, California (Tribal)",PECHANGA_WQX-ST 4:20230802:1038:SR:,Sample-Routine,Water,,2023-08-02,10:38:00,PDT,,,,,,,,,,,,PED Monitoring,,PECHANGA_WQX-ST 4,,,,,33.4405900000,-117.0320000000,,,,,,,,,,,,,,,,,,,,,,,,,,SASMN,PECHANGA_WQX,SASMN,PECHANGA_WQX,Sample Collection Method for Pechanga Tribe according to their QAPP,Water Bottle,,,,,,,,,,,,,,as NO3,Nitrate,Dissolved,1.7,mg/L,,Final,,Actual,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,10206,HACH,"Nitrate, Dimethylphenol Method",,,,2023-08-02,,,,,,,,Lower Reporting Limit,0.5,mg/L,,,,,,,,,,,,,,,,,STORET
MORONGO1_WQX,Morongo Band of Mission Indians,MORONGO1_WQX-BOG080823,Field Msr/Obs,Water,,2023-08-08,10:59:00,PDT,,,,,,,,,,,,SWQM,,MORONGO1_WQX-BOG,,,,,33.9925700000,-116.8436000000,,,,,,,,,,,,,,,,,,,,,,,,,,MBMI_QAPP,MORONGO1_WQX,Standard Method,,,Probe/Sensor,,,,,,,,,,,,,,,Total dissolved solids,,232,mg/L,,Final,,Actual,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,STORET
MORONGO1_WQX,Morongo Band of Mission Indians,MORONGO1_WQX-LM1080823,Field Msr/Obs,Water,,2023-08-08,11:18:00,PDT,,,,,,,,,,,,SWQM,,MORONGO1_WQX-LM1,,,,,33.9908000000,-116.8426000000,,,,,,,,,,,,,,,,,,,,,,,,,,MBMI_QAPP,MORONGO1_WQX,Standard Method,,,Probe/Sensor,,,,,,,,,,,,,,,Barometric pressure,,26.520,inHg,,Final,,Actual,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,STORET
SOBOBA_WQX,"Soboba Band of Luiseno Indians, California (Tribal)",SOBOBA_WQX-ICHS:20230802100000:FM:.05,Field Msr/Obs,Water,,2023-08-02,10:00:00,PST,,,,,.05,ft,,,,,,Soboba_WQM,,SOBOBA_WQX-ICHS,,,,,33.4631100000,-116.5059000000,,,,,,,,,,,,,,,,,,,,,,,,,,SOBOBA_QAPP,SOBOBA_WQX,SOBOBA_QAPP,,,Probe/Sensor,MP25T,,,,,,,,,,,,,,Dissolved oxygen (DO),,5.58,mg/L,,Final,,Actual,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,STORET
MORONGO1_WQX,Morongo Band of Mission Indians,MORONGO1_WQX-BOG080823,Field Msr/Obs,Water,,2023-08-08,10:59:00,PDT,,,,,,,,,,,,SWQM,,MORONGO1_WQX-BOG,,,,,33.9925700000,-116.8436000000,,,,,,,,,,,,,,,,,,,,,,,,,,MBMI_QAPP,MORONGO1_WQX,Standard Method,,,Probe/Sensor,,,,,,,,,,,,,,,"Temperature, water",,66.4,deg F,,Final,,Actual,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,STORET
MORONGO1_WQX,Morongo Band of Mission Indians,MORONGO1_WQX-SPS080823,Field Msr/Obs,Water,,2023-08-08,15:12:00,PDT,,,,,,,,,,,,SWQM,,MORONGO1_WQX-SPS,,,,,33.9539700000,-116.7984000000,,,,,,,,,,,,,,,,,,,,,,,,,,MBMI_QAPP,MORONGO1_WQX,Standard Method,,,Probe/Sensor,,,,,,,,,,,,,,,pH,,8.42,None,,Final,,Actual,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,STORET
PECHANGA_WQX,"Pechanga Band of Luiseno Mission Indians of the Pechanga Reservation, California (Tribal)",PECHANGA_WQX-ST 3:20230802:0843:SR:,Sample-Routine,Water,,2023-08-02,08:43:00,PDT,,,,,,,,,,,,PED Monitoring,,PECHANGA_WQX-ST 3,,,,,33.4533100000,-117.1189000000,,,,,,,,,,,,,,,,,,,,,,,,,,SASMN,PECHANGA_WQX,SASMN,PECHANGA_WQX,Sample Collection Method for Pechanga Tribe according to their QAPP,Water Bottle,,,,,,,,,,,,,,as NH4,Total Kjeldahl nitrogen,Total,0.31,mg/L,,Final,,Actual,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,351.2,USEPA,351.2 ~ EPA; Total Kjeldahl Nitrogen by Colorimetry,,https://www.nemi.gov/methods/method_summary/9626/,,2023-08-02,,,,,,,,Lower Reporting Limit,0.1,mg/L,,,,,,,,,,,,,,,,,STORET
ABCI_WQX,Augustine Band of Cahuilla Indians (Tribal),ABCI_WQX-MW_7:20230808:0000:FM:PS:,Field Msr/Obs,Water,,2023-08-08,,,,,,,,,,,,,,ABCIFY20-25,,ABCI_WQX-MW_7,,,,,33.6507000000,-116.1940000000,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,Probe/Sensor,,,,,,,,,,,,,,,pH,,8.19,None,,Final,,Actual,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,STORET
MORONGO1_WQX,Morongo Band of Mission Indians,MORONGO1_WQX-HW1080823,Field Msr/Obs,Water,,2023-08-08,09:27:00,PDT,,,,,,,,,,,,SWQM,,MORONGO1_WQX-HW1,,,,,33.9744700000,-116.8608000000,,,,,,,,,,,,,,,,,,,,,,,,,,MBMI_QAPP,MORONGO1_WQX,Standard Method,,,Probe/Sensor,,,,,,,,,,,,,,,Total dissolved solids,,217,mg/L,,Final,,Actual,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,STORET
PECHANGA_WQX,"Pechanga Band of Luiseno Mission Indians of the Pechanga Reservation, California (Tribal)",PECHANGA_WQX-ST 3:20230802:0843:SR:,Sample-Routine,Water,,2023-08-02,08:43:00,PDT,,,,,,,,,,,,PED Monitoring,,PECHANGA_WQX-ST 3,,,,,33.4533100000,-117.1189000000,,,,,,,,,,,,,,,,,,,,,,,,,,SASMN,PECHANGA_WQX,SASMN,PECHANGA_WQX,Sample Collection Method for Pechanga Tribe according to their QAPP,Water Bottle,,,,,,,,,,,,,,,Enterococcus,,190,cfu/100mL,,Final,,Actual,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,9230-C,APHA,"9230 C ~ Fecal Streptococcus and Enterococcus Groups, Membrane Filter Techniques",,,,2023-08-02,,,,,,,,Lower Reporting Limit,1,cfu/100mL,,,,,,,,,,,,,,,,,STORET
PECHANGA_WQX,"Pechanga Band of Luiseno Mission Indians of the Pechanga Reservation, California (Tribal)",PECHANGA_WQX-ST 3:20230802:0843:SR:,Sample-Routine,Water,,2023-08-02,08:43:00,PDT,,,,,,,,,,,,PED Monitoring,,PECHANGA_WQX-ST 3,,,,,33.4533100000,-117.1189000000,,,,,,,,,,,,,,,,,,,,,,,,,,SASMN,PECHANGA_WQX,SASMN,PECHANGA_WQX,Sample Collection Method for Pechanga Tribe according to their QAPP,Water Bottle,,,,,,,,,,,,,,,Escherichia coli,,2,MPN/100mL,,Final,,Actual,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,9221-E,APHA,9221 E ~ Fecal Coliform Procedure- Multiple-Tube Procedure,,https://www.nemi.gov/methods/method_summary/5588/,,2023-08-02,,,,,,,,Lower Reporting Limit,2,MPN/100mL,,,,,,,,,,,,,,,,,STORET
MORONGO1_WQX,Morongo Band of Mission Indians,MORONGO1_WQX-LM1080823,Field Msr/Obs,Water,,2023-08-08,11:18:00,PDT,,,,,,,,,,,,SWQM,,MORONGO1_WQX-LM1,,,,,33.9908000000,-116.8426000000,,,,,,,,,,,,,,,,,,,,,,,,,,MBMI_QAPP,MORONGO1_WQX,Standard Method,,,Probe/Sensor,,,,,,,,,,,,,,,Total dissolved solids,,225,mg/L,,Final,,Actual,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,STORET
```
</details>
</div>

## SSURGO

- USDA Soil Survey Geographic Database
- SOAP API that expects user-written SQL statements
- This [PDF doc](https://sdmdataaccess.nrcs.usda.gov/documents/SoilDataAccessQueryGuide.pdf) describes the database you can query

### Example Query

- Below is a portion of the env-agents code to give an idea of how the requests are structured
- I didn't attempt to run an actual query - can look into this more after the initial pass through the various data sources

```python
            soap_envelope = f"""<?xml version="1.0" encoding="utf-8"?>
            <soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
                <soap:Body>
                    <RunQuery xmlns="http://SDMDataAccess.nrcs.usda.gov/Tabular/SDMTabularService.asmx">
                        <Query>SELECT co.cokey, ch.chkey, co.compname, co.comppct_r, ch.hzname, ch.hzdept_r, ch.hzdepb_r, ch.om_r, ch.ph1to1h2o_r, ch.awc_r, ch.claytotal_r, ch.silttotal_r, ch.sandtotal_r, ch.dbthirdbar_r, ch.ksat_r, ch.cec7_r, mu.mukey, mu.musym, mu.muname, mu.mukind, mu.farmlndcl, sa.areasymbol, sa.areaname
FROM sacatalog sa 
INNER JOIN legend lg ON lg.areasymbol = sa.areasymbol 
INNER JOIN mapunit mu ON mu.lkey = lg.lkey 
AND mu.mukey IN (SELECT * from SDA_Get_Mukey_from_intersection_with_WktWgs84('point({lon_lat})'))
INNER JOIN component co ON co.mukey = mu.mukey AND co.majcompflag = 'Yes'
INNER JOIN chorizon ch ON ch.cokey = co.cokey
ORDER BY co.cokey, ch.hzdept_r ASC</Query>
                    </RunQuery>
                </soap:Body>
            </soap:Envelope>"""
```

## OpenStreetMap Overpass API

- Community maintained 
- Several Python packages already available
  - https://github.com/mvexel/overpass-api-python-wrapper
- No OpenAPI spec
- The API is described in this wiki: https://wiki.openstreetmap.org/wiki/Overpass_API
- Seems to have a very detailed custom query language (Overpass QL)
- Note on wiki about downloading large datasets:
>Downloading big data
>
>As the size of an Overpass API query result is only known when the download is complete, it is impossible to give an ETA while downloading. And the dynamically generated files from Overpass API typically take longer to generate and download than downloading existing static extracts of the same region. As a result, when you want to extract country-sized regions with all (or nearly all) data in it, it's better to use planet.osm mirrors for that. Overpass API is most useful when the amount of data needed is only a selection of the data available in the region.
- The entire dataset is downloadable (see https://wiki.openstreetmap.org/wiki/Planet.osm)
  - Updated weekly
  - 2.2 TB (uncompressed); 83 GB (PBF compressed)

### Example Query

#### Request

There is an example python script that runs a query from the wiki in `examples/osm_overpass_example.py`
To run the example and save the output to a json file:

```bash
uv sync
uv run python examples/osm_overpass_example.py > osm_overpass_output.json
```

The query embedded in the example request is:

```
[bbox:30.618338,-96.323712,30.591028,-96.330826]
[out:json]
[timeout:90]
;
(
    way
        (
              30.626917110746,
              -96.348809105664,
              30.634468750236,
              -96.339893442898
          );
);
out geom;
```

#### Response

<div>
<details>
<summary>Click to expand</summary>

```json
{
  "version": 0.6,
  "generator": "Overpass API 0.7.62.8 e802775f",
  "osm3s": {
    "timestamp_osm_base": "2025-10-17T15:20:36Z",
    "copyright": "The data included in this document is from www.openstreetmap.org. The data is made available under ODbL."
  },
  "elements": [
    {
      "type": "way",
      "id": 20714383,
      "bounds": {
        "minlat": 30.6277358,
        "minlon": -96.341929,
        "maxlat": 30.628834,
        "maxlon": -96.340566
      },
      "nodes": [
        222454378,
        4204990218,
        222454386
      ],
      "geometry": [
        {
          "lat": 30.6277358,
          "lon": -96.340566
        },
        {
          "lat": 30.6278459,
          "lon": -96.3407026
        },
        {
          "lat": 30.628834,
          "lon": -96.341929
        }
      ],
      "tags": {
        "highway": "service",
        "name": "W-X Row",
        "postal_code": "77840",
        "tiger:county": "Brazos, TX"
      }
    },
    {
      "type": "way",
      "id": 20718240,
      "bounds": {
        "minlat": 30.6266916,
        "minlon": -96.3501748,
        "maxlat": 30.6301572,
        "maxlon": -96.3459838
      },
      "nodes": [
        222493143,
        222493147,
        222493151,
        3906238127,
        3906238105,
        222493155
      ],
      "geometry": [
        {
          "lat": 30.6301572,
          "lon": -96.3501748
        },
        {
          "lat": 30.6295126,
          "lon": -96.3493944
        },
        {
          "lat": 30.6288617,
          "lon": -96.3486331
        },
        {
          "lat": 30.6285368,
          "lon": -96.348235
        },
        {
          "lat": 30.6267605,
          "lon": -96.3460901
        },
        {
          "lat": 30.6266916,
          "lon": -96.3459838
        }
      ],
      "tags": {
        "highway": "residential",
        "name": "Culpepper Drive",
        "postal_code": "77801",
        "tiger:county": "Brazos, TX"
      }
    },
    ...
  ]
}
```
</details>
</div>

## Soilgrids

- Global digital soil maps
- OpenAPI spec available

| Data Product | OpenAPI spec URL                                   | 
|--------------|----------------------------------------------------|
| soilgrids    | https://rest.isric.org/soilgrids/v2.0/openapi.json |

### Query Example

#### Request

```bash
curl -X 'GET' \
  'https://rest.isric.org/soilgrids/v2.0/properties/query?lon=-116.5&lat=33.8&property=bdod&property=cec&property=cfvo&property=clay&property=nitrogen&property=ocd&property=ocs&property=phh2o&property=sand&property=silt&property=soc&property=wv0010&property=wv0033&property=wv1500&depth=0-5cm&depth=0-30cm&depth=5-15cm&depth=15-30cm&depth=30-60cm&depth=60-100cm&depth=100-200cm&value=Q0.05&value=Q0.5&value=Q0.95&value=mean&value=uncertainty' \
  -H 'accept: application/json'
```

#### Response

<div>
<details>
<summary>Click to expand</summary>

```json
{
  "type": "Feature",
  "geometry": {
    "type": "Point",
    "coordinates": [
      -116.5,
      33.8
    ]
  },
  "properties": {
    "layers": [
      {
        "name": "bdod",
        "unit_measure": {
          "d_factor": 100,
          "mapped_units": "cg/cm³",
          "target_units": "kg/dm³",
          "uncertainty_unit": ""
        },
        "depths": [
          {
            "range": {
              "top_depth": 0,
              "bottom_depth": 5,
              "unit_depth": "cm"
            },
            "label": "0-5cm",
            "values": {
              "Q0.5": null,
              "Q0.05": null,
              "Q0.95": null,
              "mean": null,
              "uncertainty": null
            }
          },
          {
            "range": {
              "top_depth": 5,
              "bottom_depth": 15,
              "unit_depth": "cm"
            },
            "label": "5-15cm",
            "values": {
              "Q0.5": null,
              "Q0.05": null,
              "Q0.95": null,
              "mean": null,
              "uncertainty": null
            }
          },
          {
            "range": {
              "top_depth": 15,
              "bottom_depth": 30,
              "unit_depth": "cm"
            },
            "label": "15-30cm",
            "values": {
              "Q0.05": null,
              "Q0.5": null,
              "Q0.95": null,
              "mean": null,
              "uncertainty": null
            }
          },
          {
            "range": {
              "top_depth": 30,
              "bottom_depth": 60,
              "unit_depth": "cm"
            },
            "label": "30-60cm",
            "values": {
              "Q0.05": null,
              "Q0.5": null,
              "Q0.95": null,
              "mean": null,
              "uncertainty": null
            }
          },
          {
            "range": {
              "top_depth": 60,
              "bottom_depth": 100,
              "unit_depth": "cm"
            },
            "label": "60-100cm",
            "values": {
              "Q0.05": null,
              "Q0.5": null,
              "Q0.95": null,
              "mean": null,
              "uncertainty": null
            }
          },
          {
            "range": {
              "top_depth": 100,
              "bottom_depth": 200,
              "unit_depth": "cm"
            },
            "label": "100-200cm",
            "values": {
              "Q0.05": null,
              "Q0.5": null,
              "Q0.95": null,
              "mean": null,
              "uncertainty": null
            }
          }
        ]
      },
      {
        "name": "cec",
        "unit_measure": {
          "d_factor": 10,
          "mapped_units": "mmol(c)/kg",
          "target_units": "cmol(c)/kg",
          "uncertainty_unit": ""
        },
        "depths": [
          {
            "range": {
              "top_depth": 0,
              "bottom_depth": 5,
              "unit_depth": "cm"
            },
            "label": "0-5cm",
            "values": {
              "Q0.5": null,
              "Q0.05": null,
              "Q0.95": null,
              "mean": null,
              "uncertainty": null
            }
          },
          {
            "range": {
              "top_depth": 5,
              "bottom_depth": 15,
              "unit_depth": "cm"
            },
            "label": "5-15cm",
            "values": {
              "Q0.05": null,
              "Q0.5": null,
              "Q0.95": null,
              "mean": null,
              "uncertainty": null
            }
          },
          {
            "range": {
              "top_depth": 15,
              "bottom_depth": 30,
              "unit_depth": "cm"
            },
            "label": "15-30cm",
            "values": {
              "Q0.05": null,
              "Q0.5": null,
              "Q0.95": null,
              "mean": null,
              "uncertainty": null
            }
          },
          {
            "range": {
              "top_depth": 30,
              "bottom_depth": 60,
              "unit_depth": "cm"
            },
            "label": "30-60cm",
            "values": {
              "Q0.5": null,
              "Q0.05": null,
              "Q0.95": null,
              "mean": null,
              "uncertainty": null
            }
          },
          {
            "range": {
              "top_depth": 60,
              "bottom_depth": 100,
              "unit_depth": "cm"
            },
            "label": "60-100cm",
            "values": {
              "Q0.5": null,
              "Q0.05": null,
              "Q0.95": null,
              "mean": null,
              "uncertainty": null
            }
          },
          {
            "range": {
              "top_depth": 100,
              "bottom_depth": 200,
              "unit_depth": "cm"
            },
            "label": "100-200cm",
            "values": {
              "Q0.05": null,
              "Q0.5": null,
              "Q0.95": null,
              "mean": null,
              "uncertainty": null
            }
          }
        ]
      },
      {
        "name": "cfvo",
        "unit_measure": {
          "d_factor": 10,
          "mapped_units": "cm³/dm³",
          "target_units": "cm³/100cm³",
          "uncertainty_unit": ""
        },
        "depths": [
          {
            "range": {
              "top_depth": 0,
              "bottom_depth": 5,
              "unit_depth": "cm"
            },
            "label": "0-5cm",
            "values": {
              "Q0.05": null,
              "Q0.5": null,
              "Q0.95": null,
              "mean": null,
              "uncertainty": null
            }
          },
          {
            "range": {
              "top_depth": 5,
              "bottom_depth": 15,
              "unit_depth": "cm"
            },
            "label": "5-15cm",
            "values": {
              "Q0.5": null,
              "Q0.05": null,
              "Q0.95": null,
              "mean": null,
              "uncertainty": null
            }
          },
          {
            "range": {
              "top_depth": 15,
              "bottom_depth": 30,
              "unit_depth": "cm"
            },
            "label": "15-30cm",
            "values": {
              "Q0.05": null,
              "Q0.5": null,
              "Q0.95": null,
              "mean": null,
              "uncertainty": null
            }
          },
          {
            "range": {
              "top_depth": 30,
              "bottom_depth": 60,
              "unit_depth": "cm"
            },
            "label": "30-60cm",
            "values": {
              "Q0.05": null,
              "Q0.5": null,
              "Q0.95": null,
              "mean": null,
              "uncertainty": null
            }
          },
          {
            "range": {
              "top_depth": 60,
              "bottom_depth": 100,
              "unit_depth": "cm"
            },
            "label": "60-100cm",
            "values": {
              "Q0.05": null,
              "Q0.5": null,
              "Q0.95": null,
              "mean": null,
              "uncertainty": null
            }
          },
          {
            "range": {
              "top_depth": 100,
              "bottom_depth": 200,
              "unit_depth": "cm"
            },
            "label": "100-200cm",
            "values": {
              "Q0.05": null,
              "Q0.5": null,
              "Q0.95": null,
              "mean": null,
              "uncertainty": null
            }
          }
        ]
      },
      {
        "name": "clay",
        "unit_measure": {
          "d_factor": 10,
          "mapped_units": "g/kg",
          "target_units": "%",
          "uncertainty_unit": ""
        },
        "depths": [
          {
            "range": {
              "top_depth": 0,
              "bottom_depth": 5,
              "unit_depth": "cm"
            },
            "label": "0-5cm",
            "values": {
              "Q0.05": null,
              "Q0.5": null,
              "Q0.95": null,
              "mean": null,
              "uncertainty": null
            }
          },
          {
            "range": {
              "top_depth": 5,
              "bottom_depth": 15,
              "unit_depth": "cm"
            },
            "label": "5-15cm",
            "values": {
              "Q0.05": null,
              "Q0.5": null,
              "Q0.95": null,
              "mean": null,
              "uncertainty": null
            }
          },
          {
            "range": {
              "top_depth": 15,
              "bottom_depth": 30,
              "unit_depth": "cm"
            },
            "label": "15-30cm",
            "values": {
              "Q0.05": null,
              "Q0.5": null,
              "Q0.95": null,
              "mean": null,
              "uncertainty": null
            }
          },
          {
            "range": {
              "top_depth": 30,
              "bottom_depth": 60,
              "unit_depth": "cm"
            },
            "label": "30-60cm",
            "values": {
              "Q0.5": null,
              "Q0.05": null,
              "Q0.95": null,
              "mean": null,
              "uncertainty": null
            }
          },
          {
            "range": {
              "top_depth": 60,
              "bottom_depth": 100,
              "unit_depth": "cm"
            },
            "label": "60-100cm",
            "values": {
              "Q0.05": null,
              "Q0.5": null,
              "Q0.95": null,
              "mean": null,
              "uncertainty": null
            }
          },
          {
            "range": {
              "top_depth": 100,
              "bottom_depth": 200,
              "unit_depth": "cm"
            },
            "label": "100-200cm",
            "values": {
              "Q0.5": null,
              "Q0.05": null,
              "Q0.95": null,
              "mean": null,
              "uncertainty": null
            }
          }
        ]
      },
      {
        "name": "nitrogen",
        "unit_measure": {
          "d_factor": 100,
          "mapped_units": "cg/kg",
          "target_units": "g/kg",
          "uncertainty_unit": ""
        },
        "depths": [
          {
            "range": {
              "top_depth": 0,
              "bottom_depth": 5,
              "unit_depth": "cm"
            },
            "label": "0-5cm",
            "values": {
              "Q0.05": null,
              "Q0.5": null,
              "Q0.95": null,
              "mean": null,
              "uncertainty": null
            }
          },
          {
            "range": {
              "top_depth": 5,
              "bottom_depth": 15,
              "unit_depth": "cm"
            },
            "label": "5-15cm",
            "values": {
              "Q0.5": null,
              "Q0.05": null,
              "Q0.95": null,
              "mean": null,
              "uncertainty": null
            }
          },
          {
            "range": {
              "top_depth": 15,
              "bottom_depth": 30,
              "unit_depth": "cm"
            },
            "label": "15-30cm",
            "values": {
              "Q0.05": null,
              "Q0.5": null,
              "Q0.95": null,
              "mean": null,
              "uncertainty": null
            }
          },
          {
            "range": {
              "top_depth": 30,
              "bottom_depth": 60,
              "unit_depth": "cm"
            },
            "label": "30-60cm",
            "values": {
              "Q0.5": null,
              "Q0.05": null,
              "Q0.95": null,
              "mean": null,
              "uncertainty": null
            }
          },
          {
            "range": {
              "top_depth": 60,
              "bottom_depth": 100,
              "unit_depth": "cm"
            },
            "label": "60-100cm",
            "values": {
              "Q0.05": null,
              "Q0.5": null,
              "Q0.95": null,
              "mean": null,
              "uncertainty": null
            }
          },
          {
            "range": {
              "top_depth": 100,
              "bottom_depth": 200,
              "unit_depth": "cm"
            },
            "label": "100-200cm",
            "values": {
              "Q0.5": null,
              "Q0.05": null,
              "Q0.95": null,
              "mean": null,
              "uncertainty": null
            }
          }
        ]
      },
      {
        "name": "ocd",
        "unit_measure": {
          "d_factor": 10,
          "mapped_units": "dg/dm³",
          "target_units": "hg/m³",
          "uncertainty_unit": ""
        },
        "depths": [
          {
            "range": {
              "top_depth": 0,
              "bottom_depth": 5,
              "unit_depth": "cm"
            },
            "label": "0-5cm",
            "values": {
              "Q0.5": null,
              "Q0.05": null,
              "Q0.95": null,
              "mean": null,
              "uncertainty": null
            }
          },
          {
            "range": {
              "top_depth": 5,
              "bottom_depth": 15,
              "unit_depth": "cm"
            },
            "label": "5-15cm",
            "values": {
              "Q0.5": null,
              "Q0.05": null,
              "Q0.95": null,
              "mean": null,
              "uncertainty": null
            }
          },
          {
            "range": {
              "top_depth": 15,
              "bottom_depth": 30,
              "unit_depth": "cm"
            },
            "label": "15-30cm",
            "values": {
              "Q0.05": null,
              "Q0.5": null,
              "Q0.95": null,
              "mean": null,
              "uncertainty": null
            }
          },
          {
            "range": {
              "top_depth": 30,
              "bottom_depth": 60,
              "unit_depth": "cm"
            },
            "label": "30-60cm",
            "values": {
              "Q0.05": null,
              "Q0.5": null,
              "Q0.95": null,
              "mean": null,
              "uncertainty": null
            }
          },
          {
            "range": {
              "top_depth": 60,
              "bottom_depth": 100,
              "unit_depth": "cm"
            },
            "label": "60-100cm",
            "values": {
              "Q0.5": null,
              "Q0.05": null,
              "Q0.95": null,
              "mean": null,
              "uncertainty": null
            }
          },
          {
            "range": {
              "top_depth": 100,
              "bottom_depth": 200,
              "unit_depth": "cm"
            },
            "label": "100-200cm",
            "values": {
              "Q0.05": null,
              "Q0.5": null,
              "Q0.95": null,
              "mean": null,
              "uncertainty": null
            }
          }
        ]
      },
      {
        "name": "ocs",
        "unit_measure": {
          "d_factor": 10,
          "mapped_units": "t/ha",
          "target_units": "kg/m²",
          "uncertainty_unit": ""
        },
        "depths": [
          {
            "range": {
              "top_depth": 0,
              "bottom_depth": 30,
              "unit_depth": "cm"
            },
            "label": "0-30cm",
            "values": {
              "Q0.5": null,
              "Q0.05": null,
              "Q0.95": null,
              "mean": null,
              "uncertainty": null
            }
          }
        ]
      },
      {
        "name": "phh2o",
        "unit_measure": {
          "d_factor": 10,
          "mapped_units": "pH*10",
          "target_units": "-",
          "uncertainty_unit": ""
        },
        "depths": [
          {
            "range": {
              "top_depth": 0,
              "bottom_depth": 5,
              "unit_depth": "cm"
            },
            "label": "0-5cm",
            "values": {
              "Q0.5": null,
              "Q0.05": null,
              "Q0.95": null,
              "mean": null,
              "uncertainty": null
            }
          },
          {
            "range": {
              "top_depth": 5,
              "bottom_depth": 15,
              "unit_depth": "cm"
            },
            "label": "5-15cm",
            "values": {
              "Q0.5": null,
              "Q0.05": null,
              "Q0.95": null,
              "mean": null,
              "uncertainty": null
            }
          },
          {
            "range": {
              "top_depth": 15,
              "bottom_depth": 30,
              "unit_depth": "cm"
            },
            "label": "15-30cm",
            "values": {
              "Q0.5": null,
              "Q0.05": null,
              "Q0.95": null,
              "mean": null,
              "uncertainty": null
            }
          },
          {
            "range": {
              "top_depth": 30,
              "bottom_depth": 60,
              "unit_depth": "cm"
            },
            "label": "30-60cm",
            "values": {
              "Q0.05": null,
              "Q0.5": null,
              "Q0.95": null,
              "mean": null,
              "uncertainty": null
            }
          },
          {
            "range": {
              "top_depth": 60,
              "bottom_depth": 100,
              "unit_depth": "cm"
            },
            "label": "60-100cm",
            "values": {
              "Q0.5": null,
              "Q0.05": null,
              "Q0.95": null,
              "mean": null,
              "uncertainty": null
            }
          },
          {
            "range": {
              "top_depth": 100,
              "bottom_depth": 200,
              "unit_depth": "cm"
            },
            "label": "100-200cm",
            "values": {
              "Q0.05": null,
              "Q0.5": null,
              "Q0.95": null,
              "mean": null,
              "uncertainty": null
            }
          }
        ]
      },
      {
        "name": "sand",
        "unit_measure": {
          "d_factor": 10,
          "mapped_units": "g/kg",
          "target_units": "%",
          "uncertainty_unit": ""
        },
        "depths": [
          {
            "range": {
              "top_depth": 0,
              "bottom_depth": 5,
              "unit_depth": "cm"
            },
            "label": "0-5cm",
            "values": {
              "Q0.5": null,
              "Q0.05": null,
              "Q0.95": null,
              "mean": null,
              "uncertainty": null
            }
          },
          {
            "range": {
              "top_depth": 5,
              "bottom_depth": 15,
              "unit_depth": "cm"
            },
            "label": "5-15cm",
            "values": {
              "Q0.5": null,
              "Q0.05": null,
              "Q0.95": null,
              "mean": null,
              "uncertainty": null
            }
          },
          {
            "range": {
              "top_depth": 15,
              "bottom_depth": 30,
              "unit_depth": "cm"
            },
            "label": "15-30cm",
            "values": {
              "Q0.5": null,
              "Q0.05": null,
              "Q0.95": null,
              "mean": null,
              "uncertainty": null
            }
          },
          {
            "range": {
              "top_depth": 30,
              "bottom_depth": 60,
              "unit_depth": "cm"
            },
            "label": "30-60cm",
            "values": {
              "Q0.5": null,
              "Q0.05": null,
              "Q0.95": null,
              "mean": null,
              "uncertainty": null
            }
          },
          {
            "range": {
              "top_depth": 60,
              "bottom_depth": 100,
              "unit_depth": "cm"
            },
            "label": "60-100cm",
            "values": {
              "Q0.05": null,
              "Q0.5": null,
              "Q0.95": null,
              "mean": null,
              "uncertainty": null
            }
          },
          {
            "range": {
              "top_depth": 100,
              "bottom_depth": 200,
              "unit_depth": "cm"
            },
            "label": "100-200cm",
            "values": {
              "Q0.5": null,
              "Q0.05": null,
              "Q0.95": null,
              "mean": null,
              "uncertainty": null
            }
          }
        ]
      },
      {
        "name": "silt",
        "unit_measure": {
          "d_factor": 10,
          "mapped_units": "g/kg",
          "target_units": "%",
          "uncertainty_unit": ""
        },
        "depths": [
          {
            "range": {
              "top_depth": 0,
              "bottom_depth": 5,
              "unit_depth": "cm"
            },
            "label": "0-5cm",
            "values": {
              "Q0.5": null,
              "Q0.05": null,
              "Q0.95": null,
              "mean": null,
              "uncertainty": null
            }
          },
          {
            "range": {
              "top_depth": 5,
              "bottom_depth": 15,
              "unit_depth": "cm"
            },
            "label": "5-15cm",
            "values": {
              "Q0.05": null,
              "Q0.5": null,
              "Q0.95": null,
              "mean": null,
              "uncertainty": null
            }
          },
          {
            "range": {
              "top_depth": 15,
              "bottom_depth": 30,
              "unit_depth": "cm"
            },
            "label": "15-30cm",
            "values": {
              "Q0.05": null,
              "Q0.5": null,
              "Q0.95": null,
              "mean": null,
              "uncertainty": null
            }
          },
          {
            "range": {
              "top_depth": 30,
              "bottom_depth": 60,
              "unit_depth": "cm"
            },
            "label": "30-60cm",
            "values": {
              "Q0.05": null,
              "Q0.5": null,
              "Q0.95": null,
              "mean": null,
              "uncertainty": null
            }
          },
          {
            "range": {
              "top_depth": 60,
              "bottom_depth": 100,
              "unit_depth": "cm"
            },
            "label": "60-100cm",
            "values": {
              "Q0.05": null,
              "Q0.5": null,
              "Q0.95": null,
              "mean": null,
              "uncertainty": null
            }
          },
          {
            "range": {
              "top_depth": 100,
              "bottom_depth": 200,
              "unit_depth": "cm"
            },
            "label": "100-200cm",
            "values": {
              "Q0.05": null,
              "Q0.5": null,
              "Q0.95": null,
              "mean": null,
              "uncertainty": null
            }
          }
        ]
      },
      {
        "name": "soc",
        "unit_measure": {
          "d_factor": 10,
          "mapped_units": "dg/kg",
          "target_units": "g/kg",
          "uncertainty_unit": ""
        },
        "depths": [
          {
            "range": {
              "top_depth": 0,
              "bottom_depth": 5,
              "unit_depth": "cm"
            },
            "label": "0-5cm",
            "values": {
              "Q0.05": null,
              "Q0.5": null,
              "Q0.95": null,
              "mean": null,
              "uncertainty": null
            }
          },
          {
            "range": {
              "top_depth": 5,
              "bottom_depth": 15,
              "unit_depth": "cm"
            },
            "label": "5-15cm",
            "values": {
              "Q0.05": null,
              "Q0.5": null,
              "Q0.95": null,
              "mean": null,
              "uncertainty": null
            }
          },
          {
            "range": {
              "top_depth": 15,
              "bottom_depth": 30,
              "unit_depth": "cm"
            },
            "label": "15-30cm",
            "values": {
              "Q0.5": null,
              "Q0.05": null,
              "Q0.95": null,
              "mean": null,
              "uncertainty": null
            }
          },
          {
            "range": {
              "top_depth": 30,
              "bottom_depth": 60,
              "unit_depth": "cm"
            },
            "label": "30-60cm",
            "values": {
              "Q0.5": null,
              "Q0.05": null,
              "Q0.95": null,
              "mean": null,
              "uncertainty": null
            }
          },
          {
            "range": {
              "top_depth": 60,
              "bottom_depth": 100,
              "unit_depth": "cm"
            },
            "label": "60-100cm",
            "values": {
              "Q0.5": null,
              "Q0.05": null,
              "Q0.95": null,
              "mean": null,
              "uncertainty": null
            }
          },
          {
            "range": {
              "top_depth": 100,
              "bottom_depth": 200,
              "unit_depth": "cm"
            },
            "label": "100-200cm",
            "values": {
              "Q0.5": null,
              "Q0.05": null,
              "Q0.95": null,
              "mean": null,
              "uncertainty": null
            }
          }
        ]
      },
      {
        "name": "wv0010",
        "unit_measure": {
          "d_factor": 10,
          "mapped_units": "(10-2 cm³/cm³)*10",
          "target_units": "10-2 cm³/cm³",
          "uncertainty_unit": ""
        },
        "depths": [
          {
            "range": {
              "top_depth": 0,
              "bottom_depth": 5,
              "unit_depth": "cm"
            },
            "label": "0-5cm",
            "values": {
              "Q0.05": null,
              "Q0.5": null,
              "Q0.95": null,
              "mean": null,
              "uncertainty": null
            }
          },
          {
            "range": {
              "top_depth": 5,
              "bottom_depth": 15,
              "unit_depth": "cm"
            },
            "label": "5-15cm",
            "values": {
              "Q0.05": null,
              "Q0.5": null,
              "Q0.95": null,
              "mean": null,
              "uncertainty": null
            }
          },
          {
            "range": {
              "top_depth": 15,
              "bottom_depth": 30,
              "unit_depth": "cm"
            },
            "label": "15-30cm",
            "values": {
              "Q0.5": null,
              "Q0.05": null,
              "Q0.95": null,
              "mean": null,
              "uncertainty": null
            }
          },
          {
            "range": {
              "top_depth": 30,
              "bottom_depth": 60,
              "unit_depth": "cm"
            },
            "label": "30-60cm",
            "values": {
              "Q0.5": null,
              "Q0.05": null,
              "Q0.95": null,
              "mean": null,
              "uncertainty": null
            }
          },
          {
            "range": {
              "top_depth": 60,
              "bottom_depth": 100,
              "unit_depth": "cm"
            },
            "label": "60-100cm",
            "values": {
              "Q0.05": null,
              "Q0.5": null,
              "Q0.95": null,
              "mean": null,
              "uncertainty": null
            }
          },
          {
            "range": {
              "top_depth": 100,
              "bottom_depth": 200,
              "unit_depth": "cm"
            },
            "label": "100-200cm",
            "values": {
              "Q0.05": null,
              "Q0.5": null,
              "Q0.95": null,
              "mean": null,
              "uncertainty": null
            }
          }
        ]
      },
      {
        "name": "wv0033",
        "unit_measure": {
          "d_factor": 10,
          "mapped_units": "(10-2 cm³/cm³)*10",
          "target_units": "10-2 cm³/cm³",
          "uncertainty_unit": ""
        },
        "depths": [
          {
            "range": {
              "top_depth": 0,
              "bottom_depth": 5,
              "unit_depth": "cm"
            },
            "label": "0-5cm",
            "values": {
              "Q0.5": null,
              "Q0.05": null,
              "Q0.95": null,
              "mean": null,
              "uncertainty": null
            }
          },
          {
            "range": {
              "top_depth": 5,
              "bottom_depth": 15,
              "unit_depth": "cm"
            },
            "label": "5-15cm",
            "values": {
              "Q0.05": null,
              "Q0.5": null,
              "Q0.95": null,
              "mean": null,
              "uncertainty": null
            }
          },
          {
            "range": {
              "top_depth": 15,
              "bottom_depth": 30,
              "unit_depth": "cm"
            },
            "label": "15-30cm",
            "values": {
              "Q0.5": null,
              "Q0.05": null,
              "Q0.95": null,
              "mean": null,
              "uncertainty": null
            }
          },
          {
            "range": {
              "top_depth": 30,
              "bottom_depth": 60,
              "unit_depth": "cm"
            },
            "label": "30-60cm",
            "values": {
              "Q0.05": null,
              "Q0.5": null,
              "Q0.95": null,
              "mean": null,
              "uncertainty": null
            }
          },
          {
            "range": {
              "top_depth": 60,
              "bottom_depth": 100,
              "unit_depth": "cm"
            },
            "label": "60-100cm",
            "values": {
              "Q0.5": null,
              "Q0.05": null,
              "Q0.95": null,
              "mean": null,
              "uncertainty": null
            }
          },
          {
            "range": {
              "top_depth": 100,
              "bottom_depth": 200,
              "unit_depth": "cm"
            },
            "label": "100-200cm",
            "values": {
              "Q0.05": null,
              "Q0.5": null,
              "Q0.95": null,
              "mean": null,
              "uncertainty": null
            }
          }
        ]
      },
      {
        "name": "wv1500",
        "unit_measure": {
          "d_factor": 10,
          "mapped_units": "(10-2 cm³/cm³)*10",
          "target_units": "10-2 cm³/cm³",
          "uncertainty_unit": ""
        },
        "depths": [
          {
            "range": {
              "top_depth": 0,
              "bottom_depth": 5,
              "unit_depth": "cm"
            },
            "label": "0-5cm",
            "values": {
              "Q0.5": null,
              "Q0.05": null,
              "Q0.95": null,
              "mean": null,
              "uncertainty": null
            }
          },
          {
            "range": {
              "top_depth": 5,
              "bottom_depth": 15,
              "unit_depth": "cm"
            },
            "label": "5-15cm",
            "values": {
              "Q0.5": null,
              "Q0.05": null,
              "Q0.95": null,
              "mean": null,
              "uncertainty": null
            }
          },
          {
            "range": {
              "top_depth": 15,
              "bottom_depth": 30,
              "unit_depth": "cm"
            },
            "label": "15-30cm",
            "values": {
              "Q0.05": null,
              "Q0.5": null,
              "Q0.95": null,
              "mean": null,
              "uncertainty": null
            }
          },
          {
            "range": {
              "top_depth": 30,
              "bottom_depth": 60,
              "unit_depth": "cm"
            },
            "label": "30-60cm",
            "values": {
              "Q0.05": null,
              "Q0.5": null,
              "Q0.95": null,
              "mean": null,
              "uncertainty": null
            }
          },
          {
            "range": {
              "top_depth": 60,
              "bottom_depth": 100,
              "unit_depth": "cm"
            },
            "label": "60-100cm",
            "values": {
              "Q0.05": null,
              "Q0.5": null,
              "Q0.95": null,
              "mean": null,
              "uncertainty": null
            }
          },
          {
            "range": {
              "top_depth": 100,
              "bottom_depth": 200,
              "unit_depth": "cm"
            },
            "label": "100-200cm",
            "values": {
              "Q0.5": null,
              "Q0.05": null,
              "Q0.95": null,
              "mean": null,
              "uncertainty": null
            }
          }
        ]
      }
    ]
  },
  "query_time_s": 15.272417783737183
}
```
</details>
</div>


## Google Earth Engine

The remaining datasets appear to come from Google Earth Engine
- There is a python package available (https://developers.google.com/earth-engine/guides/python_install#hello-world)
  - Maybe it would be useful to explore in-depth? Could inform our design (maybe there are even ways to leverage this package for external datasets?)
  - The MODIS datasets in env-agents (v6.0 products) have been deprecated and are superceded by v6.1 products (included in table below)
- Underlying data is "multi-petabyte"

| env-agents label | Dataset                         | ID               | URL |
|------------------|---------------------------------|------------------|-----|
| SRTM             | NASA SRTM Digital Elevation 30m | USGS/SRTMGL1_003 | https://developers.google.com/earth-engine/datasets/catalog/USGS_SRTMGL1_003 |
|                  | NASADEM: NASA 30m Digital Elevation Model | NASA/NASADEM_HGT/001 | https://developers.google.com/earth-engine/datasets/catalog/NASA_NASADEM_HGT_001 |
| MODIS            | MOD13A1.061 Terra Vegetation Indices 16-Day Global 500m | MODIS/061/MOD13A1 | https://developers.google.com/earth-engine/datasets/catalog/MODIS_061_MOD13A1 |
|                  | MOD13A2.061 Terra Vegetation Indices 16-Day Global 1km  | MODIS/061/MOD13A2 | https://developers.google.com/earth-engine/datasets/catalog/MODIS_061_MOD13A2 |
|                  | MOD13Q1.061 Terra Vegetation Indices 16-Day Global 250m | MODIS/061/MOD13Q1 | https://developers.google.com/earth-engine/datasets/catalog/MODIS_061_MOD13Q1 |
|                  | MOD17A2H.061: Terra Gross Primary Productivity 8-Day Global 500m | MODIS/061/MOD17A2H | https://developers.google.com/earth-engine/datasets/catalog/MODIS_061_MOD17A2H |
|                  | MOD17A3HGF.061: Terra Net Primary Production Gap-Filled Yearly Global 500m | MODIS/061/MOD17A3HGF | https://developers.google.com/earth-engine/datasets/catalog/MODIS_061_MOD17A3HGF |
| WORLDCLIM_BIO    | WorldClim BIO Variables V1 | WORLDCLIM/V1/BIO | https://developers.google.com/earth-engine/datasets/catalog/WORLDCLIM_V1_BIO |
| TERRACLIMATE     | TerraClimate: Monthly Climate and Climatic Water Balance for Global Terrestrial Surfaces, University of Idaho | IDAHO_EPSCOR/TERRACLIMATE | https://developers.google.com/earth-engine/datasets/catalog/IDAHO_EPSCOR_TERRACLIMATE |
| GPM              | GSMaP Operational: Global Satellite Mapping of Precipitation - V6 | JAXA/GPM_L3/GSMaP/v6/operational | https://developers.google.com/earth-engine/datasets/catalog/JAXA_GPM_L3_GSMaP_v6_operational |
|                  | GSMaP Reanalysis: Global Satellite Mapping of Precipitation | JAXA/GPM_L3/GSMaP/v6/reanalysis | https://developers.google.com/earth-engine/datasets/catalog/JAXA_GPM_L3_GSMaP_v6_reanalysis |
|                  | GSMaP Operational: Global Satellite Mapping of Precipitation - V7 | JAXA/GPM_L3/GSMaP/v7/operational | https://developers.google.com/earth-engine/datasets/catalog/JAXA_GPM_L3_GSMaP_v7_operational |
|                  | GSMaP Operational: Global Satellite Mapping of Precipitation - V8 | JAXA/GPM_L3/GSMaP/v8/operational | https://developers.google.com/earth-engine/datasets/catalog/JAXA_GPM_L3_GSMaP_v8_operational |
