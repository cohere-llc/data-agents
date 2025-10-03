"""Core functionality for data agents."""

from typing import Any, Optional


class DataAgent:
    """A general-purpose data agent for processing and analyzing data."""

    def __init__(self, name: str, config: Optional[dict[str, Any]] = None):
        """Initialize the data agent.

        Args:
            name: The name of the agent
            config: Optional configuration dictionary
        """
        self.name = name
        self.config = config or {}

    def process(self, data: Any) -> Any:
        """Process input data and return results.

        Args:
            data: Input data to process

        Returns:
            Processed data
        """
        # Placeholder implementation
        print(f"Agent {self.name} processing data: {data}")
        return f"Processed: {data}"

    def get_info(self) -> dict[str, Any]:
        """Get information about the agent.

        Returns:
            Dictionary containing agent information
        """
        return {"name": self.name, "config": self.config, "type": "DataAgent"}
