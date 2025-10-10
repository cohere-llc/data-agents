#!/usr/bin/env python
"""
Example script demonstrating the OpenAQ adapter functionality.
This script shows how to use the custom OpenAQ adapter to query air quality data.
"""

import os
import sys
from pathlib import Path

# Add the src directory to the Python path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from data_agents.adapters.openaq_adapter import OpenAQAdapter


def main():
    # Configuration for the OpenAQ adapter
    config = {
        "api_key": os.getenv("OPENAQ_API_KEY"),
        "base_url": "https://api.openaq.org/v3",
    }

    if not config["api_key"]:
        print(
            "Warning: OPENAQ_API_KEY environment variable not set. "
            "Some queries may fail."
        )

    # Create the adapter
    adapter = OpenAQAdapter(config)

    print("OpenAQ Adapter Example")
    print("=====================")

    # Example 1: Query measurements by geographic region (bounding box)
    print("\n1. Querying measurements in New York City area...")

    try:
        result = adapter.query_measurements_by_region(
            bbox=[40.6, -74.2, 40.9, -73.7],  # [south, west, north, east]
            parameters="pm25",
            limit=10,
        )
        print(f"Found {len(result)} measurements")
        if not result.empty:
            print(result[["location", "parameter", "value", "unit", "date"]].head())
    except Exception as e:
        print(f"Error querying by region: {e}")

    # Example 2: Query measurements by center point and radius
    print("\n2. Querying measurements around Los Angeles...")

    try:
        result = adapter.query_measurements_by_region(
            center={"lat": 34.0522, "lon": -118.2437},
            radius=50,  # km
            parameters="no2",
            limit=10,
        )
        print(f"Found {len(result)} measurements")
        if not result.empty:
            print(result[["location", "parameter", "value", "unit", "date"]].head())
    except Exception as e:
        print(f"Error querying by center/radius: {e}")

    # Example 3: Query measurements by parameter
    print("\n3. Querying PM2.5 measurements...")

    try:
        result = adapter.query_measurements_by_parameter(parameter="pm25", limit=20)
        print(f"Found {len(result)} measurements")
        if not result.empty:
            print(result[["location", "parameter", "value", "unit", "date"]].head())
    except Exception as e:
        print(f"Error querying by parameter: {e}")

    # Example 4: Query available locations
    print("\n4. Querying available locations...")
    try:
        # Use the discover method instead of private method
        discovery = adapter.discover()
        print("Adapter discovery complete. Available methods:")
        for key in discovery.keys():
            print(f"  - {key}")
    except Exception as e:
        print(f"Error during discovery: {e}")


if __name__ == "__main__":
    main()
