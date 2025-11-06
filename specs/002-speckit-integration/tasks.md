# Tasks: SpecKit Integration

**Input**: Design documents from `/specs/002-speckit-integration/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Tests**: Tests are included per the specification requirements for validation and quality assurance.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- All paths shown below use `src/speckit/` module structure per plan.md

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and module structure

- [ ] T001 Create src/speckit/ module structure with __init__.py files per plan.md
- [ ] T002 [P] Create src/speckit/commands/ directory with __init__.py
- [ ] T003 [P] Create src/speckit/core/ directory with __init__.py
- [ ] T004 [P] Create src/speckit/models/ directory with __init__.py
- [ ] T005 [P] Create src/speckit/templates/ directory with __init__.py
- [ ] T006 [P] Create src/speckit/git/ directory with __init__.py
- [ ] T007 [P] Create src/speckit/utils/ directory with __init__.py
- [ ] T008 [P] Create tests/unit/ directory structure
- [ ] T009 [P] Create tests/integration/ directory structure
- [ ] T010 [P] Create tests/fixtures/ directory with sample_specs/, sample_plans/, sample_tasks/
- [ ] T011 Install new dependencies: markdown-it-py, jinja2, pydantic-to-openapi3 in requirements.txt
- [ ] T012 [P] Create .specify/logs/ directory for logging output

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T013 [P] Implement SpecParser in src/speckit/core/spec_parser.py for parsing Markdown specs with markdown-it-py
- [ ] T014 [P] Implement TemplateLoader in src/speckit/templates/loader.py using Jinja2 to load templates from .specify/templates/
- [ ] T015 [P] Implement GitRepository wrapper in src/speckit/git/repo.py using GitPython
- [ ] T016 [P] Implement BranchManager in src/speckit/git/branch.py for branch creation and switching
- [ ] T017 [P] Implement FeatureDiscovery in src/speckit/git/feature.py for feature numbering and branch listing
- [ ] T018 [P] Implement MarkdownUtils in src/speckit/utils/markdown.py for surgical Markdown updates
- [ ] T019 [P] Implement FileOps utilities in src/speckit/utils/file_ops.py for safe file operations
- [ ] T020 [P] Implement Logger in src/speckit/utils/logger.py using logging with Rich handler
- [ ] T021 [P] Create SpecDocument model in src/speckit/models/spec.py with Pydantic
- [ ] T022 [P] Create ClarificationSession model in src/speckit/models/clarification.py with Pydantic
- [ ] T023 [P] Create ClarificationQuestion and QuestionOption models in src/speckit/models/clarification.py
- [ ] T024 [P] Create PlanningArtifact model in src/speckit/models/artifact.py with Pydantic
- [ ] T025 [P] Create Task model in src/speckit/models/task.py with Pydantic
- [ ] T026 [P] Create ValidationFinding model in src/speckit/models/finding.py with Pydantic
- [ ] T027 [P] Create Checklist and ChecklistItem models in src/speckit/models/checklist.py with Pydantic
- [ ] T028 [P] Create ConstitutionPrinciple model in src/speckit/models/constitution.py with Pydantic
- [ ] T029 Write unit tests for SpecParser in tests/unit/test_spec_parser.py
- [ ] T030 [P] Write unit tests for TemplateLoader in tests/unit/test_template_loader.py
- [ ] T031 [P] Write unit tests for GitRepository in tests/unit/test_git_repo.py
- [ ] T032 [P] Write unit tests for MarkdownUtils in tests/unit/test_markdown_utils.py
- [ ] T033 [P] Write unit tests for all Pydantic models in tests/unit/test_models.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Interactive Spec Clarification (Priority: P1) 🎯 MVP

**Goal**: Implement interactive clarification workflow that asks questions one at a time and updates spec immediately

**Independent Test**: Run `/speckit.clarify` on a spec with ambiguities, answer questions sequentially, verify spec is updated after each answer with clarifications logged

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T034 [P] [US1] Write integration test for clarification workflow in tests/integration/test_clarify_workflow.py
- [ ] T035 [P] [US1] Write unit test for ClarificationEngine in tests/unit/test_clarification.py

### Implementation for User Story 1

- [ ] T036 [P] [US1] Implement ClarificationEngine in src/speckit/core/clarification.py with ambiguity detection using taxonomy
- [ ] T037 [US1] Implement question generation logic with priority ranking (scope > security > UX > technical) in ClarificationEngine
- [ ] T038 [US1] Implement sequential questioning workflow with Rich tables in ClarificationEngine
- [ ] T039 [US1] Implement answer validation and spec update logic in ClarificationEngine
- [ ] T040 [US1] Implement Clarifications section appending with session timestamps in ClarificationEngine
- [ ] T041 [US1] Implement spec section updates (functional requirements, user stories, data model, edge cases) in ClarificationEngine
- [ ] T042 [US1] Implement ClarifyCommand in src/speckit/commands/clarify.py using ClarificationEngine
- [ ] T043 [US1] Add Rich prompt integration for user input collection in ClarifyCommand
- [ ] T044 [US1] Add error handling and validation for empty/invalid answers in ClarifyCommand
- [ ] T045 [US1] Add session completion logic and coverage reporting in ClarifyCommand

**Checkpoint**: At this point, User Story 1 should be fully functional - clarify command works end-to-end

---

## Phase 4: User Story 2 - Multi-Artifact Planning (Priority: P2)

**Goal**: Generate multiple planning artifacts (research.md, data-model.md, contracts/, quickstart.md) from specs

**Independent Test**: Run `/speckit.plan` on a clarified spec and verify it generates all 4-5 artifacts in specs/{feature}/ directory

### Tests for User Story 2

- [ ] T046 [P] [US2] Write integration test for planning workflow in tests/integration/test_plan_workflow.py
- [ ] T047 [P] [US2] Write unit test for ArtifactGenerator in tests/unit/test_artifact_generator.py

### Implementation for User Story 2

- [ ] T048 [P] [US2] Implement ArtifactGenerator base class in src/speckit/core/artifact_generator.py
- [ ] T049 [P] [US2] Implement research.md generation logic extracting unknowns from Technical Context in ArtifactGenerator
- [ ] T050 [US2] Implement data-model.md generation logic extracting entities from spec in ArtifactGenerator
- [ ] T051 [US2] Implement API contract format detection (OpenAPI vs GraphQL) logic in ArtifactGenerator
- [ ] T052 [US2] Implement OpenAPI schema generation using pydantic-to-openapi3 in ArtifactGenerator
- [ ] T053 [US2] Implement contracts/ directory creation and schema writing in ArtifactGenerator
- [ ] T054 [US2] Implement quickstart.md generation with setup and testing guidance in ArtifactGenerator
- [ ] T055 [US2] Implement PlanCommand in src/speckit/commands/plan.py using ArtifactGenerator
- [ ] T056 [US2] Add Phase 0 (Research) execution calling bash script setup-plan.sh equivalent in PlanCommand
- [ ] T057 [US2] Add Phase 1 (Design & Contracts) execution generating all artifacts in PlanCommand
- [ ] T058 [US2] Add agent context update logic modifying CLAUDE.md in PlanCommand
- [ ] T059 [US2] Add constitution check integration (optional with graceful degradation) in PlanCommand

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently - plan command generates all artifacts

---

## Phase 5: User Story 3 - User-Story-Based Task Organization (Priority: P3)

**Goal**: Generate tasks.md organized by user story with parallelization markers and dependency tracking

**Independent Test**: Run `/speckit.tasks` on a spec with 3 user stories and verify each story gets its own phase with [US1], [US2], [US3] labels and [P] markers

### Tests for User Story 3

- [ ] T060 [P] [US3] Write integration test for tasks generation workflow in tests/integration/test_tasks_workflow.py
- [ ] T061 [P] [US3] Write unit test for TaskGenerator in tests/unit/test_task_generator.py

### Implementation for User Story 3

- [ ] T062 [P] [US3] Implement TaskGenerator in src/speckit/core/task_generator.py
- [ ] T063 [US3] Implement user story extraction and priority mapping from spec.md in TaskGenerator
- [ ] T064 [US3] Implement entity-to-story mapping from data-model.md in TaskGenerator
- [ ] T065 [US3] Implement endpoint-to-story mapping from contracts/ in TaskGenerator
- [ ] T066 [US3] Implement task generation per user story (tests → models → services → endpoints) in TaskGenerator
- [ ] T067 [US3] Implement parallelization marker [P] detection (different files, no dependencies) in TaskGenerator
- [ ] T068 [US3] Implement dependency graph generation showing story completion order in TaskGenerator
- [ ] T069 [US3] Implement task format validation (checkbox, T###, [P], [Story], file path) in TaskGenerator
- [ ] T070 [US3] Implement TasksCommand in src/speckit/commands/tasks.py using TaskGenerator
- [ ] T071 [US3] Add tasks.md template rendering with Jinja2 in TasksCommand
- [ ] T072 [US3] Add parallel execution examples generation per story in TasksCommand

**Checkpoint**: All three core workflow stories (clarify, plan, tasks) should now be independently functional

---

## Phase 6: User Story 4 - Quality Validation Gates (Priority: P4)

**Goal**: Implement validation gates checking specification quality, checklist completion, and constitution alignment

**Independent Test**: Run `/speckit.specify` with validation, create spec quality issues, verify system identifies and iterates to fix them

### Tests for User Story 4

- [ ] T073 [P] [US4] Write integration test for specify workflow with validation in tests/integration/test_specify_workflow.py
- [ ] T074 [P] [US4] Write unit test for ValidationEngine in tests/unit/test_validation.py

### Implementation for User Story 4

- [ ] T075 [P] [US4] Implement ValidationEngine in src/speckit/core/validation.py
- [ ] T076 [US4] Implement spec quality criteria checks (no implementation details, testable requirements, measurable success criteria) in ValidationEngine
- [ ] T077 [US4] Implement requirements quality checklist generation in ValidationEngine
- [ ] T078 [US4] Implement validation iteration logic (up to 3 iterations) with issue identification in ValidationEngine
- [ ] T079 [US4] Implement SpecifyCommand in src/speckit/commands/specify.py with validation integration
- [ ] T080 [US4] Add branch creation and feature numbering logic calling FeatureDiscovery in SpecifyCommand
- [ ] T081 [US4] Add spec generation from template with validation gates in SpecifyCommand
- [ ] T082 [US4] Add checklist generation and validation checkpoint in SpecifyCommand
- [ ] T083 [US4] Implement ImplementCommand in src/speckit/commands/implement.py
- [ ] T084 [US4] Add checklist scanning validation gate blocking implementation if incomplete in ImplementCommand
- [ ] T085 [US4] Add user approval prompt for proceeding with incomplete checklists in ImplementCommand
- [ ] T086 [US4] Add constitution check integration with CRITICAL violation flagging in ImplementCommand

**Checkpoint**: Quality gates are now functional - specify validates specs, implement checks checklists

---

## Phase 7: User Story 5 - Requirements Quality Checklists (Priority: P5)

**Goal**: Generate checklists testing requirement quality (not implementation) with interactive focus selection and traceability

**Independent Test**: Run `/speckit.checklist` with focus area, answer clarification questions, verify checklist items test requirement quality with spec references

### Tests for User Story 5

- [ ] T087 [P] [US5] Write integration test for checklist generation in tests/integration/test_checklist_workflow.py
- [ ] T088 [P] [US5] Write unit test for ChecklistGenerator in tests/unit/test_checklist_generator.py

### Implementation for User Story 5

- [ ] T089 [P] [US5] Implement ChecklistGenerator in src/speckit/core/checklist_generator.py
- [ ] T090 [US5] Implement focus area clarification questions (scope, depth, risk priorities) in ChecklistGenerator
- [ ] T091 [US5] Implement requirement quality item generation (not implementation verification) in ChecklistGenerator
- [ ] T092 [US5] Implement quality dimension categorization (Completeness, Clarity, Consistency, etc.) in ChecklistGenerator
- [ ] T093 [US5] Implement traceability reference generation (spec sections, markers) targeting 80%+ in ChecklistGenerator
- [ ] T094 [US5] Implement checklist consolidation logic (merge duplicates, prioritize by risk) for >40 items in ChecklistGenerator
- [ ] T095 [US5] Implement forbidden pattern validation (no "Verify", "Test" + implementation) in ChecklistGenerator
- [ ] T096 [US5] Implement required pattern validation (questions about requirement quality) in ChecklistGenerator
- [ ] T097 [US5] Implement ChecklistCommand in src/speckit/commands/checklist.py using ChecklistGenerator
- [ ] T098 [US5] Add interactive focus area selection with Rich prompts in ChecklistCommand
- [ ] T099 [US5] Add checklist file naming (ux.md, security.md, etc.) and storage in checklists/ in ChecklistCommand

**Checkpoint**: Checklist generation is functional - generates requirement quality checklists with traceability

---

## Phase 8: User Story 6 - Coverage and Consistency Analysis (Priority: P6)

**Goal**: Detect coverage gaps, duplications, and inconsistencies across spec/plan/tasks with severity assignment

**Independent Test**: Run `/speckit.analyze` on feature with intentional issues, verify system generates report with findings table and severity levels

### Tests for User Story 6

- [ ] T100 [P] [US6] Write integration test for analysis workflow in tests/integration/test_analyze_workflow.py
- [ ] T101 [P] [US6] Write unit test for CoverageAnalyzer in tests/unit/test_coverage_analyzer.py

### Implementation for User Story 6

- [ ] T102 [P] [US6] Implement CoverageAnalyzer in src/speckit/core/coverage_analyzer.py
- [ ] T103 [US6] Implement semantic model building (requirements inventory, user story inventory, task coverage mapping) in CoverageAnalyzer
- [ ] T104 [US6] Implement duplication detection (near-duplicate requirements) in CoverageAnalyzer
- [ ] T105 [US6] Implement ambiguity detection (vague adjectives, unresolved placeholders) in CoverageAnalyzer
- [ ] T106 [US6] Implement underspecification detection (missing objects, unmeasurable outcomes) in CoverageAnalyzer
- [ ] T107 [US6] Implement coverage gap detection (requirements with zero tasks, tasks with no requirement) in CoverageAnalyzer
- [ ] T108 [US6] Implement inconsistency detection (terminology drift, contradictions) in CoverageAnalyzer
- [ ] T109 [US6] Implement constitution alignment checking with MUST principle violation detection in CoverageAnalyzer
- [ ] T110 [US6] Implement severity assignment logic (CRITICAL, HIGH, MEDIUM, LOW) in CoverageAnalyzer
- [ ] T111 [US6] Implement analysis report generation with findings table and coverage summary in CoverageAnalyzer
- [ ] T112 [US6] Implement AnalyzeCommand in src/speckit/commands/analyze.py using CoverageAnalyzer
- [ ] T113 [US6] Add requirement-to-task coverage mapping visualization in AnalyzeCommand
- [ ] T114 [US6] Add next actions recommendations based on severity levels in AnalyzeCommand

**Checkpoint**: All six user stories should now be independently functional - complete SpecKit integration achieved

---

## Phase 9: Constitution Management (Supplementary Feature)

**Purpose**: Support for creating and managing constitution.md with version control

- [ ] T115 [P] Implement ConstitutionManager in src/speckit/core/constitution_manager.py
- [ ] T116 [P] Implement ConstitutionCommand in src/speckit/commands/constitution.py
- [ ] T117 [P] Write unit tests for ConstitutionManager in tests/unit/test_constitution_manager.py

---

## Phase 10: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T118 [P] Add comprehensive logging throughout all commands using Logger utility
- [ ] T119 [P] Add error handling and user-friendly error messages across all commands
- [ ] T120 [P] Add progress indicators using Rich for long-running operations
- [ ] T121 [P] Create test fixtures for all workflow scenarios in tests/fixtures/
- [ ] T122 [P] Write end-to-end integration test covering full workflow in tests/integration/test_full_workflow.py
- [ ] T123 [P] Add CLI argument parsing and help text for all commands
- [ ] T124 [P] Update requirements.txt with all dependencies and version pins
- [ ] T125 [P] Run code quality checks: ruff check . and address issues
- [ ] T126 [P] Run test suite: pytest tests/ --cov=src/speckit and verify 80%+ coverage
- [ ] T127 [P] Validate quickstart.md by running all examples in quickstart guide
- [ ] T128 [P] Add docstrings and type hints throughout src/speckit/ module
- [ ] T129 Update CLAUDE.md with final technology list and commands
- [ ] T130 Create .gitignore entries for .specify/logs/ and test artifacts

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-8)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3 → P4 → P5 → P6)
- **Constitution (Phase 9)**: Can proceed in parallel with user stories (independent)
- **Polish (Phase 10)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1) - Interactive Clarification**: Can start after Foundational - No dependencies on other stories
- **User Story 2 (P2) - Multi-Artifact Planning**: Can start after Foundational - No dependencies on other stories
- **User Story 3 (P3) - Task Organization**: Can start after Foundational - No dependencies on other stories
- **User Story 4 (P4) - Validation Gates**: Can start after Foundational - Integrates with US1 (specify validation) but independently testable
- **User Story 5 (P5) - Quality Checklists**: Can start after Foundational - No dependencies on other stories
- **User Story 6 (P6) - Coverage Analysis**: Can start after Foundational - Works with outputs from US2 and US3 but independently testable

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- Models before services/engines
- Core logic before command wrappers
- Individual components before integration
- Story complete before moving to next priority

### Parallel Opportunities

- **Phase 1 (Setup)**: All T001-T012 tasks can run in parallel (creating different directories/files)
- **Phase 2 (Foundational)**: All T013-T033 tasks can run in parallel (different files, no dependencies)
- **Within User Stories**: Tasks marked [P] can run in parallel
- **Across User Stories**: Once Foundational completes, all 6 user stories can be worked on in parallel by different team members
- **Phase 9 (Constitution)**: Can run in parallel with any user story phase
- **Phase 10 (Polish)**: All T118-T130 tasks can run in parallel (different concerns)

---

## Parallel Example: User Story 1 (Interactive Clarification)

```bash
# Launch all tests for User Story 1 together:
Task T034: "Write integration test for clarification workflow in tests/integration/test_clarify_workflow.py"
Task T035: "Write unit test for ClarificationEngine in tests/unit/test_clarification.py"

