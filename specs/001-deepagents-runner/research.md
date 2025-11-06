# Research: DeepAgents Runner Technical Decisions

**Phase**: 0 - Outline & Research
**Date**: 2025-11-05
**Purpose**: Resolve technical unknowns and establish architectural patterns

## Research Tasks

### 1. DeepAgents Library Integration

**Question**: How does DeepAgents support multiple LLM providers, and what is the API for agent creation?

**Decision**: Use DeepAgents' provider abstraction layer

**Rationale**:
- DeepAgents supports configurable LLM clients through its `ChatClient` interface
- Agents are created with `DeepAgent` class, accepting custom chat clients
- The library provides middleware for filesystem operations, task decomposition, and subagent spawning
- Supports both Anthropic and OpenAI through standard SDKs

**Implementation Pattern**:
```python
from deepagents import DeepAgent, ChatClient
from deepagents.middleware import FilesystemMiddleware, SubAgentMiddleware

# Create provider-specific client
client = AnthropicChatClient(api_key=env_var)
# or OpenAIChatClient(api_key=env_var)

# Create agent with middleware
agent = DeepAgent(
    client=client,
    system_prompt=load_agent_definition("archie-architect.md"),
    middleware=[
        FilesystemMiddleware(state_dir=".state/"),
        SubAgentMiddleware()
    ]
)
```

**Alternatives Considered**:
- Direct LLM SDK usage without DeepAgents: Rejected because we lose task decomposition, context management, and subagent capabilities
- LangChain: Rejected because spec specifically requires DeepAgents

**References**:
- DeepAgents GitHub: https://github.com/langchain-ai/deepagents
- Example usage in Claude Code-inspired workflows

---

### 2. Agent Definition Format and Loading

**Question**: How should we structure and load the 21 Ambient agent markdown files?

**Decision**: Use frontmatter + markdown format with role, capabilities, and system prompt

**Rationale**:
- Markdown is human-readable and easy to edit
- Frontmatter (YAML) provides structured metadata
- System prompt in markdown body enables rich formatting
- Compatible with version control and diffs

**Format**:
```markdown
---
role: architect
name: Archie Architect
specialization: system_architecture
capabilities:
  - architecture_design
  - component_design
  - dependency_analysis
  - scalability_planning
priority: 10  # Higher priority = more specialized
---

You are Archie, a senior software architect. Your role is to...

[Detailed system prompt with examples and guidelines]
```

**Loading Implementation**:
```python
import frontmatter
from pathlib import Path

def load_agent_definition(agent_file: str) -> tuple[dict, str]:
    path = Path(__file__).parent / "agents" / agent_file
    with open(path, 'r') as f:
        post = frontmatter.load(f)
        metadata = post.metadata  # dict with role, capabilities, etc.
        system_prompt = post.content  # markdown body
    return metadata, system_prompt
```

**Alternatives Considered**:
- Pure JSON: Rejected because not as readable for long prompts
- Separate metadata files: Rejected because splits related information
- Hardcoded in Python: Rejected because reduces flexibility

---

### 3. Agent Selection and Delegation Strategy

**Question**: How should we automatically select the appropriate agent(s) for a given task?

**Decision**: Use capability-based matching with task classification

**Rationale**:
- SpecKit commands have predictable task types (architecture, testing, documentation, etc.)
- Agent metadata includes capabilities list
- Matching algorithm can score agents by capability overlap
- Most specialized agent (highest priority score) wins

**Implementation Pattern**:
```python
def select_agents(task_type: str, required_capabilities: list[str]) -> list[AgentDef]:
    """
    task_type: 'plan', 'test', 'document', etc.
    required_capabilities: ['architecture', 'scalability', ...]
    """
    # Load all agent definitions
    agents = load_all_agents()

    # Score each agent based on capability match
    scored = []
    for agent in agents:
        capabilities = set(agent['capabilities'])
        required = set(required_capabilities)
        overlap = len(capabilities & required)

        # Priority boost for specialized agents
        score = overlap * agent.get('priority', 1)
        if score > 0:
            scored.append((score, agent))

    # Sort by score descending, return top agents
    scored.sort(reverse=True, key=lambda x: x[0])
    return [agent for score, agent in scored]

# For /speckit.plan with architecture components
agents = select_agents('plan', ['architecture', 'scalability'])
# Returns: [Archie Architect, Stella Staff Engineer]
```

