# Research & Technology Decisions: SpecKit Integration

**Feature**: 002-speckit-integration
**Date**: 2025-11-06
**Phase**: 0 - Research & Decision Making

## Overview

This document captures research decisions made during the planning phase for integrating original SpecKit functionality into DeepAgents Runner. All technical unknowns from the Technical Context have been researched and resolved.

---

## Decision 1: Spec Parsing and Manipulation Library

**Context**: Need to parse, manipulate, and update Markdown spec files programmatically for interactive clarification workflow.

**Decision**: Use `markdown-it-py` with custom extensions for structured section parsing

**Rationale**:
- `markdown-it-py` is a Python port of the popular markdown-it library
- Provides AST (Abstract Syntax Tree) for precise manipulation
- Extensible plugin system for custom parsing rules
- Active maintenance and good performance
- Can handle CommonMark + GFM (GitHub Flavored Markdown) tables
- Supports incremental updates without full file rewrites

**Alternatives Considered**:
1. **mistletoe** - Good parser but limited manipulation capabilities
2. **python-markdown** - Mature but designed for HTML conversion, not manipulation
3. **marko** - Newer, less battle-tested, smaller community
4. **Custom regex-based parser** - Rejected due to fragility with edge cases and Markdown variants

**Implementation Notes**:
- Use `markdown-it-py` for parsing spec structure into sections
- Build custom walker to locate and update specific sections (Clarifications, Requirements, etc.)
- Preserve formatting by tracking original positions and doing surgical edits
- Add validation layer to ensure Markdown structure integrity after updates

---

## Decision 2: Git Operations Library

**Context**: Need to reimplement bash script git operations (branch creation, feature numbering, status checking) in pure Python.

**Decision**: Use `GitPython` library

**Rationale**:
- GitPython is the de facto standard for Git operations in Python
- Already listed as a dependency in the project (from CLAUDE.md)
- Comprehensive API covering all needed operations:
  - Branch creation and switching
  - Remote branch listing
  - Working tree status
  - Commit operations
- Well-documented with extensive examples
- Active maintenance and wide adoption
- Cross-platform compatibility

**Alternatives Considered**:
1. **subprocess with git commands** - More fragile, harder to test, platform-dependent
2. **dulwich** - Pure Python Git implementation, but less Pythonic API and incomplete feature coverage
3. **pygit2** - Fast but requires libgit2 C library, adding installation complexity

**Implementation Notes**:
- Wrap GitPython in our own `src/speckit/git/` module for cleaner APIs
- Implement feature branch discovery by listing branches with regex patterns
- Handle non-git repositories gracefully (check `.git` directory existence first)
- Add retry logic for network operations (fetch, remote operations)

---

## Decision 3: Interactive CLI Framework

**Context**: Need to present sequential questions with tables, collect user answers, and provide rich terminal output during clarification workflow.

**Decision**: Use `Rich` library for terminal UI

**Rationale**:
- Rich is already a project dependency (from CLAUDE.md)
- Excellent support for formatted tables (needed for clarification options)
- Markdown rendering capabilities for displaying question context
- Progress indicators and spinners for long operations
- Color and styling for better UX (success/error/warning states)
- Prompt support via `rich.prompt` for input collection
- Cross-platform terminal compatibility

**Alternatives Considered**:
1. **prompt_toolkit** - More powerful but heavier, overkill for our needs
2. **click** - Great for CLI apps but limited rich formatting
3. **questionary** - Good for prompts but no table/markdown rendering
4. **simple-term-menu** - Limited to menus, doesn't support tables

**Implementation Notes**:
- Use `rich.table.Table` for clarification option presentation
- Use `rich.prompt.Prompt` for answer collection with validation
- Use `rich.console.Console` for status updates and progress
- Implement custom `ask_clarification_question()` wrapper combining table + prompt
- Support both interactive mode and non-interactive mode (for testing)

---

## Decision 4: Data Validation and Models

**Context**: Need structured data models for specs, clarifications, artifacts, tasks, findings, checklists, and constitution principles.

**Decision**: Use `Pydantic` v2 for data validation

**Rationale**:
- Pydantic is already a project dependency (from CLAUDE.md)
- Type-safe data validation with Python type hints
- Automatic JSON serialization/deserialization
- Excellent error messages for validation failures
- Performance optimizations in v2 (Rust core)
- Integration with FastAPI-style patterns
- Support for custom validators and computed fields

**Alternatives Considered**:
1. **dataclasses** - Native but no validation
2. **attrs** - Good but less modern than Pydantic
3. **marshmallow** - More verbose, Flask-centric
4. **Custom validation** - Reinventing the wheel

**Implementation Notes**:
- Define models in `src/speckit/models/` with Pydantic BaseModel
- Use Field() for validation constraints (min_length, max_length, regex)
- Add custom validators for Markdown content validation
- Use model_dump() and model_validate() for serialization
- Leverage discriminated unions for polymorphic artifact types

---

## Decision 5: API Contract Generation

**Context**: Need to auto-detect appropriate API format and generate OpenAPI or GraphQL schemas based on spec content analysis.

**Decision**: Use `pydantic-to-openapi3` for OpenAPI generation, skip GraphQL initially

