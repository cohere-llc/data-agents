#!/usr/bin/env python3
"""
NASA POWER System Manager API Parameter Fetcher

This script queries the NASA POWER System Manager API to retrieve all available
parameters for each community (AG, RE, SB) and temporal frequency (daily, monthly,
climatology, hourly) combination.

Usage:
    python fetch_parameters.py [--output OUTPUT_FILE] [--community COMMUNITY]
                                [--temporal TEMPORAL]

Examples:
    # Get all parameters for all communities and temporal frequencies
    python fetch_parameters.py

    # Get parameters for specific community and save to file
    python fetch_parameters.py --community AG --temporal daily \
                               --output ag_daily_params.json

    # Get all AG community parameters across all temporal frequencies
    python fetch_parameters.py --community AG
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Optional

import requests


class NASAPowerParameterFetcher:
    """Fetches parameter metadata from NASA POWER System Manager API."""

    BASE_URL = "https://power.larc.nasa.gov"
    COMMUNITIES = ["AG", "RE", "SB"]
    TEMPORAL_FREQUENCIES = ["daily", "monthly", "climatology", "hourly"]

    def __init__(self):
        self.session = requests.Session()

    def fetch_parameters(
        self, community: str, temporal: str
    ) -> Optional[dict[str, Any]]:
        """
        Fetch parameters for a specific community and temporal frequency.

        Args:
            community: Community code (AG, RE, SB)
            temporal: Temporal frequency (daily, monthly, climatology, hourly)

        Returns:
            Dictionary of parameter data or None if request fails
        """
        url = f"{self.BASE_URL}/api/system/manager/parameters"
        params = {"community": community, "temporal": temporal}

        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error fetching {community}/{temporal}: {e}", file=sys.stderr)
            return None

    def fetch_all_parameters(
        self,
        communities: Optional[list[str]] = None,
        temporal_frequencies: Optional[list[str]] = None,
    ) -> dict[str, Any]:
        """
        Fetch parameters for all specified community/temporal combinations.

        Args:
            communities: List of community codes to fetch (default: all)
            temporal_frequencies: List of temporal frequencies to fetch (default: all)

        Returns:
            Nested dictionary with structure: {community: {temporal: {param_data}}}
        """
        if communities is None:
            communities = self.COMMUNITIES
        if temporal_frequencies is None:
            temporal_frequencies = self.TEMPORAL_FREQUENCIES

        results: dict[str, Any] = {}

        for community in communities:
            print(f"Fetching parameters for community: {community}")
            results[community] = {}

            for temporal in temporal_frequencies:
                print(f"  - {temporal} parameters...")
                param_data = self.fetch_parameters(community, temporal)

                if param_data:
                    # Convert to more structured format
                    structured_data = self._structure_parameter_data(param_data)
                    results[community][temporal] = structured_data
                    print(f"    Found {len(structured_data)} parameters")
                else:
                    print(f"    Failed to fetch {temporal} parameters")

        return results

    def _structure_parameter_data(self, raw_data: dict[str, Any]) -> dict[str, Any]:
        """
        Convert raw API response to structured parameter data.

        Args:
            raw_data: Raw response from System Manager API

        Returns:
            Structured parameter dictionary
        """
        structured: dict[str, Any] = {}

        for param_code, param_info in raw_data.items():
            if isinstance(param_info, dict) and "name" in param_info:
                structured[param_code] = {
                    "abbreviation": param_code,
                    "name": param_info["name"],
                    "definition": param_info["definition"],
                    "units": param_info["units"],
                    "type": param_info["type"],
                    "temporal": param_info["temporal"],
                    "source": param_info["source"],
                    "community": param_info["community"],
                    "calculated": param_info.get("calculated", False),
                    "inputs": param_info.get("inputs"),
                }

        return structured

    def generate_summary(self, all_parameters: dict[str, Any]) -> dict[str, Any]:
        """
        Generate summary statistics about the fetched parameters.

        Args:
            all_parameters: Complete parameter data structure

        Returns:
            Summary dictionary with counts and statistics
        """
        summary: dict[str, Any] = {
            "total_communities": len(all_parameters),
            "communities": {},
            "parameter_types": {},
            "temporal_frequencies": {},
            "unique_parameters": set(),
        }

        for community, temporal_data in all_parameters.items():
            community_total = 0
            summary["communities"][community] = {}

            for temporal, params in temporal_data.items():
                param_count = len(params)
                community_total += param_count

                summary["communities"][community][temporal] = param_count
                if temporal not in summary["temporal_frequencies"]:
                    summary["temporal_frequencies"][temporal] = 0
                summary["temporal_frequencies"][temporal] += param_count

                # Collect parameter types and unique parameters
                for param_code, param_info in params.items():
                    param_type = param_info["type"]
                    if param_type not in summary["parameter_types"]:
                        summary["parameter_types"][param_type] = 0
                    summary["parameter_types"][param_type] += 1
                    summary["unique_parameters"].add(param_code)

            summary["communities"][community]["total"] = community_total

        summary["total_unique_parameters"] = len(summary["unique_parameters"])
        summary["unique_parameters"] = sorted(summary["unique_parameters"])

        return summary


def main():
    """Main script entry point."""
    parser = argparse.ArgumentParser(
        description="Fetch NASA POWER API parameter metadata",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    parser.add_argument(
        "--community",
        choices=["AG", "RE", "SB"],
        help="Specific community to fetch (default: all)",
    )

    parser.add_argument(
        "--temporal",
        choices=["daily", "monthly", "climatology", "hourly"],
        help="Specific temporal frequency to fetch (default: all)",
    )

    parser.add_argument(
        "--output", "-o", type=Path, help="Output JSON file path (default: stdout)"
    )

    parser.add_argument(
        "--summary",
        "-s",
        action="store_true",
        help="Include summary statistics in output",
    )

    parser.add_argument(
        "--pretty", action="store_true", help="Pretty-print JSON output"
    )

    args = parser.parse_args()

    # Determine what to fetch
    communities = [args.community] if args.community else None
    temporal_frequencies = [args.temporal] if args.temporal else None

    # Create fetcher and get parameters
    fetcher = NASAPowerParameterFetcher()
    print("Fetching NASA POWER API parameters...")

    all_parameters = fetcher.fetch_all_parameters(communities, temporal_frequencies)

    # Prepare output data
    output_data: dict[str, Any] = {
        "metadata": {
            "source": "NASA POWER System Manager API",
            "base_url": fetcher.BASE_URL,
            "fetched_communities": communities or fetcher.COMMUNITIES,
            "fetched_temporal_frequencies": temporal_frequencies
            or fetcher.TEMPORAL_FREQUENCIES,
        },
        "parameters": all_parameters,
    }

    # Add summary if requested
    if args.summary:
        output_data["summary"] = fetcher.generate_summary(all_parameters)

    # Format JSON output
    json_kwargs: dict[str, Any] = {"indent": 2} if args.pretty else {}
    json_output = json.dumps(output_data, **json_kwargs)

    # Write output
    if args.output:
        args.output.write_text(json_output)
        print(f"Parameters saved to: {args.output}")

        if args.summary:
            summary = output_data["summary"]
            print("\nSummary:")
            print(f"  Total unique parameters: {summary['total_unique_parameters']}")
            print(f"  Communities: {', '.join(summary['communities'].keys())}")
            print(f"  Parameter types: {', '.join(summary['parameter_types'].keys())}")
    else:
        print(json_output)


if __name__ == "__main__":
    main()
