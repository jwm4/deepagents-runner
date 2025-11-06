"""Agent management and selection."""

from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from enum import Enum
import frontmatter
from tenacity import retry, stop_after_attempt, wait_exponential

from deepagents_runner.models import CommandType
from deepagents_runner.llm.base import LLMProvider, Message
from deepagents_runner.utils.exceptions import (
    AgentDefinitionError,
    AgentExecutionError
)


class AgentDefinition:
    """Represents a loaded agent definition."""

    def __init__(self, file_path: Path, metadata: Dict[str, Any], content: str):
        """Initialize agent definition.

        Args:
            file_path: Path to agent definition file
            metadata: Frontmatter metadata
            content: Agent prompt content
        """
        self.file_path = file_path
        self.name = metadata.get('name', file_path.stem)
        self.role = metadata.get('role', 'generic')
        self.specialization = metadata.get('specialization')
        self.capabilities = metadata.get('capabilities', [])
        self.priority = metadata.get('priority', 1)
        self.content = content
        self.enabled = True  # Can be disabled at session level

    def matches_capabilities(self, required_capabilities: List[str]) -> bool:
        """Check if agent has required capabilities.

        Args:
            required_capabilities: List of capability names

        Returns:
            True if agent has all required capabilities
        """
        return all(cap in self.capabilities for cap in required_capabilities)

    def score_for_task(self, required_capabilities: List[str]) -> int:
        """Calculate priority score for a task.

        Args:
            required_capabilities: List of capability names

        Returns:
            Priority score (higher is better)
        """
        if not self.matches_capabilities(required_capabilities):
            return 0

        # Base score from priority
        score = self.priority

        # Bonus for exact capability match
        if set(required_capabilities) == set(self.capabilities):
            score += 5

        return score


