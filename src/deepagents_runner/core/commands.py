"""Command execution engine for SpecKit commands."""

from pathlib import Path
from typing import Optional, Dict, Any, Callable
from datetime import datetime

from deepagents_runner.models import CommandType, WorkflowPhase
from deepagents_runner.models.feature import Feature
from deepagents_runner.models.workflow import WorkflowState
from deepagents_runner.core.state import StateManager
from deepagents_runner.core.agents import AgentManager
from deepagents_runner.core.config import RunnerConfig
from deepagents_runner.llm.base import LLMProvider, Message
from deepagents_runner.llm.factory import LLMProviderFactory
from deepagents_runner.utils.exceptions import CommandExecutionError
from deepagents_runner.utils.files import write_json


async def generate_suggestions(
    llm_provider: LLMProvider,
    command_type: CommandType,
    generated_content: str,
    agent_manager,
    temperature: float = 0.7
) -> str:
    """Generate suggestions for next steps based on completed work.

    Args:
        llm_provider: LLM provider to use
        command_type: Type of command that was executed
        generated_content: The content that was generated
        agent_manager: Agent manager for listing available agents
        temperature: Sampling temperature

    Returns:
        Markdown-formatted suggestions
    """
    # Get list of available agents
    available_agents = agent_manager.list_agents()
    agent_list = "\n".join([f"  - {agent.name}: {agent.specialization}" for agent in available_agents[:10]])  # Show top 10

    suggestions_prompt = f"""I just completed a {command_type.value} command and generated the following content:

---
{generated_content}
---

Based on this {command_type.value}, provide 2-4 specific, actionable suggestions for what to do next.

Available commands you can suggest:
  - /speckit.specify <description> - Create feature specification
  - /speckit.clarify - Ask clarification questions
  - /speckit.plan - Generate implementation plan
  - /speckit.tasks - Generate task breakdown
  - /speckit.implement - Execute implementation
  - /speckit.analyze - Analyze consistency
  - /speckit.checklist - Generate checklist
  - /speckit.constitution - Create project constitution

Available agents (use with --agent flag):
{agent_list}

Example: "/speckit.plan --agent archie-architect"

Consider:
- What's the logical next step in the workflow?
- What might need clarification or refinement?
- What technical considerations should be addressed?
- Which specialized agents would be most helpful?

Format your response as a brief bulleted list (2-4 items). Be specific and concrete. Include command suggestions when relevant. Start directly with the bullets, no introduction needed."""

    messages = [
        Message("user", suggestions_prompt)
    ]

    suggestions = await llm_provider.generate(
        messages=messages,
        temperature=temperature,
        max_tokens=500
    )

    return suggestions


