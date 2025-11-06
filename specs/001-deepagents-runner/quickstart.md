# QuickStart: DeepAgents Runner

**Last Updated**: 2025-11-05
**Target Audience**: Developers implementing the DeepAgents Runner
**Prerequisites**: Python 3.11+, git, API key for Anthropic or OpenAI

## Overview

This quickstart guides you through setting up and running the DeepAgents Runner for the first time.

## Installation

### 1. Clone Repository

```bash
git clone <repository-url>
cd deepagents-runner
```

### 2. Create Virtual Environment

```bash
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -e .
```

This installs:
- `deepagents` - Agent orchestration framework
- `anthropic` - Anthropic Claude SDK
- `openai` - OpenAI GPT SDK
- `rich` - Terminal UI library
- `python-frontmatter` - Parse agent definitions
- `tenacity` - Retry logic
- `gitpython` - Git operations
- `pydantic` - Data validation

### 4. Configure LLM Provider

Set API key for your chosen provider:

**For Anthropic Claude**:
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

**For OpenAI GPT**:
```bash
export OPENAI_API_KEY="sk-..."
```

Tip: Add to your shell profile (`.bashrc`, `.zshrc`) for persistence:

```bash
echo 'export ANTHROPIC_API_KEY="sk-ant-..."' >> ~/.zshrc
source ~/.zshrc
```

## Running the Runner

### Launch Interactive Terminal

```bash
deepagents-runner
```

**What happens**:
1. Detects feature context from current git branch
2. If on feature branch (e.g., `001-user-auth`), auto-loads that feature
3. If on main/master, prompts to select from available features
4. Displays welcome screen with feature context
5. Enters interactive command mode

### Example Session

```
$ deepagents-runner

╔══════════════════════════════════════════════════╗
║         DeepAgents Runner v1.0.0                 ║
╚══════════════════════════════════════════════════╝

Feature: 001-user-auth
Provider: Anthropic Claude (claude-sonnet-4-5)
Branch: 001-user-auth

Available commands:
  /speckit.specify <description>  - Create feature specification
  /speckit.clarify                - Resolve spec ambiguities
  /speckit.plan                   - Generate implementation plan
  /speckit.tasks                  - Break down into tasks
  /speckit.implement [task_ids]   - Execute implementation
  /speckit.analyze                - Analyze artifacts
  /speckit.checklist              - Generate checklists
  /help                           - Show help
  /exit                           - Exit runner

> /speckit.specify "Add OAuth2 authentication for users"

🔄 Executing /speckit.specify...

┌─────────────────────────────────────────────────┐
│ Agent Activity                                  │
├───────────────┬───────────┬─────────────────────┤
│ Agent         │ Status    │ Task                │
├───────────────┼───────────┼─────────────────────┤
│ Generic Agent │ 🔄 Working│ Creating spec...    │
└───────────────┴───────────┴─────────────────────┘

✅ Specification created: specs/001-user-auth/spec.md

Suggested next: /speckit.clarify

> /speckit.plan

🔄 Executing /speckit.plan...

┌─────────────────────────────────────────────────┐
│ Agent Activity                                  │
├──────────────────┬───────────┬──────────────────┤
│ Archie Architect │ 🔄 Working│ Designing arch...│
│ Aria UX Architect│ 🔄 Working│ UX flows...      │
│ Stella Engineer  │ ⏳ Waiting│ Pending arch...  │
└──────────────────┴───────────┴──────────────────┘

✅ Plan created: specs/001-user-auth/plan.md
✅ Research: specs/001-user-auth/research.md
✅ Data Model: specs/001-user-auth/data-model.md

Suggested next: /speckit.tasks

> /exit
Goodbye!
```

## Feature Workflow

### 1. Create New Feature

```bash
# On main branch
git checkout -b 002-payment-integration

# Launch runner - will detect new feature context
deepagents-runner
```

### 2. Specify Feature

```
> /speckit.specify "Integrate Stripe for payment processing with subscription support"
```

**Output**: `specs/002-payment-integration/spec.md`

### 3. Clarify Ambiguities (Optional)

```
> /speckit.clarify
```

Runner asks targeted questions to resolve underspecified areas.

### 4. Generate Plan

```
> /speckit.plan
```

**Output**:
- `specs/002-payment-integration/plan.md` - Implementation plan
- `specs/002-payment-integration/research.md` - Technical decisions
- `specs/002-payment-integration/data-model.md` - Data entities
- `specs/002-payment-integration/contracts/` - API contracts

### 5. Break Down Tasks

```
> /speckit.tasks
```

**Output**: `specs/002-payment-integration/tasks.md` - Actionable task list

### 6. Implement

```
> /speckit.implement
```

Executes all pending tasks, coordinating agents for each task.

## Project Structure

After running through workflow, your directory looks like:

```
deepagents-runner/
├── src/
│   ├── deepagents_runner/       # Runner implementation
│   └── agents/                  # Bundled agent definitions
├── specs/
│   ├── 001-user-auth/
│   │   ├── spec.md
│   │   ├── plan.md
│   │   ├── research.md
│   │   ├── data-model.md
│   │   ├── tasks.md
│   │   ├── contracts/
│   │   └── .state/              # Workflow state (JSON files)
│   │       ├── workflow.json
│   │       ├── context.json
│   │       └── command_history.json
│   └── 002-payment-integration/
│       └── ...
└── config/
    └── .env.example
```

## Configuration

### Environment Variables

Create `.env` file or set in shell:

```bash
# Required: At least one provider
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...

# Optional: Advanced configuration
RUNNER_DEFAULT_PROVIDER=anthropic  # or 'openai'
RUNNER_MODEL=claude-sonnet-4-5
RUNNER_MAX_TOKENS=4096
RUNNER_TEMPERATURE=0.7
RUNNER_TIMEOUT=120
```

### Config File

Create `~/.deepagents-runner/config.yaml`:

```yaml
default_provider: anthropic
providers:
  anthropic:
    model: claude-sonnet-4-5
    max_tokens: 4096
    temperature: 0.7
  openai:
    model: gpt-4-turbo
    max_tokens: 4096
    temperature: 0.7
```

## Troubleshooting

### API Key Not Found

**Error**: `ProviderNotAvailableError: No API key found`

**Solution**:
```bash
# Check if environment variable is set
echo $ANTHROPIC_API_KEY

# If empty, set it
export ANTHROPIC_API_KEY="sk-ant-..."
```

### Rate Limit Exceeded

**Error**: `RateLimitError: Rate limit exceeded`

**What happens**:
- Runner automatically retries with exponential backoff (2s, 4s)
- Falls back to generic agent if specialized agent keeps failing
- You'll see status: `⚠️ Retry` or `🔀 Fallback` in progress display

**Solution**: Wait a minute and retry, or switch providers

### Feature Context Not Detected

**Error**: Branch doesn't match pattern

**Solution**:
- Ensure branch follows pattern: `[number]-[feature-name]`
- Example: `001-user-auth`, `042-payment-integration`
- Or manually select feature from prompt

### Agent Execution Timeout

**Error**: `TimeoutError: Agent execution exceeded 120s`

**Solution**:
Increase timeout in config:
```bash
export RUNNER_TIMEOUT=300  # 5 minutes
```

## Next Steps

1. **Review Generated Artifacts**: Open `specs/[feature]/spec.md`, `plan.md`, etc.
2. **Customize Agent Definitions**: Edit files in `src/agents/` to tune agent behavior
3. **Run Tests**: `pytest tests/` to verify implementation
4. **Extend with Custom Agents**: Add new agent definition files for specialized needs

## Common Commands Reference

| Command | Purpose | Example |
|---------|---------|---------|
| `/speckit.specify <desc>` | Create specification | `/speckit.specify "Add user authentication"` |
| `/speckit.clarify` | Resolve ambiguities | `/speckit.clarify` |
| `/speckit.plan` | Generate plan | `/speckit.plan` |
| `/speckit.tasks` | Break into tasks | `/speckit.tasks` |
| `/speckit.implement [ids]` | Execute tasks | `/speckit.implement` or `/speckit.implement T001 T002` |
| `/speckit.analyze` | Analyze artifacts | `/speckit.analyze` |
| `/speckit.checklist` | Generate checklist | `/speckit.checklist` |
| `/help` | Show help | `/help` |
| `/status` | Show workflow state | `/status` |
| `/switch <feature>` | Switch feature context | `/switch 002-payment-integration` |
| `/exit` | Exit runner | `/exit` |

## Tips

1. **Work on Feature Branches**: Always create a feature branch first
2. **Use Tab Completion**: Commands support tab completion
3. **Check State**: Use `/status` to see current workflow phase
4. **Review Before Proceeding**: Review outputs at each step before moving forward
5. **Interrupt Safely**: Use Ctrl+C to interrupt long-running commands - state is checkpointed

## Resources

- **Spec Template**: `.specify/templates/spec-template.md`
- **Plan Template**: `.specify/templates/plan-template.md`
- **Agent Definitions**: `src/agents/*.md`
- **Documentation**: `docs/`
- **GitHub Issues**: Report bugs and request features

## Example: Complete Workflow

```bash
# 1. Create feature branch
git checkout -b 003-notification-system

# 2. Launch runner
deepagents-runner

# 3. Specify feature
> /speckit.specify "Build notification system with email, SMS, and push notifications"

# 4. Clarify (if needed)
> /speckit.clarify
# Answer clarification questions

# 5. Generate plan
> /speckit.plan

# 6. Generate tasks
> /speckit.tasks

# 7. Review tasks, then implement
> /speckit.implement

# 8. Verify and commit
> /exit
git add specs/003-notification-system/
git commit -m "Specify and plan notification system"
```

That's it! You're ready to use the DeepAgents Runner for spec-driven development.
