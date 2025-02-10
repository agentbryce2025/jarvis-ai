"""
JARVIS API Interface
Provides HTTP API endpoints for interacting with JARVIS
"""

from fastapi import FastAPI, HTTPException
from typing import Dict, Any
from pydantic import BaseModel
import logging
import os
import yaml
from pathlib import Path

app = FastAPI(title="JARVIS API")
logger = logging.getLogger(__name__)

# Load configuration
CONFIG_PATH = Path(__file__).parent / "config" / "config.yaml"
with open(CONFIG_PATH, "r") as f:
    config = yaml.safe_load(f)

# Initialize components
try:
    from jarvis.core.memory import MemoryCore
    from jarvis.core.planner import TaskManager, TaskStatus
    from jarvis.core.system import SystemCore
    from jarvis.core.persona import PersonaEngine
    from jarvis.modules.io_manager import InputOutputManager
    from jarvis.modules.scheduler import TimeManager
    from jarvis.modules.code_evolver import CodeEvolver
    from jarvis.utils.data_bus import DataHub

    memory_config = {
        "short_term": {
            "type": "redis",
            "ttl": 1800,
            "host": "localhost",
            "port": 6379,
            "db": 0
        },
        "mid_term": {
            "type": "chromadb",
            "collection": "recent_interactions",
            "retention_days": 30
        },
        "long_term": {
            "type": "postgresql",
            "table": "historical_memory",
            "connection_string": "sqlite:///jarvis_memory.db"
        }
    }
    memory = MemoryCore(memory_config)
    planner = TaskManager(config["task_planning"])
    system = SystemCore(config["security"])
    persona = PersonaEngine(config["personality"])
    io_manager = InputOutputManager(config["multimodal"])
    scheduler = TimeManager(config["scheduler"])
    code_evolver = CodeEvolver()
    data_bus = DataHub()

    logger.info("Core components initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize core components: {e}")
    raise

# Request/Response models
class ChatRequest(BaseModel):
    message: str
    context: Dict[str, Any] = {}

class ChatResponse(BaseModel):
    response: str
    task_id: str = None
    context: Dict[str, Any] = {}
    status: str = "success"

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """
    Process a chat message
    
    Args:
        request: Input message and context
        
    Returns:
        Generated response with task information
    """
    try:
        # Process input
        input_result = await io_manager.process_input(request.message)
        
        # Create task
        task_id = await planner.create_task(request.message, request.context)
        
        # Execute task
        result = await planner.execute_task(task_id)
        
        # Generate response
        output = await io_manager.generate_output(
            str(result["results"][-1]["observation"])
            if result["results"]
            else "Task completed successfully"
        )
        
        # Store in memory
        await memory.store({
            "input": request.message,
            "task_id": task_id,
            "result": result,
            "context": request.context
        })
        
        # Update persona
        persona.adapt_persona({
            "input": request.message,
            "result": result,
            "context": request.context
        })
        
        return ChatResponse(
            response=output["content"],
            task_id=task_id,
            context=request.context
        )
        
    except Exception as e:
        logger.error(f"Chat request failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@app.get("/status")
async def status() -> Dict[str, Any]:
    """
    Get system status
    
    Returns:
        Dictionary containing system status information
    """
    try:
        return await system.check_system_status()
    except Exception as e:
        logger.error(f"Status check failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@app.get("/tasks/{task_id}")
async def get_task(task_id: str) -> Dict[str, Any]:
    """
    Get task status and results
    
    Args:
        task_id: ID of task to look up
        
    Returns:
        Dictionary containing task information
    """
    try:
        status = planner.get_task_status(task_id)
        return {
            "status": status.value,
            "task_id": task_id,
            "completed": status == TaskStatus.COMPLETED
        }
    except ValueError:
        raise HTTPException(
            status_code=404,
            detail=f"Task {task_id} not found"
        )
    except Exception as e:
        logger.error(f"Failed to get task {task_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )