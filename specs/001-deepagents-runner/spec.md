# Feature Specification: DeepAgents Runner with SpecKit Integration

**Feature Branch**: `001-deepagents-runner`
**Created**: 2025-11-05
**Status**: Draft
**Input**: User description: "Make an agent runner using https://github.com/langchain-ai/deepagents that implements the speckit commands in https://github.com/github/spec-kit and provides access to the agents in https://github.com/ambient-code/platform/tree/main/agents"

## Clarifications

### Session 2025-11-05

- Q: Where should LLM provider API credentials and configuration be stored? → A: User manages API keys via environment variables or config file outside the runner, with standard naming conventions (ANTHROPIC_API_KEY, OPENAI_API_KEY)
- Q: How should workflow state and context be persisted between command executions? → A: Store workflow state as JSON files in the feature directory (specs/[number]-[feature-name]/.state/)
- Q: What is the recovery strategy when an agent fails or times out? → A: Retry failed agent once with exponential backoff, then fall back to a generic agent if specialized agent unavailable
- Q: How should terminal sessions determine which feature context to use on launch? → A: Auto-detect feature from current git branch (if matches pattern [number]-[feature-name]), otherwise prompt user to select
- Q: How should the system resolve conflicts when multiple agents provide contradictory recommendations? → A: Flag conflicts, show both recommendations with agent attribution, use most specialized agent's output as default

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Execute SpecKit Command (Priority: P1)

A developer launches the interactive terminal, types a SpecKit command (such as `/speckit.specify`, `/speckit.plan`, or `/speckit.implement`), and sees real-time progress as agents work to generate results.

**Why this priority**: This is the core functionality - without the ability to execute commands in an interactive session, the runner has no value. This represents the minimal viable product.

**Independent Test**: Can be fully tested by launching the terminal, typing `/speckit.specify "add user authentication"`, and verifying that it shows progress updates and returns a valid specification document. Delivers immediate value by enabling spec-driven development.

**Acceptance Scenarios**:

1. **Given** a developer is on a feature branch (e.g., 001-deepagents-runner) and launches the runner, **When** the terminal loads, **Then** the system auto-detects and displays the feature context, allowing immediate command execution
1a. **Given** a developer is on a non-feature branch (e.g., main) and launches the runner, **When** the terminal loads, **Then** the system prompts them to select from available features
2. **Given** a developer launches the runner in their terminal, **When** they type `/speckit.specify "feature description"` and press enter, **Then** the system shows real-time progress and returns a complete feature specification document
3. **Given** a developer is in an active terminal session with a created specification, **When** they type `/speckit.plan`, **Then** the system shows which agents are working on planning and returns a detailed implementation plan
4. **Given** a developer types an invalid command in the terminal, **When** they press enter, **Then** they receive a clear error message explaining what went wrong
5. **Given** a developer executes a command that takes significant time, **When** the command is running, **Then** they see live updates showing which agents are active and what tasks they are working on

---

### User Story 2 - Delegate to Specialized Agents (Priority: P2)

A developer executes a SpecKit command that requires specialized expertise (architecture, UX design, testing, etc.), and the runner automatically delegates subtasks to appropriate Ambient agents (e.g., Archie Architect, Steve UX Designer, Neil Test Engineer).

**Why this priority**: This unlocks the power of specialized agents, providing expert-level outputs for different aspects of software development. Significantly improves quality over generic responses.

**Independent Test**: Can be tested by executing `/speckit.plan` on a feature that requires both architecture and UX considerations, then verifying that both Archie Architect and Aria UX Architect were consulted. Delivers value through higher-quality, specialized outputs.

**Acceptance Scenarios**:

