# Data Model: SpecKit Integration

**Feature**: 002-speckit-integration
**Date**: 2025-11-06
**Phase**: 1 - Design & Contracts

## Overview

This document defines the data entities and their relationships for the SpecKit Integration feature. All entities are derived from the Key Entities section in [spec.md](./spec.md) and functional requirements.

---

## Entity Definitions

### 1. ClarificationSession

**Purpose**: Represents a single clarification workflow execution run

**Fields**:
- `session_id` (string, UUID): Unique identifier for the session
- `feature_id` (string): Feature identifier (e.g., "002-speckit-integration")
- `timestamp` (datetime): Session start time (ISO 8601 format)
- `spec_path` (string): Absolute path to spec file being clarified
- `questions_asked` (list[ClarificationQuestion]): Questions presented in this session
- `answers_provided` (list[dict]): User answers with question_id and answer_text
- `sections_updated` (list[string]): Names of spec sections modified during session
- `status` (enum): SessionStatus - ACTIVE, COMPLETED, CANCELLED
- `question_limit` (integer, default=5): Maximum questions for this session
- `priority_impact` (enum): Impact priority order - SCOPE, SECURITY, UX, TECHNICAL

**Relationships**:
- Has many `ClarificationQuestion` objects
- References one `SpecDocument` via spec_path
- Generates multiple `SpecSectionUpdate` records

**Validation Rules**:
- session_id must be valid UUID v4
- timestamp must not be in future
- questions_asked length <= question_limit
- answers_provided length <= questions_asked length
- sections_updated must reference valid spec sections

**State Transitions**:
```
ACTIVE → COMPLETED (when all questions answered or user signals completion)
ACTIVE → CANCELLED (when user terminates session early)
```

---

### 2. ClarificationQuestion

**Purpose**: Represents a single question in a clarification workflow

**Fields**:
- `question_id` (string): Unique identifier within session (e.g., "Q1", "Q2")
- `session_id` (string, foreign key): References parent ClarificationSession
- `text` (string, max 500 chars): Question text presented to user
- `recommended_answer` (string): AI-suggested best answer with reasoning
- `options` (list[QuestionOption]): Available answer choices (2-5 options)
- `impact_category` (enum): ImpactCategory - SCOPE, SECURITY, UX, TECHNICAL
- `allow_custom_answer` (boolean, default=true): Whether user can provide free-form answer
- `max_answer_words` (integer, optional): Word limit for custom answers (default=5)
- `answer` (string, nullable): User's selected or provided answer
- `answered_at` (datetime, nullable): Timestamp when answer was provided

**Relationships**:
- Belongs to one `ClarificationSession`
- Has many `QuestionOption` objects
- Triggers `SpecSectionUpdate` when answered

**Validation Rules**:
- text must not be empty
- options length must be between 2 and 5
- recommended_answer must match one of the options
- answer (if provided) must match an option label or meet custom answer constraints
- answered_at must be >= session timestamp

---

### 3. QuestionOption

**Purpose**: Represents a single answer option for a clarification question

**Fields**:
- `option_id` (string): Option label (e.g., "A", "B", "C", "D", "E")
- `question_id` (string, foreign key): References parent ClarificationQuestion
- `label` (string, max 100 chars): Short answer text displayed to user
- `description` (string, max 300 chars): Explanation of implications
- `is_recommended` (boolean, default=false): Whether this is the recommended option

**Relationships**:
- Belongs to one `ClarificationQuestion`

**Validation Rules**:
- option_id must be single letter A-E
- label must not be empty
- description must explain implications
- Only one option per question can have is_recommended=true

---

### 4. SpecDocument

**Purpose**: Represents a parsed specification document

**Fields**:
- `spec_path` (string): Absolute path to spec.md file
- `feature_id` (string): Extracted from path (e.g., "002-speckit-integration")
- `branch_name` (string): Git branch name
- `created_date` (date): Extracted from spec metadata
- `status` (enum): SpecStatus - DRAFT, CLARIFIED, PLANNED, READY
- `sections` (dict[string, SpecSection]): Keyed by section name
- `user_stories` (list[UserStory]): Extracted user stories with priorities
- `functional_requirements` (list[Requirement]): FR-### items
- `success_criteria` (list[SuccessCriterion]): SC-### items
- `entities` (list[Entity]): Key entities if defined
- `clarifications` (dict[string, list[ClarificationRecord]]): Q&A by session date

**Relationships**:
- Has many `SpecSection` objects
- Has many `UserStory` objects
- Has many `Requirement` objects
- Has many `SuccessCriterion` objects
- Has many `ClarificationSession` instances (historical)

**Validation Rules**:
- spec_path must exist and be readable
- feature_id must match directory name pattern ###-feature-name
- Must have at least one user story
- Must have at least one functional requirement
- Must have at least one success criterion

---

### 5. PlanningArtifact

**Purpose**: Represents a generated planning artifact (research.md, data-model.md, etc.)

