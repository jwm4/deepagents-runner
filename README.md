# DeepAgents Runner

An interactive runner for SpecKit commands powered by DeepAgents.

## Current Status: Phase 4 Complete - Full Agent Orchestration! 🚀

The MVP is fully functional with LLM-powered command execution, specialized agent selection, and automatic retry/fallback!

### What Works (Phase 3-4)

- **Package Installation**: Install via `pip install -e .`
- **CLI Entry Point**: Launch with `deepagents-runner` command
- **Command-Line Arguments**: `--provider`, `--model`, `--workspace`, `--feature`
- **Interactive Terminal**: Rich-based REPL with formatted output
- **Context Detection**: Auto-detects feature from git branch (pattern: `001-feature-name`)
- **State Management**: Workflow state persistence to `.state/workflow.json`
- **Agent Management**: Loads agent definitions from markdown files with capability matching
- **LLM Providers**: Anthropic Claude and OpenAI GPT integration with streaming support
- **Configuration**: Environment variables and command-line configuration
- **Real Command Execution**:
  - `/speckit.specify` - Creates feature specifications using LLM
  - `/speckit.plan` - Generates implementation plans
  - `/speckit.tasks` - Breaks down plans into actionable tasks
  - `/speckit.clarify` - Identifies ambiguities and asks questions
  - Additional commands (implement, analyze, checklist, constitution) have placeholders
- **22 Specialized Agents**: Full suite of expert agents for different domains
- **Agent Management Commands**: List, show, enable/disable agents at runtime
- **Automatic Agent Selection**: System selects best agents based on task capabilities
- **Retry Logic**: Exponential backoff with automatic fallback to generic agent
- **Session-Level Control**: Enable/disable specific agents during your session

### Future Enhancements (Optional)

- **Agent Attribution in Output**: Show which agent wrote which section in files
- **DeepAgents Library Integration**: Full task decomposition and subprocess spawning
- **Parallel Agent Execution**: Run multiple specialized agents concurrently
- **--agent Flag**: Override automatic selection from command line
- **Streaming Output**: Show LLM responses in real-time
- **Full Implementation Command**: Actual code generation for tasks

## Installation

```bash
# Install in development mode
pip install -e .

# Or install from requirements.txt
pip install -r requirements.txt
```

## Usage

### Quick Start

```bash
# Set your API key
export ANTHROPIC_API_KEY=sk-ant-api03-...

# Launch the runner
deepagents-runner

# In the REPL, create a new feature
> /speckit.specify Build a user authentication system with OAuth2 support

# Follow the workflow
> /speckit.plan
> /speckit.tasks
```

### Command-Line Options

```bash
# Use specific provider
deepagents-runner --provider openai

# Use specific model
deepagents-runner --model claude-sonnet-4-5

# Work on specific feature
deepagents-runner --feature 002-my-feature

# Different workspace
deepagents-runner --workspace /path/to/project
```

### Available Commands (in REPL)

**SpecKit Commands (LLM-powered):**
- `/speckit.specify <description>` - Create feature specification from description
- `/speckit.clarify` - Identify ambiguities and ask clarification questions
- `/speckit.plan` - Generate implementation plan from specification
- `/speckit.tasks` - Break down plan into actionable tasks
- `/speckit.implement` - Execute implementation (placeholder)
- `/speckit.analyze` - Analyze cross-artifact consistency (placeholder)
- `/speckit.checklist` - Generate custom checklist (placeholder)
- `/speckit.constitution` - Create project constitution (placeholder)

**Agent Override:**
All SpecKit commands support `--agent` or `--agents` flags to override automatic agent selection:
- `/speckit.specify --agent bobby-backend Build a REST API` - Use specific agent
- `/speckit.plan --agents archie-architect,bobby-backend` - Use multiple agents

**Agent Commands (NEW):**
- `agents list` - Show all 22 available agents with capabilities
- `agents show <name>` - Show detailed info about a specific agent
- `agents enable <name>` - Enable an agent for this session
- `agents disable <name>` - Disable an agent for this session

**Built-in Commands:**
- `help` or `?` - Show available commands
- `context` - Display current feature context and workflow state
- `refresh` - Reload feature context from git branch
- `exit`, `quit`, or `q` - Exit the REPL

## Configuration

### Required Setup

**Set your LLM API key** (choose one):

```bash
# For Anthropic Claude (default)
export ANTHROPIC_API_KEY=sk-ant-api03-...

# For OpenAI GPT
export OPENAI_API_KEY=sk-...
export RUNNER_DEFAULT_PROVIDER=openai
```

### Optional Configuration

```bash
# Choose default provider (anthropic or openai)
export RUNNER_DEFAULT_PROVIDER=anthropic

# Specify model to use
export RUNNER_MODEL=claude-sonnet-4-5

# Adjust generation parameters
export RUNNER_TEMPERATURE=0.7
export RUNNER_MAX_TOKENS=4096
```

See `config/.env.example` for a template.

## Project Structure