1. **Given** a feature specification requiring architectural decisions, **When** `/speckit.plan` executes, **Then** Archie Architect agent is consulted for architecture guidance
2. **Given** a feature specification with UX components, **When** `/speckit.plan` executes, **Then** Aria UX Architect and Steve UX Designer agents provide UX recommendations
3. **Given** a complex task requiring multiple specialties, **When** the command executes, **Then** multiple specialized agents work together and their outputs are coordinated
4. **Given** a developer views command results, **When** examining the output, **Then** they can see which agents contributed to each section

---

### User Story 3 - Multi-Step Workflow Coordination (Priority: P3)

A developer executes a complete SpecKit workflow (from constitution through implementation), and the runner coordinates multiple agents across commands while maintaining context and state.

**Why this priority**: Enables end-to-end spec-driven development with continuity across the entire workflow. Critical for complex projects but can be partially achieved through sequential individual commands.

**Independent Test**: Can be tested by running the full sequence: `/speckit.constitution` → `/speckit.specify` → `/speckit.plan` → `/speckit.tasks` → `/speckit.implement`, then verifying each step references outputs from previous steps. Delivers value through seamless workflow automation.

**Acceptance Scenarios**:

1. **Given** a developer has created a project constitution, **When** they run `/speckit.specify`, **Then** the specification reflects principles from the constitution
2. **Given** a developer has a specification and plan, **When** they run `/speckit.tasks`, **Then** tasks are generated that align with the plan's architecture
3. **Given** a workflow is interrupted, **When** the developer resumes later, **Then** the runner maintains context from previous steps
4. **Given** multiple features are being developed, **When** a developer switches between features, **Then** each feature maintains its own independent context

---

### User Story 4 - Progress Tracking and Visibility (Priority: P4)

A developer running a long-running SpecKit command can monitor agent activity, see which agents are working on what, and track overall progress toward completion.

**Why this priority**: Improves developer experience and enables intervention if needed, but the core functionality works without it. Nice-to-have for transparency and debugging.

**Independent Test**: Can be tested by executing `/speckit.implement` on a multi-task feature, then querying the system for status while it runs. Delivers value through visibility and control.

**Acceptance Scenarios**:

1. **Given** a command is executing, **When** a developer checks status, **Then** they see a list of active agents and their current tasks
2. **Given** multiple tasks are in progress, **When** a developer views the dashboard, **Then** they see completion percentage and estimated time remaining
3. **Given** an agent encounters an error, **When** the error occurs, **Then** the developer is notified immediately with details
4. **Given** a command completes, **When** the developer reviews results, **Then** they see a log of all agent activities and decisions made

---

### Edge Cases

