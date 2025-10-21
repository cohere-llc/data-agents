"""
OpenStreetMap Overpass API Example

This example demonstrates how to query the Overpass API to retrieve
OpenStreetMap data for a specific geographic area.
"""

import json
from urllib.parse import quote

import requests


def main():
    # Overpass API endpoint
    url = "https://overpass-api.de/api/interpreter"

    # Overpass QL query
    query = """
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
    """

    # Prepare the POST data
    post_data = "data=" + quote(query)

    response = None
    try:
        # Make the POST request
        response = requests.post(
            url,
            data=post_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=90,
        )

        # Check if the request was successful
        response.raise_for_status()

        # Parse JSON response
        result = response.json()

        # Print the response data (equivalent to console.log with pretty formatting)
        print(json.dumps(result, indent=2))

    except requests.exceptions.RequestException as e:
        print(f"Error making request: {e}")
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON response: {e}")
        if response is not None:
            print(f"Raw response: {response.text}")


if __name__ == "__main__":
    main()
