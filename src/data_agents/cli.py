"""Command-line interface for data-agents."""

import argparse
import json
import sys
from typing import Optional

from .core import DataAgent


def create_agent(name: str, config_file: Optional[str] = None) -> DataAgent:
    """Create a data agent with optional configuration file.

    Args:
        name: Name for the agent
        config_file: Path to JSON configuration file

    Returns:
        Configured DataAgent instance
    """
    config = {}
    if config_file:
        try:
            with open(config_file) as f:
                config = json.load(f)
        except FileNotFoundError:
            print(f"Warning: Configuration file {config_file} not found")
        except json.JSONDecodeError:
            print(f"Warning: Invalid JSON in configuration file {config_file}")

    return DataAgent(name, config)


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Data Agents CLI - A prototype for general data agents"
    )
    parser.add_argument("--version", action="version", version="%(prog)s 0.1.0")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Create command
    create_parser = subparsers.add_parser("create", help="Create a new data agent")
    create_parser.add_argument("name", help="Name for the agent")
    create_parser.add_argument("--config", help="Path to JSON configuration file")

    # Process command
    process_parser = subparsers.add_parser("process", help="Process data with an agent")
    process_parser.add_argument("name", help="Name for the agent")
    process_parser.add_argument("data", help="Data to process")
    process_parser.add_argument("--config", help="Path to JSON configuration file")

    # Info command
    info_parser = subparsers.add_parser("info", help="Get agent information")
    info_parser.add_argument("name", help="Name for the agent")
    info_parser.add_argument("--config", help="Path to JSON configuration file")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == "create":
        agent = create_agent(args.name, args.config)
        print(f"Created agent: {agent.name}")
        if agent.config:
            print(f"Configuration: {agent.config}")

    elif args.command == "process":
        agent = create_agent(args.name, args.config)
        result = agent.process(args.data)
        print(f"Result: {result}")

    elif args.command == "info":
        agent = create_agent(args.name, args.config)
        info = agent.get_info()
        print(json.dumps(info, indent=2))


if __name__ == "__main__":
    main()
