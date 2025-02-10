"""
Task Planning Module for JARVIS
Implements ReAct-based planning with chain-of-thought reasoning and self-reflection
"""

import logging
from typing import Dict, List, Any, Optional, TypedDict, Literal
from dataclasses import dataclass
from enum import Enum
from datetime import datetime


class TaskInput(TypedDict):
    """Input for task execution"""
    task_id: str
    description: str
    context: Dict[str, Any]


class TaskState(TypedDict):
    """State for task execution"""
    status: Literal["pending", "in_progress", "completed", "failed", "blocked"]
    current_step: str
    steps_completed: int
    total_steps: int
    history: List[Dict[str, Any]]

from langgraph.graph import StateGraph
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_community.llms import OpenAI

@dataclass
class TaskStep:
    """Represents a single step in a task execution plan"""
    action: str
    thought: str
    observation: Optional[str] = None
    reflection: Optional[str] = None
    status: str = "pending"
    
class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"

class TaskManager:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.llm = OpenAI(openai_api_key="dummy-key")  # Initialize language model
        self.state_graph = self._initialize_state_graph()
        self.active_tasks: Dict[str, List[TaskStep]] = {}
        
    def _initialize_state_graph(self) -> StateGraph:
        """Initialize the state graph for task planning"""
        states = ["start", "analyze", "plan", "execute", "reflect", "complete"]
        
        # Create a StateGraph instance with schema
        graph = StateGraph(
            state_schema=TaskState,
            config_schema=TaskInput,
        )
        
        # Define state functions
        async def analyze(state: TaskState, inputs: TaskInput) -> TaskState:
            state["current_step"] = "analyze"
            return state
            
        async def plan(state: TaskState, inputs: TaskInput) -> TaskState:
            state["current_step"] = "plan"
            return state
            
        async def execute(state: TaskState, inputs: TaskInput) -> TaskState:
            state["current_step"] = "execute"
            state["steps_completed"] += 1
            return state
            
        async def reflect(state: TaskState, inputs: TaskInput) -> TaskState:
            state["current_step"] = "reflect"
            return state
            
        async def complete(state: TaskState, inputs: TaskInput) -> TaskState:
            state["current_step"] = "complete"
            state["status"] = "completed"
            return state
            
        # Create state function mapping
        state_functions = {
            "start": analyze,  # Start is same as analyze
            "analyze": analyze,
            "plan": plan,
            "execute": execute,
            "reflect": reflect,
            "complete": complete
        }
        
        # Add nodes
        for state_name in states:
            graph.add_node(state_name, state_functions[state_name])
            
        # Add edges
        for i in range(len(states) - 1):
            curr_state = states[i]
            next_state = states[i + 1]
            graph.add_edge(curr_state, next_state)
            
        # Add conditional transitions
        graph.add_edge("reflect", "plan")  # For replanning if needed
        graph.add_edge("execute", "analyze")  # For handling unexpected situations
            
        return graph
        
    async def create_task(self, 
                         task_description: str, 
                         context: Dict[str, Any]) -> str:
        """
        Create a new task with ReAct-based planning
        
        Args:
            task_description: Description of the task to be performed
            context: Additional context for task planning
            
        Returns:
            task_id: Unique identifier for the created task
        """
        task_id = self._generate_task_id()
        
        try:
            # Generate initial thought process
            initial_thought = await self._generate_thought(task_description, context)
            
            # Create initial plan
            plan = await self._create_plan(initial_thought, context)
            
            # Store task
            self.active_tasks[task_id] = plan
            
            self.logger.info(f"Created task {task_id}: {task_description}")
            return task_id
            
        except Exception as e:
            self.logger.error(f"Failed to create task: {e}")
            raise
            
    async def execute_task(self, task_id: str) -> Dict[str, Any]:
        """
        Execute a planned task
        
        Args:
            task_id: ID of the task to execute
            
        Returns:
            Dictionary containing execution results
        """
        if task_id not in self.active_tasks:
            raise ValueError(f"Task {task_id} not found")
            
        try:
            steps = self.active_tasks[task_id]
            results = []
            
            for step in steps:
                # Execute step
                result = await self._execute_step(step)
                
                # Reflect on execution
                reflection = await self._reflect_on_step(result)
                
                # Update step with results
                step.observation = result
                step.reflection = reflection
                step.status = "completed"
                
                results.append({
                    "action": step.action,
                    "thought": step.thought,
                    "observation": result,
                    "reflection": reflection
                })
                
                # Check if replanning is needed
                if await self._needs_replanning(reflection):
                    new_plan = await self._replan_task(task_id, results)
                    steps.extend(new_plan)
                    
            return {"status": "success", "results": results}
            
        except Exception as e:
            self.logger.error(f"Failed to execute task {task_id}: {e}")
            return {"status": "failed", "error": str(e)}
            
    async def _generate_thought(self, 
                              task: str, 
                              context: Dict[str, Any]) -> str:
        """Generate thought process for task planning"""
        prompt = PromptTemplate(
            template="Task: {task}\nContext: {context}\nThink step by step about how to accomplish this task:",
            input_variables=["task", "context"]
        )
        
        chain = LLMChain(llm=self.llm, prompt=prompt)
        thought = await chain.arun(task=task, context=str(context))
        return thought
        
    async def _create_plan(self, 
                          thought: str, 
                          context: Dict[str, Any]) -> List[TaskStep]:
        """Create execution plan based on thought process"""
        # Implementation of plan creation
        plan = []
        # Add plan creation logic here
        return plan
        
    async def _execute_step(self, step: TaskStep) -> str:
        """Execute a single task step"""
        # Implementation of step execution
        return "Step execution result"
        
    async def _reflect_on_step(self, result: str) -> str:
        """Reflect on step execution results"""
        # Implementation of reflection
        return "Step reflection"
        
    async def _needs_replanning(self, reflection: str) -> bool:
        """Determine if task needs replanning"""
        # Implementation of replanning decision
        return False
        
    async def _replan_task(self, 
                          task_id: str, 
                          previous_results: List[Dict[str, Any]]) -> List[TaskStep]:
        """Replan task based on previous results"""
        # Implementation of task replanning
        return []
        
    def _generate_task_id(self) -> str:
        """Generate unique task ID"""
        return f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
    def get_task_status(self, task_id: str) -> TaskStatus:
        """Get current status of a task"""
        if task_id not in self.active_tasks:
            raise ValueError(f"Task {task_id} not found")
            
        steps = self.active_tasks[task_id]
        if not steps:
            return TaskStatus.PENDING
            
        completed = sum(1 for step in steps if step.status == "completed")
        total = len(steps)
        
        if completed == 0:
            return TaskStatus.PENDING
        elif completed == total:
            return TaskStatus.COMPLETED
        else:
            return TaskStatus.IN_PROGRESS