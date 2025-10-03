"""Tests for data_agents package."""

import json
import tempfile
from pathlib import Path

from data_agents.cli import create_agent
from data_agents.core import DataAgent


class TestDataAgent:
    """Test cases for DataAgent class."""

    def test_init_default(self):
        """Test DataAgent initialization with default parameters."""
        agent = DataAgent("test-agent")
        assert agent.name == "test-agent"
        assert agent.config == {}

    def test_init_with_config(self):
        """Test DataAgent initialization with configuration."""
        config = {"setting1": "value1", "setting2": 42}
        agent = DataAgent("test-agent", config)
        assert agent.name == "test-agent"
        assert agent.config == config

    def test_process(self):
        """Test data processing functionality."""
        agent = DataAgent("test-agent")
        result = agent.process("test data")
        assert result == "Processed: test data"

    def test_get_info(self):
        """Test agent information retrieval."""
        config = {"key": "value"}
        agent = DataAgent("test-agent", config)
        info = agent.get_info()

        expected = {"name": "test-agent", "config": config, "type": "DataAgent"}
        assert info == expected


class TestCLI:
    """Test cases for CLI functionality."""

    def test_create_agent_without_config(self):
        """Test creating agent without configuration file."""
        agent = create_agent("test-cli-agent")
        assert agent.name == "test-cli-agent"
        assert agent.config == {}

    def test_create_agent_with_config(self):
        """Test creating agent with configuration file."""
        config_data = {"test_setting": "test_value"}

        # Create temporary config file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(config_data, f)
            config_file = f.name

        try:
            agent = create_agent("test-cli-agent", config_file)
            assert agent.name == "test-cli-agent"
            assert agent.config == config_data
        finally:
            # Clean up
            Path(config_file).unlink()

    def test_create_agent_missing_config(self):
        """Test creating agent with missing configuration file."""
        agent = create_agent("test-cli-agent", "nonexistent.json")
        assert agent.name == "test-cli-agent"
        assert agent.config == {}
