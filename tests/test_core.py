"""
Core functionality tests for JARVIS
"""

import pytest
import asyncio
from pathlib import Path
import yaml
from datetime import datetime, timedelta

from jarvis.core.memory import MemoryCore
from jarvis.core.planner import TaskManager
from jarvis.core.system import SystemCore
from jarvis.core.persona import PersonaEngine
from jarvis.modules.io_manager import InputOutputManager
from jarvis.modules.scheduler import TimeManager
from jarvis.modules.code_evolver import CodeEvolver
from jarvis.utils.data_bus import DataHub

# Load test configuration
# Core component fixtures
@pytest.fixture
def memory_core(memory_config):
    return MemoryCore(memory_config)

@pytest.fixture
def task_manager(task_config):
    return TaskManager(task_config)

@pytest.fixture
def system_core(system_config):
    return SystemCore(system_config)

@pytest.fixture
def persona_engine(persona_config):
    return PersonaEngine(persona_config)

# Memory tests
@pytest.mark.asyncio
async def test_memory_storage(memory_core):
    # Test short-term memory
    data = {"type": "test", "content": "test data"}
    result = await memory_core.store(data, "short_term")
    assert result == True
    
    # Test retrieval
    retrieved = await memory_core.retrieve("test", "short_term")
    assert retrieved.get("short_term") is not None

# Task Manager tests
@pytest.mark.asyncio
async def test_task_creation(task_manager):
    # Skip test that requires OpenAI API
    pytest.skip("Skipping test that requires OpenAI API")

# System Core tests
@pytest.mark.asyncio
async def test_system_command(system_core):
    result = await system_core.execute_command("echo test")
    assert result["status"] == "success"
    assert "test" in result["stdout"]

# Persona Engine tests
def test_persona_adaptation(persona_engine):
    context = {
        "formality": "high",
        "user_emotion": "happy"
    }
    initial_style = persona_engine.get_response_style()
    persona_engine.adapt_persona(context)
    new_style = persona_engine.get_response_style()
    assert new_style != initial_style

# Integration tests
@pytest.mark.asyncio
async def test_end_to_end_interaction(memory_core, task_manager, system_core, persona_engine):
    # Skip OpenAI API calls
    pytest.skip("Skipping end-to-end test that requires OpenAI API")

if __name__ == "__main__":
    pytest.main([__file__])