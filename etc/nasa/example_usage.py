#!/usr/bin/env python3
"""
Example usage of NASA POWER parameter data fetched using fetch_parameters.py

This script demonstrates how to work with the parameter metadata JSON files
created by the fetch_parameters.py script.
"""

import json
from pathlib import Path
from typing import Any


def load_parameters(json_file: Path) -> dict[str, Any]:
    """Load parameter data from JSON file."""
    with open(json_file) as f:
        return json.load(f)


def find_parameters_by_type(
    data: dict[str, Any], param_type: str
) -> list[dict[str, Any]]:
    """Find all parameters of a specific type (e.g., 'METEOROLOGY', 'RADIATION')."""
    results = []

    for community, temporal_data in data["parameters"].items():
        for temporal, params in temporal_data.items():
            for _param_code, param_info in params.items():
                if param_info["type"] == param_type:
                    results.append(
                        {**param_info, "community": community, "temporal": temporal}
                    )

    return results


def find_temperature_parameters(data: dict[str, Any]) -> list[dict[str, Any]]:
    """Find all temperature-related parameters."""
    results = []

    for community, temporal_data in data["parameters"].items():
        for temporal, params in temporal_data.items():
            for _param_code, param_info in params.items():
                name_lower = param_info["name"].lower()
                if "temperature" in name_lower or "temp" in name_lower:
                    results.append(
                        {**param_info, "community": community, "temporal": temporal}
                    )

    return results


def find_parameters_by_units(data: dict[str, Any], units: str) -> list[dict[str, Any]]:
    """Find parameters with specific units (e.g., 'C', 'mm/day', 'm/s')."""
    results = []

    for community, temporal_data in data["parameters"].items():
        for temporal, params in temporal_data.items():
            for _param_code, param_info in params.items():
                if param_info["units"] == units:
                    results.append(
                        {**param_info, "community": community, "temporal": temporal}
                    )

    return results


def get_parameter_list_for_query(
    data: dict[str, Any], community: str, temporal: str, param_types: list[str] = None
) -> list[str]:
    """
    Get a list of parameter abbreviations suitable for NASA POWER API queries.

    Args:
        data: Parameter data loaded from JSON
        community: Community code (AG, RE, SB)
        temporal: Temporal frequency (daily, monthly, etc.)
        param_types: Optional list of parameter types to filter by

    Returns:
        List of parameter abbreviations
    """
    if community not in data["parameters"]:
        return []

    if temporal not in data["parameters"][community]:
        return []

    params = data["parameters"][community][temporal]

    if param_types:
        # Filter by parameter types
        return [
            param_code
            for param_code, param_info in params.items()
            if param_info["type"] in param_types
        ]
    else:
        return list(params.keys())


def main():
    """Example usage of the parameter data."""

    # Load parameter data (assuming you've run fetch_parameters.py)
    json_files = ["ag_daily_sample.json", "all_daily_parameters.json"]

    script_dir = Path(__file__).parent

    for json_file in json_files:
        file_path = script_dir / json_file
        if not file_path.exists():
            print(f"File not found: {file_path}")
            continue

        print(f"\n=== Analyzing {json_file} ===")

        # Load the data
        data = load_parameters(file_path)

        # Show basic info
        print(f"Source: {data['metadata']['source']}")
        print(f"Communities: {', '.join(data['metadata']['fetched_communities'])}")
        print(
            f"Temporal frequencies: "
            f"{', '.join(data['metadata']['fetched_temporal_frequencies'])}"
        )

        if "summary" in data:
            print(
                f"Total unique parameters: {data['summary']['total_unique_parameters']}"
            )

        # Find all meteorology parameters
        meteor_params = find_parameters_by_type(data, "METEOROLOGY")
        print(f"\nMETEOROLOGY parameters: {len(meteor_params)}")
        for param in meteor_params[:5]:  # Show first 5
            print(f"  {param['abbreviation']}: {param['name']} ({param['units']})")
        if len(meteor_params) > 5:
            print(f"  ... and {len(meteor_params) - 5} more")

        # Find temperature parameters
        temp_params = find_temperature_parameters(data)
        print(f"\nTemperature parameters: {len(temp_params)}")
        for param in temp_params[:3]:  # Show first 3
            print(f"  {param['abbreviation']}: {param['name']}")

        # Find parameters with specific units
        celsius_params = find_parameters_by_units(data, "C")
        print(f"\nParameters in Celsius: {len(celsius_params)}")

        # Generate parameter list for API query
        if "AG" in data["parameters"] and "daily" in data["parameters"]["AG"]:
            meteor_codes = get_parameter_list_for_query(
                data, "AG", "daily", ["METEOROLOGY"]
            )
            print("\nAG daily meteorology parameters for API query:")
            print(f"parameters={','.join(meteor_codes[:10])}")  # Show first 10
            if len(meteor_codes) > 10:
                print(f"... and {len(meteor_codes) - 10} more")


if __name__ == "__main__":
    main()