**Fields**:
- `artifact_id` (string, UUID): Unique identifier
- `feature_id` (string): Feature this artifact belongs to
- `artifact_type` (enum): ArtifactType - RESEARCH, DATA_MODEL, CONTRACT, QUICKSTART
- `file_path` (string): Absolute path where artifact is stored
- `content` (string): Generated content (Markdown or YAML)
- `generated_at` (datetime): Creation timestamp
- `dependencies` (list[string]): Artifact IDs this depends on
- `metadata` (dict): Type-specific metadata (e.g., contract format, entity count)

**Relationships**:
- Belongs to one `SpecDocument` via feature_id
- May depend on other `PlanningArtifact` instances
- Referenced by `Task` objects during implementation

**Validation Rules**:
- artifact_type determines file extension (.md or .yaml)
- file_path must be under specs/{feature_id}/ directory
- RESEARCH artifacts have no dependencies
- DATA_MODEL artifacts depend on RESEARCH
- CONTRACT artifacts depend on RESEARCH and DATA_MODEL
- QUICKSTART artifacts depend on all other artifact types

**Artifact Type Metadata**:
- RESEARCH: `{decisions: int, alternatives: int}`
- DATA_MODEL: `{entities: int, relationships: int}`
- CONTRACT: `{format: "openapi"|"graphql", endpoints: int}`
- QUICKSTART: `{setup_steps: int, integration_scenarios: int}`

---

### 6. Task

**Purpose**: Represents a single implementation task from tasks.md

**Fields**:
- `task_id` (string): Formatted as T### (e.g., T001, T002)
- `feature_id` (string): Feature this task belongs to
- `description` (string): Clear action description
- `file_path` (string): Target file path for task
- `user_story_ref` (string, nullable): Reference to user story (e.g., "US1", "US2")
- `is_parallelizable` (boolean, default=false): Whether task can run in parallel (marked with [P])
- `phase` (integer): Phase number (1=Setup, 2=Foundational, 3+=User Stories)
- `dependencies` (list[string]): Task IDs that must complete before this task
- `completion_status` (enum): TaskStatus - PENDING, IN_PROGRESS, COMPLETED, FAILED

**Relationships**:
- Belongs to one `SpecDocument` via feature_id
- References one `UserStory` via user_story_ref
- May depend on other `Task` objects

**Validation Rules**:
- task_id must match pattern T\d{3}
- description must include file path
- user_story_ref must match existing user story if provided
- is_parallelizable=true only if no dependencies on same file
- phase must be >= 1
- Dependencies must reference valid task IDs

**State Transitions**:
```
PENDING → IN_PROGRESS (when task execution starts)
IN_PROGRESS → COMPLETED (when task finishes successfully)
IN_PROGRESS → FAILED (when task encounters error)
FAILED → PENDING (when task is reset for retry)
```

---

### 7. ValidationFinding

**Purpose**: Represents a quality issue detected during validation or analysis

**Fields**:
- `finding_id` (string): Unique identifier (e.g., "F001", "F002")
- `feature_id` (string): Feature being analyzed
- `category` (enum): FindingCategory - DUPLICATION, AMBIGUITY, UNDERSPECIFICATION, CONSTITUTION_VIOLATION, COVERAGE_GAP, INCONSISTENCY
- `severity` (enum): Severity - CRITICAL, HIGH, MEDIUM, LOW
- `location` (string): Spec section, requirement ID, or task ID
- `description` (string): Detailed finding description
- `recommendation` (string): Suggested remediation action
- `detected_at` (datetime): Timestamp when finding was detected

**Relationships**:
- Belongs to one `SpecDocument` via feature_id
- May reference specific `Requirement`, `Task`, or `SuccessCriterion`

**Validation Rules**:
- finding_id must be unique within feature
- category determines expected location format
- CRITICAL severity requires constitution_principle reference for CONSTITUTION_VIOLATION
- recommendation must be actionable

**Severity Assignment Rules**:
- CRITICAL: Violates constitution MUST, missing core artifact, zero coverage blocking baseline
- HIGH: Duplicate/conflicting requirement, ambiguous security/performance, untestable acceptance
- MEDIUM: Terminology drift, missing non-functional coverage, underspecified edge case
- LOW: Style/wording, minor redundancy

---

### 8. Checklist

**Purpose**: Represents a requirements quality checklist

**Fields**:
- `checklist_id` (string, UUID): Unique identifier
- `feature_id` (string): Feature this checklist validates
- `focus_area` (string): Area of focus (e.g., "security", "UX", "performance")
- `created_at` (datetime): Creation timestamp
- `items` (list[ChecklistItem]): Individual checklist items
- `traceability_percentage` (float): Percentage of items with spec references
- `completion_percentage` (float): Percentage of checked items

**Relationships**:
- Belongs to one `SpecDocument` via feature_id
- Has many `ChecklistItem` objects

**Validation Rules**:
- focus_area must not be empty
- items length must be > 0
- traceability_percentage must be >= 80% (per FR-022)
- completion_percentage = (checked items / total items) * 100

