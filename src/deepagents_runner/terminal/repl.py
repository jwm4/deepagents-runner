"""Interactive REPL session."""

import sys
import asyncio
from typing import Optional
from pathlib import Path

from deepagents_runner.terminal.ui import TerminalUI
from deepagents_runner.core.context import ContextDetector
from deepagents_runner.core.state import StateManager
from deepagents_runner.core.commands import CommandExecutor
from deepagents_runner.core.config import RunnerConfig
from deepagents_runner.models import CommandType
from deepagents_runner.models.feature import Feature
from deepagents_runner.models.workflow import WorkflowState


class REPLSession:
    """Interactive Read-Eval-Print Loop session."""

    def __init__(
        self,
        config: RunnerConfig,
        workspace_root: Optional[Path] = None
    ):
        """Initialize REPL session.

        Args:
            config: Runner configuration
            workspace_root: Root directory of workspace
        """
        self.ui = TerminalUI()
        self.config = config
        self.context_detector = ContextDetector(workspace_root or config.workspace_root)
        self.command_executor = CommandExecutor(config)
        self.feature: Optional[Feature] = None
        self.state: Optional[WorkflowState] = None
        self.running = False

    def start(self) -> None:
        """Start the REPL session."""
        self.ui.show_banner()
        self.ui.console.print()

        # Auto-detect feature context
        self.feature = self.context_detector.detect_feature()

        # Load or create workflow state
        if self.feature:
            state_manager = StateManager(self.feature.spec_dir)
            self.state = state_manager.load_state(self.feature.id)

        # Show context
        self.ui.show_feature_context(self.feature)
        self.ui.console.print()

        if self.state:
            self.ui.show_workflow_state(self.state)
            self.ui.console.print()

        # Show help
        self.ui.show_available_commands()
        self.ui.console.print()

        self.ui.print_info("Type a command or 'help' for assistance. Press Ctrl+C to exit.")
        self.ui.console.print()

        # Start main loop
        self.running = True
        try:
            while self.running:
                self._handle_input()
        except KeyboardInterrupt:
            self.ui.console.print("\n")
            self.ui.print_info("Goodbye!")
            sys.exit(0)

    def _handle_input(self) -> None:
        """Handle a single input from the user."""
        try:
            user_input = self.ui.console.input("[bold cyan]>[/bold cyan] ").strip()

            if not user_input:
                return

            # Handle built-in commands
            if user_input.lower() in ('exit', 'quit', 'q'):
                self.running = False
                self.ui.print_info("Goodbye!")
                return

            if user_input.lower() in ('help', '?'):
                self.ui.show_available_commands()
                return

            if user_input.lower() == 'context':
                self.ui.show_feature_context(self.feature)
                if self.state:
                    self.ui.console.print()
                    self.ui.show_workflow_state(self.state)
                return

            if user_input.lower() == 'refresh':
                self.feature = self.context_detector.detect_feature()
                if self.feature:
                    state_manager = StateManager(self.feature.spec_dir)
                    self.state = state_manager.load_state(self.feature.id)
                self.ui.show_feature_context(self.feature)
                return

            # Handle agent commands
            if user_input.lower().startswith('agents '):
                self._handle_agent_command(user_input)
                return

            # Handle SpecKit commands
            if user_input.startswith('/speckit.'):
                self._execute_command(user_input)
                return

            self.ui.print_warning(f"Unknown command: {user_input}")
            self.ui.print_info("Type 'help' for available commands or 'agents list' to see agents.")

        except Exception as e:
            self.ui.print_error(f"Error: {e}")

    def _handle_agent_command(self, command_input: str) -> None:
        """Handle agent-related commands.

        Args:
            command_input: Full command string (e.g., "agents list")
        """
        parts = command_input.split(maxsplit=2)
        if len(parts) < 2:
            self.ui.print_error("Invalid agent command. Use: agents list|show|enable|disable")
            return

        subcommand = parts[1].lower()

        if subcommand == 'list':
            # Show all agents with their capabilities
            agents = self.command_executor.agent_manager.list_agents(include_disabled=True)
            self.ui.show_agent_list(agents)

        elif subcommand == 'show':
            if len(parts) < 3:
                self.ui.print_error("Usage: agents show <agent-name>")
                return

            agent_name = parts[2]
            agent = self.command_executor.agent_manager.get_agent_by_name(agent_name)

            if agent:
                self.ui.show_agent_details(agent)
            else:
                self.ui.print_error(f"Agent not found: {agent_name}")
                self.ui.print_info("Use 'agents list' to see all available agents")

        elif subcommand == 'enable':
            if len(parts) < 3:
                self.ui.print_error("Usage: agents enable <agent-name>")
                return

            agent_name = parts[2]
            if self.command_executor.agent_manager.enable_agent(agent_name):
                self.ui.print_success(f"Enabled agent: {agent_name}")
            else:
                self.ui.print_error(f"Agent not found: {agent_name}")

        elif subcommand == 'disable':
            if len(parts) < 3:
                self.ui.print_error("Usage: agents disable <agent-name>")
                return

            agent_name = parts[2]
            if self.command_executor.agent_manager.disable_agent(agent_name):
                self.ui.print_success(f"Disabled agent: {agent_name}")
            else:
                self.ui.print_error(f"Agent not found: {agent_name}")

        else:
            self.ui.print_error(f"Unknown agent command: {subcommand}")
            self.ui.print_info("Available: agents list|show|enable|disable")

    def _parse_agent_override(self, text: str) -> tuple[Optional[list], str]:
        """Parse --agent or --agents flag from command input.

        Args:
            text: Command input text

        Returns:
            Tuple of (agent_list, remaining_text)
        """
        import re

        # Match --agent agent-name or --agents agent1,agent2
        agent_pattern = r'--agents?\s+([a-z0-9,-]+)'
        match = re.search(agent_pattern, text)

        if not match:
            return None, text

        # Extract agent names
        agent_names_str = match.group(1)
        agent_names = [name.strip() for name in agent_names_str.split(',')]

        # Look up agents
        agents = []
        for name in agent_names:
            agent = self.command_executor.agent_manager.get_agent_by_name(name)
            if agent:
                agents.append(agent)
            else:
                self.ui.print_warning(f"Agent not found: {name}")

        # Remove the flag from text
        remaining_text = re.sub(agent_pattern, '', text).strip()

        return agents if agents else None, remaining_text

    def _execute_command(self, command_input: str) -> None:
        """Execute a SpecKit command.

        Args:
            command_input: Full command string (e.g., "/speckit.specify")
        """
        # Parse command
        parts = command_input.split(maxsplit=1)
        command_name = parts[0].replace('/speckit.', '')
        remaining_input = parts[1] if len(parts) > 1 else None

        # Parse agent override
        agent_override = None
        user_input = remaining_input
        if remaining_input:
            agent_override, user_input = self._parse_agent_override(remaining_input)

        # Map command name to CommandType
        try:
            command_type = CommandType(command_name)
        except ValueError:
            self.ui.print_error(f"Unknown command: {command_name}")
            return

        # Check if we have a feature context
        if not self.feature:
            # For specify command, we can create a new feature
            if command_type == CommandType.SPECIFY:
                if not user_input:
                    user_input = self.ui.prompt("Enter feature description")
                    if not user_input:
                        self.ui.print_error("Feature description is required")
                        return

                # Prompt for feature ID and name
                feature_id = self.ui.prompt("Enter feature ID (e.g., 001)", "001")
                feature_name = self.ui.prompt(
                    "Enter feature name (kebab-case, e.g., my-feature)",
                    "new-feature"
                )

                self.feature = self.context_detector.get_or_create_feature(
                    feature_id, feature_name
                )
                state_manager = StateManager(self.feature.spec_dir)
                self.state = state_manager.load_state(self.feature.id)
            else:
                self.ui.print_error(
                    "No feature context detected. "
                    "Use /speckit.specify to create a new feature."
                )
                return

        # Execute command asynchronously
        self.ui.print_info(f"Executing: {command_input}")

        # Show which agents will be selected for this command
        if agent_override:
            # User explicitly specified agents
            self.ui.print_info(f"Using agent override: {', '.join([a.name for a in agent_override])}")
            selected_agents = agent_override
        else:
            # Automatic selection
            selected_agents = self.command_executor.agent_manager.select_agents_for_command(command_type)

        if selected_agents:
            self.ui.show_selected_agents(selected_agents)

        self.ui.console.print()

        try:
            # Show progress indicator while model is running
            agent_name = selected_agents[0].name if selected_agents else "agent"

            with self.ui.console.status(
                f"[cyan]Running {command_type.value} with {agent_name}...[/cyan]",
                spinner="dots"
            ):
                # Run async command in event loop
                result = asyncio.run(
                    self.command_executor.execute_command(
                        command_type=command_type,
                        feature=self.feature,
                        agent_override=agent_override,
                        state=self.state,
                        user_input=user_input
                    )
                )

            # Show results
            if result.get("success"):
                self.ui.console.print()

                # Show which agent was used
                if "agent_used" in result:
                    agent_name = result["agent_used"]
                    selected_agents = result.get("selected_agents", [])

                    # Check if fallback happened
                    if selected_agents and agent_name not in selected_agents:
                        self.ui.print_warning(
                            f"Primary agents failed, used fallback: {agent_name}"
                        )
                    elif len(selected_agents) == 1:
                        self.ui.print_info(f"Agent used: {agent_name}")
                    elif len(selected_agents) > 1:
                        self.ui.print_info(f"Primary agent: {agent_name}")
                        other_agents = [a for a in selected_agents if a != agent_name]
                        if other_agents:
                            self.ui.console.print(f"  [dim]Available agents: {', '.join(other_agents)}[/dim]")

                self.ui.print_success(f"Command completed: {command_type.value}")

                # Show file paths if created
                if "spec_file" in result:
                    self.ui.print_info(f"Created: {result['spec_file']}")
                if "plan_file" in result:
                    self.ui.print_info(f"Created: {result['plan_file']}")
                if "tasks_file" in result:
                    self.ui.print_info(f"Created: {result['tasks_file']}")
                if "implementation_file" in result:
                    self.ui.print_info(f"Created: {result['implementation_file']}")
                if "analysis_file" in result:
                    self.ui.print_info(f"Created: {result['analysis_file']}")
                if "clarify_file" in result:
                    self.ui.print_info(f"Created: {result['clarify_file']}")
                if "checklist_file" in result:
                    self.ui.print_info(f"Created: {result['checklist_file']}")
                if "constitution_file" in result:
                    self.ui.print_info(f"Created: {result['constitution_file']}")

                # Show full content if available
                if "content" in result and len(result["content"]) > 0:
                    self.ui.console.print()
                    self.ui.console.print("[bold]Generated Content:[/bold]")
                    self.ui.print_markdown(result["content"])

                # Show suggestions if available
                if "suggestions" in result and result["suggestions"]:
                    self.ui.console.print()
                    self.ui.console.print("[bold cyan]💡 Suggested Next Steps:[/bold cyan]")
                    self.ui.print_markdown(result["suggestions"])

                # Refresh state
                if self.feature:
                    state_manager = StateManager(self.feature.spec_dir)
                    self.state = state_manager.load_state(self.feature.id)

                    # Show suggested next command
                    if self.state.suggested_next:
                        self.ui.console.print()
                        self.ui.print_info(
                            f"Suggested next: /{self.state.suggested_next.value}"
                        )
            else:
                self.ui.print_warning(f"Command completed with warnings")
                if "message" in result:
                    self.ui.print_info(result["message"])

        except Exception as e:
            self.ui.console.print()

            # Extract helpful error message
            error_msg = str(e)

            # Check if it's a command execution error with helpful details
            if "Authentication failed" in error_msg:
                self.ui.print_error("Authentication failed")
                self.ui.console.print("\n[yellow]Please set your API key:[/yellow]")
                self.ui.console.print("  export ANTHROPIC_API_KEY=your-key-here")
                self.ui.console.print("  export OPENAI_API_KEY=your-key-here")
            elif "Rate limit exceeded" in error_msg:
                self.ui.print_error("Rate limit exceeded")
                self.ui.console.print("\n[yellow]Please wait a moment and try again.[/yellow]")
            else:
                self.ui.print_error(f"Command failed: {error_msg}")

            # Show full traceback only if verbose debugging
            import os
            if os.getenv("DEBUG"):
                import traceback
                self.ui.console.print("\n[dim]Full traceback:[/dim]")
                self.ui.console.print("[dim]" + traceback.format_exc() + "[/dim]")
