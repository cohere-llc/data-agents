"""
NASA POWER API Adapter

A specialized adapter for the NASA POWER API that provides a parameter-centric interface.
Each parameter is exposed as a discoverable record type, and queries are made by parameter name
with temporal and community specified as kwargs.
"""

import json
from typing import Dict, Any, Optional, List
import requests
import pandas as pd

from ..core.adapter import Adapter


class NasaPowerAdapter(Adapter):
    """
    NASA POWER API Adapter
    
    This adapter treats each NASA POWER parameter as a discoverable record type.
    Users can query by parameter name and specify temporal frequency and community
    as keyword arguments.
    """
    
    # NASA POWER API endpoints mapped by temporal frequency
    TEMPORAL_ENDPOINTS = {
        'daily': 'api/temporal/daily',
        'monthly': 'api/temporal/monthly', 
        'climatology': 'api/temporal/climatology',
        'hourly': 'api/temporal/hourly'
    }
    
    # Available communities
    COMMUNITIES = ['AG', 'RE', 'SB']
    
    # Available spatial types
    SPATIAL_TYPES = ['point', 'regional']
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize NASA POWER adapter.
        
        Args:
            config: Configuration dictionary that may contain 'base_url'
        """
        super().__init__(config)
        self.base_url = (config or {}).get('base_url', 'https://power.larc.nasa.gov')
        self._parameter_cache: Optional[Dict[str, Any]] = None
        self.session = requests.Session()
    
    def _fetch_all_parameters(self) -> Dict[str, Any]:
        """
        Fetch and cache all available parameters from NASA POWER System Manager API.
        
        Returns:
            Dictionary containing all parameters organized by community and temporal frequency
        """
        if self._parameter_cache is not None:
            return self._parameter_cache
        
        all_parameters = {}
        
        for community in self.COMMUNITIES:
            all_parameters[community] = {}
            
            for temporal in self.TEMPORAL_ENDPOINTS.keys():
                try:
                    url = f"{self.base_url}/api/system/manager/parameters"
                    params = {
                        'community': community,
                        'temporal': temporal
                    }
                    
                    response = self.session.get(url, params=params)
                    response.raise_for_status()
                    
                    param_data = response.json()
                    all_parameters[community][temporal] = param_data
                    
                except requests.RequestException as e:
                    print(f"Warning: Failed to fetch {community}/{temporal} parameters: {e}")
                    all_parameters[community][temporal] = {}
        
        self._parameter_cache = all_parameters
        return all_parameters
    
    def _get_parameter_superset(self) -> Dict[str, Any]:
        """
        Get the superset of all unique parameters across all communities and temporal frequencies.
        
        Returns:
            Dictionary mapping parameter codes to their consolidated information
        """
        all_parameters = self._fetch_all_parameters()
        superset = {}
        
        for community, temporals in all_parameters.items():
            for temporal, params in temporals.items():
                for param_code, param_info in params.items():
                    if param_info is None:
                        continue
                        
                    if param_code not in superset:
                        # First time seeing this parameter - add it
                        superset[param_code] = {
                            'name': param_info.get('name', param_code),
                            'definition': param_info.get('definition', f'Parameter {param_code}'),
                            'units': param_info.get('units', 'dimensionless'),
                            'type': param_info.get('type', ''),
                            'source': param_info.get('source', ''),
                            'calculated': param_info.get('calculated', False),
                            'inputs': param_info.get('inputs'),
                            'available_in': []
                        }
                    
                    # Add availability info for this parameter
                    if param_code in superset:
                        availability = {
                            'community': community,
                            'temporal': temporal
                        }
                        if availability not in superset[param_code]['available_in']:
                            superset[param_code]['available_in'].append(availability)
                            
        return superset
    
    def discover(self) -> Dict[str, Any]:
        """
        Discover all available NASA POWER parameters as record types.
        
        Returns:
            Discovery information with each parameter as a separate record type
        """
        parameter_superset = self._get_parameter_superset()

        # Convert parameters to record types
        record_types = {}

        for param_code, param_info in parameter_superset.items():
            if param_info is None:
                print(f"Warning: param_info is None for {param_code}")
                continue
                
            if not isinstance(param_info, dict):
                print(f"Warning: param_info is not a dict for {param_code}: {type(param_info)}")
                continue
                
            # Handle empty or missing name/definition fields safely
            name = param_info.get('name', param_code) or param_code  # Use param_code as fallback
            definition = param_info.get('definition', f'Parameter {param_code}') or f'Parameter {param_code}'  # Use fallback
            units = param_info.get('units', 'dimensionless') or 'dimensionless'
            
            # Create description safely
            description = f"{name} - {definition[:100]}..."
            if len(definition) <= 100:
                description = f"{name} - {definition}"
            
            record_types[param_code] = {
                'description': description,
                'fields': {
                    'parameter': {
                        'type': 'string',
                        'description': f"Parameter code: {param_code}"
                    },
                    'value': {
                        'type': 'number',
                        'description': f"Parameter value in {units}"
                    },
                    'date': {
                        'type': 'string',
                        'description': 'Date of the measurement'
                    },
                    'latitude': {
                        'type': 'number',
                        'description': 'Latitude coordinate'
                    },
                    'longitude': {
                        'type': 'number',
                        'description': 'Longitude coordinate'
                    }
                },
                'metadata': {
                    'name': name,
                    'definition': definition,
                    'units': units,
                    'type': param_info.get('type', ''),
                    'source': param_info.get('source', ''),
                    'calculated': param_info.get('calculated', False),
                    'inputs': param_info.get('inputs'),
                    'available_in': param_info.get('available_in', [])
                },
                'required_kwargs': [
                    'temporal',  # daily, monthly, climatology, hourly
                    'community',  # AG, RE, SB
                    'spatial_type',  # point, regional
                    'start',  # start date (YYYYMMDD)
                    'end',  # end date (YYYYMMDD)
                    # Spatial parameters depend on spatial_type:
                    # For point: latitude, longitude
                    # For regional: latitude_min, latitude_max, longitude_min, longitude_max
                ],
                'optional_kwargs': [
                    'format',  # output format
                    'units',  # metric or imperial
                    'time_standard',  # UTC or LST
                    'site_elevation',  # site elevation correction
                    'wind_elevation',  # wind elevation correction
                    'wind_surface'  # wind surface type
                ],
                'spatial_parameters': {
                    'point': ['latitude', 'longitude'],
                    'regional': ['latitude_min', 'latitude_max', 'longitude_min', 'longitude_max']
                }
            }

        return {
            'adapter_type': 'nasa_power',
            'base_url': self.base_url,
            'total_parameters': len(record_types),
            'communities': self.COMMUNITIES,
            'temporal_frequencies': list(self.TEMPORAL_ENDPOINTS.keys()),
            'spatial_types': self.SPATIAL_TYPES,
            'record_types': record_types
        }
    
    def _build_query_url(self, temporal: str, spatial_type: str) -> str:
        """
        Build the appropriate API endpoint URL based on temporal and spatial type.
        
        Args:
            temporal: Temporal frequency (daily, monthly, climatology, hourly)
            spatial_type: Spatial type (point, regional)
            
        Returns:
            Complete API endpoint URL
        """
        if temporal not in self.TEMPORAL_ENDPOINTS:
            raise ValueError(f"Invalid temporal frequency: {temporal}. Must be one of {list(self.TEMPORAL_ENDPOINTS.keys())}")
        
        if spatial_type not in self.SPATIAL_TYPES:
            raise ValueError(f"Invalid spatial type: {spatial_type}. Must be one of {self.SPATIAL_TYPES}")
        
        endpoint = self.TEMPORAL_ENDPOINTS[temporal]
        return f"{self.base_url}/{endpoint}/{spatial_type}"
    
    def _validate_kwargs(self, **kwargs: Any) -> None:
        """
        Validate query parameters.
        
        Args:
            **kwargs: Query parameters to validate
            
        Raises:
            ValueError: If required parameters are missing or invalid
        """
        # Base required parameters
        base_required = ['temporal', 'community', 'spatial_type', 'start', 'end']
        
        for param in base_required:
            if param not in kwargs:
                raise ValueError(f"Missing required parameter: {param}")
        
        # Validate specific parameter values
        if kwargs['temporal'] not in self.TEMPORAL_ENDPOINTS:
            raise ValueError(f"Invalid temporal: {kwargs['temporal']}. Must be one of {list(self.TEMPORAL_ENDPOINTS.keys())}")
        
        if kwargs['community'] not in self.COMMUNITIES:
            raise ValueError(f"Invalid community: {kwargs['community']}. Must be one of {self.COMMUNITIES}")
        
        if kwargs['spatial_type'] not in self.SPATIAL_TYPES:
            raise ValueError(f"Invalid spatial_type: {kwargs['spatial_type']}. Must be one of {self.SPATIAL_TYPES}")
        
        # Validate spatial parameters based on spatial_type
        if kwargs['spatial_type'] == 'point':
            # Point queries require latitude and longitude
            if 'latitude' not in kwargs or 'longitude' not in kwargs:
                raise ValueError("Point queries require latitude and longitude parameters")
        elif kwargs['spatial_type'] == 'regional':
            # Regional queries require bounding box coordinates
            required_regional = ['latitude_min', 'latitude_max', 'longitude_min', 'longitude_max']
            missing = [param for param in required_regional if param not in kwargs]
            if missing:
                raise ValueError(f"Regional queries require latitude_min, latitude_max, longitude_min, longitude_max parameters. Missing: {missing}")
    
    def query(self, query: str, **kwargs: Any) -> pd.DataFrame:
        """
        Query NASA POWER API for a specific parameter.
        
        Args:
            query: Parameter name to query (e.g., 'T2M', 'PRECTOTCORR')
            **kwargs: Query parameters including:
                - temporal: Temporal frequency (daily, monthly, climatology, hourly)
                - community: Community (AG, RE, SB)
                - spatial_type: Spatial type (point, regional)
                - start: Start date (YYYYMMDD format)
                - end: End date (YYYYMMDD format)
                
                For point queries:
                - latitude: Latitude coordinate
                - longitude: Longitude coordinate
                
                For regional queries:
                - latitude_min: Minimum latitude
                - latitude_max: Maximum latitude
                - longitude_min: Minimum longitude
                - longitude_max: Maximum longitude
                
                Optional parameters:
                - format: Output format (optional)
                - units: Unit system (optional)
                - time_standard: Time standard (optional)
                - site_elevation: Site elevation (optional)
                - wind_elevation: Wind elevation (optional)
                - wind_surface: Wind surface type (optional)
                
        Returns:
            pandas.DataFrame with query results
            
        Raises:
            ValueError: If required parameters are missing or invalid
            requests.RequestException: If API request fails
        """
        parameter_name = query
        
        # Validate inputs
        self._validate_kwargs(**kwargs)
        
        # Build URL
        url = self._build_query_url(kwargs['temporal'], kwargs['spatial_type'])
        
        # Build query parameters
        query_params: Dict[str, Any] = {
            'parameters': parameter_name,
            'community': kwargs['community'],
            'start': kwargs['start'],
            'end': kwargs['end']
        }
        
        # Add spatial parameters
        if kwargs['spatial_type'] == 'point':
            query_params.update({
                'latitude': kwargs['latitude'],
                'longitude': kwargs['longitude']
            })
        else:  # regional
            query_params.update({
                'latitude-min': kwargs['latitude_min'],
                'latitude-max': kwargs['latitude_max'],
                'longitude-min': kwargs['longitude_min'],
                'longitude-max': kwargs['longitude_max']
            })
        
        # Add optional parameters
        optional_params = {
            'format': 'format',
            'units': 'units', 
            'time_standard': 'time-standard',
            'site_elevation': 'site-elevation',
            'wind_elevation': 'wind-elevation',
            'wind_surface': 'wind-surface'
        }
        
        for kwarg_name, api_param in optional_params.items():
            if kwarg_name in kwargs:
                query_params[api_param] = kwargs[kwarg_name]
        
        # Make API request
        try:
            response = self.session.get(url, params=query_params)
            response.raise_for_status()
            
            # Parse response 
            data = response.json()
            
            # Convert to DataFrame
            return self._parse_nasa_response(data, parameter_name)
            
        except requests.RequestException as e:
            raise requests.RequestException(f"NASA POWER API request failed: {e}")
    
    def _parse_nasa_response(self, data: Dict[str, Any], parameter_name: str) -> pd.DataFrame:
        """
        Parse NASA POWER API response into a pandas DataFrame.
        
        Args:
            data: Raw API response data
            parameter_name: Parameter that was queried
            
        Returns:
            pandas.DataFrame with parsed data
        """
        # NASA POWER returns GeoJSON-like structure
        if 'features' in data:
            features = data['features']
        elif 'properties' in data:
            # Single feature response
            features = [data]
        else:
            # Try to extract from the structure we see in responses
            features = [data]
        
        records = []
        
        for feature in features:
            if 'properties' in feature:
                properties = feature['properties']
                geometry = feature.get('geometry', {})
                
                # Extract coordinates
                coords = geometry.get('coordinates', [None, None])
                longitude = coords[0] if len(coords) > 0 else None
                latitude = coords[1] if len(coords) > 1 else None
                
                # Extract parameter data
                if 'parameter' in properties:
                    param_data = properties['parameter'].get(parameter_name, {})
                    
                    for date_str, value in param_data.items():
                        records.append({
                            'parameter': parameter_name,
                            'date': date_str,
                            'value': value,
                            'latitude': latitude,
                            'longitude': longitude
                        })
                else:
                    # Handle different response structure
                    records.append({
                        'parameter': parameter_name,
                        'value': properties,
                        'latitude': latitude,
                        'longitude': longitude,
                        'date': None
                    })
        
        if not records:
            # Create empty DataFrame with expected columns
            return pd.DataFrame(columns=['parameter', 'date', 'value', 'latitude', 'longitude'])
        
        return pd.DataFrame(records)