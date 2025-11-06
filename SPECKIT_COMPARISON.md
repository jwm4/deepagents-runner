# SpecKit Command Comparison: Original vs. DeepAgents Runner Implementation

**Date**: 2025-11-06
**Purpose**: Detailed comparison between the original SpecKit command templates and our DeepAgents Runner implementation

## Executive Summary

The **original SpecKit** is a sophisticated, bash-integrated workflow system with validation gates, multi-artifact generation, and progressive refinement. Our **DeepAgents Runner** is a simplified LLM-powered implementation focused on generating single artifacts per command with agent orchestration.

**Key Philosophical Differences**:
- **Original**: Multi-phase, validation-gated, bash-integrated, produces multiple interconnected artifacts
- **Ours**: Single-phase, LLM-driven, Python-based, one primary artifact per command

---

## Command-by-Command Comparison

### 1. `/speckit.specify`

#### Original SpecKit Features:
- **Branch Management**:
  - Generates short names from descriptions (2-4 words, kebab-case)
  - Checks remote, local branches, and spec directories for existing numbers
  - Auto-increments feature numbers (001, 002, etc.)
  - Runs `create-new-feature.sh` to create branch and directory structure

- **Specification Quality Validation**:
  - Generates quality checklist at `checklists/requirements.md`
  - Validates against criteria: no implementation details, testable requirements, measurable success criteria
  - Iterates up to 3 times to fix validation failures
  - Warns if still failing after iterations

- **Interactive Clarification**:
  - Limits [NEEDS CLARIFICATION] markers to maximum 3
  - Prioritizes by impact: scope > security > UX > technical details
  - Presents options as formatted tables with implications
  - Waits for user responses before updating spec
  - Updates spec inline by replacing markers

- **Template Structure**:
  - User Scenarios prioritized (P1, P2, P3) with independent testability
  - Each story must be standalone MVP-capable slice
  - Functional Requirements with FR-### IDs
  - Success criteria must be measurable and technology-agnostic

#### Our Implementation:
- **Simple generation**:
  - Takes feature description as input
  - Generates spec in one shot using LLM
  - Saves to `spec_file` location
  - No branch management (assumes branch exists)
  - No validation checkpoints
  - No interactive clarification during spec creation
  - No quality checklist generation

**Assessment**: Original is **significantly more robust** with validation gates and quality assurance.

---

### 2. `/speckit.clarify`

#### Original SpecKit Features:
- **Structured Ambiguity Analysis**:
  - Uses comprehensive taxonomy (11 categories):
    - Functional Scope & Behavior
    - Domain & Data Model
    - Interaction & UX Flow
    - Non-Functional Quality Attributes
    - Integration & External Dependencies
    - Edge Cases & Failure Handling
    - Constraints & Tradeoffs
    - Terminology & Consistency
    - Completion Signals
    - Misc / Placeholders
  - Marks each category: Clear / Partial / Missing
  - Generates internal coverage map for prioritization

- **Interactive Sequential Questioning**:
  - **One question at a time** (not batch)
  - Maximum 10 questions per session, presents max 5
  - Each question has **recommended answer** with reasoning
  - Presents options as formatted tables
  - User can accept recommendation with "yes" or provide alternative
  - Supports short-answer format (≤5 words) for appropriate questions

- **Incremental Spec Updates**:
  - Creates `## Clarifications` section with `### Session YYYY-MM-DD` subsection
  - Appends bullet after each accepted answer: `- Q: <question> → A: <answer>`
  - **Immediately applies** clarification to appropriate spec sections:
    - Functional ambiguity → Update Functional Requirements
    - User interaction → Update User Stories
    - Data shape → Update Data Model
    - Non-functional → Update Quality Attributes
    - Edge case → Add to Edge Cases / Error Handling
    - Terminology conflict → Normalize across spec
  - **Saves after each integration** (atomic writes)
  - Removes obsolete contradictory statements

- **Validation**:
  - Checks clarifications session has one bullet per answer (no duplicates)
  - Verifies ≤5 total questions asked
  - Ensures no lingering vague placeholders
  - Confirms no contradictory statements remain
  - Validates Markdown structure

