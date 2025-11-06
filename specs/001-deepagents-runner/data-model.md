# Data Model: DeepAgents Runner

**Phase**: 1 - Design & Contracts
**Date**: 2025-11-05
**Source**: Extracted from [spec.md](./spec.md) Key Entities section

## Entities

### Feature

Represents a software feature being developed through the SpecKit workflow.

**Attributes**:
- `id`: string - Feature number (e.g., "001")
- `name`: string - Feature short name (e.g., "deepagents-runner")
- `branch`: string - Git branch name (e.g., "001-deepagents-runner")
- `spec_dir`: Path - Directory path (e.g., "specs/001-deepagents-runner/")
- `spec_file`: Path - Specification file path
- `plan_file`: Path | None - Implementation plan file path
- `tasks_file`: Path | None - Tasks file path
- `status`: FeatureStatus - Current development status
- `created_at`: datetime
- `updated_at`: datetime

**Relationships**:
- Has many: CommandExecution (1:N)
- Has one: WorkflowState (1:1)

**Validation Rules**:
- `id` must match pattern `^\d{3}$` (3 digits)
- `name` must match pattern `^[a-z0-9-]+$` (lowercase, numbers, hyphens)
- `branch` must match pattern `^\d{3}-[a-z0-9-]+$`
- `spec_file` must exist and be readable
- `spec_dir` must exist and be writable

**State Transitions**:
```
draft → specified → planned → tasked → implementing → completed
   ↓        ↓          ↓         ↓           ↓
 [Can move backward for revisions at any stage]
```

---

### Specification

Document defining what a feature should do.

**Attributes**:
- `feature_id`: string - Foreign key to Feature
- `file_path`: Path - Path to spec.md file
- `content`: string - Raw markdown content
- `user_stories`: list[UserStory] - Extracted user scenarios
- `requirements`: list[Requirement] - Functional requirements
- `success_criteria`: list[SuccessCriterion] - Measurable outcomes
- `entities`: list[EntityDef] - Key domain entities
- `version`: int - Spec version for tracking changes
- `last_modified`: datetime

**Validation Rules**:
- `file_path` must end with "spec.md"
- `content` must contain mandatory sections: User Scenarios, Requirements, Success Criteria
- `version` increments on each modification

---

### ImplementationPlan

Technical design document detailing architecture and approach.

**Attributes**:
- `feature_id`: string - Foreign key to Feature
- `file_path`: Path - Path to plan.md file
- `content`: string - Raw markdown content
- `language`: string - Primary programming language
- `dependencies`: list[string] - External libraries/frameworks
- `architecture`: dict - Component structure and relationships
- `research_file`: Path | None - Path to research.md
- `data_model_file`: Path | None - Path to data-model.md
- `contracts_dir`: Path | None - Path to contracts/ directory
- `version`: int
- `created_at`: datetime

**Validation Rules**:
- `file_path` must end with "plan.md"
- `language` must be specified (not "NEEDS CLARIFICATION")
- `dependencies` must not be empty

---

### Task

An actionable, atomic work item with dependencies.

**Attributes**:
- `id`: string - Unique task identifier (e.g., "T001")
- `feature_id`: string - Foreign key to Feature
- `title`: string - Brief task description
- `description`: string - Detailed task explanation
- `assigned_agent`: string | None - Agent responsible (e.g., "archie-architect")
- `dependencies`: list[string] - Task IDs that must complete first
- `status`: TaskStatus - pending | in_progress | completed | blocked
- `priority`: int - Execution priority (1=highest)
- `estimated_effort`: string | None - Rough effort estimate
- `actual_effort`: string | None - Actual time taken
- `created_at`: datetime
- `started_at`: datetime | None
- `completed_at`: datetime | None

**Relationships**:
- Belongs to: Feature (N:1)
- Has many: AgentAssignment (1:N)

**Validation Rules**:
- `id` must be unique within feature
- `dependencies` must reference valid task IDs
- No circular dependencies allowed
- `status` transitions: pending → in_progress → completed
- `status` can transition to blocked from any state

**State Transitions**:
```
pending → in_progress → completed
   ↓           ↓
blocked ←──────┘
   ↓
pending (when unblocked)
```

---

