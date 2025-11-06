# Quickstart Guide: SpecKit Integration

**Feature**: 002-speckit-integration
**Last Updated**: 2025-11-06

## Overview

This guide provides step-by-step instructions for setting up, integrating, and testing the SpecKit Integration feature. It covers local development setup, integration scenarios, and validation procedures.

---

## Prerequisites

Before beginning, ensure you have:

- **Python 3.11+** installed
- **Git** installed and configured
- **DeepAgents Runner** repository cloned locally
- API keys for LLM providers (Anthropic, OpenAI) configured

---

## Setup Instructions

### 1. Install Dependencies

```bash
# Navigate to repository root
cd /path/to/deepagents-runner

# Install Python dependencies
pip install -r requirements.txt

# Install new dependencies for SpecKit integration
pip install markdown-it-py jinja2 pydantic-to-openapi3
```

### 2. Verify Existing Dependencies

Confirm these are already installed:

```bash
# Check GitPython
python -c "import git; print(git.__version__)"

# Check Rich
python -c "import rich; print(rich.__version__)"

# Check Pydantic
python -c "import pydantic; print(pydantic.__version__)"
```

### 3. Set Up Development Environment

```bash
# Create .env file for configuration (if not exists)
cp .env.example .env

# Edit .env to add API keys and configuration
# ANTHROPIC_API_KEY=your_key_here
# OPENAI_API_KEY=your_key_here
```

### 4. Initialize Testing Fixtures

```bash
# Create test fixtures directory
mkdir -p tests/fixtures/sample_specs
mkdir -p tests/fixtures/sample_plans
mkdir -p tests/fixtures/sample_tasks

# Run fixture generation script (created during implementation)
python -m src.speckit.utils.generate_fixtures
```

---

## Integration Scenarios

### Scenario 1: Full Workflow Integration (Recommended)

**Use Case**: Replace all existing speckit commands with integrated versions

**Steps**:

1. **Create Feature Specification**:
   ```bash
   python -m src.speckit.commands.specify "Add user authentication"
   ```

   **Expected Output**:
   - New branch `003-user-auth` created
   - Spec file generated at `specs/003-user-auth/spec.md`
   - Quality validation checklist created
   - Validation report showing any issues

2. **Interactive Clarification**:
   ```bash
   python -m src.speckit.commands.clarify
   ```

   **Expected Behavior**:
   - Presents questions one at a time
   - Shows recommended answers with reasoning
   - Updates spec after each answer
   - Logs Q&A in Clarifications section

3. **Generate Planning Artifacts**:
   ```bash
   python -m src.speckit.commands.plan
   ```

   **Expected Output**:
   - `research.md` with technology decisions
   - `data-model.md` with entities and relationships
   - `contracts/` directory with OpenAPI schemas
   - `quickstart.md` with setup instructions
   - Agent context file updated

4. **Generate Tasks**:
   ```bash
   python -m src.speckit.commands.tasks
   ```

   **Expected Output**:
   - `tasks.md` with user-story-based organization
   - Tasks marked with [P] for parallelization
   - Tasks labeled with [US1], [US2], etc.
   - Dependency graph included

5. **Validate Before Implementation**:
   ```bash
   python -m src.speckit.commands.analyze
   ```

   **Expected Output**:
   - Coverage analysis report
   - Findings table with severity assignments
   - Constitution check results (if constitution exists)
   - Recommendations for next steps

6. **Execute Implementation**:
   ```bash
   python -m src.speckit.commands.implement
   ```

   **Expected Behavior**:
   - Validates all checklists complete
   - Executes tasks phase by phase
   - Marks tasks as completed in tasks.md
   - Handles parallel tasks appropriately

---

### Scenario 2: Partial Integration (Testing)

**Use Case**: Test specific components without full workflow

**A. Test Spec Parsing**:
```python
from src.speckit.core.spec_parser import SpecParser

# Parse existing spec
parser = SpecParser("specs/002-speckit-integration/spec.md")
spec = parser.parse()

# Access structured data
print(f"User Stories: {len(spec.user_stories)}")
print(f"Requirements: {len(spec.functional_requirements)}")
```

**B. Test Clarification Workflow**:
```python
from src.speckit.core.clarification import ClarificationEngine

# Create clarification engine
engine = ClarificationEngine(
    spec_path="specs/002-speckit-integration/spec.md",
    question_limit=5
)

# Analyze for ambiguities
session = engine.create_session()
questions = engine.generate_questions()

# Simulate answering questions
for q in questions:
    answer = "A"  # Or user input
    engine.submit_answer(q.question_id, answer)
```

**C. Test Artifact Generation**:
```python
from src.speckit.core.artifact_generator import ArtifactGenerator

# Generate single artifact
generator = ArtifactGenerator(
    feature_id="002-speckit-integration",
    spec_path="specs/002-speckit-integration/spec.md"
)

# Generate research
research = generator.generate_research()
print(f"Generated: {research.file_path}")
```

---

### Scenario 3: CLI Interactive Testing

**Use Case**: Test interactive features manually

```bash
# Start interactive clarification session
python -m src.speckit.commands.clarify --interactive

# Generate checklist with interactive focus selection
python -m src.speckit.commands.checklist --interactive

# Review and approve validation gate
python -m src.speckit.commands.implement --dry-run
```

---

## Testing Guidance