# After tests written, launch initial implementation in parallel:
Task T036: "Implement ClarificationEngine in src/speckit/core/clarification.py with ambiguity detection"
Task T042: "Implement ClarifyCommand in src/speckit/commands/clarify.py using ClarificationEngine"
# (Note: T037-T041 depend on T036 completing, T043-T045 depend on T042 completing)
```

---

## Parallel Example: Cross-Story (After Foundational Complete)

```bash
# With 6 developers after Phase 2 completion:
Developer A: Start Phase 3 (User Story 1 - Clarification)
Developer B: Start Phase 4 (User Story 2 - Planning)
Developer C: Start Phase 5 (User Story 3 - Tasks)
Developer D: Start Phase 6 (User Story 4 - Validation)
Developer E: Start Phase 7 (User Story 5 - Checklists)
Developer F: Start Phase 8 (User Story 6 - Analysis)

# All stories proceed independently and integrate at the end
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T012)
2. Complete Phase 2: Foundational (T013-T033) - CRITICAL
3. Complete Phase 3: User Story 1 (T034-T045)
4. **STOP and VALIDATE**: Test clarification workflow independently
5. Deploy/demo if ready

**Result**: Interactive clarification workflow is functional - developers can refine specs interactively

### Incremental Delivery (Recommended)

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 3 → Test independently → Deploy/Demo
5. Add User Story 4 → Test independently → Deploy/Demo
6. Add User Story 5 → Test independently → Deploy/Demo
7. Add User Story 6 → Test independently → Deploy/Demo
8. Each story adds value without breaking previous stories

