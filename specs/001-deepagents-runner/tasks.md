# Tasks: DeepAgents Runner with SpecKit Integration

**Input**: Design documents from `/specs/001-deepagents-runner/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Tests are NOT explicitly requested in the feature specification, therefore test tasks are EXCLUDED from this task list. Implementation tasks only.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- Paths assume single project structure as defined in plan.md

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Create project directory structure: src/deepagents_runner/{core,terminal,llm,models,utils}, src/agents/, tests/{unit,integration,fixtures}, config/
- [X] T002 Initialize Python project with pyproject.toml and setup.py for package distribution
- [X] T003 [P] Create requirements.txt with dependencies: deepagents, anthropic, openai, rich, python-frontmatter, tenacity, gitpython, pydantic, pytest, pytest-asyncio
- [X] T004 [P] Create .gitignore for Python project (venv/, __pycache__/, *.pyc, .env, .state/)
- [X] T005 [P] Create config/.env.example with ANTHROPIC_API_KEY and OPENAI_API_KEY placeholders
- [X] T006 [P] Create src/deepagents_runner/__init__.py with package version and exports
- [X] T007 [P] Copy 21 agent definition markdown files from Ambient platform to src/agents/ directory

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T008 [P] Create src/deepagents_runner/models/__init__.py and define FeatureStatus, TaskStatus, ExecutionStatus, WorkflowPhase, CommandType, ProviderType enums
- [ ] T009 [P] Implement Feature model with validation in src/deepagents_runner/models/feature.py using Pydantic
- [ ] T010 [P] Implement WorkflowState model in src/deepagents_runner/models/workflow.py with JSON serialization
- [ ] T011 [P] Implement CommandExecution model in src/deepagents_runner/models/command.py
- [ ] T012 [P] Implement AgentAssignment and AgentOutput models in src/deepagents_runner/models/agent.py
- [ ] T013 [P] Implement LLMProviderConfiguration model in src/deepagents_runner/models/config.py
- [ ] T014 Create custom exception hierarchy (RunnerError, AgentError, CommandError, StateError, ProviderError) in src/deepagents_runner/utils/exceptions.py
- [ ] T015 Implement file operations utility in src/deepagents_runner/utils/files.py (read/write JSON with schema versioning, atomic writes, file locking)
- [ ] T016 Implement git operations utility in src/deepagents_runner/utils/git.py (get current branch, check if repo, list branches)
- [ ] T017 Implement retry utility with exponential backoff in src/deepagents_runner/utils/retry.py using tenacity library
- [ ] T018 Implement LLMProvider abstract base class in src/deepagents_runner/llm/base.py with generate() and stream_generate() methods
- [ ] T019 [P] Implement AnthropicProvider in src/deepagents_runner/llm/anthropic.py extending LLMProvider
- [ ] T020 [P] Implement OpenAIProvider in src/deepagents_runner/llm/openai.py extending LLMProvider
- [ ] T021 Implement LLMProviderFactory in src/deepagents_runner/llm/factory.py with create_provider() and get_default_provider() methods
- [ ] T022 Implement agent definition loader in src/deepagents_runner/core/agents.py to parse frontmatter markdown files from src/agents/
- [ ] T023 Implement StateManager in src/deepagents_runner/core/state.py with load/save workflow state, checkpointing, and file-based locking

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Execute SpecKit Command (Priority: P1) 🎯 MVP

**Goal**: Enable developers to launch the interactive terminal, execute SpecKit commands, and see real-time progress with agent activity

**Independent Test**: Launch runner on a feature branch, execute `/speckit.specify "add user authentication"`, verify it shows progress and creates spec.md file

### Implementation for User Story 1

- [ ] T024 [P] [US1] Implement ContextDetector in src/deepagents_runner/core/context.py with detect_feature_from_branch(), list_available_features(), and prompt_feature_selection()
- [ ] T025 [P] [US1] Implement TerminalUI in src/deepagents_runner/terminal/ui.py using Rich library for welcome screen, progress display, command output, and error messages
- [ ] T026 [US1] Implement REPLSession in src/deepagents_runner/terminal/repl.py with start(), read_command(), parse_command(), execute_command(), handle_error(), and shutdown()
- [ ] T027 [US1] Implement CommandExecutor base structure in src/deepagents_runner/core/commands.py with execute_command() dispatcher and event emission hooks
- [ ] T028 [US1] Implement execute_specify() in src/deepagents_runner/core/commands.py to create specification from user description
- [ ] T029 [US1] Implement execute_plan() in src/deepagents_runner/core/commands.py to generate implementation plan and research
- [ ] T030 [P] [US1] Implement execute_tasks() in src/deepagents_runner/core/commands.py to break down plan into tasks
- [ ] T031 [P] [US1] Implement execute_implement() in src/deepagents_runner/core/commands.py to execute task implementations
- [ ] T032 [P] [US1] Implement execute_clarify() in src/deepagents_runner/core/commands.py to resolve spec ambiguities
- [ ] T033 [US1] Implement execute_analyze() and execute_checklist() in src/deepagents_runner/core/commands.py for artifact analysis
- [ ] T034 [US1] Implement execute_constitution() in src/deepagents_runner/core/commands.py to create project principles
- [ ] T035 [US1] Create CLI entry point in src/cli.py that launches REPLSession with context detection and configuration loading
- [ ] T036 [US1] Add command-line argument parsing in src/cli.py for --provider, --feature, --help options
- [ ] T037 [US1] Implement configuration loading from environment variables and config files in src/deepagents_runner/core/config.py
- [ ] T038 [US1] Wire up TerminalUI progress updates to CommandExecutor events (command_started, command_progress, command_completed, command_failed)
- [ ] T039 [US1] Add error handling and graceful shutdown for Ctrl+C interrupts in REPLSession

**Checkpoint**: At this point, User Story 1 should be fully functional - can launch runner, execute commands, see basic progress

---

## Phase 4: User Story 2 - Delegate to Specialized Agents (Priority: P2)

**Goal**: Automatically route tasks to specialized Ambient agents based on capabilities, showing which agents are working in the terminal

**Independent Test**: Execute `/speckit.plan` on a feature with UX and architecture needs, verify both Archie Architect and Aria UX Architect are invoked and attributed in output

### Implementation for User Story 2

- [ ] T040 [US2] Implement AgentManager.load_agent_definitions() in src/deepagents_runner/core/agents.py to load all 21 agent markdown files with frontmatter metadata
- [ ] T041 [US2] Implement AgentManager.select_agents() in src/deepagents_runner/core/agents.py with capability-based scoring algorithm
- [ ] T042 [US2] Create task type to capability mappings in src/deepagents_runner/core/agents.py (specify→generic, plan→architecture, tasks→project_management, etc.)
- [ ] T043 [US2] Implement AgentManager.execute_agent() in src/deepagents_runner/core/agents.py using DeepAgent with LLM provider client and system prompt from agent definition
- [ ] T044 [US2] Add retry logic with exponential backoff to execute_agent() using tenacity, with fallback to generic agent on failure
- [ ] T045 [US2] Implement agent output attribution tracking in AgentOutput model to record which agent produced which content
- [ ] T046 [US2] Update TerminalUI to display active agents table with columns: Agent, Status, Task (using Rich Table)
- [ ] T047 [US2] Add agent event handlers (agent_started, agent_progress, agent_completed, agent_failed, agent_fallback) to update terminal UI
- [ ] T048 [US2] Update CommandExecutor to delegate command subtasks to AgentManager.select_agents() based on command type
- [ ] T049 [US2] Implement output merging logic in CommandExecutor to combine multiple agent outputs with clear attribution headers
- [ ] T050 [US2] Add conflict detection when multiple agents provide contradictory recommendations in command output
- [ ] T051 [US2] Implement most-specialized-agent-wins logic for conflict resolution based on agent priority scores
- [ ] T052 [US2] Update command output formatting to show agent attribution for each section (e.g., "Architecture (by Archie Architect)")

**Checkpoint**: At this point, User Stories 1 AND 2 should both work - commands execute with specialized agents and clear attribution

---

## Phase 5: User Story 3 - Multi-Step Workflow Coordination (Priority: P3)

**Goal**: Maintain context and state across multiple SpecKit commands in a workflow, enabling resume after interruption and context switching between features

**Independent Test**: Run `/speckit.constitution` → `/speckit.specify` → `/speckit.plan` sequence, verify each step references previous outputs and state persists across sessions

### Implementation for User Story 3

- [ ] T053 [P] [US3] Implement StateManager.load_workflow_state() in src/deepagents_runner/core/state.py to read workflow.json from .state/ directory
- [ ] T054 [P] [US3] Implement StateManager.save_workflow_state() in src/deepagents_runner/core/state.py with atomic writes and schema versioning
- [ ] T055 [US3] Implement StateManager.create_checkpoint() to save workflow state after each successful command completion
- [ ] T056 [US3] Implement StateManager.restore_checkpoint() to resume from last saved state after interruption
- [ ] T057 [US3] Implement StateManager.acquire_lock() and release_lock() using file-based locking to prevent concurrent execution on same feature
- [ ] T058 [US3] Add workflow state initialization in REPLSession.start() to load existing state or create new state for feature
- [ ] T059 [US3] Update CommandExecutor to persist command execution records in .state/command_history.json
- [ ] T060 [US3] Implement context.json persistence in StateManager to store feature metadata, LLM provider config, and agent cache
- [ ] T061 [US3] Add workflow phase tracking in WorkflowState (constitution → specify → clarify → plan → tasks → implement)
- [ ] T062 [US3] Implement suggested_next_command logic based on current workflow phase and completed commands
- [ ] T063 [US3] Display workflow state and suggested next command in terminal welcome screen
- [ ] T064 [US3] Implement /status command in REPLSession to show current workflow state, completed commands, and suggested next steps
- [ ] T065 [US3] Implement /switch command in REPLSession to change active feature context (save current state, load new feature state)
- [ ] T066 [US3] Add feature isolation by storing separate .state/ directories per feature under specs/{feature}/.state/
- [ ] T067 [US3] Implement constitution loading in CommandExecutor commands to reference project principles when they exist
- [ ] T068 [US3] Add context passing between commands (e.g., pass spec.md content to /speckit.plan, pass plan.md to /speckit.tasks)
- [ ] T069 [US3] Implement checkpoint restoration on startup if previous command was interrupted (detect incomplete state)

**Checkpoint**: All workflow coordination features should work - state persists, context maintained, resume works, feature switching works

---

## Phase 6: User Story 4 - Progress Tracking and Visibility (Priority: P4)

**Goal**: Provide detailed real-time visibility into agent activity, progress tracking, and completion estimates during long-running commands

**Independent Test**: Execute `/speckit.implement` on a multi-task feature, verify progress percentage, active agents list, and completion time estimates are displayed and updated in real-time

### Implementation for User Story 4

- [ ] T070 [P] [US4] Implement AgentManager.execute_agents_parallel() in src/deepagents_runner/core/agents.py using asyncio task groups with dependency tracking
- [ ] T071 [US4] Add progress tracking to CommandExecution model (progress float 0.0-1.0, started_at, completed_at, duration_seconds)
- [ ] T072 [US4] Implement progress calculation logic in CommandExecutor based on completed subtasks vs total subtasks
- [ ] T073 [US4] Update TerminalUI with Rich Progress bars showing overall command progress and individual agent progress
- [ ] T074 [US4] Add real-time status emoji updates to agent status display (🔄 Working, ✅ Complete, ⚠️ Retry, 🔀 Fallback, ⏳ Waiting, ❌ Error)
- [ ] T075 [US4] Implement completion time estimation based on average task duration and remaining tasks
- [ ] T076 [US4] Add agent activity logging to .state/command_history.json with timestamps, agent names, tasks, and status
- [ ] T077 [US4] Implement live update mechanism in TerminalUI using Rich Live display to refresh progress table every 0.25s
- [ ] T078 [US4] Add error notification display when agent encounters error (show error message in terminal with agent name and task)
- [ ] T079 [US4] Implement agent activity log viewer (display at command completion showing all agent activities and decisions)
- [ ] T080 [US4] Add progress update events every 2 seconds during long-running operations to meet SC-012 (<2s feedback) requirement
- [ ] T081 [US4] Implement parallel execution visualization showing which agents are working simultaneously
- [ ] T082 [US4] Add dependency waiting visualization (show which agents are waiting for which prerequisites)

**Checkpoint**: All user stories should now be independently functional with comprehensive progress tracking and visibility

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories, documentation, and deployment readiness

- [ ] T083 [P] Create comprehensive README.md with installation, configuration, and usage instructions
- [ ] T084 [P] Create CONTRIBUTING.md with development setup and contribution guidelines
- [ ] T085 [P] Add inline code documentation (docstrings) to all public methods following Google Python style
- [ ] T086 [P] Create package distribution files (pyproject.toml, setup.py, MANIFEST.in) for PyPI publishing
- [ ] T087 [P] Create example agent definition file template in docs/examples/custom-agent-template.md
- [ ] T088 Add input validation and sanitization for all user commands in REPLSession.parse_command()
- [ ] T089 Implement comprehensive logging throughout all modules using Python logging library with configurable log levels
- [ ] T090 Add performance monitoring to track command execution times and identify bottlenecks
- [ ] T091 Implement graceful degradation when LLM provider is unavailable (clear error messages, suggestions to check API keys)
- [ ] T092 Add rate limit handling with automatic backoff when provider rate limits are hit
- [ ] T093 Optimize parallel agent execution to achieve 40% performance improvement target (SC-005)
- [ ] T094 Add memory management for large specifications using DeepAgents filesystem middleware
- [ ] T095 Implement security checks to prevent command injection or path traversal attacks
- [ ] T096 Add telemetry (optional, opt-in) to collect anonymous usage statistics for improvement
- [ ] T097 Create troubleshooting guide in docs/TROUBLESHOOTING.md with common issues and solutions
- [ ] T098 Run through quickstart.md end-to-end validation on clean environment
- [ ] T099 Create demo video or animated GIF showing typical workflow for README
- [ ] T100 Tag v1.0.0 release and publish to PyPI

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion
  - User Story 1 (P1): Can start after Foundational - No dependencies on other stories
  - User Story 2 (P2): Can start after Foundational - No dependencies on other stories
  - User Story 3 (P3): Can start after Foundational - Builds on US1 but independently testable
  - User Story 4 (P4): Can start after Foundational - Enhances US1/US2 but independently testable
- **Polish (Phase 7)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: MVP - Basic command execution and terminal UI
- **User Story 2 (P2)**: Independent - Adds agent specialization on top of US1
- **User Story 3 (P3)**: Integrates with US1 - Adds state persistence and workflow coordination
- **User Story 4 (P4)**: Enhances US1/US2 - Adds detailed progress tracking

### Within Each User Story

- Models before services
- Services before commands
- Core implementation before UI integration
- Story complete before moving to next priority

### Parallel Opportunities

**Phase 1 (Setup)**:
- T003, T004, T005, T006, T007 can all run in parallel (different files)

**Phase 2 (Foundational)**:
- T008-T012 (models) can run in parallel
- T019-T020 (provider implementations) can run in parallel after T018
- T024 (context detector) can run in parallel with other foundational work

**Within User Stories**:
- US1: T030, T031, T032 can run in parallel (different command implementations)
- US2: T040-T043 can run in parallel initially, then T046-T052 need coordination
- US3: T053-T054 can run in parallel, T066 can run parallel with others
- US4: T070, T074 can run in parallel

**Cross-Story Parallelization**:
- With multiple developers, US1, US2, US3, US4 can be worked on in parallel after Phase 2 completes
- However, recommended to do US1 first for MVP validation

---

## Parallel Example: User Story 1

```bash
# These tasks can start simultaneously after Phase 2:
T024: "Implement ContextDetector in src/deepagents_runner/core/context.py"
T025: "Implement TerminalUI in src/deepagents_runner/terminal/ui.py"

