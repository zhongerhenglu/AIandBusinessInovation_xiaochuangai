import logging
from typing import Dict, List, Any, Callable, Optional
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class WorkflowStep:
    step_id: str
    agent_name: str
    task_type: str
    payload: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    priority: int = 0


@dataclass
class Workflow:
    workflow_id: str
    steps: List[WorkflowStep] = field(default_factory=list)
    status: str = "idle"
    results: Dict[str, Any] = field(default_factory=dict)


class Harness:
    def __init__(self, scheduler):
        self.scheduler = scheduler
        self.agents: Dict[str, Any] = {}
        self.workflows: Dict[str, Workflow] = {}
    
    def register_agent(self, agent_name: str, agent_instance):
        self.agents[agent_name] = agent_instance
        self.scheduler.register_agent(agent_name, agent_instance.execute)
        logger.info(f"Agent registered in Harness: {agent_name}")
    
    def create_workflow(self, workflow_id: str, steps: List[WorkflowStep]) -> Workflow:
        workflow = Workflow(workflow_id=workflow_id, steps=steps)
        self.workflows[workflow_id] = workflow
        logger.info(f"Workflow created: {workflow_id}")
        return workflow
    
    async def execute_workflow(self, workflow_id: str, inputs: Dict[str, Any] = None) -> Dict[str, Any]:
        workflow = self.workflows.get(workflow_id)
        if not workflow:
            raise ValueError(f"Workflow not found: {workflow_id}")
        
        workflow.status = "running"
        workflow.results = {}
        
        for step in workflow.steps:
            merged_payload = {**step.payload, **(inputs or {})}
            
            if step.dependencies:
                for dep in step.dependencies:
                    if dep not in workflow.results:
                        raise ValueError(f"Missing dependency result: {dep}")
                    merged_payload[dep] = workflow.results[dep]
            
            agent = self.agents.get(step.agent_name)
            if not agent:
                raise ValueError(f"Agent not found: {step.agent_name}")
            
            logger.info(f"Executing workflow step: {workflow_id}/{step.step_id}")
            result = await agent.execute(step.task_type, merged_payload)
            workflow.results[step.step_id] = result
            inputs = {**(inputs or {}), **result}
        
        workflow.status = "completed"
        logger.info(f"Workflow completed: {workflow_id}")
        return workflow.results
    
    def get_workflow_status(self, workflow_id: str) -> Optional[Workflow]:
        return self.workflows.get(workflow_id)
    
    def list_workflows(self) -> List[str]:
        return list(self.workflows.keys())