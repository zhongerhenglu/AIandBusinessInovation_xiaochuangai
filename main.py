import asyncio
import logging
from harness.scheduler import CentralScheduler, Task
from harness.harness import Harness, WorkflowStep
from vertical_agents.alpha_agent import AlphaAgent
from vertical_agents.factor_agent import FactorAgent
from vertical_agents.risk_agent import RiskAgent
from vertical_agents.review_agent import ReviewAgent
from utils.logging_utils import setup_logger

logger = setup_logger("super_agent_main")


async def main():
    logger.info("Starting Super Agent System...")
    
    scheduler = CentralScheduler()
    harness = Harness(scheduler)
    
    alpha_agent = AlphaAgent()
    factor_agent = FactorAgent()
    risk_agent = RiskAgent()
    review_agent = ReviewAgent()
    
    harness.register_agent("AlphaAgent", alpha_agent)
    harness.register_agent("FactorAgent", factor_agent)
    harness.register_agent("RiskAgent", risk_agent)
    harness.register_agent("ReviewAgent", review_agent)
    
    workflow_steps = [
        WorkflowStep(
            step_id="market_analysis",
            agent_name="AlphaAgent",
            task_type="market_analysis",
            priority=1
        ),
        WorkflowStep(
            step_id="factor_research",
            agent_name="FactorAgent",
            task_type="research_factors",
            priority=2
        ),
        WorkflowStep(
            step_id="trade_decision",
            agent_name="AlphaAgent",
            task_type="trade_decision",
            dependencies=["market_analysis", "factor_research"],
            priority=3
        ),
        WorkflowStep(
            step_id="risk_check",
            agent_name="RiskAgent",
            task_type="risk_check",
            dependencies=["trade_decision"],
            priority=4
        )
    ]
    
    workflow = harness.create_workflow("trading_workflow", workflow_steps)
    
    logger.info("Executing trading workflow...")
    results = await harness.execute_workflow("trading_workflow", {"timestamp": "2024-01-15"})
    
    logger.info("Workflow completed!")
    for step_id, result in results.items():
        logger.info(f"Step {step_id}: {result}")
    
    await scheduler.shutdown()
    
    logger.info("Super Agent System shutdown complete.")


if __name__ == "__main__":
    asyncio.run(main())