- **Agent failure or timeout**: System retries the failed agent once with exponential backoff (e.g., wait 2s, then 4s). If still failing, falls back to a generic agent to complete the task. User is notified of the fallback.
- **Missing agent specialization**: If a command requires an agent type not in the bundled set, the system uses the closest available agent or a generic agent and logs a warning.
- **Concurrent execution on same feature**: System prevents concurrent command execution on the same feature through file-based locking to avoid state conflicts.
- **Large specifications or codebases**: System uses DeepAgents' filesystem middleware to manage context overflow by storing intermediate results in the .state/ directory.
- **Conflicting agent outputs**: System flags conflicts in the output, displays all conflicting recommendations with clear agent attribution (FR-020), and automatically applies the most specialized agent's recommendation as the default (e.g., Archie Architect's architectural advice takes precedence over a generalist). Users can see alternative recommendations and override if needed.
- **Partial failures**: Some agents succeed while others fail, fallback agents are used for failed tasks, workflow continues to completion with degraded quality noted in logs.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST support execution of all core SpecKit commands when requested by the user: `/speckit.constitution`, `/speckit.specify`, `/speckit.plan`, `/speckit.tasks`, `/speckit.implement`
- **FR-002**: System MUST support execution of optional SpecKit commands when requested by the user: `/speckit.clarify`, `/speckit.analyze`, `/speckit.checklist`
- **FR-003**: System MUST suggest appropriate next steps in the workflow based on current feature state, but allow users to choose which commands to execute
- **FR-004**: System MUST support Anthropic Claude models as an LLM provider for agent inference
- **FR-005**: System MUST support OpenAI GPT models as an LLM provider for agent inference
- **FR-006**: System MUST allow users to configure which LLM provider to use via environment variables (ANTHROPIC_API_KEY, OPENAI_API_KEY) or external configuration files
- **FR-007**: System MUST provide an extensible configuration mechanism to support additional LLM providers in the future (e.g., vLLM, local models)
- **FR-008**: System MUST provide an interactive terminal interface where users can type SpecKit commands and see results in real-time
- **FR-009**: System MUST auto-detect the active feature context from the current git branch name (matching pattern [number]-[feature-name]), or prompt user to select a feature if on a non-feature branch
- **FR-010**: System MUST accept SpecKit commands in the terminal using slash command syntax (e.g., `/speckit.specify "feature description"`)
- **FR-011**: System MUST display real-time progress updates during command execution in the terminal
- **FR-012**: System MUST show which agents are currently active and what they are working on during command execution
- **FR-013**: System MUST provide access to all 21 Ambient platform agents for task delegation
- **FR-014**: System MUST automatically select appropriate agents based on task requirements (e.g., Archie Architect for architecture tasks, Neil Test Engineer for testing tasks)
- **FR-015**: System MUST maintain context across multi-step workflows within a single feature
- **FR-016**: System MUST persist feature state (specifications, plans, tasks) and workflow context as JSON files in the feature directory (.state/ subdirectory) between command executions
- **FR-017**: System MUST handle agent failures gracefully by retrying once with exponential backoff, then falling back to a generic agent if the specialized agent remains unavailable, without stopping the entire workflow
- **FR-018**: System MUST support parallel agent execution when tasks are independent
- **FR-019**: System MUST handle conflicts when agents provide contradictory recommendations by flagging them, showing all recommendations with agent attribution, and using the most specialized agent's output as the default
- **FR-020**: Users MUST be able to see which agents contributed to each output section
- **FR-021**: System MUST validate command inputs before execution and provide clear error messages for invalid inputs
- **FR-022**: System MUST support resuming interrupted workflows from the last successful checkpoint
- **FR-023**: System MUST isolate context between different features being developed simultaneously
- **FR-024**: System MUST log all agent activities, decisions, and outputs for audit and debugging purposes

### Key Entities *(include if feature involves data)*

- **Feature**: Represents a software feature being developed, containing specification, plan, tasks, and implementation status. Links to a feature branch and spec directory.
- **Specification**: Document defining what a feature should do, including user scenarios, requirements, success criteria, and key entities. Created by `/speckit.specify` command.
- **Implementation Plan**: Technical design document detailing architecture, components, dependencies, and technical approach. Created by `/speckit.plan` command.
- **Task**: An actionable, atomic work item with description, dependencies, assigned agent, and completion status. Created by `/speckit.tasks` command.
- **Agent Assignment**: Links a task or command component to a specific Ambient agent (e.g., Archie Architect, Steve UX Designer) responsible for executing it.
- **Command Execution**: Represents a single SpecKit command invocation with input parameters, execution status, progress tracking, and output artifacts.
- **Workflow State**: Tracks the current state of a feature's development workflow (constitution → specify → plan → tasks → implement), including completed steps and next actions. Persisted as JSON files in the feature's .state/ subdirectory for resumability and isolation between features.
- **Agent Output**: Result produced by an agent for a specific task, including recommendations, generated artifacts, and confidence level.
- **LLM Provider Configuration**: Settings that specify which LLM service to use (Anthropic Claude, OpenAI GPT, or future providers). API credentials are read from environment variables (ANTHROPIC_API_KEY, OPENAI_API_KEY) or external configuration files managed by the user. Includes model selection and provider-specific parameters.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Developers can execute any SpecKit command and receive valid output in under 5 minutes for simple features (under 10 requirements)
- **SC-002**: System correctly selects appropriate specialized agents for 95% of tasks without manual intervention
- **SC-003**: Command execution success rate of 90% or higher (excluding invalid user inputs)
- **SC-004**: Developers can complete a full SpecKit workflow (constitution through tasks) for a typical feature in under 20 minutes
- **SC-005**: When agents are invoked in parallel, total execution time is reduced by at least 40% compared to sequential execution
- **SC-006**: System maintains context across workflow steps with 100% accuracy (no lost information between commands)
- **SC-007**: Agent failures are detected and handled within 30 seconds, with automatic retry once (exponential backoff) and fallback to generic agent
- **SC-008**: Developers can trace 100% of output content back to the specific agent that produced it
- **SC-009**: System handles at least 5 concurrent feature workflows without performance degradation
- **SC-010**: Error messages are clear and actionable, enabling developers to resolve issues in under 2 minutes on average
- **SC-011**: Developers can switch between LLM providers (Anthropic Claude and OpenAI GPT) and execute commands successfully with either provider
- **SC-012**: Interactive terminal provides responsive feedback with progress updates appearing within 2 seconds of starting any command

