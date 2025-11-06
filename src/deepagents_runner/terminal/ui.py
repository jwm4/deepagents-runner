"""Terminal UI using Rich library."""

from typing import Optional
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.markdown import Markdown
from rich.table import Table

from deepagents_runner.models.feature import Feature
from deepagents_runner.models.workflow import WorkflowState


class TerminalUI:
    """Rich-based terminal user interface."""

    def __init__(self):
        """Initialize terminal UI."""
        self.console = Console()

    def show_banner(self) -> None:
        """Display startup banner."""
        banner = """
# ACP prototype runner using DeepAgents

An interactive runner for SpecKit commands powered by DeepAgents.
        """
        self.console.print(Panel(Markdown(banner.strip()), border_style="blue"))

    def show_feature_context(self, feature: Optional[Feature]) -> None:
        """Display current feature context.

        Args:
            feature: Current feature, or None if not detected
        """
        if feature:
            table = Table(show_header=False, box=None, padding=(0, 2))
            table.add_row("Feature:", f"[bold]{feature.id}-{feature.name}[/bold]")
            table.add_row("Branch:", feature.branch)
            table.add_row("Status:", f"[cyan]{feature.status.value}[/cyan]")

            self.console.print(Panel(table, title="Current Context", border_style="green"))
        else:
            self.console.print(
                Panel(
                    "[yellow]No feature context detected.[/yellow]\n"
                    "Create a new feature with a command to get started.",
                    title="Current Context",
                    border_style="yellow"
                )
            )

    def show_workflow_state(self, state: WorkflowState) -> None:
        """Display workflow state information.

        Args:
            state: Current workflow state
        """
        table = Table(show_header=False, box=None, padding=(0, 2))
        table.add_row("Phase:", f"[cyan]{state.current_phase.value}[/cyan]")
        table.add_row("Commands:", str(len(state.completed_commands)))

        if state.suggested_next:
            table.add_row(
                "Suggested:",
                f"[green]/{state.suggested_next.value}[/green]"
            )

        self.console.print(Panel(table, title="Workflow State", border_style="blue"))

    def show_available_commands(self) -> None:
        """Display list of available SpecKit commands."""
        # SpecKit Commands
        speckit_commands = [
            ("/speckit.specify <desc>", "Create feature specification"),
            ("/speckit.clarify", "Ask clarification questions"),
            ("/speckit.plan", "Generate implementation plan"),
            ("/speckit.tasks", "Generate task breakdown"),
            ("/speckit.implement", "Execute implementation"),
            ("/speckit.analyze", "Analyze cross-artifact consistency"),
            ("/speckit.checklist", "Generate custom checklist"),
            ("/speckit.constitution", "Create or update project constitution"),
        ]

        table = Table(show_header=True, title="SpecKit Commands")
        table.add_column("Command", style="cyan")
        table.add_column("Description")

        for cmd, desc in speckit_commands:
            table.add_row(cmd, desc)

        self.console.print(table)
        self.console.print()

        # Agent Commands
        agent_commands = [
            ("agents list", "Show all available agents"),
            ("agents show <name>", "Show agent details"),
            ("agents enable <name>", "Enable an agent"),
            ("agents disable <name>", "Disable an agent"),
        ]

        agent_table = Table(show_header=True, title="Agent Commands")
        agent_table.add_column("Command", style="green")
        agent_table.add_column("Description")

        for cmd, desc in agent_commands:
            agent_table.add_row(cmd, desc)

        self.console.print(agent_table)
        self.console.print()

        # Built-in Commands
        builtin_commands = [
            ("help, ?", "Show this help message"),
            ("context", "Display current context and state"),
            ("refresh", "Reload feature context"),
            ("exit, quit, q", "Exit the REPL"),
        ]

        builtin_table = Table(show_header=True, title="Built-in Commands")
        builtin_table.add_column("Command", style="yellow")
        builtin_table.add_column("Description")

        for cmd, desc in builtin_commands:
            builtin_table.add_row(cmd, desc)

        self.console.print(builtin_table)

    def print_info(self, message: str) -> None:
        """Print info message.

        Args:
            message: Message to display
        """
        self.console.print(f"[blue]ℹ[/blue] {message}")

    def print_success(self, message: str) -> None:
        """Print success message.

        Args:
            message: Message to display
        """
        self.console.print(f"[green]✓[/green] {message}")

    def print_warning(self, message: str) -> None:
        """Print warning message.

        Args:
            message: Message to display
        """
        self.console.print(f"[yellow]⚠[/yellow] {message}")

    def print_error(self, message: str) -> None:
        """Print error message.

        Args:
            message: Message to display
        """
        self.console.print(f"[red]✗[/red] {message}")

    def print_markdown(self, content: str) -> None:
        """Print formatted markdown content.

        Args:
            content: Markdown content to render
        """
        self.console.print(Markdown(content))

    def create_progress(self, description: str) -> Progress:
        """Create a progress indicator.

        Args:
            description: Progress description

        Returns:
            Progress object
        """
        return Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            console=self.console
        )

    def prompt(self, message: str, default: str = "") -> str:
        """Prompt user for input.

        Args:
            message: Prompt message
            default: Default value

        Returns:
            User input
        """
        if default:
            prompt_text = f"[cyan]{message}[/cyan] [dim]({default})[/dim]: "
        else:
            prompt_text = f"[cyan]{message}[/cyan]: "

        return self.console.input(prompt_text) or default

    def confirm(self, message: str, default: bool = False) -> bool:
        """Ask for yes/no confirmation.

        Args:
            message: Confirmation message
            default: Default value

        Returns:
            True if confirmed, False otherwise
        """
        suffix = " [Y/n]" if default else " [y/N]"
        response = self.console.input(f"[cyan]{message}{suffix}[/cyan]: ").lower().strip()

        if not response:
            return default

        return response in ('y', 'yes')

    def show_selected_agents(self, agents: list) -> None:
        """Display selected agents before execution.

        Args:
            agents: List of AgentDefinition objects
        """
        if not agents:
            self.print_warning("No agents selected")
            return

        if len(agents) == 1:
            agent = agents[0]
            self.print_info(f"Selected: {agent.name} ({agent.specialization or 'general'})")
        else:
            self.print_info(f"Selected {len(agents)} agents:")
            for agent in agents:
                role_desc = agent.specialization or "general"
                self.console.print(f"  • {agent.name} ([cyan]{role_desc}[/cyan])")

    def show_active_agents_table(self, active_agents: dict) -> Table:
        """Create and display active agents table.

        Args:
            active_agents: Dict mapping agent names to status info
                          Example: {'archie-architect': {'status': 'Running', 'task': 'Architecture design'}}

        Returns:
            Rich Table object
        """
        table = Table(title="Active Agents", show_header=True)
        table.add_column("Agent", style="cyan")
        table.add_column("Status")
        table.add_column("Task")

        for agent_name, info in active_agents.items():
            status = info.get('status', 'Unknown')
            task = info.get('task', '')

            # Color code status
            if status == 'Running':
                status_str = f"[yellow]{status}[/yellow]"
            elif status == 'Completed':
                status_str = f"[green]{status}[/green]"
            elif status == 'Failed':
                status_str = f"[red]{status}[/red]"
            else:
                status_str = status

            table.add_row(agent_name, status_str, task)

        self.console.print(table)
        return table

    def show_agent_list(self, agents: list) -> None:
        """Display list of all agents with their capabilities.

        Args:
            agents: List of AgentDefinition objects
        """
        table = Table(title="Available Agents", show_header=True)
        table.add_column("Status", width=6)
        table.add_column("Name", style="cyan")
        table.add_column("Specialization")
        table.add_column("Capabilities")
        table.add_column("Priority", justify="right")

        # Sort by priority (descending)
        sorted_agents = sorted(agents, key=lambda a: a.priority, reverse=True)

        for agent in sorted_agents:
            status = "✓" if agent.enabled else "✗"
            status_color = "green" if agent.enabled else "dim"

            caps = ", ".join(agent.capabilities[:3])  # Show first 3
            if len(agent.capabilities) > 3:
                caps += f" [dim](+{len(agent.capabilities) - 3} more)[/dim]"

            table.add_row(
                f"[{status_color}]{status}[/{status_color}]",
                agent.name,
                agent.specialization or "[dim]general[/dim]",
                caps if caps else "[dim]none[/dim]",
                str(agent.priority)
            )

        self.console.print(table)

    def show_agent_details(self, agent) -> None:
        """Display detailed information about an agent.

        Args:
            agent: AgentDefinition object
        """
        table = Table(show_header=False, box=None, padding=(0, 2))
        table.add_row("Name:", f"[bold]{agent.name}[/bold]")
        table.add_row("Role:", agent.role)
        table.add_row("Specialization:", agent.specialization or "[dim]none[/dim]")
        table.add_row("Priority:", str(agent.priority))
        table.add_row("Status:", "[green]Enabled[/green]" if agent.enabled else "[red]Disabled[/red]")

        caps = ", ".join(agent.capabilities) if agent.capabilities else "[dim]none[/dim]"
        table.add_row("Capabilities:", caps)
        table.add_row("File:", str(agent.file_path.name))

        self.console.print(Panel(table, title=f"Agent: {agent.name}", border_style="blue"))

        # Show full prompt content
        self.console.print()
        self.console.print("[bold]Agent Prompt:[/bold]")
        self.console.print(Panel(agent.content, border_style="dim"))