### AgentAssignment

Links a task or command component to a specific agent.

**Attributes**:
- `id`: string - Unique assignment ID
- `task_id`: string | None - Foreign key to Task (if task-level assignment)
- `command_id`: string | None - Foreign key to CommandExecution (if command-level)
- `agent_name`: string - Agent identifier (e.g., "archie-architect")
- `agent_role`: string - Agent's role (e.g., "architect", "tester")
- `priority`: int - Agent specialization priority (higher = more specialized)
- `assigned_at`: datetime
- `completed_at`: datetime | None
- `output_id`: string | None - Foreign key to AgentOutput

**Relationships**:
- Belongs to: Task | CommandExecution (polymorphic)
- Has one: AgentOutput (1:1)

**Validation Rules**:
- Either `task_id` or `command_id` must be set (not both)
- `agent_name` must match a bundled agent definition file
- `agent_role` must match role in agent definition metadata

---

### CommandExecution

Represents a single SpecKit command invocation.

**Attributes**:
- `id`: string - Unique execution ID
- `feature_id`: string - Foreign key to Feature
- `command`: CommandType - specify | plan | tasks | implement | clarify | analyze | checklist | constitution
- `arguments`: dict - Command arguments (e.g., {"feature_desc": "..."})
- `status`: ExecutionStatus - queued | running | completed | failed
- `progress`: float - Percentage complete (0.0 to 1.0)
- `started_at`: datetime
- `completed_at`: datetime | None
- `duration_seconds`: float | None
- `output_artifacts`: list[Path] - Generated files
- `error_message`: string | None - Error details if failed

**Relationships**:
- Belongs to: Feature (N:1)
- Has many: AgentAssignment (1:N)
- Has many: AgentOutput (1:N)

**Validation Rules**:
- `command` must be valid SpecKit command
- `status` transitions: queued → running → (completed | failed)
- `progress` must be between 0.0 and 1.0
- `completed_at` must be after `started_at`

**State Transitions**:
```
queued → running → completed
            ↓
          failed
```

---

### WorkflowState

Tracks the current state of a feature's development workflow.

**Attributes**:
- `feature_id`: string - Foreign key to Feature (unique)
- `current_phase`: WorkflowPhase - constitution | specify | clarify | plan | tasks | implement
- `completed_commands`: list[CommandRecord] - History of completed commands
- `suggested_next`: CommandType | None - Recommended next command
- `context_data`: dict - Additional workflow context
- `state_file`: Path - Path to workflow.json in .state/ directory
- `last_checkpoint`: datetime - Last successful checkpoint
- `last_updated`: datetime

**Persistent Storage**: JSON file at `specs/{feature}/.state/workflow.json`

**Validation Rules**:
- `feature_id` is unique (one workflow state per feature)
- `current_phase` must follow SpecKit lifecycle order
- `state_file` must be in feature's .state/ directory
- `completed_commands` is append-only (never remove)

**State Transitions**:
```
(none) → constitution → specify → clarify → plan → tasks → implement
   ↑          ↓            ↓         ↓        ↓        ↓
   └──────────┴────────────┴─────────┴────────┴────────┘
   (Can restart cycle for new features)
```

---

### AgentOutput

Result produced by an agent for a specific task.

**Attributes**:
- `id`: string - Unique output ID
- `assignment_id`: string - Foreign key to AgentAssignment
- `agent_name`: string - Agent that produced output
- `content`: string - Generated content (markdown, code, etc.)
- `recommendations`: list[string] - Agent's recommendations
- `confidence_level`: float - Agent's confidence (0.0 to 1.0)
- `metadata`: dict - Additional agent-specific data
- `tokens_used`: int | None - LLM tokens consumed
- `created_at`: datetime

**Relationships**:
- Belongs to: AgentAssignment (N:1)

**Validation Rules**:
- `confidence_level` must be between 0.0 and 1.0
- `content` must not be empty
- `tokens_used` must be positive if set

---

### LLMProviderConfiguration

Settings that specify which LLM service to use.

