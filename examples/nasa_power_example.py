#!/usr/bin/env python3
"""
Example usage of the NASA POWER Adapter.

This adapter exposes each NASA POWER parameter as a discoverable record type,
allowing users to query specific parameters with appropriate metadata.
"""

from data_agents.adapters.nasa_power_adapter import NasaPowerAdapter


def main():
    """Demonstrate NASA POWER adapter usage."""
    
    # Create the adapter
    adapter = NasaPowerAdapter()
    
    print("=== NASA POWER Adapter Demo ===\n")
    
    # 1. Discover available parameters
    print("1. Discovering parameters...")
    discovery = adapter.discover()
    
    print(f"   Total parameters available: {discovery['total_parameters']}")
    print(f"   Communities: {discovery['communities']}")
    print(f"   Temporal frequencies: {discovery['temporal_frequencies']}")
    print(f"   Spatial types: {discovery['spatial_types']}")
    
    # 2. Show information about some common parameters
    print("\n2. Common parameter information:")
    
    common_params = ['T2M', 'PRECTOTCORR', 'ALLSKY_SFC_SW_DWN', 'WS2M']
    record_types = discovery['record_types']
    
    for param in common_params:
        if param in record_types:
            metadata = record_types[param]['metadata']
            print(f"   {param}: {metadata['name']} ({metadata['units']})")
            print(f"      {metadata['definition'][:100]}...")
            print(f"      Available in: {len(metadata['available_in'])} community/temporal combinations")
    
    # 3. Query a specific parameter (point query)
    print("\n3. Querying temperature data (T2M) for New York City (point query)...")
    
    try:
        result = adapter.query(
            "T2M",                    # Parameter name
            latitude=40.7128,         # NYC latitude
            longitude=-74.0060,       # NYC longitude  
            start="20240101",         # Start date
            end="20240107",           # End date (one week)
            community="AG",           # Agriculture community
            temporal="daily",         # Daily data
            spatial_type="point"      # Point data
        )
        
        print(f"   Query successful!")
        print(f"   Result type: {type(result)}")
        print(f"   Data shape: {result.shape}")
        print(f"   Columns: {list(result.columns)}")
        print(f"   First few rows:")
        print(result.head())
        
    except Exception as e:
        print(f"   Query failed: {e}")
    
    # 4. Query regional data
    print("\n4. Querying temperature data (T2M) for Northeast US region (regional query)...")
    
    try:
        result = adapter.query(
            "T2M",                    # Parameter name
            latitude_min=40.0,        # Southern boundary
            latitude_max=45.0,        # Northern boundary
            longitude_min=-80.0,      # Western boundary  
            longitude_max=-70.0,      # Eastern boundary
            start="20240101",         # Start date
            end="20240102",           # Two days only (regional queries can be large)
            community="AG",           # Agriculture community
            temporal="daily",         # Daily data
            spatial_type="regional"   # Regional data
        )
        
        print(f"   Regional query successful!")
        print(f"   Result type: {type(result)}")
        print(f"   Data shape: {result.shape}")
        print(f"   Columns: {list(result.columns)}")
        if hasattr(result, 'head'):
            print(f"   First few rows:")
            print(result.head())
        
    except Exception as e:
        print(f"   Regional query failed: {e}")
        print("   (This might be expected - not all parameters support regional queries)")
    
    # 5. Show parameter metadata for a specific parameter
    print("\n5. Detailed metadata for T2M parameter:")
    if 'T2M' in record_types:
        t2m = record_types['T2M']
        print(f"   Description: {t2m['description']}")
        print(f"   Required parameters: {t2m['required_kwargs']}")
        print(f"   Optional parameters: {t2m['optional_kwargs']}")
        
        # Show spatial parameter requirements
        if 'spatial_parameters' in t2m:
            print(f"   Spatial parameters by type:")
            for spatial_type, params in t2m['spatial_parameters'].items():
                print(f"     {spatial_type}: {params}")
        
        metadata = t2m['metadata']
        print(f"   Type: {metadata['type']}")
        print(f"   Source: {metadata['source']}")
        print(f"   Calculated: {metadata['calculated']}")
        
        print(f"   Available in {len(metadata['available_in'])} combinations:")
        for avail in metadata['available_in'][:5]:  # Show first 5
            print(f"     - {avail['community']}/{avail['temporal']}")
        if len(metadata['available_in']) > 5:
            print(f"     ... and {len(metadata['available_in']) - 5} more")
    
    print("\n=== Demo Complete ===")


if __name__ == "__main__":
    main()