"""
DeepAgents Runner - Interactive terminal for SpecKit commands

This package provides an interactive terminal application that executes SpecKit commands
using the DeepAgents library for agent orchestration, with support for specialized
Ambient agents and configurable LLM providers.
"""

__version__ = "1.0.0"
__author__ = "DeepAgents Runner Contributors"

# Export main components
from deepagents_runner.core.agents import AgentManager
from deepagents_runner.core.state import StateManager
from deepagents_runner.core.context import ContextDetector
from deepagents_runner.terminal.repl import REPLSession

__all__ = [
    "AgentManager",
    "StateManager",
    "ContextDetector",
    "REPLSession",
    "__version__",
]
