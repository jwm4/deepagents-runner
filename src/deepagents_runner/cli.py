"""CLI entry point for DeepAgents Runner."""

import sys
import argparse
from pathlib import Path

from deepagents_runner.terminal.repl import REPLSession
from deepagents_runner.core.config import ConfigLoader
from deepagents_runner.utils.exceptions import ProviderConfigError


def parse_args():
    """Parse command-line arguments.

    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="DeepAgents Runner - Interactive terminal for SpecKit commands",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Launch with default provider (from env)
  deepagents-runner

  # Use specific provider
  deepagents-runner --provider anthropic

  # Use specific model
  deepagents-runner --model claude-sonnet-4-5

  # Set feature context manually
  deepagents-runner --feature 001-my-feature

Environment Variables:
  ANTHROPIC_API_KEY       Anthropic API key
  OPENAI_API_KEY          OpenAI API key
  RUNNER_DEFAULT_PROVIDER Default provider (anthropic or openai)
  RUNNER_MODEL            Model name to use
  RUNNER_TEMPERATURE      Sampling temperature (0.0-1.0)
  RUNNER_MAX_TOKENS       Maximum tokens to generate
        """
    )

    parser.add_argument(
        "--provider",
        choices=["anthropic", "openai"],
        help="LLM provider to use (default: from RUNNER_DEFAULT_PROVIDER or anthropic)"
    )

    parser.add_argument(
        "--model",
        help="Model name to use (default: provider's default model)"
    )

    parser.add_argument(
        "--feature",
        help="Feature ID and name (e.g., 001-my-feature)"
    )

    parser.add_argument(
        "--workspace",
        type=Path,
        help="Workspace root directory (default: current directory)"
    )

    parser.add_argument(
        "--version",
        action="version",
        version="DeepAgents Runner 1.0.0"
    )

    return parser.parse_args()


def main() -> int:
    """Main entry point for the CLI.

    Returns:
        Exit code (0 for success, non-zero for error)
    """
    try:
        # Parse arguments
        args = parse_args()

        # Load configuration
        try:
            config = ConfigLoader.load_from_args(
                provider=args.provider,
                model=args.model
            )
        except ProviderConfigError as e:
            print(f"Configuration error: {e}", file=sys.stderr)
            print("\nMake sure to set the appropriate API key:", file=sys.stderr)
            print("  export ANTHROPIC_API_KEY=your-key-here", file=sys.stderr)
            print("  export OPENAI_API_KEY=your-key-here", file=sys.stderr)
            return 1

        # Override workspace if specified
        if args.workspace:
            config.workspace_root = args.workspace

        # Start REPL session
        session = REPLSession(config=config, workspace_root=config.workspace_root)
        session.start()

        return 0

    except KeyboardInterrupt:
        print("\nInterrupted by user")
        return 130

    except Exception as e:
        print(f"Fatal error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