**Task Type Mapping**:
- `/speckit.specify`: Generic agent (no specialization needed for initial spec)
- `/speckit.plan`: Archie Architect, Aria UX Architect (if UX components), Stella Staff Engineer
- `/speckit.tasks`: Diego Program Manager, Lee Team Lead, Emma Engineering Manager
- `/speckit.implement`: Stella Staff Engineer, Neil Test Engineer, Terry Technical Writer
- `/speckit.analyze`: Dan Senior Director, Parker Product Manager

**Alternatives Considered**:
- Manual agent assignment: Rejected because defeats automation purpose
- LLM-based classification: Rejected as too slow and expensive
- Rule-based only: Chosen as deterministic and fast

---

### 4. State Persistence Format

**Question**: What specific structure should the JSON state files use?

**Decision**: Separate files for different state aspects with schema versioning

**Rationale**:
- Separate concerns: workflow state vs. command history vs. agent context
- Easier to read/debug individual files
- Schema versioning supports migration
- File-based locking prevents concurrent modifications

**File Structure**:
```text
specs/001-feature/.state/
├── workflow.json        # Current workflow position
├── context.json         # Feature context and metadata
├── command_history.json # Log of all command executions
└── agents/              # Agent-specific context
    ├── archie.json
    └── neil.json
```

**Workflow State Schema**:
```json
{
  "schema_version": "1.0",
  "feature_number": "001",
  "feature_name": "deepagents-runner",
  "current_phase": "plan",
  "completed_commands": [
    {"command": "specify", "timestamp": "2025-11-05T10:00:00Z"},
    {"command": "clarify", "timestamp": "2025-11-05T10:30:00Z"}
  ],
  "suggested_next": "plan",
  "branch": "001-deepagents-runner",
  "last_updated": "2025-11-05T11:00:00Z"
}
```

**Context Schema**:
```json
{
  "schema_version": "1.0",
  "feature": {
    "id": "001",
    "name": "deepagents-runner",
    "description": "Interactive terminal for SpecKit commands"
  },
  "files": {
    "spec": "specs/001-deepagents-runner/spec.md",
    "plan": "specs/001-deepagents-runner/plan.md",
    "tasks": null
  },
  "llm_provider": "anthropic",  # or "openai"
  "agent_cache": {}  # Cached agent outputs for reuse
}
```

**Alternatives Considered**:
- SQLite database: Rejected as over-engineering for this use case
- Single monolithic JSON: Rejected as harder to read and update atomically
- Plain text logs: Rejected as not structured enough for programmatic access

---

### 5. Terminal UI and Progress Display

**Question**: What library and patterns should we use for the interactive terminal UI?

**Decision**: Use Rich library for terminal UI with structured progress display

**Rationale**:
- Rich provides excellent terminal formatting, progress bars, live updates
- Supports async/concurrent operations natively
- Cross-platform (Windows, macOS, Linux)
- Clean separation between business logic and UI

**Implementation Pattern**:
```python
from rich.console import Console
from rich.live import Live
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()

# Session startup with feature context
console.print(f"[bold green]DeepAgents Runner[/bold green]")
console.print(f"Feature: [cyan]001-deepagents-runner[/cyan]")
console.print(f"Provider: [yellow]{provider}[/yellow]\n")

# Command execution with live progress
with Live(console=console, refresh_per_second=4) as live:
    table = Table(title="Agent Activity")
    table.add_column("Agent", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Task", style="white")

    # Update table as agents work
    table.add_row("Archie Architect", "🔄 Working", "Designing component architecture")
    table.add_row("Neil Test Engineer", "⏳ Waiting", "Pending architecture")

    live.update(table)
```

**Progress States**:
- `🔄 Working` - Agent actively processing
- `✅ Complete` - Agent finished successfully
- `⚠️  Retry` - Agent failed, retrying with backoff
- `🔀 Fallback` - Using generic agent fallback
- `⏳ Waiting` - Queued, waiting for dependencies
- `❌ Error` - Fatal error

**Alternatives Considered**:
- Raw terminal output: Rejected as poor UX
- Prompt Toolkit: Rejected as more complex than needed for our use case
- Custom ANSI codes: Rejected due to cross-platform issues

---

### 6. Concurrent Agent Execution

**Question**: How should we implement parallel agent execution while maintaining coordination?

**Decision**: Use asyncio with task groups and dependency tracking

**Rationale**:
- Asyncio provides cooperative multitasking without threading complexity
- Task groups allow waiting for multiple agents simultaneously
- Dependency tracking ensures correct execution order
- Compatible with async LLM SDK calls