- **Completion Report**:
  - Number of questions asked & answered
  - Path to updated spec
  - Sections touched (list names)
  - **Coverage summary table** with each taxonomy category:
    - Resolved (was Partial/Missing, now addressed)
    - Deferred (exceeds quota or better for planning)
    - Clear (already sufficient)
    - Outstanding (still Partial/Missing but low impact)
  - Recommendation whether to proceed to `/speckit.plan` or run `/speckit.clarify` again

#### Our Implementation:
- **Simple generation**:
  - Reads spec file
  - Generates up to 5 clarification questions in batch
  - Saves to `clarifications.md` file
  - No interactive workflow
  - No spec updates
  - No coverage analysis
  - No recommendations

**Assessment**: Original is **vastly superior** - it's an interactive refinement workflow vs. our static question generator.

---

### 3. `/speckit.plan`

#### Original SpecKit Features:
- **Multi-Phase Workflow**:
  - Runs `setup-plan.sh` to initialize plan structure
  - Loads spec and `/memory/constitution.md`
  - Copies plan template to feature directory

- **Phase 0: Research & Clarification**:
  - Extracts all NEEDS CLARIFICATION markers from Technical Context
  - Creates research tasks for each unknown
  - Creates best practices tasks for each technology
  - Creates patterns tasks for each integration
  - **Generates `research.md`** with:
    - Decision made
    - Rationale
    - Alternatives considered
  - **Resolves all NEEDS CLARIFICATION** before proceeding

- **Phase 1: Design & Contracts**:
  - **Generates `data-model.md`**:
    - Extracts entities from spec
    - Defines fields, relationships
    - Adds validation rules from requirements
    - Includes state transitions if applicable

  - **Generates API contracts** in `/contracts/`:
    - Maps user actions → endpoints
    - Uses standard REST/GraphQL patterns
    - Outputs OpenAPI/GraphQL schemas

  - **Generates `quickstart.md`**:
    - Setup instructions
    - Integration scenarios
    - Testing guidance

  - **Agent Context Update**:
    - Runs `update-agent-context.sh __AGENT__`
    - Detects which AI agent is in use (Claude Code, Copilot, etc.)
    - Updates agent-specific context file
    - Adds only new technology from current plan
    - Preserves manual additions between markers

- **Constitution Checking**:
  - Evaluates plan against constitution gates
  - ERROR if violations unjustified
  - Re-evaluates after Phase 1 design

- **Stopping Point**:
  - Command ends after Phase 1 (design artifacts)
  - Reports branch, plan path, and all generated artifacts
  - Next step is `/speckit.tasks`

#### Our Implementation:
- **Simple generation**:
  - Reads spec file
  - Generates plan.md in one shot
  - Saves to single file
  - No research phase
  - No data-model.md generation
  - No contracts/ generation
  - No quickstart.md generation
  - No agent context updates
  - No constitution checking
  - No NEEDS CLARIFICATION resolution

**Assessment**: Original is **dramatically more comprehensive** - generates 4-5 artifacts vs. our single plan.md.

---

### 4. `/speckit.tasks`

#### Original SpecKit Features:
- **User Story Organization** (PRIMARY):
  - Each user story (P1, P2, P3) gets its own phase
  - Maps all components to their story:
    - Models needed for that story
    - Services needed for that story
    - Endpoints/UI needed for that story
    - Tests specific to that story (if requested)
  - Each story must be **independently testable**
  - Each story should be a complete, viable increment

- **Strict Checklist Format** (REQUIRED):
  ```text
  - [ ] [TaskID] [P?] [Story?] Description with file path
  ```
  - Components:
    - Checkbox: `- [ ]` (markdown checkbox)
    - Task ID: T001, T002, T003... (sequential)
    - [P] marker: Include ONLY if parallelizable (different files, no dependencies)
    - [Story] label: [US1], [US2], [US3] for user story tasks
    - Description: Clear action with exact file path

- **Phase Structure**:
  - Phase 1: Setup (project initialization)
  - Phase 2: Foundational (blocking prerequisites before user stories)
  - Phase 3+: User Stories in priority order (P1, P2, P3...)
    - Within each story: Tests (if requested) → Models → Services → Endpoints → Integration
  - Final Phase: Polish & Cross-Cutting Concerns

- **Artifact Mapping**:
  - From spec.md: Extract user stories with priorities
  - From plan.md: Extract tech stack, libraries, structure
  - From data-model.md (if exists): Map entities to stories
  - From contracts/ (if exists): Map endpoints to stories
  - From research.md (if exists): Extract decisions for setup

