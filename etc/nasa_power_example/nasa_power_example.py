# This is a draft example file for using NASA POWER DATA via a proposed python package
# based on the Python API of Google Earth Engine (GEE).
#
# The proposed API consists of similar top-level functions as the GEE JavaScript API,
# but is intended to pull data from various sources (REST APIs, databases, local files,
# etc.) instead of just GEE datasets. The data and computation are local, not in the
# GEE cloud.
# Primary references:
# - https://developers.google.com/earth-engine/apidocs/ee-featurecollection
# - https://developers.google.com/earth-engine/guides/joins_spatial
# - https://developers.google.com/earth-engine/guides/feature_collection_reducing
# - https://developers.google.com/earth-engine/apidocs/ee-featurecollection-reducecolumns
#
# The example is based on the NASA POWER example R script included in this folder and is
# intended to demonstrate querying and processing of data from two data sources:
# the NASA POWER REST API and a local CSV file.
import etc.nasa_power_example.datapackage as dp

# some authentication setup for services that require it
dp.Authenticate()

# load CSV data with point data, using column labels to define geometry for each feature
muri = dp.FeatureCollection(
    "path/to/local/muri_coring_locations.csv",
    dp.Geometry.toPoint(["Longitude", "Latitude"], dp.Geometry.Units.DEGREES),
)

# reference the NASA POWER data source
nasa_power = dp.FeatureCollection("NASA_POWER/DAILY")

# examine properties available in the NASA POWER dataset (could do the same for Muri
# Coring collection)
print(
    "All non-system properties in NASA POWER dataset as a dictionary:",
    nasa_power.toDictionary().getInfo(),
)
print(
    "Selected properties in NASA POWER dataset as a dictionary:",
    nasa_power.toDictionary(["*temperature*", "*precip*"]).getInfo(),
)

# define a distance-based spatial filter to use with the join to match points
# within 5 km
spatial_filter = dp.Filter.withinDistance(
    leftField=".geo", rightField=".geo", distance=5000
)

# define a join that saves the best (closest) match
save_best_join = dp.Join.saveBest(matchesKey="bestMeasurement", distanceKey="distance")

# apply the join to link each feature in the Muri Coring collection to NASA POWER
# features within 5 km and within the date range 2024-01-01 to 2024-12-31
joined = (
    save_best_join.apply(muri, nasa_power, spatial_filter)
    .filter(dp.Filter.lt("distance", 5000))
    .filter(dp.Filter.date("2024-01-01", "2024-12-31"))
)


# define the Hargreaves function to compute PET
def calculatePet(feature: dp.Feature) -> dp.Feature:
    """Calculate Potential Evapotranspiration (PET) using the Hargreaves method."""
    tmean: float = feature.get("T2M")  # Average temperature
    tmax: float = feature.get("T2M_MAX")  # Maximum temperature
    tmin: float = feature.get("T2M_MIN")  # Minimum temperature
    ra: float = feature.get("ALLSKY_SFC_SW_DWN")  # Solar radiation

    # Hargreaves equation for PET (mm/day)
    pet: float = 0.0023 * ra * (tmean + 17.8) * ((tmax - tmin) ** 0.5)
    return feature.set({"PET": pet})


# reduce to annual averages (temperatures and radiation) and annual totals
# (precipitation) and calculate PET for each Muri Coring point
mean_annuals = joined.reduceColumns(
    reducer=[
        dp.Reducer.mean().repeat(4),
        dp.Reducer.sum(),
    ],
    selectors=["T2M", "T2M_MAX", "T2M_MIN", "ALLSKY_SFC_SW_DWN", "PRECTOTCORR"],
).map(calculatePet)

# print the results
print("Mean annual values with PET for each Muri Coring point:")
print(mean_annuals.getInfo())

# we could have .toDataframe(), .toXarray(), .toCSV(), etc. methods to
# export the results