# These command implementations can run in parallel:
T030: "Implement execute_tasks() in src/deepagents_runner/core/commands.py"
T031: "Implement execute_implement() in src/deepagents_runner/core/commands.py"
T032: "Implement execute_clarify() in src/deepagents_runner/core/commands.py"
```

---

## Parallel Example: User Story 2

```bash
# These tasks can start simultaneously:
T040: "Load agent definitions in src/deepagents_runner/core/agents.py"
T046: "Update TerminalUI to display active agents table"

# After agent selection is implemented, these can run in parallel:
T048: "Update CommandExecutor to delegate to specialized agents"
T050: "Add conflict detection for contradictory recommendations"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T007)
2. Complete Phase 2: Foundational (T008-T023) - **CRITICAL**
3. Complete Phase 3: User Story 1 (T024-T039)
4. **STOP and VALIDATE**: Test that you can launch runner, execute commands, see progress
5. Deploy/demo basic working version

**MVP Delivery**: At this point you have a working interactive terminal that executes SpecKit commands with basic progress display. This is independently valuable.

### Incremental Delivery

1. **Foundation** (Phases 1-2): T001-T023 → Project initialized, models ready
2. **MVP** (Phase 3): T024-T039 → Basic command execution working
   - Deploy/Demo: Developers can use runner for SpecKit workflow
