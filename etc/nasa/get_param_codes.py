#!/usr/bin/env python3
"""
Quick parameter list generator for NASA POWER API queries.

This script extracts just the parameter abbreviations from fetched parameter data
for easy copy-paste into API queries.
"""

import json
import argparse
from pathlib import Path
from typing import List


def get_parameter_codes(json_file: Path, community: str, temporal: str, 
                       param_type: str = None, max_params: int = 20) -> List[str]:
    """Extract parameter codes from JSON file."""
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    if community not in data['parameters']:
        return []
    
    if temporal not in data['parameters'][community]:
        return []
    
    params = data['parameters'][community][temporal]
    
    # Filter by type if specified
    if param_type:
        filtered_params = {
            code: info for code, info in params.items() 
            if info['type'] == param_type
        }
    else:
        filtered_params = params
    
    # Sort by name for consistency
    sorted_params = sorted(filtered_params.items(), key=lambda x: x[1]['name'])
    
    # Return just the codes, limited by max_params
    return [code for code, _ in sorted_params[:max_params]]


def main():
    parser = argparse.ArgumentParser(description="Get parameter codes for NASA POWER API queries")
    parser.add_argument('json_file', type=Path, help='Parameter JSON file')
    parser.add_argument('--community', choices=['AG', 'RE', 'SB'], required=True)
    parser.add_argument('--temporal', choices=['daily', 'monthly', 'climatology', 'hourly'], required=True)
    parser.add_argument('--type', help='Parameter type filter (METEOROLOGY, RADIATION, etc.)')
    parser.add_argument('--max', type=int, default=20, help='Maximum number of parameters')
    parser.add_argument('--format', choices=['comma', 'list'], default='comma', 
                       help='Output format: comma-separated or list')
    
    args = parser.parse_args()
    
    if not args.json_file.exists():
        print(f"Error: File not found: {args.json_file}")
        return 1
    
    codes = get_parameter_codes(args.json_file, args.community, args.temporal, 
                               args.type, args.max)
    
    if not codes:
        print(f"No parameters found for {args.community}/{args.temporal}")
        if args.type:
            print(f"with type {args.type}")
        return 1
    
    # Output in requested format
    if args.format == 'comma':
        print(','.join(codes))
    else:
        for code in codes:
            print(code)
    
    return 0


if __name__ == "__main__":
    exit(main())