- **Dependency Graph**:
  - Shows user story completion order
  - Identifies blocking dependencies
  - Creates parallel execution examples per story

- **Validation**:
  - Ensures each user story has all needed tasks
  - Confirms all tasks follow checklist format
  - Validates independent testability

- **Tests are OPTIONAL**:
  - Only generate test tasks if explicitly requested in spec
  - Or if user requests TDD approach

#### Our Implementation:
- **Simple generation**:
  - Reads spec and plan
  - Generates tasks.md with task breakdown
  - No user story organization
  - No parallel markers [P]
  - No dependency graph
  - No format validation
  - No independent testability requirement

**Assessment**: Original is **much more sophisticated** with strict format requirements and user-story-based organization.

---

### 5. `/speckit.implement`

#### Original SpecKit Features:
- **Checklist Validation Gate**:
  - Scans `checklists/` directory
  - Counts total, completed, incomplete items for each checklist
  - Creates status table:
    ```
    | Checklist     | Total | Completed | Incomplete | Status |
    |---------------|-------|-----------|------------|--------|
    | ux.md         | 12    | 12        | 0          | ✓ PASS |
    | test.md       | 8     | 5         | 3          | ✗ FAIL |
    | security.md   | 6     | 6         | 0          | ✓ PASS |
    ```
  - **If any incomplete**: STOPS and asks "Do you want to proceed anyway?"
  - Only continues if user explicitly approves

- **Project Setup Verification**:
  - Detects git repo: `git rev-parse --git-dir`
  - Creates/verifies ignore files based on actual setup:
    - `.gitignore` (if git repo)
    - `.dockerignore` (if Dockerfile exists or Docker in plan)
    - `.eslintignore` (if .eslintrc* exists)
    - `.prettierignore` (if .prettierrc* exists)
    - `.npmignore` (if package.json and publishing)
    - `.terraformignore` (if *.tf files exist)
    - `.helmignore` (if helm charts present)
  - Technology-specific patterns from plan.md tech stack:
    - Node.js/JS/TS, Python, Java, C#/.NET, Go, Ruby, PHP, Rust, Kotlin, C++, C, Swift, R
  - Tool-specific patterns (Docker, ESLint, Prettier, Terraform, K8s)

- **Task Execution**:
  - Parses tasks.md for phases, dependencies, parallel markers
  - **Phase-by-phase execution**: Complete each before next
  - **Respects dependencies**: Sequential tasks in order, parallel [P] together
  - **TDD approach**: Test tasks before implementation
  - **File-based coordination**: Tasks on same files run sequentially

- **Progress Tracking**:
  - Reports progress after each completed task
  - **Marks tasks as [X]** in tasks.md when completed
  - Halts if non-parallel task fails
  - For parallel [P] tasks: continue with successful, report failed

- **Completion Validation**:
  - Verifies all required tasks completed
  - Checks features match specification
  - Validates tests pass and coverage met
  - Confirms implementation follows technical plan

#### Our Implementation:
- **Implementation Guidance Generation**:
  - Reads tasks, spec, plan
  - Generates implementation.md with:
    - Step-by-step approach for each task
    - Code snippets/pseudocode
    - Testing guidance
    - Dependencies
  - **Does not actually implement**
  - No checklist validation
  - No project setup verification
  - No task execution
  - No progress tracking

**Assessment**: Original **actually implements** with gates and validation. Ours just generates guidance.

---

### 6. `/speckit.analyze`

#### Original SpecKit Features:
- **Read-Only Analysis** (STRICTLY):
  - Does NOT modify any files
  - Outputs structured report
  - Offers optional remediation plan (requires user approval)

- **Constitution Authority**:
  - Loads `/memory/constitution.md`
  - Constitution conflicts are CRITICAL
  - Requires adjustment of spec/plan/tasks
  - No dilution or reinterpretation allowed

- **Semantic Model Building**:
  - Requirements inventory with stable keys
  - User story/action inventory
  - Task coverage mapping (inference by keyword/IDs)
  - Constitution rule set (MUST/SHOULD statements)