## Assumptions *(mandatory)*

### Technical Assumptions

- DeepAgents library provides stable APIs for agent creation, task decomposition, and subagent spawning
- DeepAgents library supports integration with multiple LLM providers (Anthropic Claude and OpenAI GPT at minimum)
- Ambient agent definitions (markdown files) contain sufficient information to configure specialized agents with distinct roles and capabilities
- Each Ambient agent definition has a clearly defined scope and capabilities that can be mapped to task types
- SpecKit command specifications are well-documented and stable
- The system has sufficient computational resources to run multiple agents in parallel
- Both Anthropic and OpenAI APIs provide comparable capabilities for the agent use cases required by SpecKit commands

### Workflow Assumptions

- Developers using this system are familiar with SpecKit workflow and command structure
- Features follow the standard SpecKit lifecycle: constitution → specify → clarify → plan → tasks → implement
- Each feature is developed in its own git branch following the naming pattern [number]-[feature-name]
- Developers typically launch the runner from within a feature branch, enabling auto-detection of context
- Developers work on one feature at a time in a single session (though the system supports switching between features)

### Data Assumptions

- Feature specifications, plans, and tasks are stored in the standard SpecKit directory structure (`specs/[number]-[feature-name]/`)
- Workflow state and context are stored as JSON files in `specs/[number]-[feature-name]/.state/` directory
- Command outputs are text-based documents (Markdown, JSON, or similar) that can be easily stored and versioned
- Agent outputs can be deterministically combined or merged when multiple agents contribute to the same artifact
- State files are git-compatible and can be versioned alongside feature artifacts

### Integration Assumptions

- The runner operates as an interactive terminal application accessible to developers
- Developers are comfortable working in terminal/command-line environments
- Ambient agent definitions can be loaded and used to instantiate specialized DeepAgents instances
- Agent responses are returned in a structured format that can be parsed and integrated into SpecKit artifacts
- The system can detect task types from command context and feature specifications
- Terminal supports basic formatting for progress indicators and status displays

## Out of Scope *(mandatory)*

### Explicitly Excluded

- **Custom Agent Development**: Creating new agents beyond the 21 provided by the Ambient platform. Users must work within the existing agent roster.
- **Code Compilation and Deployment**: The runner generates specifications, plans, and tasks but does not compile, build, test, or deploy actual code to production environments.
- **Real-time Collaboration**: Multiple developers editing the same feature specification simultaneously is not supported. Features must be worked on by one developer at a time.
- **Natural Language Command Parsing**: Commands must use exact SpecKit syntax (e.g., `/speckit.plan`). Arbitrary natural language like "help me plan this feature" is not supported.
- **Agent Performance Optimization**: The runner uses agents as-is from the Ambient platform. Tuning, training, or modifying agent behavior is outside scope.
- **Graphical User Interface**: This is an interactive terminal application. Web dashboards, desktop applications, or graphical interfaces are not included in the initial version.
- **Integration with Non-SpecKit Workflows**: The runner specifically implements SpecKit commands and methodology. Integration with other development frameworks (Agile tools, issue trackers, etc.) is not included.
- **Agent Simulation or Mocking**: Testing must use real Ambient agents. Simulated agents for offline development or testing are not provided.

