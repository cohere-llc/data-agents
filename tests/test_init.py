"""Test for __init__ module of data_agents package."""

from data_agents import Authenticate


def test_authenticate():
    """Test the Authenticate function."""
    assert Authenticate() is None
