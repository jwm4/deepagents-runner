# deepagents-runner Development Guidelines

Auto-generated from all feature plans. Last updated: 2025-11-06

## Active Technologies

- Python 3.11+ + DeepAgents library, Anthropic SDK, OpenAI SDK, GitPython, Rich (terminal UI), Pydantic (data validation) (001-deepagents-runner)
- Python 3.11+ + markdown-it-py (spec parsing), Jinja2 (templates), pydantic-to-openapi3 (API contracts) (002-speckit-integration)

## Project Structure

```text
src/
├── speckit/           # SpecKit integration module (002-speckit-integration)
│   ├── commands/      # Slash command implementations
│   ├── core/          # Business logic (parsing, validation, clarification)
│   ├── models/        # Pydantic data models
│   ├── templates/     # Template management
│   ├── git/           # Git operations
│   └── utils/         # Utilities
tests/
├── unit/              # Unit tests for components
├── integration/       # Integration workflow tests
└── fixtures/          # Test fixtures
```

## Commands

cd src [ONLY COMMANDS FOR ACTIVE TECHNOLOGIES][ONLY COMMANDS FOR ACTIVE TECHNOLOGIES] pytest [ONLY COMMANDS FOR ACTIVE TECHNOLOGIES][ONLY COMMANDS FOR ACTIVE TECHNOLOGIES] ruff check .

## Code Style

Python 3.11+: Follow standard conventions

## Recent Changes

- 002-speckit-integration: Added markdown-it-py (spec parsing), Jinja2 (templates), pydantic-to-openapi3 (API contracts)
- 001-deepagents-runner: Added Python 3.11+ + DeepAgents library, Anthropic SDK, OpenAI SDK, GitPython, Rich (terminal UI), Pydantic (data validation)

<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