---

### 9. ChecklistItem

**Purpose**: Represents a single item in a requirements quality checklist

**Fields**:
- `item_id` (string): Formatted as CHK### (e.g., CHK001)
- `checklist_id` (string, foreign key): References parent Checklist
- `question` (string): Quality question about requirements (not implementation)
- `quality_dimension` (enum): QualityDimension - COMPLETENESS, CLARITY, CONSISTENCY, ACCEPTANCE_CRITERIA, SCENARIO_COVERAGE, EDGE_CASE_COVERAGE, NON_FUNCTIONAL, DEPENDENCIES, AMBIGUITIES
- `spec_reference` (string, nullable): Reference to spec section or marker
- `is_checked` (boolean, default=false): Completion status
- `notes` (string, optional): Additional notes or findings

**Relationships**:
- Belongs to one `Checklist`

**Validation Rules**:
- item_id must match pattern CHK\d{3}
- question must ask about requirement quality, not implementation behavior
- Forbidden patterns: "Verify", "Test", "Confirm" + implementation behavior
- Required patterns: "Are ... defined/specified?", "Is ... quantified?", "Can ... be measured?"
- spec_reference should be provided (80%+ requirement)

---

### 10. ConstitutionPrinciple

**Purpose**: Represents a MUST or SHOULD principle from constitution.md

**Fields**:
- `principle_id` (string): Identifier (e.g., "I", "II", "III")
- `title` (string): Principle name (e.g., "Library-First", "CLI Interface")
- `rules` (list[string]): Non-negotiable rules as bullet points
- `rationale` (string, optional): Explanation if not obvious
- `principle_type` (enum): PrincipleType - MUST, SHOULD
- `version` (string): Constitution version when principle was added

**Relationships**:
- Validated against by `ValidationFinding` objects
- Referenced in Constitution Check sections of plans

**Validation Rules**:
- principle_id must be unique
- title must be succinct and descriptive
- rules must be declarative and testable
- MUST principles cannot be violated without justification
- SHOULD principles are recommendations but not blockers

---

## Entity Relationships Diagram

```
SpecDocument
    ├── has many → UserStory
    ├── has many → Requirement
    ├── has many → SuccessCriterion
    ├── has many → Entity
    ├── has many → ClarificationSession
    │       ├── has many → ClarificationQuestion
    │       │       └── has many → QuestionOption
    │       └── generates many → SpecSectionUpdate
    ├── has many → PlanningArtifact
    ├── has many → Task
    │       └── references one → UserStory
    ├── has many → ValidationFinding
    └── has many → Checklist
            └── has many → ChecklistItem

ConstitutionPrinciple
    └── validated by → ValidationFinding
```

---

## Storage Strategy

### File-Based Storage

All entities are stored in files within the `specs/{feature_id}/` directory:

**Spec Files**:
- `spec.md` - Contains SpecDocument, UserStory, Requirement, SuccessCriterion, ClarificationSession records
- `plan.md` - References PlanningArtifact metadata
- `tasks.md` - Contains Task records
- `research.md` - PlanningArtifact of type RESEARCH
- `data-model.md` - PlanningArtifact of type DATA_MODEL
- `quickstart.md` - PlanningArtifact of type QUICKSTART

**Contracts Directory**:
- `contracts/*.yaml` - PlanningArtifact of type CONTRACT

**Checklists Directory**:
- `checklists/*.md` - Checklist and ChecklistItem records

**Constitution File**:
- `.specify/memory/constitution.md` - ConstitutionPrinciple records

### In-Memory Representation

During workflow execution, entities are:
1. Parsed from Markdown/YAML files into Pydantic models
2. Manipulated in memory
3. Serialized back to files with formatting preservation

### Persistence Strategy

- **Read**: Parse Markdown with markdown-it-py, extract structured data into Pydantic models
- **Write**: Update specific sections using AST manipulation, preserve formatting
- **Validation**: Pydantic validators ensure data integrity before persistence
- **Concurrency**: File-level locking for multi-process safety

---

## Validation Summary

| Entity | Key Validations |
|--------|-----------------|
| ClarificationSession | UUID format, question limit, timestamp ordering |
| ClarificationQuestion | Option count (2-5), impact category, answer constraints |
| SpecDocument | Path existence, required sections, minimum content |
| PlanningArtifact | Dependency chain, file path patterns, type-specific metadata |
| Task | ID format, parallelization rules, dependency resolution |
| ValidationFinding | Severity-category alignment, actionable recommendations |
| Checklist | Traceability threshold (80%), completion tracking |
| ChecklistItem | Forbidden/required patterns, quality dimension alignment |
| ConstitutionPrinciple | Uniqueness, testability, MUST vs SHOULD semantics |

---

## Next Steps

With the data model defined, proceed to:
1. Generate API contracts in `contracts/` directory (Phase 1)
2. Generate quickstart documentation (Phase 1)
3. Implement Pydantic models in `src/speckit/models/` during task execution