- **Detection Passes** (max 50 findings):
  - **A. Duplication Detection**: Near-duplicate requirements
  - **B. Ambiguity Detection**: Vague adjectives, unresolved placeholders
  - **C. Underspecification**: Missing objects, unmeasurable outcomes
  - **D. Constitution Alignment**: MUST principle violations
  - **E. Coverage Gaps**: Requirements with zero tasks, tasks with no requirement
  - **F. Inconsistency**: Terminology drift, contradictions

- **Severity Assignment**:
  - CRITICAL: Violates constitution MUST, missing core artifact, zero coverage blocking baseline
  - HIGH: Duplicate/conflicting requirement, ambiguous security/performance, untestable acceptance
  - MEDIUM: Terminology drift, missing non-functional coverage, underspecified edge case
  - LOW: Style/wording, minor redundancy

- **Compact Analysis Report**:
  - Finding table: ID | Category | Severity | Location | Summary | Recommendation
  - Coverage summary table: Requirement Key | Has Task? | Task IDs | Notes
  - Constitution alignment issues
  - Unmapped tasks
  - Metrics: Total requirements, total tasks, coverage %, ambiguity count, duplication count, critical issues

- **Next Actions**:
  - If CRITICAL: Must resolve before `/speckit.implement`
  - If LOW/MEDIUM: May proceed with improvement suggestions
  - Explicit command suggestions

- **Remediation Offer**:
  - Asks: "Would you like concrete remediation edits for top N issues?"
  - Does NOT apply automatically

#### Our Implementation:
- **Simple analysis**:
  - Reads spec, plan, tasks
  - Generates analysis of consistency, completeness, quality
  - Saves to analysis.md
  - No semantic models
  - No constitution checking
  - No severity assignment
  - No coverage gap detection
  - No remediation plan

**Assessment**: Original is **highly sophisticated** with multiple detection passes and constitution enforcement.

---

### 7. `/speckit.checklist`

#### Original SpecKit Features:
- **"Unit Tests for Requirements" Philosophy**:
  - Checklists test REQUIREMENT QUALITY, not implementation
  - ❌ NOT verification/testing: "Verify button clicks", "Test error handling"
  - ✅ FOR requirements validation: "Are visual hierarchy requirements defined?", "Is 'prominent' quantified?"

- **Interactive Clarification** (up to 5 questions):
  - Dynamically generated from user's phrasing + extracted signals
  - Only asks about information that materially changes checklist
  - Question archetypes:
    - Scope refinement
    - Risk prioritization
    - Depth calibration (lightweight vs. formal gate)
    - Audience framing (author, reviewer, QA, release)
    - Boundary exclusion
    - Scenario class gaps
  - Presents options as tables when appropriate
  - Defaults: Depth=Standard, Audience=Reviewer

- **Context Loading Strategy**:
  - Progressive disclosure: loads only necessary portions
  - Summarizes long sections
  - Avoids full-file dumping

- **Category Structure** (Requirements Quality Dimensions):
  - Requirement Completeness (Are all necessary requirements documented?)
  - Requirement Clarity (Are requirements specific/unambiguous?)
  - Requirement Consistency (Do requirements align?)
  - Acceptance Criteria Quality (Are success criteria measurable?)
  - Scenario Coverage (Are all flows/cases addressed?)
  - Edge Case Coverage (Are boundary conditions defined?)
  - Non-Functional Requirements (Performance, Security, Accessibility specified?)
  - Dependencies & Assumptions (Documented and validated?)
  - Ambiguities & Conflicts (What needs clarification?)

- **Item Writing Patterns**:
  - ❌ WRONG: "Verify landing page displays 3 cards" (testing implementation)
  - ✅ CORRECT: "Are the number and layout of featured episodes specified?" (testing requirements)

  - Each item format: Question about requirement quality
  - Include quality dimension: [Completeness/Clarity/Consistency/etc.]
  - Reference spec section: [Spec §X.Y] or markers [Gap], [Ambiguity], [Conflict]

- **Traceability Requirements**:
  - MINIMUM: ≥80% of items must include traceability reference
  - Spec section references or markers (Gap, Ambiguity, Conflict, Assumption)

- **File Management**:
  - Creates `checklists/` directory
  - Uses short, descriptive names: `ux.md`, `api.md`, `security.md`, `performance.md`
  - Each run creates NEW file (never overwrites)
  - Numbers items: CHK001, CHK002, etc.

- **Content Consolidation**:
  - Soft cap: If >40 items, prioritize by risk/impact
  - Merge near-duplicates
  - If >5 low-impact edge cases, create one item

