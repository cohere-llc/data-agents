"""
GBIF Occurrence API Adapter

A specialized adapter for the GBIF Occurrence API that provides access to
biodiversity occurrence data from the Global Biodiversity Information Facility.
"""

from typing import Any, Optional
from urllib.parse import urljoin

import pandas as pd
import requests

from ..core.adapter import Adapter


class GBIFOccurrenceAdapter(Adapter):
    """
    GBIF Occurrence API Adapter

    This adapter provides access to the GBIF Occurrence Search API, allowing
    users to search for biodiversity occurrence records using various filters
    such as scientific names, geographic coordinates, dates, and taxonomic keys.
    """

    def __init__(self, config: Optional[dict[str, Any]] = None):
        """
        Initialize GBIF Occurrence adapter.

        Args:
            config: Configuration dictionary that may contain 'base_url'
        """
        super().__init__(config)
        self.base_url = (config or {}).get("base_url", "https://api.gbif.org/v1")
        self.session = requests.Session()
        self.session.headers.update({
            "Accept": "application/json",
            "User-Agent": "data-agents/1.0",
        })

    def discover(self) -> dict[str, Any]:
        """
        Discover the GBIF Occurrence Search API capabilities.

        Returns:
            Discovery information with available search parameters for the
            occurrence/search endpoint
        """
        # Based on the GBIF API documentation from the JSON file
        parameters = {
            # Common search parameters
            "q": {
                "type": "string",
                "description": "Simple full-text search parameter. The value can be a simple word or a phrase.",
                "example": "Puma concolor"
            },
            "scientificName": {
                "type": "array",
                "description": "A scientific name from the GBIF backbone. All included and synonym taxa are included in the search.",
                "example": "Quercus robur"
            },
            "taxonKey": {
                "type": "array", 
                "description": "A taxon key from the GBIF backbone. All included (child) and synonym taxa are included in the search.",
                "example": 2476674
            },
            "kingdomKey": {
                "type": "array",
                "description": "Kingdom classification key.",
                "example": 1
            },
            "phylumKey": {
                "type": "array", 
                "description": "Phylum classification key.",
                "example": 54
            },
            "classKey": {
                "type": "array",
                "description": "Class classification key.", 
                "example": 216
            },
            "orderKey": {
                "type": "array",
                "description": "Order classification key.",
                "example": 797
            },
            "familyKey": {
                "type": "array",
                "description": "Family classification key.",
                "example": 6950
            },
            "genusKey": {
                "type": "array",
                "description": "Genus classification key.",
                "example": 1977775
            },
            "speciesKey": {
                "type": "array",
                "description": "Species classification key.",
                "example": 5148248
            },
            
            # Geographic parameters
            "country": {
                "type": "array",
                "description": "The 2-letter country code (as per ISO-3166-1) of the country in which the occurrence was recorded.",
                "example": "US"
            },
            "continent": {
                "type": "array",
                "description": "Continent, as defined in GBIF Continent vocabulary.",
                "example": "NORTH_AMERICA"
            },
            "decimalLatitude": {
                "type": "object",
                "description": "Latitude in decimal degrees between -90° and 90° based on WGS 84. Supports range queries.",
                "example": "40.5,45"
            },
            "decimalLongitude": {
                "type": "object", 
                "description": "Longitude in decimals between -180 and 180 based on WGS 84. Supports range queries.",
                "example": "-120,-95.5"
            },
            "geometry": {
                "type": "array",
                "description": "Searches for occurrences inside a polygon described in Well Known Text (WKT) format.",
                "example": "POLYGON ((30.1 10.1, 40 40, 20 40, 10 20, 30.1 10.1))"
            },
            "geoDistance": {
                "type": "string",
                "description": "Filters to match occurrence records within a specified distance of a coordinate.",
                "example": "90,100,5km"
            },
            "hasCoordinate": {
                "type": "boolean",
                "description": "Limits searches to occurrence records which contain coordinate values.",
                "example": True
            },
            "hasGeospatialIssue": {
                "type": "boolean",
                "description": "Includes/excludes occurrence records which contain spatial issues.",
                "example": False
            },
            
            # Temporal parameters
            "year": {
                "type": "array",
                "description": "The 4 digit year. Supports range queries.",
                "example": 2020
            },
            "month": {
                "type": "array", 
                "description": "The month of the year, starting with 1 for January. Supports range queries.",
                "example": 5
            },
            "day": {
                "type": "array",
                "description": "The day of the month, a number between 1 and 31. Supports range queries.",
                "example": 15
            },
            "eventDate": {
                "type": "array",
                "description": "Occurrence date in ISO 8601 format: yyyy, yyyy-MM or yyyy-MM-dd. Supports range queries.",
                "example": "2020-01-01,2020-12-31"
            },
            
            # Dataset and organization parameters
            "datasetKey": {
                "type": "array",
                "description": "The occurrence dataset key (a UUID).",
                "example": "13b70480-bd69-11dd-b15f-b8a03c50a862"
            },
            "publishingOrg": {
                "type": "array",
                "description": "The publishing organization's GBIF key (a UUID).",
                "example": "e2e717bf-551a-4917-bdc9-4fa0f342c530"
            },
            "publishingCountry": {
                "type": "array",
                "description": "The 2-letter country code of the owning organization's country.",
                "example": "US"
            },
            "institutionCode": {
                "type": "array",
                "description": "An identifier of any form assigned by the source to identify the institution.",
                "example": "GBIF"
            },
            "collectionCode": {
                "type": "array",
                "description": "An identifier of any form assigned by the source to identify the collection.",
                "example": "Specimens"
            },
            
            # Record quality parameters  
            "basisOfRecord": {
                "type": "array",
                "description": "Basis of record, as defined in GBIF BasisOfRecord vocabulary.",
                "example": "PRESERVED_SPECIMEN"
            },
            "issue": {
                "type": "array",
                "description": "A specific interpretation issue as defined in GBIF OccurrenceIssue enumeration.",
                "example": "COUNTRY_COORDINATE_MISMATCH"
            },
            "license": {
                "type": "array",
                "description": "The licence applied to the dataset or record by the publisher.",
                "example": "CC0_1_0"
            },
            
            # Pagination and formatting
            "limit": {
                "type": "integer",
                "description": "Controls the number of results in the page. Maximum is 300.",
                "example": 20
            },
            "offset": {
                "type": "integer", 
                "description": "Determines the offset for the search results. Maximum offset is 100,000.",
                "example": 0
            },
            
            # Faceting
            "facet": {
                "type": "string",
                "description": "A facet name used to retrieve the most frequent values for a field.",
                "example": "basisOfRecord"
            },
            "facetMincount": {
                "type": "integer",
                "description": "Used with facet parameter to exclude facets with a count less than specified.",
                "example": 1
            },
            "facetMultiselect": {
                "type": "boolean",
                "description": "Used with facet parameter to return counts for values not currently filtered.",
                "example": True
            },
            "facetLimit": {
                "type": "integer",
                "description": "Facet parameters allow paging requests using facetOffset and facetLimit.",
                "example": 10
            },
            "facetOffset": {
                "type": "integer",
                "description": "Facet parameters allow paging requests using facetOffset and facetLimit.",
                "example": 0
            }
        }

        return {
            "adapter_type": "gbif_occurrence",
            "base_url": self.base_url,
            "endpoint": "occurrence/search",
            "description": "GBIF Occurrence Search API - Search for biodiversity occurrence records",
            "total_parameters": len(parameters),
            "parameters": parameters,
            "response_format": {
                "type": "object",
                "description": "Paginated search results with occurrence records",
                "fields": {
                    "offset": "Starting offset of results",
                    "limit": "Number of results per page", 
                    "endOfRecords": "Whether this is the last page",
                    "count": "Total number of matching records",
                    "results": "Array of occurrence records"
                }
            },
            "supported_operations": [
                "Search occurrence records by scientific name",
                "Filter by geographic location (country, coordinates, geometry)",
                "Filter by temporal criteria (year, month, date ranges)",
                "Filter by taxonomic hierarchy (kingdom to species)",
                "Filter by dataset and institutional criteria",
                "Filter by record quality and basis of record",
                "Faceted search for data exploration"
            ]
        }

    def query(self, query: str = "", **kwargs: Any) -> pd.DataFrame:
        """
        Query GBIF Occurrence Search API.

        Args:
            query: Optional simple search query (mapped to 'q' parameter)
            **kwargs: Search parameters including:
                - q: Full-text search query
                - scientificName: Scientific name(s) to search for
                - taxonKey: Taxonomic key(s)
                - country: Country code(s)
                - year: Year(s) or year range
                - limit: Number of results to return (default: 20, max: 300)
                - offset: Offset for pagination (default: 0)
                - hasCoordinate: Filter for records with/without coordinates
                - basisOfRecord: Basis of record type(s)
                - And many other parameters from the discover() method

        Returns:
            pandas.DataFrame with occurrence records

        Raises:
            requests.RequestException: If API request fails
            ValueError: If parameters are invalid
        """
        # Build the URL
        url = urljoin(self.base_url + "/", "occurrence/search")
        
        # Prepare query parameters
        params = {}
        
        # Add the main query if provided
        if query:
            params["q"] = query
            
        # Add all other parameters
        for key, value in kwargs.items():
            if value is not None:
                # Handle array/list parameters that can be repeated
                if isinstance(value, (list, tuple)):
                    # For array parameters, add each value separately
                    for item in value:
                        if key not in params:
                            params[key] = []
                        if not isinstance(params[key], list):
                            params[key] = [params[key]]
                        params[key].append(str(item))
                else:
                    params[key] = str(value)
        
        # Set default limit if not specified
        if "limit" not in params:
            params["limit"] = "20"
            
        try:
            # Make API request
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            # Parse response
            data = response.json()
            
            # Convert to DataFrame
            return self._parse_gbif_response(data)
            
        except requests.RequestException as e:
            raise requests.RequestException(
                f"GBIF Occurrence API request failed: {e}"
            ) from e

    def _parse_gbif_response(self, data: dict[str, Any]) -> pd.DataFrame:
        """
        Parse GBIF Occurrence API response into a pandas DataFrame.

        Args:
            data: Raw API response data

        Returns:
            pandas.DataFrame with parsed occurrence data
        """
        if "results" not in data:
            # Return empty DataFrame with standard columns
            return pd.DataFrame(columns=[
                "gbifID", "scientificName", "taxonKey", "kingdom", "phylum", 
                "class", "order", "family", "genus", "species",
                "country", "countryCode", "decimalLatitude", "decimalLongitude",
                "year", "month", "day", "eventDate", "basisOfRecord",
                "datasetKey", "publishingOrgKey", "institutionCode", "collectionCode"
            ])
        
        results = data["results"]
        records = []
        
        # Extract key fields from each occurrence record (if any)
        for occurrence in results:
            record = {
                # Core identifiers
                "gbifID": occurrence.get("key"),
                "occurrenceID": occurrence.get("occurrenceID"),
                "catalogNumber": occurrence.get("catalogNumber"),
                
                # Taxonomic information
                "scientificName": occurrence.get("scientificName"),
                "acceptedScientificName": occurrence.get("acceptedScientificName"),
                "taxonKey": occurrence.get("taxonKey"),
                "acceptedTaxonKey": occurrence.get("acceptedTaxonKey"),
                "kingdom": occurrence.get("kingdom"),
                "kingdomKey": occurrence.get("kingdomKey"),
                "phylum": occurrence.get("phylum"),
                "phylumKey": occurrence.get("phylumKey"),
                "class": occurrence.get("class"),
                "classKey": occurrence.get("classKey"),
                "order": occurrence.get("order"),
                "orderKey": occurrence.get("orderKey"),
                "family": occurrence.get("family"),
                "familyKey": occurrence.get("familyKey"),
                "genus": occurrence.get("genus"),
                "genusKey": occurrence.get("genusKey"),
                "species": occurrence.get("species"),
                "speciesKey": occurrence.get("speciesKey"),
                "taxonRank": occurrence.get("taxonRank"),
                "taxonomicStatus": occurrence.get("taxonomicStatus"),
                
                # Geographic information
                "country": occurrence.get("country"),
                "countryCode": occurrence.get("countryCode"),
                "continent": occurrence.get("continent"),
                "stateProvince": occurrence.get("stateProvince"),
                "locality": occurrence.get("locality"),
                "decimalLatitude": occurrence.get("decimalLatitude"),
                "decimalLongitude": occurrence.get("decimalLongitude"),
                "coordinateUncertaintyInMeters": occurrence.get("coordinateUncertaintyInMeters"),
                "elevation": occurrence.get("elevation"),
                "depth": occurrence.get("depth"),
                
                # Temporal information
                "year": occurrence.get("year"),
                "month": occurrence.get("month"),
                "day": occurrence.get("day"),
                "eventDate": occurrence.get("eventDate"),
                
                # Dataset and institutional information
                "datasetKey": occurrence.get("datasetKey"),
                "datasetName": occurrence.get("datasetName"),
                "publishingOrgKey": occurrence.get("publishingOrgKey"),
                "publishingCountry": occurrence.get("publishingCountry"),
                "institutionCode": occurrence.get("institutionCode"),
                "institutionKey": occurrence.get("institutionKey"),
                "collectionCode": occurrence.get("collectionCode"),
                "collectionKey": occurrence.get("collectionKey"),
                
                # Record metadata
                "basisOfRecord": occurrence.get("basisOfRecord"),
                "occurrenceStatus": occurrence.get("occurrenceStatus"),
                "individualCount": occurrence.get("individualCount"),
                "license": occurrence.get("license"),
                "recordedBy": occurrence.get("recordedBy"),
                "identifiedBy": occurrence.get("identifiedBy"),
                "lastInterpreted": occurrence.get("lastInterpreted"),
                "issues": occurrence.get("issues"),
                
                # Additional fields
                "sex": occurrence.get("sex"),
                "lifeStage": occurrence.get("lifeStage"),
                "preparations": occurrence.get("preparations"),
                "typeStatus": occurrence.get("typeStatus"),
                "establishmentMeans": occurrence.get("establishmentMeans"),
                "isSequenced": occurrence.get("isSequenced"),
                "protocol": occurrence.get("protocol"),
            }
            records.append(record)
        
        df = pd.DataFrame(records)
        
        # Add metadata as attributes
        if hasattr(df, "attrs"):
            df.attrs["gbif_metadata"] = {
                "offset": data.get("offset", 0),
                "limit": data.get("limit", 20),
                "endOfRecords": data.get("endOfRecords", True),
                "count": data.get("count", len(records)),
                "facets": data.get("facets", {}),
            }
        
        return df

    def count(self, **kwargs: Any) -> int:
        """
        Get the count of matching occurrence records without retrieving the data.

        Args:
            **kwargs: Same search parameters as query() method

        Returns:
            Total number of matching records

        Raises:
            requests.RequestException: If API request fails
        """
        # Use limit=0 to get just the count
        kwargs_copy = kwargs.copy()
        kwargs_copy["limit"] = 0
        
        result_df = self.query("", **kwargs_copy)
        
        # Get count from metadata if available, otherwise return 0
        if hasattr(result_df, "attrs") and "gbif_metadata" in result_df.attrs:
            return result_df.attrs["gbif_metadata"]["count"]
        return 0

    def search_by_scientific_name(self, scientific_name: str, **kwargs: Any) -> pd.DataFrame:
        """
        Convenience method to search by scientific name.

        Args:
            scientific_name: Scientific name to search for
            **kwargs: Additional search parameters

        Returns:
            pandas.DataFrame with occurrence records
        """
        return self.query(scientificName=scientific_name, **kwargs)

    def search_by_location(self, country: Optional[str] = None, 
                          lat_min: Optional[float] = None, lat_max: Optional[float] = None,
                          lon_min: Optional[float] = None, lon_max: Optional[float] = None,
                          **kwargs: Any) -> pd.DataFrame:
        """
        Convenience method to search by geographic location.

        Args:
            country: 2-letter ISO country code
            lat_min: Minimum latitude
            lat_max: Maximum latitude  
            lon_min: Minimum longitude
            lon_max: Maximum longitude
            **kwargs: Additional search parameters

        Returns:
            pandas.DataFrame with occurrence records
        """
        if country:
            kwargs["country"] = country
            
        if lat_min is not None and lat_max is not None:
            kwargs["decimalLatitude"] = f"{lat_min},{lat_max}"
            
        if lon_min is not None and lon_max is not None:
            kwargs["decimalLongitude"] = f"{lon_min},{lon_max}"
            
        return self.query("", **kwargs)

    def search_by_year_range(self, start_year: int, end_year: int, **kwargs: Any) -> pd.DataFrame:
        """
        Convenience method to search by year range.

        Args:
            start_year: Start year (inclusive)
            end_year: End year (inclusive)
            **kwargs: Additional search parameters

        Returns:
            pandas.DataFrame with occurrence records
        """
        kwargs["year"] = f"{start_year},{end_year}"
        return self.query("", **kwargs)