**Rationale**:
- Auto-detection logic: Default to OpenAPI (simpler, more widely adopted)
- OpenAPI 3.0 is sufficient for most CRUD-style APIs described in specs
- `pydantic-to-openapi3` generates schemas from existing Pydantic models
- GraphQL is more complex and less commonly needed
- Can add GraphQL support later if usage patterns emerge

**Alternatives Considered**:
1. **Manual template-based generation** - Too rigid, hard to maintain
2. **swagger-py-codegen** - Outdated, not actively maintained
3. **apispec** - Good but requires manual schema definition
4. **Full GraphQL support upfront** - Premature optimization, adds complexity

**Implementation Notes**:
- Build detection heuristics: Analyze user stories and functional requirements
- Look for patterns: "subscribe", "real-time", "stream" → future GraphQL consideration
- Default to REST/OpenAPI for standard CRUD patterns
- Generate OpenAPI schema with:
  - Paths extracted from user actions (e.g., "create account" → POST /accounts)
  - Request/response models from data entities
  - Standard HTTP methods (GET, POST, PUT, DELETE, PATCH)
  - Authentication schemes inferred from security requirements
- Store generated schemas in `specs/{feature}/contracts/` as YAML files

---

## Decision 6: Template Management

**Context**: Need to load and populate templates from `.specify/templates/` directory.

**Decision**: Use `jinja2` for template rendering

**Rationale**:
- Industry-standard Python templating engine
- Powerful template inheritance and include system
- Control flow (if/for) for conditional content
- Filters and custom functions for formatting
- Can render both Markdown and YAML templates
- Widely used and well-documented

**Alternatives Considered**:
1. **string.Template** - Too basic, no control flow
2. **mako** - Powerful but more complex than needed
3. **Custom template system** - Unnecessary reinvention
4. **f-strings** - Not suitable for complex templates with conditionals

**Implementation Notes**:
- Load templates from `.specify/templates/` directory
- Create template loader in `src/speckit/templates/loader.py`
- Define custom filters for Markdown formatting (heading levels, list formatting)
- Support template inheritance for common spec sections
- Cache compiled templates for performance

---

## Decision 7: Testing Strategy

**Context**: Need comprehensive testing for spec generation workflows.

**Decision**: Use `pytest` with fixtures and parametrization

**Rationale**:
- pytest is already specified as the testing framework (from Technical Context)
- Excellent fixture support for complex test setup
- Parametrization for testing multiple scenarios
- Rich plugin ecosystem (pytest-cov, pytest-asyncio if needed)
- Better assertion introspection than unittest
- Widely adopted Python testing standard

**Testing Approach**:
- **Unit tests**: Test individual components (parsers, validators, generators)
- **Integration tests**: Test complete workflows (specify, clarify, plan)
- **Fixtures**: Sample specs, plans, tasks in `tests/fixtures/`
- **Parametrization**: Test edge cases with multiple inputs
- **Mocking**: Mock LLM calls for deterministic tests
- **Coverage target**: 80%+ for core business logic

**Implementation Notes**:
- Create sample spec fixtures representing different feature types
- Mock GitPython for git operation tests
- Use `tmp_path` fixture for file operation tests
- Test clarification workflow with predefined Q&A pairs
- Validate generated artifacts against expected structure

---

## Decision 8: Logging and Observability

**Context**: Need logging for debugging, warning for missing constitution, and operation tracking.

**Decision**: Use Python's `logging` module with `Rich` handler

**Rationale**:
- Standard library logging is sufficient for CLI application
- Rich provides RichHandler for beautiful formatted logs
- Structured logging with context (feature ID, session ID)
- Configurable log levels (DEBUG for development, INFO for production)
- File and console logging support
- No additional dependencies needed

**Implementation Notes**:
- Configure logging in `src/speckit/utils/logger.py`
- Use RichHandler for console output with syntax highlighting
- Add file handler for persistent logs in `.specify/logs/`
- Include context in log messages (feature branch, command, user)
- Log levels:
  - DEBUG: Detailed operation traces
  - INFO: Workflow progress updates
  - WARNING: Missing constitution, skipped checks
  - ERROR: Validation failures, file errors
  - CRITICAL: Gate failures, corruption issues

---

## Summary

All technical unknowns from the Technical Context have been resolved:

| Unknown | Decision |
|---------|----------|
| Spec parsing/manipulation library | markdown-it-py with custom extensions |
| Git operations | GitPython (already a dependency) |
| Interactive CLI | Rich (already a dependency) |
| Data models | Pydantic v2 (already a dependency) |
| API contract generation | pydantic-to-openapi3 for OpenAPI schemas |
| Template management | Jinja2 templating engine |
| Testing framework | pytest (already specified) |
| Logging | Standard logging with Rich handler |

**Dependencies to Add**:
- `markdown-it-py` - Markdown parsing and manipulation
- `jinja2` - Template rendering
- `pydantic-to-openapi3` - OpenAPI schema generation

**Existing Dependencies Confirmed**:
- `GitPython` - Git operations
- `Rich` - Terminal UI
- `Pydantic` - Data validation
- `pytest` - Testing

**Next Phase**: Proceed to Phase 1 (Design & Contracts) to generate data-model.md, contracts/, and quickstart.md.