class AgentManager:
    """Manages agent definitions and selection."""

    # Map command types to required capabilities
    COMMAND_CAPABILITIES: Dict[CommandType, List[str]] = {
        CommandType.SPECIFY: [],  # Use generic
        CommandType.CLARIFY: [],  # Use generic
        CommandType.PLAN: ['architecture_design', 'component_design'],
        CommandType.TASKS: ['project_management', 'task_breakdown'],
        CommandType.IMPLEMENT: ['backend_implementation', 'frontend_implementation'],
        CommandType.ANALYZE: ['code_quality', 'code_review'],
        CommandType.CHECKLIST: ['quality_assurance', 'testing'],
        CommandType.CONSTITUTION: ['project_management'],
    }

    def __init__(self, agents_dir: Optional[Path] = None):
        """Initialize agent manager.

        Args:
            agents_dir: Directory containing agent definitions
        """
        if agents_dir is None:
            # Default to bundled agents
            agents_dir = Path(__file__).parent.parent.parent / "agents"

        self.agents_dir = agents_dir
        self.agents: List[AgentDefinition] = []
        self._load_agents()

    def _load_agents(self) -> None:
        """Load all agent definitions from disk."""
        if not self.agents_dir.exists():
            raise AgentDefinitionError(f"Agents directory not found: {self.agents_dir}")

        for agent_file in self.agents_dir.glob("*.md"):
            try:
                self.agents.append(self._load_agent(agent_file))
            except Exception as e:
                # Log but don't fail on individual agent load errors
                print(f"Warning: Failed to load agent {agent_file}: {e}")

    def _load_agent(self, file_path: Path) -> AgentDefinition:
        """Load a single agent definition.

        Args:
            file_path: Path to agent markdown file

        Returns:
            AgentDefinition object

        Raises:
            AgentDefinitionError: If agent file is invalid
        """
        try:
            with open(file_path, 'r') as f:
                post = frontmatter.load(f)

            return AgentDefinition(
                file_path=file_path,
                metadata=post.metadata,
                content=post.content
            )
        except Exception as e:
            raise AgentDefinitionError(f"Failed to parse {file_path}: {e}")

    def select_agent(self, required_capabilities: List[str]) -> Optional[AgentDefinition]:
        """Select best agent for required capabilities.

        Args:
            required_capabilities: List of capability names needed

        Returns:
            Best matching agent, or None if no match
        """
        candidates = [
            (agent, agent.score_for_task(required_capabilities))
            for agent in self.agents
        ]

        # Filter to only agents that can handle the task
        candidates = [(agent, score) for agent, score in candidates if score > 0]

        if not candidates:
            return None

        # Sort by score (descending) then by priority
        candidates.sort(key=lambda x: (x[1], x[0].priority), reverse=True)

        return candidates[0][0]

    def get_generic_agent(self) -> Optional[AgentDefinition]:
        """Get the generic fallback agent.

        Returns:
            Generic agent definition, or None if not found
        """
        for agent in self.agents:
            if agent.role == 'generic':
                return agent
        return None

    def list_agents(self, include_disabled: bool = False) -> List[AgentDefinition]:
        """Get all loaded agents.

        Args:
            include_disabled: Include disabled agents in the list

        Returns:
            List of all agent definitions
        """
        if include_disabled:
            return self.agents.copy()
        return [agent for agent in self.agents if agent.enabled]

    def select_agents(
        self,
        required_capabilities: List[str],
        max_agents: int = 3
    ) -> List[AgentDefinition]:
        """Select multiple agents for required capabilities.

        Args:
            required_capabilities: List of capability names needed
            max_agents: Maximum number of agents to select

        Returns:
            List of best matching agents (up to max_agents)
        """
        # Score all enabled agents
        candidates = [
            (agent, agent.score_for_task(required_capabilities))
            for agent in self.agents
            if agent.enabled
        ]

        # Filter to only agents that can handle the task
        candidates = [(agent, score) for agent, score in candidates if score > 0]

        if not candidates:
            return []

        # Sort by score (descending)
        candidates.sort(key=lambda x: (x[1], x[0].priority), reverse=True)

        # Return top N agents
        return [agent for agent, score in candidates[:max_agents]]

    def select_agents_for_command(
        self,
        command_type: CommandType
    ) -> List[AgentDefinition]:
        """Select agents appropriate for a command type.

        Args:
            command_type: Type of command to execute

        Returns:
            List of selected agents (may be empty if using generic)
        """
        required_caps = self.COMMAND_CAPABILITIES.get(command_type, [])

        if not required_caps:
            # Use generic agent
            generic = self.get_generic_agent()
            return [generic] if generic else []

        # Select specialized agents
        agents = self.select_agents(required_caps)

        # Fallback to generic if no specialized agents
        if not agents:
            generic = self.get_generic_agent()
            if generic:
                agents = [generic]

        return agents

    def enable_agent(self, agent_name: str) -> bool:
        """Enable an agent for this session.

        Args:
            agent_name: Name of agent to enable

        Returns:
            True if agent was found and enabled
        """
        for agent in self.agents:
            if agent.name.lower() == agent_name.lower():
                agent.enabled = True
                return True
        return False

    def disable_agent(self, agent_name: str) -> bool:
        """Disable an agent for this session.

        Args:
            agent_name: Name of agent to disable

        Returns:
            True if agent was found and disabled
        """
        for agent in self.agents:
            if agent.name.lower() == agent_name.lower():
                agent.enabled = False
                return True
        return False

    def get_agent_by_name(self, agent_name: str) -> Optional[AgentDefinition]:
        """Get an agent by name.

        Args:
            agent_name: Name of the agent

        Returns:
            AgentDefinition if found, None otherwise
        """
        for agent in self.agents:
            if agent.name.lower() == agent_name.lower():
                return agent
        return None

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def execute_agent(
        self,
        agent: AgentDefinition,
        llm_provider: LLMProvider,
        task_prompt: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> str:
        """Execute an agent task with retry logic.

        Args:
            agent: Agent to execute
            llm_provider: LLM provider to use
            task_prompt: User/task prompt for the agent
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate

        Returns:
            Generated response from agent

        Raises:
            AgentExecutionError: If execution fails after retries
        """
        try:
            messages = [
                Message("system", agent.content),
                Message("user", task_prompt)
            ]

            response = await llm_provider.generate(
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )

            return response

        except Exception as e:
            raise AgentExecutionError(f"Agent {agent.name} execution failed: {e}")

    async def execute_with_fallback(
        self,
        agents: List[AgentDefinition],
        llm_provider: LLMProvider,
        task_prompt: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> Tuple[AgentDefinition, str]:
        """Execute with automatic fallback to generic agent on failure.

        Args:
            agents: List of agents to try (in order)
            llm_provider: LLM provider to use
            task_prompt: User/task prompt
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate

        Returns:
            Tuple of (agent_used, response)

        Raises:
            AgentExecutionError: If all agents fail including generic
        """
        last_error = None
        error_details = None

        for agent in agents:
            try:
                response = await self.execute_agent(
                    agent=agent,
                    llm_provider=llm_provider,
                    task_prompt=task_prompt,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                return (agent, response)
            except Exception as e:
                last_error = e
                # Extract the actual error from RetryError if present
                if hasattr(e, '__cause__') and e.__cause__:
                    error_details = str(e.__cause__)
                else:
                    error_details = str(e)
                continue

        # Try generic agent as last resort
        generic = self.get_generic_agent()
        if generic and generic not in agents:
            try:
                response = await self.execute_agent(
                    agent=generic,
                    llm_provider=llm_provider,
                    task_prompt=task_prompt,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                return (generic, response)
            except Exception as e:
                last_error = e
                if hasattr(e, '__cause__') and e.__cause__:
                    error_details = str(e.__cause__)
                else:
                    error_details = str(e)

        # Provide helpful error message
        error_msg = error_details or str(last_error)

        # Check for common issues
        if "authentication" in error_msg.lower() or "api key" in error_msg.lower() or "401" in error_msg:
            raise AgentExecutionError(
                "Authentication failed. Please check your API key is set correctly:\n"
                "  export ANTHROPIC_API_KEY=your-key-here\n"
                "  export OPENAI_API_KEY=your-key-here\n"
                f"Original error: {error_msg}"
            )
        elif "rate limit" in error_msg.lower() or "429" in error_msg:
            raise AgentExecutionError(
                f"Rate limit exceeded. Please wait a moment and try again.\n"
                f"Original error: {error_msg}"
            )
        else:
            raise AgentExecutionError(
                f"All agents failed to execute.\n"
                f"Error: {error_msg}"
            )