3. **Specialization** (Phase 4): T040-T052 → Specialized agents routing
   - Deploy/Demo: Higher quality outputs with expert agents
4. **Workflow** (Phase 5): T053-T069 → State persistence and coordination
   - Deploy/Demo: Can resume workflows, switch features
5. **Visibility** (Phase 6): T070-T082 → Advanced progress tracking
   - Deploy/Demo: Full transparency into agent activity
6. **Polish** (Phase 7): T083-T100 → Production ready
   - Deploy/Demo: PyPI published, documented, secure

Each increment adds value without breaking previous functionality.

### Parallel Team Strategy

With multiple developers after Phase 2 completes:

1. **Team completes Setup + Foundational together** (T001-T023)
2. **Once Foundational is done, split work**:
   - **Developer A**: User Story 1 (T024-T039) - Core terminal and commands
   - **Developer B**: User Story 2 (T040-T052) - Agent specialization
   - **Developer C**: User Story 3 (T053-T069) - State and workflow
   - **Developer D**: User Story 4 (T070-T082) - Progress tracking
3. **Stories integrate and test independently**
4. **Team reconvenes for Phase 7 polish**

---

## Task Statistics

- **Total Tasks**: 100
- **Setup Phase**: 7 tasks
- **Foundational Phase**: 16 tasks
- **User Story 1 (P1)**: 16 tasks
- **User Story 2 (P2)**: 13 tasks
- **User Story 3 (P3)**: 17 tasks
- **User Story 4 (P4)**: 13 tasks
- **Polish Phase**: 18 tasks

**Parallel Opportunities**: 35 tasks marked [P] can run in parallel within their phase
**MVP Scope**: Phases 1-3 (39 tasks) delivers basic working runner
**Full Feature Scope**: All 100 tasks for complete implementation

---

## Notes

- [P] tasks = different files, no dependencies within phase
- [Story] label maps task to specific user story (US1, US2, US3, US4) for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Tests are not included per specification - implementation tasks only
- Validate quickstart.md instructions work as part of final testing

---

## Validation Checklist

Before marking complete, verify:

- [ ] All 100 tasks follow correct checklist format (checkbox, ID, labels, file paths)
- [ ] Each user story has independent test criteria defined
- [ ] Dependencies are clearly mapped between phases and stories
- [ ] Parallel opportunities identified with [P] markers
- [ ] MVP scope is clearly defined (Phases 1-3)
- [ ] File paths match plan.md project structure
- [ ] No circular dependencies between tasks
- [ ] Each task is specific enough for LLM to execute without additional context