- **Absolutely Prohibited Patterns**:
  - ❌ "Verify", "Test", "Confirm", "Check" + implementation behavior
  - ❌ References to code execution, user actions, system behavior
  - ❌ "Displays correctly", "works properly", "functions as expected"
  - ❌ Implementation details (frameworks, APIs, algorithms)

- **Required Patterns**:
  - ✅ "Are [requirement type] defined/specified for [scenario]?"
  - ✅ "Is [vague term] quantified with specific criteria?"
  - ✅ "Are requirements consistent between [A] and [B]?"
  - ✅ "Can [requirement] be objectively measured?"

#### Our Implementation:
- **Simple checklist generation**:
  - Reads spec, plan, tasks
  - Generates checklist with pre-implementation, implementation, pre-deployment, post-deployment sections
  - Saves to checklist.md
  - No interactive clarification
  - No requirements quality focus
  - No traceability requirements
  - Mixes implementation verification with requirement quality

**Assessment**: Original has **fundamentally different philosophy** - testing requirement quality vs. our implementation verification.

---

### 8. `/speckit.constitution`

#### Original SpecKit Features:
- **Template-Based with Placeholders**:
  - Loads existing `/memory/constitution.md`
  - Identifies placeholders: `[ALL_CAPS_IDENTIFIER]`
  - Respects user-specified principle count (less or more than template)

- **Value Collection**:
  - If user provides value: use it
  - Otherwise infer from repo context (README, docs, prior versions)
  - Governance dates:
    - `RATIFICATION_DATE`: Original adoption (ask if unknown or mark TODO)
    - `LAST_AMENDED_DATE`: Today if changed, else keep previous
  - Version management (`CONSTITUTION_VERSION`):
    - MAJOR: Backward incompatible governance/principle removals or redefinitions
    - MINOR: New principle/section added or materially expanded
    - PATCH: Clarifications, wording, typo fixes

- **Constitution Structure**:
  - Succinct principle names
  - Non-negotiable rules (paragraph or bullets)
  - Explicit rationale if not obvious
  - Governance section: amendment procedure, versioning policy, compliance review

- **Consistency Propagation**:
  - Updates `/templates/plan-template.md` (Constitution Check alignment)
  - Updates `/templates/spec-template.md` (scope/requirements alignment)
  - Updates `/templates/tasks-template.md` (task categorization reflects principles)
  - Updates command files in `/templates/commands/*.md` (no outdated references)
  - Updates runtime docs (README.md, quickstart.md, agent guidance files)

- **Sync Impact Report** (HTML comment at top):
  - Version change: old → new
  - Modified principles (old title → new title if renamed)
  - Added sections
  - Removed sections
  - Templates requiring updates (✅ updated / ⚠ pending) with paths
  - Follow-up TODOs for deferred placeholders

- **Validation**:
  - No remaining unexplained bracket tokens
  - Version line matches report
  - Dates ISO format YYYY-MM-DD
  - Principles declarative, testable, free of vague language

- **Output**:
  - Writes to `/memory/constitution.md` (overwrite)
  - Reports new version and bump rationale
  - Files flagged for manual follow-up
  - Suggested commit message

#### Our Implementation:
- **Simple document generation**:
  - Generates constitution document with principles, standards, guidelines
  - Saves to `CONSTITUTION.md` in workspace root
  - No template system
  - No placeholder replacement
  - No version management
  - No consistency propagation
  - No sync impact report

**Assessment**: Original is **template-based system** with version control and cross-artifact propagation.

---

## Missing Bash Integration

The original SpecKit relies heavily on bash scripts for:

### 1. **create-new-feature.sh**:
   - Creates feature branch with auto-incremented number
   - Checks remote/local branches and spec directories
   - Creates spec directory structure
   - Initializes spec file from template
   - Returns JSON with paths

### 2. **setup-plan.sh**:
   - Copies plan template to feature directory
   - Initializes research.md, data-model.md, contracts/, quickstart.md
   - Returns JSON with all paths

### 3. **check-prerequisites.sh**:
   - Verifies required files exist
   - Returns JSON with available documents
   - Flags for various modes (--require-tasks, --include-tasks, --paths-only)

