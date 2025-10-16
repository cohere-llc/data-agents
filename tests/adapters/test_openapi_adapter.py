"""Tests for OpenAPI adapter."""

import json
import os
from typing import Any, Hashable
import pytest
from requests import Request, Session
from openapi_core.contrib.requests import RequestsOpenAPIRequest, RequestsOpenAPIResponse

from src.data_agents.adapters.openapi_adapter import OpenAPIAdapter

def test_openapi_adapter_initialization():
    """Test initialization of OpenAPIAdapter."""
    sample_spec: dict[Hashable, Any] = {
        "openapi": "3.0.0",
        "info": {
            "title": "Sample API",
            "version": "1.0.0"
        },
        "paths": {}
    }
    adapter = OpenAPIAdapter(openapi_spec=sample_spec, config={"base_url": "https://api.example.com"})
    assert adapter.openapi_spec.spec["openapi"] == "3.0.0"
    assert adapter.openapi_spec.spec["info"]["title"] == "Sample API"

def test_openapi_adapter_discover():
    """Test the discover method of OpenAPIAdapter."""
    sample_spec: dict[Hashable, Any] = {
        "openapi": "3.0.0",
        "info": {
            "title": "Sample API",
            "version": "1.0.0"
        },
        "paths": {
            "/items": {
                "get": {
                    "summary": "List items",
                    "responses": {
                        "200": {
                            "description": "A list of items"
                        }
                    }
                }
            }
        }
    }
    adapter = OpenAPIAdapter(openapi_spec=sample_spec, config={"base_url": "https://api.example.com"})
    discovery_info = adapter.discover()
    assert "openapi" in discovery_info
    assert discovery_info["openapi"] == "3.0.0"
    assert "/items" in discovery_info["paths"]

def test_openapi_adapter_from_nasa_power_file():
    """Test initialization of OpenAPIAdapter from a local JSON file."""
    test_dir = os.path.dirname(__file__)
    test_file_path = os.path.join(test_dir, "..", "fixtures", "nasa_openapi.json")
    with open(test_file_path, "r") as f:
        spec_from_file = json.load(f)
    adapter = OpenAPIAdapter(openapi_spec=spec_from_file, config={"base_url": "https://power.larc.nasa.gov"})
    assert adapter.openapi_spec.spec["info"]["title"] == "POWER Daily API"
    request = Request(
        'GET',
        url=adapter.base_url + "/api/temporal/daily/point",
        params={
              "community": "ag",
              "longitude": -116.5,
              "latitude": 33.8,
              "start": "20220101",
              "end": "20220111",
              "parameters": ["T2M", "PRECTOT"],
              "format": "json",
        })
    openapi_request = RequestsOpenAPIRequest(request)
    request_result = adapter.openapi_spec.unmarshal_request(openapi_request)
    print("\nUnmarshalled Request:")
    print(request_result)
    session = Session()
    prepped = session.prepare_request(request)
    print("\nPrepared Request URL:")
    print(prepped.url)
    response = session.send(prepped)
    print("\nResponse Content:")
    print(response.content.decode())
    openapi_response = RequestsOpenAPIResponse(response)
    adapter.openapi_spec.validate_response(openapi_request, openapi_response)
    response_result = adapter.openapi_spec.unmarshal_response(openapi_request, openapi_response)
    print("\nUnmarshalled Response:")
    print(response_result)


if __name__ == "__main__":
    pytest.main()