class CommandExecutor:
    """Executes SpecKit commands using agents and LLM providers."""

    def __init__(self, config: RunnerConfig):
        """Initialize command executor.

        Args:
            config: Runner configuration
        """
        self.config = config
        self.agent_manager = AgentManager(config.agents_dir)
        self.llm_provider = LLMProviderFactory.create(
            provider_type=config.provider_type,
            api_key=config.api_key,
            model=config.model
        )

        # Map commands to their executor methods
        self.command_handlers: Dict[CommandType, Callable] = {
            CommandType.CONSTITUTION: self.execute_constitution,
            CommandType.SPECIFY: self.execute_specify,
            CommandType.CLARIFY: self.execute_clarify,
            CommandType.PLAN: self.execute_plan,
            CommandType.TASKS: self.execute_tasks,
            CommandType.IMPLEMENT: self.execute_implement,
            CommandType.ANALYZE: self.execute_analyze,
            CommandType.CHECKLIST: self.execute_checklist,
        }

    async def execute_command(
        self,
        command_type: CommandType,
        feature: Feature,
        state: WorkflowState,
        user_input: Optional[str] = None,
        agent_override: Optional[list] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Execute a SpecKit command.

        Args:
            command_type: Type of command to execute
            feature: Current feature
            state: Current workflow state
            user_input: Optional user input for the command
            agent_override: Optional list of agents to use (overrides automatic selection)
            **kwargs: Additional command-specific parameters

        Returns:
            Dictionary with execution results including:
                - success: bool
                - selected_agents: List of agent names
                - agent_used: Name of agent that executed
                - other command-specific fields

        Raises:
            CommandExecutionError: If command execution fails
        """
        handler = self.command_handlers.get(command_type)
        if not handler:
            raise CommandExecutionError(f"Unknown command: {command_type}")

        try:
            # Select agents for this command (use override if provided)
            if agent_override:
                selected_agents = agent_override
            else:
                selected_agents = self.agent_manager.select_agents_for_command(command_type)

            # Pass selected agents to handler
            result = await handler(feature, state, user_input, selected_agents=selected_agents, **kwargs)

            # Ensure selected_agents is in result
            if 'selected_agents' not in result:
                result['selected_agents'] = [agent.name for agent in selected_agents]

            return result
        except Exception as e:
            raise CommandExecutionError(f"Command {command_type} failed: {e}")

    async def execute_specify(
        self,
        feature: Feature,
        state: WorkflowState,
        user_input: Optional[str] = None,
        selected_agents: Optional[list] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Execute the /speckit.specify command.

        Creates a feature specification from user description.

        Args:
            feature: Current feature
            state: Current workflow state
            user_input: Feature description from user
            selected_agents: Pre-selected agents for this command
            **kwargs: Additional parameters

        Returns:
            Dictionary with spec_file path and content
        """
        # Use selected agents or fallback to generic
        if not selected_agents:
            selected_agents = [self.agent_manager.get_generic_agent()]

        if not selected_agents or not selected_agents[0]:
            raise CommandExecutionError("No agents available")

        # Use primary agent (first in list)
        agent = selected_agents[0]

        # Build prompt
        user_prompt = f"""Create a detailed feature specification for:

{user_input}

Generate a comprehensive specification document in markdown format following this structure:

# Feature Specification: [Feature Name]

## Overview
Brief description of the feature.

## User Stories
List prioritized user stories (P1, P2, P3, P4).

## Functional Requirements
Detailed functional requirements (FR-001, FR-002, etc.).

## Non-Functional Requirements
Performance, security, scalability requirements.

## Constraints & Dependencies
Technical constraints and external dependencies.

## Edge Cases & Error Handling
Expected edge cases and how to handle them.

Please generate the complete specification document now."""

        # Execute with agent and automatic fallback
        agent_used, spec_content = await self.agent_manager.execute_with_fallback(
            agents=selected_agents,
            llm_provider=self.llm_provider,
            task_prompt=user_prompt,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens
        )

        # Ensure directory exists
        feature.spec_dir.mkdir(parents=True, exist_ok=True)

        # Write specification file
        with open(feature.spec_file, 'w') as f:
            f.write(spec_content)

        # Generate suggestions for next steps
        suggestions = await generate_suggestions(
            llm_provider=self.llm_provider,
            command_type=CommandType.SPECIFY,
            generated_content=spec_content,
            agent_manager=self.agent_manager,
            temperature=self.config.temperature
        )

        # Update state
        state_manager = StateManager(feature.spec_dir)
        state.current_phase = WorkflowPhase.SPECIFY
        state_manager.record_command(state, CommandType.SPECIFY)
        state.suggested_next = CommandType.PLAN

        return {
            "spec_file": str(feature.spec_file),
            "content": spec_content,
            "suggestions": suggestions,
            "selected_agents": [agent.name for agent in selected_agents],
            "agent_used": agent_used.name,
            "success": True
        }

    async def execute_plan(
        self,
        feature: Feature,
        state: WorkflowState,
        user_input: Optional[str] = None,
        selected_agents: Optional[list] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Execute the /speckit.plan command.

        Generates an implementation plan from the specification.

        Args:
            feature: Current feature
            state: Current workflow state
            user_input: Optional additional context
            selected_agents: Pre-selected agents for this command
            **kwargs: Additional parameters

        Returns:
            Dictionary with plan_file path and content
        """
        # Read the specification
        if not feature.spec_file.exists():
            raise CommandExecutionError("Specification file not found. Run /speckit.specify first.")

        with open(feature.spec_file, 'r') as f:
            spec_content = f.read()

        # Use selected agents or fallback to generic
        if not selected_agents:
            selected_agents = self.agent_manager.select_agents_for_command(CommandType.PLAN)

        if not selected_agents:
            selected_agents = [self.agent_manager.get_generic_agent()]

        if not selected_agents or not selected_agents[0]:
            raise CommandExecutionError("No agents available")

        # Build prompt
        user_prompt = f"""Based on the following feature specification, create a detailed implementation plan.

## Specification:
{spec_content}

Generate a comprehensive implementation plan in markdown format following this structure:

# Implementation Plan

## Technical Context
Technologies, frameworks, and tools to be used.

## Architecture & Design
High-level architecture and component design.

## Data Model
Key entities and their relationships.

## API Contracts
Interface definitions and contracts.

## Testing Strategy
Approach to testing and validation.

## Deployment Plan
How the feature will be deployed.

Please generate the complete implementation plan now."""

        # Execute with agent and automatic fallback
        agent_used, plan_content = await self.agent_manager.execute_with_fallback(
            agents=selected_agents,
            llm_provider=self.llm_provider,
            task_prompt=user_prompt,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens
        )

        # Write plan file
        plan_file = feature.spec_dir / "plan.md"
        with open(plan_file, 'w') as f:
            f.write(plan_content)

        feature.plan_file = plan_file

        # Generate suggestions for next steps
        suggestions = await generate_suggestions(
            llm_provider=self.llm_provider,
            command_type=CommandType.PLAN,
            generated_content=plan_content,
            agent_manager=self.agent_manager,
            temperature=self.config.temperature
        )

        # Update state
        state_manager = StateManager(feature.spec_dir)
        state.current_phase = WorkflowPhase.PLAN
        state_manager.record_command(state, CommandType.PLAN)
        state.suggested_next = CommandType.TASKS

        return {
            "plan_file": str(plan_file),
            "content": plan_content,
            "suggestions": suggestions,
            "selected_agents": [agent.name for agent in selected_agents],
            "agent_used": agent_used.name,
            "success": True
        }

    async def execute_tasks(
        self,
        feature: Feature,
        state: WorkflowState,
        user_input: Optional[str] = None,
        selected_agents: Optional[list] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Execute the /speckit.tasks command.

        Generates a task breakdown from the plan.

        Args:
            feature: Current feature
            state: Current workflow state
            user_input: Optional additional context
            selected_agents: Pre-selected agents for this command
            **kwargs: Additional parameters

        Returns:
            Dictionary with tasks_file path and content
        """
        # Read the plan
        if not feature.plan_file or not feature.plan_file.exists():
            raise CommandExecutionError("Plan file not found. Run /speckit.plan first.")

        with open(feature.plan_file, 'r') as f:
            plan_content = f.read()

        # Also read spec for context
        spec_content = ""
        if feature.spec_file.exists():
            with open(feature.spec_file, 'r') as f:
                spec_content = f.read()

        # Use selected agents or fallback to generic
        if not selected_agents:
            selected_agents = self.agent_manager.select_agents_for_command(CommandType.TASKS)

        if not selected_agents:
            selected_agents = [self.agent_manager.get_generic_agent()]

        if not selected_agents or not selected_agents[0]:
            raise CommandExecutionError("No agents available")

        # Build prompt
        user_prompt = f"""Based on the following specification and implementation plan, create a detailed task breakdown.

## Specification:
{spec_content}

## Implementation Plan:
{plan_content}

Generate a comprehensive task list in markdown format following this structure:

# Implementation Tasks

## Phase 1: Setup
- [ ] T001 [P1] Task description with file path

## Phase 2: Core Implementation
- [ ] T002 [P1] Task description with file path

... organize tasks by phase and priority ...

Each task should:
- Have a unique ID (T001, T002, etc.)
- Include priority (P1, P2, P3, P4)
- Have a clear, actionable description
- Specify the file or component to be modified

Please generate the complete task breakdown now."""

        # Execute with agent and automatic fallback
        agent_used, tasks_content = await self.agent_manager.execute_with_fallback(
            agents=selected_agents,
            llm_provider=self.llm_provider,
            task_prompt=user_prompt,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens
        )

        # Write tasks file
        tasks_file = feature.spec_dir / "tasks.md"
        with open(tasks_file, 'w') as f:
            f.write(tasks_content)

        feature.tasks_file = tasks_file

        # Generate suggestions for next steps
        suggestions = await generate_suggestions(
            llm_provider=self.llm_provider,
            command_type=CommandType.TASKS,
            generated_content=tasks_content,
            agent_manager=self.agent_manager,
            temperature=self.config.temperature
        )

        # Update state
        state_manager = StateManager(feature.spec_dir)
        state.current_phase = WorkflowPhase.TASKS
        state_manager.record_command(state, CommandType.TASKS)
        state.suggested_next = CommandType.IMPLEMENT

        return {
            "tasks_file": str(tasks_file),
            "content": tasks_content,
            "suggestions": suggestions,
            "selected_agents": [agent.name for agent in selected_agents],
            "agent_used": agent_used.name,
            "success": True
        }

    async def execute_implement(
        self,
        feature: Feature,
        state: WorkflowState,
        user_input: Optional[str] = None,
        selected_agents: Optional[list] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Execute the /speckit.implement command.

        Generates implementation guidance from the task breakdown.

        Args:
            feature: Current feature
            state: Current workflow state
            user_input: Optional task filter or specific task ID
            selected_agents: Pre-selected agents for this command
            **kwargs: Additional parameters

        Returns:
            Dictionary with implementation results
        """
        # Use selected agents or fallback to generic
        if not selected_agents:
            selected_agents = self.agent_manager.select_agents_for_command(CommandType.IMPLEMENT)

        if not selected_agents:
            selected_agents = [self.agent_manager.get_generic_agent()]

        if not selected_agents or not selected_agents[0]:
            raise CommandExecutionError("No agents available")

        # Read required artifacts
        if not feature.tasks_file or not feature.tasks_file.exists():
            raise CommandExecutionError("Tasks file not found. Run /speckit.tasks first.")

        with open(feature.tasks_file, 'r') as f:
            tasks_content = f.read()

        # Read spec and plan for context
        context = ""
        if feature.spec_file.exists():
            with open(feature.spec_file, 'r') as f:
                context += f"\n## Specification:\n{f.read()}\n"

        if feature.plan_file and feature.plan_file.exists():
            with open(feature.plan_file, 'r') as f:
                context += f"\n## Plan:\n{f.read()}\n"

        # Build prompt
        task_filter = f"\n\nFocus on: {user_input}" if user_input else ""

        user_prompt = f"""Generate detailed implementation guidance based on the following tasks and context.

{context}

## Tasks:
{tasks_content}

{task_filter}

For each task (or the specified tasks), provide:

## Implementation Guidance

For each task, include:

### [Task ID]: [Task Description]

**Implementation Approach:**
- Step-by-step approach to implement this task
- Key considerations and gotchas
- Suggested file structure or changes

**Code Snippets/Pseudocode:**
- Relevant code examples or pseudocode
- API signatures or interfaces to implement

**Testing Guidance:**
- How to test this implementation
- Key test cases to cover

**Dependencies:**
- What needs to be done first
- What other tasks this affects

Provide concrete, actionable guidance that a developer can use to implement each task."""

        # Execute with agent and automatic fallback
        agent_used, implementation_content = await self.agent_manager.execute_with_fallback(
            agents=selected_agents,
            llm_provider=self.llm_provider,
            task_prompt=user_prompt,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens
        )

        # Write implementation guidance file
        implementation_file = feature.spec_dir / "implementation.md"
        with open(implementation_file, 'w') as f:
            f.write(implementation_content)

        # Generate suggestions for next steps
        suggestions = await generate_suggestions(
            llm_provider=self.llm_provider,
            command_type=CommandType.IMPLEMENT,
            generated_content=implementation_content,
            agent_manager=self.agent_manager,
            temperature=self.config.temperature
        )

        # Update state
        state_manager = StateManager(feature.spec_dir)
        state.current_phase = WorkflowPhase.IMPLEMENT
        state_manager.record_command(state, CommandType.IMPLEMENT)

        return {
            "implementation_file": str(implementation_file),
            "content": implementation_content,
            "suggestions": suggestions,
            "selected_agents": [agent.name for agent in selected_agents],
            "agent_used": agent_used.name,
            "success": True
        }

    async def execute_clarify(
        self,
        feature: Feature,
        state: WorkflowState,
        user_input: Optional[str] = None,
        selected_agents: Optional[list] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Execute the /speckit.clarify command.

        Identifies ambiguities in the spec and asks clarification questions.

        Args:
            feature: Current feature
            state: Current workflow state
            user_input: Optional context
            selected_agents: Pre-selected agents for this command
            **kwargs: Additional parameters

        Returns:
            Dictionary with clarification questions
        """
        # Read the specification
        if not feature.spec_file.exists():
            raise CommandExecutionError("Specification file not found.")

        with open(feature.spec_file, 'r') as f:
            spec_content = f.read()

        # Use selected agents or fallback to generic
        if not selected_agents:
            selected_agents = self.agent_manager.select_agents_for_command(CommandType.CLARIFY)

        if not selected_agents:
            selected_agents = [self.agent_manager.get_generic_agent()]

        if not selected_agents or not selected_agents[0]:
            raise CommandExecutionError("No agents available")

        # Build prompt
        user_prompt = f"""Analyze the following specification and identify any ambiguities or underspecified areas.

## Specification:
{spec_content}

Generate up to 5 clarification questions that would help resolve ambiguities. Format as:

## Clarification Questions

1. **Question**: [Clear question]
   - Context: [Why this matters]
   - Options: [Possible answers]

Please generate the clarification questions now."""

        # Execute with agent and automatic fallback
        agent_used, clarifications = await self.agent_manager.execute_with_fallback(
            agents=selected_agents,
            llm_provider=self.llm_provider,
            task_prompt=user_prompt,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens
        )

        # Write clarifications to file
        clarify_file = feature.spec_dir / "clarifications.md"
        with open(clarify_file, 'w') as f:
            f.write(clarifications)

        # Generate suggestions for next steps
        suggestions = await generate_suggestions(
            llm_provider=self.llm_provider,
            command_type=CommandType.CLARIFY,
            generated_content=clarifications,
            agent_manager=self.agent_manager,
            temperature=self.config.temperature
        )

        # Update state
        state_manager = StateManager(feature.spec_dir)
        state_manager.record_command(state, CommandType.CLARIFY)

        return {
            "clarify_file": str(clarify_file),
            "content": clarifications,
            "suggestions": suggestions,
            "selected_agents": [agent.name for agent in selected_agents],
            "agent_used": agent_used.name,
            "success": True
        }

    async def execute_analyze(
        self,
        feature: Feature,
        state: WorkflowState,
        user_input: Optional[str] = None,
        selected_agents: Optional[list] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Execute the /speckit.analyze command.

        Analyzes cross-artifact consistency.

        Args:
            feature: Current feature
            state: Current workflow state
            user_input: Optional context
            selected_agents: Pre-selected agents for this command
            **kwargs: Additional parameters

        Returns:
            Dictionary with analysis results
        """
        # Use selected agents or fallback to generic
        if not selected_agents:
            selected_agents = self.agent_manager.select_agents_for_command(CommandType.ANALYZE)

        if not selected_agents:
            selected_agents = [self.agent_manager.get_generic_agent()]

        if not selected_agents or not selected_agents[0]:
            raise CommandExecutionError("No agents available")

        # Read all available artifacts
        artifacts = {}

        if feature.spec_file.exists():
            with open(feature.spec_file, 'r') as f:
                artifacts['spec.md'] = f.read()

        if feature.plan_file and feature.plan_file.exists():
            with open(feature.plan_file, 'r') as f:
                artifacts['plan.md'] = f.read()

        if feature.tasks_file and feature.tasks_file.exists():
            with open(feature.tasks_file, 'r') as f:
                artifacts['tasks.md'] = f.read()

        if not artifacts:
            raise CommandExecutionError("No artifacts found to analyze. Run /speckit.specify first.")

        # Build analysis prompt
        artifacts_text = "\n\n---\n\n".join([f"## {name}\n\n{content}" for name, content in artifacts.items()])

        user_prompt = f"""Analyze the following artifacts for consistency, completeness, and quality:

{artifacts_text}

Please provide a comprehensive analysis covering:

## Consistency Analysis
- Are the plan and tasks aligned with the specification?
- Do requirements in the spec have corresponding implementation in plan/tasks?
- Are there any contradictions between artifacts?

## Completeness Analysis
- Are all functional requirements covered?
- Are there gaps in the implementation plan?
- Are any edge cases or error scenarios missing?

## Quality Assessment
- Are requirements clear and testable?
- Is the architecture sound?
- Are tasks well-defined and actionable?

## Recommendations
- What should be addressed before implementation?
- What could be improved or clarified?
- Are there any risks or concerns?

Generate a detailed analysis report in markdown format."""

        # Execute with agent and automatic fallback
        agent_used, analysis_content = await self.agent_manager.execute_with_fallback(
            agents=selected_agents,
            llm_provider=self.llm_provider,
            task_prompt=user_prompt,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens
        )

        # Write analysis file
        analysis_file = feature.spec_dir / "analysis.md"
        with open(analysis_file, 'w') as f:
            f.write(analysis_content)

        # Generate suggestions for next steps
        suggestions = await generate_suggestions(
            llm_provider=self.llm_provider,
            command_type=CommandType.ANALYZE,
            generated_content=analysis_content,
            agent_manager=self.agent_manager,
            temperature=self.config.temperature
        )

        # Update state
        state_manager = StateManager(feature.spec_dir)
        state_manager.record_command(state, CommandType.ANALYZE)

        return {
            "analysis_file": str(analysis_file),
            "content": analysis_content,
            "suggestions": suggestions,
            "selected_agents": [agent.name for agent in selected_agents],
            "agent_used": agent_used.name,
            "success": True
        }

    async def execute_checklist(
        self,
        feature: Feature,
        state: WorkflowState,
        user_input: Optional[str] = None,
        selected_agents: Optional[list] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Execute the /speckit.checklist command.

        Generates a custom checklist.

        Args:
            feature: Current feature
            state: Current workflow state
            user_input: Checklist requirements
            selected_agents: Pre-selected agents for this command
            **kwargs: Additional parameters

        Returns:
            Dictionary with checklist
        """
        # Use selected agents or fallback to generic
        if not selected_agents:
            selected_agents = self.agent_manager.select_agents_for_command(CommandType.CHECKLIST)

        if not selected_agents:
            selected_agents = [self.agent_manager.get_generic_agent()]

        if not selected_agents or not selected_agents[0]:
            raise CommandExecutionError("No agents available")

        # Read available artifacts for context
        context = ""

        if feature.spec_file.exists():
            with open(feature.spec_file, 'r') as f:
                context += f"\n## Specification:\n{f.read()}\n"

        if feature.plan_file and feature.plan_file.exists():
            with open(feature.plan_file, 'r') as f:
                context += f"\n## Plan:\n{f.read()}\n"

        if feature.tasks_file and feature.tasks_file.exists():
            with open(feature.tasks_file, 'r') as f:
                context += f"\n## Tasks:\n{f.read()}\n"

        if not context:
            raise CommandExecutionError("No artifacts found. Run /speckit.specify first.")

        # Build prompt
        user_prompt = f"""Based on the following feature artifacts, generate a comprehensive quality checklist for this feature.

{context}

{f"Additional requirements: {user_input}" if user_input else ""}

Generate a detailed checklist covering:

## Pre-Implementation Checklist
- [ ] Requirements review items
- [ ] Design validation items
- [ ] Dependency verification items

## Implementation Checklist
- [ ] Code quality items
- [ ] Testing items
- [ ] Documentation items

## Pre-Deployment Checklist
- [ ] Security review items
- [ ] Performance validation items
- [ ] Integration testing items

## Post-Deployment Checklist
- [ ] Monitoring setup items
- [ ] Rollback plan items
- [ ] Documentation updates items

Each checklist item should be specific and actionable for this feature."""

        # Execute with agent and automatic fallback
        agent_used, checklist_content = await self.agent_manager.execute_with_fallback(
            agents=selected_agents,
            llm_provider=self.llm_provider,
            task_prompt=user_prompt,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens
        )

        # Write checklist file
        checklist_file = feature.spec_dir / "checklist.md"
        with open(checklist_file, 'w') as f:
            f.write(checklist_content)

        # Generate suggestions for next steps
        suggestions = await generate_suggestions(
            llm_provider=self.llm_provider,
            command_type=CommandType.CHECKLIST,
            generated_content=checklist_content,
            agent_manager=self.agent_manager,
            temperature=self.config.temperature
        )

        # Update state
        state_manager = StateManager(feature.spec_dir)
        state_manager.record_command(state, CommandType.CHECKLIST)

        return {
            "checklist_file": str(checklist_file),
            "content": checklist_content,
            "suggestions": suggestions,
            "selected_agents": [agent.name for agent in selected_agents],
            "agent_used": agent_used.name,
            "success": True
        }

    async def execute_constitution(
        self,
        feature: Feature,
        state: WorkflowState,
        user_input: Optional[str] = None,
        selected_agents: Optional[list] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Execute the /speckit.constitution command.

        Creates or updates project constitution.

        Args:
            feature: Current feature
            state: Current workflow state
            user_input: Optional principles
            selected_agents: Pre-selected agents for this command
            **kwargs: Additional parameters

        Returns:
            Dictionary with constitution
        """
        # Use selected agents or fallback to generic
        if not selected_agents:
            selected_agents = self.agent_manager.select_agents_for_command(CommandType.CONSTITUTION)

        if not selected_agents:
            selected_agents = [self.agent_manager.get_generic_agent()]

        if not selected_agents or not selected_agents[0]:
            raise CommandExecutionError("No agents available")

        # Build prompt
        user_prompt = f"""Create a project constitution that defines the principles, standards, and guidelines for this project.

{f"User-provided principles: {user_input}" if user_input else ""}

Generate a comprehensive constitution document in markdown format covering:

# Project Constitution

## Core Principles
Define the fundamental values and principles that guide all decisions in this project.

## Technical Standards
### Code Quality
- Coding standards and best practices
- Review requirements
- Testing requirements

### Architecture
- Architectural principles
- Design patterns to follow
- Integration patterns

### Security
- Security requirements
- Authentication/authorization standards
- Data protection policies

## Development Workflow
### Version Control
- Branching strategy
- Commit message standards
- Pull request requirements

### Testing Strategy
- Unit testing requirements
- Integration testing requirements
- Coverage thresholds

### Documentation
- Code documentation standards
- API documentation requirements
- README requirements

## Quality Assurance
- Definition of Done
- Code review checklist
- Quality gates

## Deployment & Operations
- Deployment process
- Monitoring requirements
- Incident response guidelines

Each section should contain specific, actionable guidelines that team members can follow."""

        # Execute with agent and automatic fallback
        agent_used, constitution_content = await self.agent_manager.execute_with_fallback(
            agents=selected_agents,
            llm_provider=self.llm_provider,
            task_prompt=user_prompt,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens
        )

        # Write constitution file to project root (not feature-specific)
        constitution_file = self.config.workspace_root / "CONSTITUTION.md"
        with open(constitution_file, 'w') as f:
            f.write(constitution_content)

        # Generate suggestions for next steps
        suggestions = await generate_suggestions(
            llm_provider=self.llm_provider,
            command_type=CommandType.CONSTITUTION,
            generated_content=constitution_content,
            agent_manager=self.agent_manager,
            temperature=self.config.temperature
        )

        # Update state
        state_manager = StateManager(feature.spec_dir)
        state.current_phase = WorkflowPhase.CONSTITUTION
        state_manager.record_command(state, CommandType.CONSTITUTION)

        return {
            "constitution_file": str(constitution_file),
            "content": constitution_content,
            "suggestions": suggestions,
            "selected_agents": [agent.name for agent in selected_agents],
            "agent_used": agent_used.name,
            "success": True
        }