```
deepagents-runner/
├── src/
│   ├── agents/                    # Bundled agent definitions
│   │   ├── archie-architect.md
│   │   ├── neil-test-engineer.md
│   │   └── generic-agent.md
│   └── deepagents_runner/
│       ├── core/                  # Core functionality
│       │   ├── agents.py          # Agent management
│       │   ├── context.py         # Feature context detection
│       │   └── state.py           # Workflow state persistence
│       ├── models/                # Data models
│       │   ├── __init__.py        # Enums (FeatureStatus, CommandType, etc.)
│       │   ├── feature.py         # Feature model
│       │   └── workflow.py        # WorkflowState model
│       ├── terminal/              # Terminal UI
│       │   ├── ui.py              # Rich-based UI components
│       │   └── repl.py            # Interactive REPL session
│       ├── utils/                 # Utilities
│       │   ├── exceptions.py      # Exception hierarchy
│       │   ├── files.py           # File I/O with atomic writes
│       │   └── git.py             # Git operations
│       └── cli.py                 # CLI entry point
├── specs/                         # Feature specifications
│   └── 001-deepagents-runner/
│       ├── spec.md                # Feature spec
│       ├── plan.md                # Implementation plan
│       ├── tasks.md               # Task breakdown
│       └── .state/                # Workflow state (auto-generated)
│           └── workflow.json
├── pyproject.toml
├── requirements.txt
└── README.md
```

## Architecture

### Context Detection

Automatically detects feature context from git branch:
- Pattern: `{feature_id}-{feature-name}` (e.g., `001-deepagents-runner`)
- Determines feature status from filesystem (draft → specified → planned → in_progress)

### State Persistence

Workflow state is persisted to `specs/{feature}/.state/workflow.json`:
- Current phase (draft, specify, plan, implement, etc.)
- Completed commands with timestamps
- Suggested next command
- Context data for command execution

### Agent Definitions

Agents are markdown files with YAML frontmatter:

```yaml
---
role: architect
name: archie-architect
specialization: system_architecture
capabilities:
  - architecture_design
  - component_design
priority: 10
---

You are Archie, a system architect specialized in...
```

## Development

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black src/
ruff check src/
```

## Example Workflows

### Basic Workflow

```bash
$ export ANTHROPIC_API_KEY=sk-ant-...
$ deepagents-runner

# See all available agents
> agents list

                                Available Agents
┏━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━┓
┃ Status ┃ Name                  ┃ Specialization      ┃ Capabilities  ┃ Priority┃
┡━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━┩
│   ✓    │ sam-security          │ security            │ security_d... │     10 │
│   ✓    │ archie-architect      │ system_architecture │ architectu... │     10 │
...

# Check out a specific agent
> agents show archie-architect

╭─────────────────────────────── Agent: archie-architect ───────────────────────╮
│   Name:            archie-architect                                           │
│   Role:            architect                                                  │
│   Specialization:  system_architecture                                        │
│   Capabilities:    architecture_design, component_design                      │
...

# Create a feature specification
> /speckit.specify Add a REST API for managing user profiles with CRUD operations

ℹ Executing: /speckit.specify

✓ Command completed: specify
ℹ Created: specs/001-user-profiles-api/spec.md

Preview:
# Feature Specification: User Profiles REST API

## Overview
This feature implements a RESTful API for managing user profiles...

... (truncated)

ℹ Suggested next: /plan

> /speckit.plan

ℹ Executing: /speckit.plan

✓ Command completed: plan
ℹ Created: specs/001-user-profiles-api/plan.md

ℹ Suggested next: /tasks

> /speckit.tasks

ℹ Executing: /speckit.tasks

✓ Command completed: tasks
ℹ Created: specs/001-user-profiles-api/tasks.md

ℹ Suggested next: /implement

# Disable an agent you don't need
> agents disable aria-ux-architect
✓ Disabled agent: aria-ux-architect
```

### Agent Management Workflow

```bash
# List all agents and their status
> agents list

# Disable agents you don't want to use
> agents disable molly-mobile
> agents disable donna-data-engineer

# Create a plan (will automatically select archie-architect)
> /speckit.plan

# Re-enable agents
> agents enable molly-mobile
```

## Available Agents (22 Total)

**Core Engineering:**
- archie-architect, bobby-backend, felicia-frontend, dana-database

**Quality & Security:**
- neil-test-engineer, sam-security, colin-code-reviewer, quinn-qa

**UX & Design:**
- aria-ux-architect, alex-accessibility

**Infrastructure:**
- derek-devops, iris-infrastructure, riley-reliability, monica-monitoring

**API & Integration:**
- andy-api-designer, ian-integration

**Data & Mobile:**
- donna-data-engineer, molly-mobile

**Documentation & Management:**
- diana-docs, pete-project-manager

**Fallback:**
- generic-agent

See `PHASE4_OPTION_A_UX.md` for detailed agent information.

## Development Status

### ✅ Completed Phases

**Phase 1: Setup** - Project structure, dependencies, agent definitions
**Phase 2: Foundational** - Core models, utilities, state management
**Phase 3: User Story 1 MVP** - LLM integration, command execution, configuration
**Phase 4: Agent Orchestration** - Automatic selection, retry logic, transparent UX

### Implementation Details:

1. ~~**Specialized Agent Delegation**~~ ✅ - Automatic command-to-agent mapping
2. ~~**Retry Logic**~~ ✅ - Exponential backoff (3 attempts + fallback)
3. ~~**Agent Management UI**~~ ✅ - All agent commands (list/show/enable/disable)
4. ~~**Wire Agents to Commands**~~ ✅ - All commands use orchestration
5. ~~**Transparent UX**~~ ✅ - Shows selected and used agents

See `PHASE4_COMPLETE.md` for detailed implementation documentation.

## License

MIT