### Future Considerations

- **Graphical User Interface**: Add web-based or desktop GUI for users who prefer visual interfaces over terminal
- **Additional LLM Provider Support**: Expand beyond Anthropic and OpenAI to support vLLM, local models, Azure OpenAI, Google Gemini, and other providers
- **Custom Agent Registration**: Allow users to register their own agents beyond the Ambient platform set
- **Cross-Feature Analytics**: Aggregate insights across multiple features (common patterns, frequently used agents, bottlenecks)
- **Interactive Clarification**: Allow agents to ask follow-up questions during command execution for ambiguous requirements
- **Agent Performance Metrics**: Track and display agent success rates, average execution times, and quality scores
- **Workflow Templates**: Pre-configured workflows for common feature types (CRUD operations, authentication, API integrations)
- **Integration Hooks**: Allow custom scripts or webhooks to trigger before/after command execution

## Dependencies *(mandatory)*

### External Dependencies

- **DeepAgents Library**: Core foundation for agent orchestration, task decomposition, context management, and subagent spawning. Must be available and functional.
- **Anthropic Claude API**: LLM service provider for agent inference when Anthropic is selected. Requires API credentials and network access.
- **OpenAI GPT API**: LLM service provider for agent inference when OpenAI is selected. Requires API credentials and network access.
- **SpecKit Templates**: Requires access to SpecKit template files for specifications, plans, tasks, and checklists to generate correctly formatted outputs.

### Internal Dependencies

- **Ambient Agent Definitions**: Requires bundled markdown files defining all 21 agent roles, capabilities, and system prompts
- **File System Access**: Must be able to read/write to the specs directory structure for persisting specifications, plans, tasks, and workflow state files (.state/ subdirectory)
- **Process Management**: Requires ability to spawn and manage multiple concurrent agent processes for parallel execution
- **State Persistence**: Workflow state stored as JSON files in feature's .state/ directory, enabling resumability and feature isolation

### Workflow Dependencies

- **Linear Command Execution**: Some commands depend on previous commands (e.g., `/speckit.plan` requires `/speckit.specify` to be completed first)
- **Constitution-First**: Features that reference project principles must have `/speckit.constitution` executed before other commands
- **Git Branch Context**: Runner auto-detects feature context from current git branch name (matching [number]-[feature-name] pattern), or prompts for selection if on non-feature branch

## Constraints *(include if applicable)*

### Resource Constraints

- Agent execution is limited by available computational resources (CPU, memory) for parallel processing
- Very large features (100+ requirements or tasks) may require additional processing time beyond standard success criteria
- Network connectivity required for underlying LLM API calls (e.g., OpenAI, Anthropic) that power the agents

### Platform Constraints

- System must operate in environments where DeepAgents library is supported (Python 3.8+)
- Requires valid API credentials for at least one supported LLM provider set via environment variables (ANTHROPIC_API_KEY or OPENAI_API_KEY) or external configuration file
- Requires network connectivity to reach LLM provider APIs (api.anthropic.com for Claude, api.openai.com for GPT)
- File system permissions must allow read/write access to the SpecKit specs directory

### Operational Constraints

- Command execution may be limited by rate limits or quotas on underlying LLM API usage (both Anthropic and OpenAI have provider-specific rate limits)
- Different LLM providers may have different performance characteristics (latency, throughput, context window sizes)
- Long-running commands may require timeout thresholds to prevent indefinite execution
- Concurrent command execution on the same feature must be prevented to avoid state conflicts