### 4. **update-agent-context.sh**:
   - Detects which AI agent is in use (Claude Code, Copilot, Cursor, etc.)
   - Updates agent-specific context file
   - Preserves manual additions between markers
   - Adds only new technology from current plan

### 5. **common.sh**:
   - Utility functions for all scripts
   - `get_repo_root()`: Finds repo root with fallback for non-git repos
   - `get_current_branch()`: Checks git, SPECIFY_FEATURE env var, or finds latest feature
   - `find_feature_dir_by_prefix()`: Supports multiple branches per spec
   - `check_feature_branch()`: Validates branch naming

Our implementation has **none of this bash integration** - it's pure Python with no git operations or shell script execution.

---

## Architecture Comparison

### Original SpecKit:
```
User → Slash Command → Command Template
                          ↓
                    Bash Scripts
                      ↓       ↓
                Git Ops    File Ops
                      ↓       ↓
                 Templates ← LLM → Validation
                      ↓
              Multiple Artifacts
```

### Our DeepAgents Runner:
```
User → REPL → Command Executor
                  ↓
            Agent Manager → LLM Provider
                  ↓
            Single Artifact
```

---

## Recommendation

### Which is Better?

**For Production Use**: **Original SpecKit** is significantly better because:

1. **Quality Assurance**: Validation gates, quality checklists, constitution checking
2. **Completeness**: Multi-artifact generation (research, data-model, contracts, quickstart)
3. **Interactive Refinement**: Sequential clarification with recommendations
4. **Git Integration**: Branch management, feature numbering
5. **Implementation**: Actually implements tasks vs. just generating guidance
6. **Traceability**: Coverage mapping, dependency graphs
7. **Progressive Disclosure**: Phase-based workflow with checkpoints

**For LLM Research/Prototyping**: **Our DeepAgents Runner** is better because:

1. **Agent Orchestration**: Demonstrates multi-agent collaboration
2. **Simplicity**: Easy to understand and modify
3. **Python-Native**: No bash dependency
4. **Flexible**: Can use any LLM provider
5. **Fast Iteration**: Single-shot generation for rapid prototyping

---

## Suggested Enhancements to Our Implementation

If we want to bring our implementation closer to SpecKit quality:

### High Priority:
1. **Multi-artifact generation in `/speckit.plan`**:
   - Generate research.md, data-model.md, contracts/, quickstart.md
   - Two-phase approach: Research → Design

2. **Interactive clarification in `/speckit.clarify`**:
   - Sequential questioning with recommendations
   - Incremental spec updates after each answer
   - Coverage taxonomy and reporting

3. **User-story-based task organization in `/speckit.tasks`**:
   - Enforce [P] markers for parallelizable tasks
   - Generate dependency graphs
   - Validate independent testability

4. **Checklist validation gate in `/speckit.implement`**:
   - Check all checklists complete before proceeding
   - Require explicit user approval if incomplete

5. **"Unit tests for requirements" in `/speckit.checklist`**:
   - Focus on requirement quality, not implementation verification
   - Interactive focus area selection
   - Traceability requirements

### Medium Priority:
6. **Constitution checking**:
   - Load `/memory/constitution.md`
   - Validate plans against MUST principles
   - Flag violations as CRITICAL

7. **Coverage analysis in `/speckit.analyze`**:
   - Build semantic models
   - Detect coverage gaps
   - Assign severity levels

8. **Quality validation in `/speckit.specify`**:
   - Generate requirements quality checklist
   - Validate spec against criteria
   - Iterate to fix issues

### Low Priority:
9. **Git integration**:
   - Branch numbering and creation
   - Feature directory auto-setup

10. **Bash script compatibility**:
    - Python wrappers for bash scripts
    - JSON output parsing

---

## Files to Reference

If implementing enhancements, refer to:

- **Command templates**: `/Users/bmurdock/git/spec-kit/templates/commands/*.md`
- **Artifact templates**: `/Users/bmurdock/git/spec-kit/templates/*.md`
- **Bash scripts**: `/Users/bmurdock/git/spec-kit/scripts/bash/*.sh`
- **Constitution**: `/Users/bmurdock/git/spec-kit/memory/constitution.md`

---

**Conclusion**: The original SpecKit is a production-grade workflow system with sophisticated validation and multi-artifact generation. Our DeepAgents Runner is a simplified research prototype demonstrating agent orchestration. Both have value for different use cases.
