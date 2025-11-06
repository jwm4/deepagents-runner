# Implementation Plan: DeepAgents Runner with SpecKit Integration

**Branch**: `001-deepagents-runner` | **Date**: 2025-11-05 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-deepagents-runner/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Build an interactive terminal application that executes SpecKit commands (constitution, specify, plan, tasks, implement, clarify, analyze, checklist) using the DeepAgents library for agent orchestration. The runner delegates tasks to 21 specialized Ambient agents (bundled as markdown definitions), supports configurable LLM providers (Anthropic Claude, OpenAI GPT), maintains workflow state across multi-step processes, and provides real-time progress visibility. The system auto-detects feature context from git branches, persists state as JSON files, and implements resilient failure handling with retry and fallback mechanisms.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: DeepAgents library, Anthropic SDK, OpenAI SDK, GitPython, Rich (terminal UI), Pydantic (data validation)
**Storage**: File-based (JSON state files in `.state/` subdirectories, markdown for specs/plans/tasks)
**Testing**: pytest (unit tests), pytest-asyncio (async tests), integration tests with real LLM APIs
**Target Platform**: Cross-platform terminal application (macOS, Linux, Windows with WSL)
**Project Type**: Single CLI application with library core
**Performance Goals**: Command execution <5 min for simple features, progress updates within 2s, support 5 concurrent workflows
**Constraints**: <30s agent failure detection, exponential backoff for retries, 100% context preservation across commands
**Scale/Scope**: 7 core SpecKit commands, 21 agent definitions, support for 100+ requirement features

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Status**: No constitution file defined yet - proceeding with standard best practices:
- Library-first architecture (core logic separate from CLI)
- Test coverage for critical paths
- Clear separation of concerns
- Minimal external dependencies
- Configuration via environment variables

✅ **Gate Status**: PASS (using default best practices)

## Project Structure

### Documentation (this feature)

```text
specs/001-deepagents-runner/
├── spec.md              # Feature specification
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
│   └── runner-api.yaml  # Internal component contracts
├── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
└── checklists/
    └── requirements.md  # Quality checklist
```

### Source Code (repository root)

```text
src/
├── deepagents_runner/
│   ├── __init__.py
│   ├── core/                    # Core business logic
│   │   ├── __init__.py
│   │   ├── agents.py            # Agent management and delegation
│   │   ├── commands.py          # SpecKit command implementations
│   │   ├── state.py             # Workflow state persistence
│   │   ├── context.py           # Feature context detection
│   │   └── config.py            # LLM provider configuration
│   ├── terminal/                # Terminal interface layer
│   │   ├── __init__.py
│   │   ├── repl.py              # Interactive REPL loop
│   │   ├── ui.py                # Progress display and formatting
│   │   └── session.py           # Session management
│   ├── llm/                     # LLM provider integrations
│   │   ├── __init__.py
│   │   ├── base.py              # Abstract provider interface
│   │   ├── anthropic.py         # Anthropic Claude provider
│   │   ├── openai.py            # OpenAI GPT provider
│   │   └── factory.py           # Provider factory
│   ├── models/                  # Data models
│   │   ├── __init__.py
│   │   ├── feature.py           # Feature entity
│   │   ├── workflow.py          # Workflow state
│   │   ├── command.py           # Command execution
│   │   └── agent.py             # Agent assignment and output
│   └── utils/                   # Utilities
│       ├── __init__.py
│       ├── git.py               # Git operations
│       ├── files.py             # File system operations
│       └── retry.py             # Retry logic with exponential backoff
├── cli.py                       # CLI entry point
└── agents/                      # Bundled Ambient agent definitions
    ├── archie-architect.md
    ├── aria-ux-architect.md
    ├── casey-content-strategist.md
    ├── dan-senior-director.md
    ├── diego-program-manager.md
    ├── emma-engineering-manager.md
    ├── felix-ux-feature-lead.md
    ├── jack-delivery-owner.md
    ├── lee-team-lead.md
    ├── neil-test-engineer.md
    ├── olivia-product-owner.md
    ├── parker-product-manager.md
    ├── phoenix-pxe-specialist.md
    ├── ryan-ux-researcher.md
    ├── sam-scrum-master.md
    ├── stella-staff-engineer.md
    ├── steve-ux-designer.md
    ├── taylor-team-member.md
    ├── terry-technical-writer.md
    ├── tessa-writing-manager.md
    └── uma-ux-team-lead.md

tests/
├── unit/                        # Unit tests
│   ├── test_agents.py
│   ├── test_commands.py
│   ├── test_state.py
│   ├── test_context.py
│   ├── test_config.py
│   └── test_llm_providers.py
├── integration/                 # Integration tests
│   ├── test_full_workflow.py   # End-to-end workflow tests
│   ├── test_agent_delegation.py
│   └── test_state_persistence.py
└── fixtures/                    # Test fixtures
    ├── sample_specs/
    └── mock_agent_outputs/

config/
└── .env.example                 # Example environment variables
```

**Structure Decision**: Single project structure chosen because:
- This is a standalone CLI tool, not a web/mobile application
- Core logic (deepagents_runner/) is library-like and importable
- Clear separation between core logic, terminal UI, and LLM integrations
- Agent definitions bundled as data files alongside code
- Standard Python project layout enables easy packaging and distribution

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations - constitution not yet defined. Using standard best practices.
