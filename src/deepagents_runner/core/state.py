"""State management for workflow persistence."""

from pathlib import Path
from datetime import datetime
from typing import Optional

from deepagents_runner.models.workflow import WorkflowState, CommandRecord
from deepagents_runner.models import WorkflowPhase, CommandType
from deepagents_runner.utils.files import read_json, write_json
from deepagents_runner.utils.exceptions import StateLoadError, StateSaveError


class StateManager:
    """Manages workflow state persistence."""

    STATE_FILENAME = "workflow.json"

    def __init__(self, feature_spec_dir: Path):
        """Initialize state manager.

        Args:
            feature_spec_dir: Directory containing feature specification
        """
        self.feature_spec_dir = feature_spec_dir
        self.state_dir = feature_spec_dir / ".state"
        self.state_file = self.state_dir / self.STATE_FILENAME

    def load_state(self, feature_id: str) -> WorkflowState:
        """Load workflow state from disk.

        Args:
            feature_id: Feature identifier

        Returns:
            WorkflowState object

        Raises:
            StateLoadError: If state cannot be loaded
        """
        if not self.state_file.exists():
            # Create new state
            return WorkflowState(
                feature_id=feature_id,
                current_phase=WorkflowPhase.DRAFT,
                state_file=self.state_file
            )

        try:
            data = read_json(self.state_file)

            # Parse command records
            completed_commands = [
                CommandRecord(
                    command=CommandType(rec['command']),
                    timestamp=datetime.fromisoformat(rec['timestamp'])
                )
                for rec in data.get('completed_commands', [])
            ]

            return WorkflowState(
                feature_id=data['feature_id'],
                current_phase=WorkflowPhase(data['current_phase']),
                completed_commands=completed_commands,
                suggested_next=CommandType(data['suggested_next']) if data.get('suggested_next') else None,
                context_data=data.get('context_data', {}),
                state_file=self.state_file,
                last_checkpoint=datetime.fromisoformat(data['last_checkpoint']),
                last_updated=datetime.fromisoformat(data['last_updated'])
            )
        except Exception as e:
            raise StateLoadError(f"Failed to load state: {e}")

    def save_state(self, state: WorkflowState) -> None:
        """Save workflow state to disk.

        Args:
            state: WorkflowState to persist

        Raises:
            StateSaveError: If state cannot be saved
        """
        # Update timestamp
        state.last_updated = datetime.now()

        # Convert to dict
        data = {
            'feature_id': state.feature_id,
            'current_phase': state.current_phase.value,
            'completed_commands': [
                {
                    'command': cmd.command.value,
                    'timestamp': cmd.timestamp.isoformat()
                }
                for cmd in state.completed_commands
            ],
            'suggested_next': state.suggested_next.value if state.suggested_next else None,
            'context_data': state.context_data,
            'last_checkpoint': state.last_checkpoint.isoformat(),
            'last_updated': state.last_updated.isoformat()
        }

        write_json(self.state_file, data)

    def record_command(self, state: WorkflowState, command: CommandType) -> None:
        """Record a completed command.

        Args:
            state: Current workflow state
            command: Command that was executed
        """
        state.completed_commands.append(
            CommandRecord(command=command, timestamp=datetime.now())
        )
        self.save_state(state)

    def update_phase(self, state: WorkflowState, phase: WorkflowPhase) -> None:
        """Update current workflow phase.

        Args:
            state: Current workflow state
            phase: New phase
        """
        state.current_phase = phase
        state.last_checkpoint = datetime.now()
        self.save_state(state)
