import asyncio
import logging
from harness.scheduler import CentralScheduler
from harness.harness import Harness, WorkflowStep
from vertical_agents.alpha_agent import AlphaAgent
from vertical_agents.factor_agent import FactorAgent
from vertical_agents.risk_agent import RiskAgent
from vertical_agents.review_agent import ReviewAgent
from utils.logging_utils import setup_logger

logger = setup_logger("workflow_runner")


async def run_full_trading_cycle():
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
    
    steps = [
        WorkflowStep(
            step_id="collect_data",
            agent_name="AlphaAgent",
            task_type="market_analysis",
            priority=1
        ),
        WorkflowStep(
            step_id="factor_analysis",
            agent_name="FactorAgent",
            task_type="analyze_factors",
            priority=2
        ),
        WorkflowStep(
            step_id="make_decision",
            agent_name="AlphaAgent",
            task_type="trade_decision",
            dependencies=["collect_data", "factor_analysis"],
            priority=3
        ),
        WorkflowStep(
            step_id="check_risk",
            agent_name="RiskAgent",
            task_type="risk_check",
            dependencies=["make_decision"],
            priority=4
        ),
        WorkflowStep(
            step_id="review_strategy",
            agent_name="ReviewAgent",
            task_type="generate_replay_data",
            dependencies=["check_risk"],
            priority=5
        )
    ]
    
    workflow = harness.create_workflow("full_trading_cycle", steps)
    results = await harness.execute_workflow("full_trading_cycle", {"timestamp": "2024-01-15"})
    
    return results


if __name__ == "__main__":
    results = asyncio.run(run_full_trading_cycle())
    print("=== Full Trading Cycle Results ===")
    for step, result in results.items():
        print(f"\n{step}:")
        print(result)