**Attributes**:
- `provider`: ProviderType - anthropic | openai | vllm | custom
- `api_key_env_var`: string - Environment variable name (e.g., "ANTHROPIC_API_KEY")
- `model_name`: string - Specific model (e.g., "claude-sonnet-4-5", "gpt-4")
- `base_url`: string | None - Custom API base URL (for vllm, local models)
- `max_tokens`: int - Maximum tokens per request
- `temperature`: float - Sampling temperature (0.0 to 1.0)
- `timeout_seconds`: int - Request timeout
- `rate_limit_rpm`: int | None - Requests per minute limit
- `additional_params`: dict - Provider-specific parameters

**Source**: Loaded from environment variables and config files

**Validation Rules**:
- `api_key_env_var` must be set in environment (checked at runtime)
- `model_name` must match provider's available models
- `temperature` must be between 0.0 and 1.0
- `max_tokens` must be positive
- `timeout_seconds` must be positive

**Default Configurations**:

**Anthropic**:
```python
{
    "provider": "anthropic",
    "api_key_env_var": "ANTHROPIC_API_KEY",
    "model_name": "claude-sonnet-4-5",
    "max_tokens": 4096,
    "temperature": 0.7,
    "timeout_seconds": 120
}
```

**OpenAI**:
```python
{
    "provider": "openai",
    "api_key_env_var": "OPENAI_API_KEY",
    "model_name": "gpt-4-turbo",
    "max_tokens": 4096,
    "temperature": 0.7,
    "timeout_seconds": 120
}
```

---

## Enumerations

### FeatureStatus
- `draft` - Initial state, spec not yet complete
- `specified` - Spec complete, ready for planning
- `planned` - Plan complete, ready for task breakdown
- `tasked` - Tasks defined, ready for implementation
- `implementing` - Work in progress
- `completed` - Feature fully implemented

### TaskStatus
- `pending` - Not yet started
- `in_progress` - Currently being worked on
- `completed` - Successfully finished
- `blocked` - Cannot proceed due to dependencies or issues

### ExecutionStatus
- `queued` - Command queued for execution
- `running` - Command currently executing
- `completed` - Command finished successfully
- `failed` - Command encountered fatal error

### WorkflowPhase
- `constitution` - Defining project principles
- `specify` - Writing feature specification
- `clarify` - Resolving ambiguities in spec
- `plan` - Creating implementation plan
- `tasks` - Breaking down into tasks
- `implement` - Executing implementation

### CommandType
- `constitution` - /speckit.constitution
- `specify` - /speckit.specify
- `plan` - /speckit.plan
- `tasks` - /speckit.tasks
- `implement` - /speckit.implement
- `clarify` - /speckit.clarify
- `analyze` - /speckit.analyze
- `checklist` - /speckit.checklist

### ProviderType
- `anthropic` - Anthropic Claude
- `openai` - OpenAI GPT
- `vllm` - vLLM inference
- `custom` - Custom provider implementation

---

## Relationships Diagram

```
Feature (1) ──┬── (N) CommandExecution ──┬── (N) AgentAssignment ──── (1) AgentOutput
              │                           │
              ├── (1) WorkflowState       └── (N) AgentAssignment
              │
              └── (N) Task ────────────────── (N) AgentAssignment
```

---

## Persistence Strategy

### File-Based Storage

**Workflow State**: `specs/{feature}/.state/workflow.json`
**Context**: `specs/{feature}/.state/context.json`
**Command History**: `specs/{feature}/.state/command_history.json`
**Agent Context**: `specs/{feature}/.state/agents/{agent_name}.json`

### In-Memory Objects

All models instantiated as Pydantic models for validation and serialization:

```python
from pydantic import BaseModel, Field
from pathlib import Path
from datetime import datetime
from typing import Optional

class Feature(BaseModel):
    id: str = Field(pattern=r"^\d{3}$")
    name: str = Field(pattern=r"^[a-z0-9-]+$")
    branch: str
    spec_dir: Path
    spec_file: Path
    plan_file: Optional[Path] = None
    tasks_file: Optional[Path] = None
    status: FeatureStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        json_encoders = {
            Path: str,
            datetime: lambda v: v.isoformat()
        }
```

### Serialization

All state persisted as JSON with schema versioning:

```json
{
  "schema_version": "1.0",
  "data": { ... }
}
```

Migration strategy: Check `schema_version`, apply transformations if older version detected.