### Unit Tests

Run unit tests for individual components:

```bash
# Test spec parser
pytest tests/unit/test_spec_parser.py -v

# Test validation engine
pytest tests/unit/test_validation.py -v

# Test clarification engine
pytest tests/unit/test_clarification.py -v

# Test artifact generator
pytest tests/unit/test_artifact_generator.py -v

# Test coverage analyzer
pytest tests/unit/test_coverage_analyzer.py -v

# Run all unit tests
pytest tests/unit/ -v --cov=src/speckit
```

### Integration Tests

Run integration tests for complete workflows:

```bash
# Test specify workflow
pytest tests/integration/test_specify_workflow.py -v

# Test clarify workflow
pytest tests/integration/test_clarify_workflow.py -v

# Test plan workflow
pytest tests/integration/test_plan_workflow.py -v

# Test full end-to-end workflow
pytest tests/integration/test_full_workflow.py -v --slow

# Run all integration tests
pytest tests/integration/ -v
```

### Test Coverage

Check test coverage:

```bash
# Generate coverage report
pytest tests/ --cov=src/speckit --cov-report=html

# View coverage report
open htmlcov/index.html
```

**Target**: 80%+ coverage for core business logic

---

## Common Operations

### Create New Feature Specification

```bash
# With feature description
python -m src.speckit.commands.specify "Feature description here"

# With validation
python -m src.speckit.commands.specify "Feature description" --validate

# Skip validation (for exploratory work)
python -m src.speckit.commands.specify "Feature description" --no-validate
```

### Run Clarification Session

```bash
# Interactive mode (default)
python -m src.speckit.commands.clarify

# Non-interactive (use recommendations)
python -m src.speckit.commands.clarify --auto-recommend

# Limit questions
python -m src.speckit.commands.clarify --max-questions=3
```

### Generate Planning Artifacts

```bash
# Generate all artifacts
python -m src.speckit.commands.plan

# Generate specific artifacts only
python -m src.speckit.commands.plan --artifacts=research,data-model

# Skip constitution check
python -m src.speckit.commands.plan --no-constitution-check
```

### Generate Requirements Checklist

```bash
# With interactive focus selection
python -m src.speckit.commands.checklist

# Specific focus area
python -m src.speckit.commands.checklist --focus=security

# Set depth level
python -m src.speckit.commands.checklist --depth=formal
```

### Run Coverage Analysis

```bash
# Full analysis
python -m src.speckit.commands.analyze

# Skip constitution check
python -m src.speckit.commands.analyze --no-constitution

# Output JSON report
python -m src.speckit.commands.analyze --format=json > analysis-report.json
```

---

## Troubleshooting

### Issue: "Spec file not found"

**Solution**:
- Ensure you're in the repository root
- Check branch name matches feature ID
- Verify spec file exists at `specs/{feature-id}/spec.md`

### Issue: "Constitution validation failed"

**Solution**:
- Check if `.specify/memory/constitution.md` exists
- If not needed, run with `--no-constitution-check` flag
- If needed, create constitution using `/speckit.constitution` command

### Issue: "Markdown parsing error"

**Solution**:
- Validate spec Markdown syntax
- Ensure headers follow proper hierarchy (##, ###, etc.)
- Check for unclosed code blocks or malformed tables

### Issue: "Git operations failed"

**Solution**:
- Ensure Git is installed and accessible
- Check repository is a valid git repo (`.git` directory exists)
- Verify remote is configured if fetching remote branches

### Issue: "API contract generation failed"

**Solution**:
- Ensure user stories and functional requirements are defined
- Check that entities are defined if generating data-driven APIs
- Verify `pydantic-to-openapi3` is installed

---

## Performance Optimization

### Tips for Fast Workflow Execution

1. **Use incremental clarification**: Limit to 3-5 questions per session
2. **Skip optional artifacts**: Generate only needed artifacts
3. **Leverage caching**: Templates and parsed specs are cached
4. **Parallel task execution**: Use [P] markers for concurrent tasks
5. **Dry-run validation**: Use `--dry-run` to preview without execution

### Performance Targets

- **Clarification response**: < 5 seconds per question
- **Spec update**: < 1 second
- **Full workflow**: < 30 minutes for medium features
- **Artifact generation**: < 10 seconds per artifact

---

## Next Steps

After completing setup and integration:

1. **Review Generated Artifacts**: Check research.md, data-model.md, contracts/, quickstart.md
2. **Run Quality Validation**: Execute `/speckit.analyze` to catch issues early
3. **Generate Tasks**: Run `/speckit.tasks` to create implementation tasks
4. **Begin Implementation**: Execute `/speckit.implement` to start task execution
5. **Monitor Progress**: Track task completion in tasks.md

---

## Additional Resources

- **SpecKit Comparison**: See `SPECKIT_COMPARISON.md` for feature comparison
- **Feature Specification**: See `specs/002-speckit-integration/spec.md`
- **Implementation Plan**: See `specs/002-speckit-integration/plan.md`
- **Data Model**: See `specs/002-speckit-integration/data-model.md`
- **API Contracts**: See `specs/002-speckit-integration/contracts/`

---

## Support

For issues or questions:

1. Check troubleshooting section above
2. Review test fixtures in `tests/fixtures/`
3. Examine logs in `.specify/logs/`
4. Consult feature specification for expected behavior
