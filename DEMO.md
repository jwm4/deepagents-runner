# DeepAgents Runner - Minimal Prototype Demo

## What Works

The minimal working prototype successfully demonstrates:

### 1. Interactive Terminal Launch

```bash
deepagents-runner
```

**Shows:**
- Beautiful Rich-formatted banner
- Auto-detected feature context from git branch (`001-deepagents-runner`)
- Current workflow state (phase: draft, commands: 0)
- Table of available SpecKit commands
- Interactive prompt

### 2. Built-in Commands

Try these commands in the REPL:

- `help` - Show available commands
- `context` - Display current feature context and workflow state
- `refresh` - Reload context from git branch
- `exit` or `quit` or `q` - Exit the REPL

### 3. Context Auto-Detection

The runner automatically detects your feature from the git branch pattern:
- Branch: `001-deepagents-runner`
- Detected Feature ID: `001`
- Detected Feature Name: `deepagents-runner`
- Status: `tasked` (because `tasks.md` exists)

### 4. State Persistence

Workflow state is saved to:
```
specs/001-deepagents-runner/.state/workflow.json
```

Contains:
- Current workflow phase
- Completed commands with timestamps
- Suggested next command
- Context data

### 5. Agent Definitions

Agent definitions loaded from markdown files in `src/agents/`:
- `archie-architect.md` - System architecture specialist
- `neil-test-engineer.md` - Testing and validation expert
- `generic-agent.md` - Fallback general-purpose agent

Each agent has:
- YAML frontmatter with capabilities and priority
- Markdown prompt content

## What Doesn't Work Yet

These are placeholder implementations in the minimal prototype:

### SpecKit Command Execution

All `/speckit.*` commands show a progress bar but don't actually execute:
- `/speckit.specify`
- `/speckit.plan`
- `/speckit.tasks`
- etc.

**Why:** Requires integration with:
- DeepAgents library for agent orchestration
- LLM provider clients (Anthropic/OpenAI)
- Command-specific execution logic
- Agent selection and task decomposition

## Example Session

```bash
$ deepagents-runner

╭──────────────────────────────────────────────────────────────────────────────╮
│ ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓ │
│ ┃                            DeepAgents Runner                             ┃ │
│ ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛ │
│                                                                              │
│ An interactive runner for SpecKit commands powered by DeepAgents.            │
╰──────────────────────────────────────────────────────────────────────────────╯

╭────────────────────────────── Current Context ───────────────────────────────╮
│   Feature:    001-deepagents-runner                                          │
│   Branch:     001-deepagents-runner                                          │
│   Status:     tasked                                                         │
╰──────────────────────────────────────────────────────────────────────────────╯

╭─────────────────────────────── Workflow State ───────────────────────────────╮
│   Phase:       draft                                                         │
│   Commands:    0                                                             │
╰──────────────────────────────────────────────────────────────────────────────╯

╭───────────────────────────── Available Commands ─────────────────────────────╮
│ ... table of commands ...                                                   │
╰──────────────────────────────────────────────────────────────────────────────╯

ℹ Type a command or 'help' for assistance. Press Ctrl+C to exit.

> help
╭───────────────────────────── Available Commands ─────────────────────────────╮
│ ... shows commands again ...                                                │
╰──────────────────────────────────────────────────────────────────────────────╯

> context
╭────────────────────────────── Current Context ───────────────────────────────╮
│   Feature:    001-deepagents-runner                                          │
│   Branch:     001-deepagents-runner                                          │
│   Status:     tasked                                                         │
╰──────────────────────────────────────────────────────────────────────────────╯

╭─────────────────────────────── Workflow State ───────────────────────────────╮
│   Phase:       draft                                                         │
│   Commands:    0                                                             │
╰──────────────────────────────────────────────────────────────────────────────╯

> /speckit.specify
ℹ Executing: /speckit.specify
⠋ Running /speckit.specify... ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100%
✓ Command completed: /speckit.specify
⚠ Note: Command execution is not yet implemented in this prototype.

> exit
ℹ Goodbye!
```

## Architecture Highlights

### Component Structure

```
src/deepagents_runner/
├── core/
│   ├── agents.py       # AgentManager - loads agent definitions
│   ├── context.py      # ContextDetector - auto-detects features
│   └── state.py        # StateManager - persists workflow state
├── models/
│   ├── __init__.py     # Enums (FeatureStatus, CommandType, WorkflowPhase)
│   ├── feature.py      # Feature model with validation
│   └── workflow.py     # WorkflowState model
├── terminal/
│   ├── ui.py           # TerminalUI - Rich-based components
│   └── repl.py         # REPLSession - interactive loop
├── utils/
│   ├── exceptions.py   # Exception hierarchy
│   ├── files.py        # Atomic JSON I/O
│   └── git.py          # Git operations
└── cli.py              # Entry point
```

### Key Design Patterns

**1. Context Detection**
- Parses git branch with regex `(\d{3})-([a-z0-9-]+)`
- Determines status from filesystem (spec.md → plan.md → tasks.md)
- Creates Feature object with all paths

**2. State Persistence**
- Atomic writes using temp file + rename
- JSON serialization with datetime handling
- Separate state directory (`.state/`) per feature

**3. Agent Management**
- Loads agents from markdown with YAML frontmatter
- Capability-based matching with priority scoring
- Generic agent fallback

**4. Terminal UI**
- Rich library for formatting
- Panels, tables, markdown rendering
- Progress indicators for long operations

## Next Steps

To complete the MVP (Phase 3), implement:

1. **CommandExecutor** - Execute SpecKit commands using DeepAgents
2. **LLM Providers** - Anthropic and OpenAI client integration
3. **Agent Orchestration** - Connect agent selection to DeepAgents execution
4. **Retry Logic** - Exponential backoff and fallback to generic agent
5. **Real Command Execution** - Replace REPL placeholder with actual execution

See `specs/001-deepagents-runner/tasks.md` for full task list.