**Implementation Pattern**:
```python
import asyncio
from typing import List, Dict

async def execute_agents_parallel(
    agents: List[AgentTask],
    dependencies: Dict[str, List[str]]
) -> Dict[str, AgentOutput]:
    """
    agents: List of (agent_name, task) tuples
    dependencies: {agent_name: [depends_on_agent1, ...]}
    """
    results = {}
    completed = set()

    async def run_agent(agent_name: str, task: str):
        # Wait for dependencies
        deps = dependencies.get(agent_name, [])
        while not all(d in completed for d in deps):
            await asyncio.sleep(0.1)

        # Execute agent
        output = await agent_client.execute(task)
        results[agent_name] = output
        completed.add(agent_name)
        return output

    # Create tasks for all independent agents
    tasks = [
        asyncio.create_task(run_agent(agent, task))
        for agent, task in agents
    ]

    # Wait for all to complete
    await asyncio.gather(*tasks)
    return results

# Example: /speckit.plan execution
dependencies = {
    "aria-ux": [],  # No dependencies, can start immediately
    "archie-architect": [],  # Independent
    "neil-test": ["archie-architect"],  # Needs architecture first
}

results = await execute_agents_parallel(
    [("aria-ux", "Design UX"), ("archie-architect", "Design arch"), ("neil-test", "Plan tests")],
    dependencies
)
```

**Alternatives Considered**:
- Threading: Rejected due to GIL and complexity
- Multiprocessing: Rejected as overkill for I/O-bound LLM calls
- Sequential execution only: Rejected due to 40% performance improvement requirement (SC-005)

---

### 7. Error Handling and Retry Logic

**Question**: What is the specific implementation of exponential backoff for agent failures?

**Decision**: Tenacity library with exponential backoff and jitter

**Rationale**:
- Tenacity is battle-tested for retry logic
- Supports exponential backoff with configurable parameters
- Jitter prevents thundering herd on rate limit recovery
- Integrates well with async/await

**Implementation Pattern**:
```python
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)

@retry(
    retry=retry_if_exception_type((RateLimitError, TimeoutError)),
    wait=wait_exponential(multiplier=1, min=2, max=10),  # 2s, 4s, 8s, 10s
    stop=stop_after_attempt(2),  # Original + 1 retry = 2 total attempts
    reraise=True
)
async def execute_agent_with_retry(agent: DeepAgent, task: str) -> AgentOutput:
    try:
        return await agent.execute(task)
    except Exception as e:
        logger.warning(f"Agent execution failed: {e}")
        raise

# Fallback wrapper
async def execute_with_fallback(
    specialized_agent: DeepAgent,
    generic_agent: DeepAgent,
    task: str
) -> tuple[AgentOutput, str]:
    """Returns (output, agent_used)"""
    try:
        output = await execute_agent_with_retry(specialized_agent, task)
        return output, "specialized"
    except Exception as e:
        logger.info(f"Falling back to generic agent due to: {e}")
        output = await generic_agent.execute(task)
        return output, "generic"
```

**Backoff Schedule**:
- Attempt 1: Immediate
- Attempt 2: 2 seconds wait
- Fallback: Use generic agent

**Alternatives Considered**:
- Linear backoff: Rejected as not optimal for rate limiting
- Unlimited retries: Rejected due to 30s failure detection requirement (SC-007)
- No backoff: Rejected as wastes API quota during rate limits

---

## Summary

All technical unknowns resolved. Ready to proceed to Phase 1 (Design & Contracts).

**Key Technical Choices**:
1. DeepAgents with custom ChatClient wrappers for Anthropic/OpenAI
2. Frontmatter markdown format for agent definitions
3. Capability-based agent selection with priority scoring
4. Separate JSON files for workflow state with schema versioning
5. Rich library for terminal UI with live progress updates
6. Asyncio for parallel agent execution with dependency tracking
7. Tenacity for exponential backoff retry with generic agent fallback

**Dependencies to Add**:
- `deepagents` - Core agent orchestration
- `anthropic` - Anthropic Claude SDK
- `openai` - OpenAI GPT SDK
- `python-frontmatter` - Parse agent definition files
- `rich` - Terminal UI
- `tenacity` - Retry logic
- `gitpython` - Git operations
- `pydantic` - Data validation
- `pytest`, `pytest-asyncio` - Testing