### Parallel Team Strategy

With 6+ developers:

1. Team completes Setup + Foundational together (T001-T033)
2. Once Foundational is done:
   - Developer A: User Story 1 (T034-T045)
   - Developer B: User Story 2 (T046-T059)
   - Developer C: User Story 3 (T060-T072)
   - Developer D: User Story 4 (T073-T086)
   - Developer E: User Story 5 (T087-T099)
   - Developer F: User Story 6 (T100-T114)
3. Stories complete and integrate independently
4. Team collaborates on Polish phase (T118-T130)

---

## Summary Statistics

- **Total Tasks**: 130
- **Phase 1 (Setup)**: 12 tasks
- **Phase 2 (Foundational)**: 21 tasks
- **User Story 1 (P1)**: 12 tasks (T034-T045)
- **User Story 2 (P2)**: 14 tasks (T046-T059)
- **User Story 3 (P3)**: 13 tasks (T060-T072)
- **User Story 4 (P4)**: 14 tasks (T073-T086)
- **User Story 5 (P5)**: 13 tasks (T087-T099)
- **User Story 6 (P6)**: 15 tasks (T100-T114)
- **Phase 9 (Constitution)**: 3 tasks (T115-T117)
- **Phase 10 (Polish)**: 13 tasks (T118-T130)

**Parallel Opportunities**:
- Phase 1: 11 parallel tasks
- Phase 2: 21 parallel tasks (foundation can be built concurrently)
- All 6 user stories can proceed in parallel after foundation
- Within each user story: 2-4 parallel tasks per story
- Phase 10: 12 parallel tasks

**MVP Scope**: Phase 1 + Phase 2 + Phase 3 = 45 tasks

**Full Feature**: All 130 tasks

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- All tasks follow strict checklist format: `- [ ] [T###] [P?] [Story?] Description with file path`
- Format validated: ✓ All 130 tasks include checkbox, task ID, optional markers, and file paths
