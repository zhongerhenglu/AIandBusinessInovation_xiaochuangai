# Super Agent Project Structure

## Overview

This project implements a multi-agent trading system based on Beyond Gradients + Beyond RAG + Harness architecture. The system features a centralized scheduler, multiple vertical agents, and comprehensive knowledge management.

## Directory Structure

```
super_agent/
├── __init__.py              # Package initialization
├── config.py                # System configuration (LLM, data, risk, agent)
├── requirements.txt         # Python dependencies
├── README.md                # Project README
├── main.py                  # Main entry point
├── run_workflow.py          # Workflow execution script
├── PROJECT_STRUCTURE.md     # This file
├── start_notification_service.py  # Notification service starter
├── logs/                    # Log files
├── data/                    # Data cache
├── output/                  # Output files (charts, reports)
├── perception/              # Perception Layer
│   ├── __init__.py
│   ├── data_providers.py    # Data providers (OHLC, News, Fundamental, OnChain, Sentiment)
│   ├── feature_engine.py    # Feature extraction (technical, statistical, sentiment)
│   ├── vector_store.py      # Vector encoding and storage
│   └── perception_layer.py  # Unified perception layer
├── brain/                   # Brain Layer
│   ├── __init__.py
│   ├── agent_base.py        # Base agent class
│   ├── llm_client.py        # LLM client (GPT-4o, DeepSeek, Kimi, GLM)
│   ├── reasoning_chain.py   # Reasoning chain for decision making
│   └── brain_layer.py       # Main brain layer with memory
├── action/                  # Action Layer
│   ├── __init__.py
│   ├── risk_manager.py      # Risk management and constraints
│   ├── position_manager.py  # Position calculation and tracking
│   ├── execution_logger.py  # Execution logging
│   └── action_layer.py      # Unified action layer
├── knowledge/               # Beyond RAG Knowledge Layer
│   ├── __init__.py
│   ├── document_store.py    # Document storage
│   ├── vector_store.py      # Chroma vector store
│   ├── structured_wiki.py   # Structured wiki (entity/topic/decision pages)
│   ├── knowledge_schema.py  # Schema validation
│   ├── knowledge_base.py    # Unified knowledge base
│   ├── versioned_wiki.py    # Versioned wiki with git-style version control
│   ├── knowledge_graph.py   # Knowledge graph for relationship modeling
│   └── enhanced_knowledge_base.py  # Enhanced knowledge base with wiki+graph+RAG
├── factor_library/          # Factor Library (AQRA-style)
│   ├── __init__.py
│   ├── factor_library.py    # Factor definitions and calculations
│   └── factor_analyzer.py   # IC/IR analysis and factor evaluation
├── vertical_agents/         # Vertical Research Agents
│   ├── __init__.py
│   ├── alpha_agent.py       # Alpha strategy execution agent
│   ├── factor_agent.py      # Factor research agent
│   ├── risk_agent.py        # Risk management agent
│   ├── review_agent.py      # Review and optimization agent
│   └── research_agent.py    # Research report analysis agent
├── quant/                   # Quantitative Analysis Module
│   ├── __init__.py
│   ├── quant_analyzer.py    # Quantitative analysis (periods, CSI300, factors)
│   ├── data_simulator.py    # Data simulation (realistic price generation)
│   ├── macro_scenario_analyzer.py  # Macro scenario analysis
│   └── chart_generator.py   # Statistical chart generation
├── research/                # Research Report Analysis Module
│   ├── __init__.py
│   ├── document_parser.py   # Multi-format document parser (PDF/DOCX/TXT)
│   ├── keyword_extractor.py # Financial keyword extraction
│   ├── chart_analyzer.py    # Table and chart analysis
│   └── report_fetcher.py    # Report fetching and management
├── notification/            # Notification Service Module
│   ├── __init__.py
│   ├── message_sender.py    # PushPlus message sender
│   ├── task_scheduler.py    # Scheduled task scheduler
│   ├── message_queue.py     # Message queue management
│   ├── market_notification_service.py  # Market notification service
│   └── knowledge_notification_service.py  # Knowledge base update notification service
└── utils/                   # Utilities
    ├── __init__.py
    ├── logging_utils.py     # Logging setup
    ├── data_utils.py        # Data loading/saving
    └── time_utils.py        # Time utilities
```

## Core Components

### Central Scheduler (`harness/scheduler.py`)
- Manages task queue with priority
- Supports task dependencies
- Tracks task status (pending/running/completed/failed)
- Async task processing

### Harness Orchestration (`harness/harness.py`)
- Registers and manages agents
- Creates and executes workflows
- Handles step dependencies and data flow
- Supports workflow status tracking

### Vertical Agents (`vertical_agents/`)

| Agent | Responsibility | Task Types |
|-------|---------------|------------|
| **AlphaAgent** | Strategy execution | market_analysis, trade_decision, strategy_review |
| **FactorAgent** | Factor research | calculate_factor, analyze_factors, deduplicate_factors, research_factors |
| **RiskAgent** | Risk management | risk_check, portfolio_risk, drawdown_monitor |
| **ReviewAgent** | Review & optimization | generate_replay_data, build_codex_prompt, optimize_strategy |
| **ResearchAgent** | Report analysis | fetch_reports, analyze_report, extract_keywords, analyze_charts, summarize_report, batch_analyze |

### Factor Library (`factor_library/`)

**Factor Categories:**
- Momentum: roc_5, roc_20, roc_60, ma_cross
- Value: pe_ratio, pb_ratio, ev_ebitda, dividend_yield
- Quality: roe, roa, profit_margin, debt_ratio
- Volatility: std_20, atr, beta, downside_deviation
- Volume: volume_ratio, vwap, money_flow

**Analysis Metrics:**
- IC (Information Coefficient)
- IR (Information Ratio)

### Beyond RAG Knowledge Base (`knowledge/`)

**Wiki Page Types:**
- Entity Page: Stock/company/factor details
- Topic Page: Strategy/method/approach knowledge
- Comparison Page: Multi-entity comparison
- Decision Page: Trading decision records
- Index Page: Knowledge navigation
- Log Page: Change tracking

### Quantitative Analysis (`quant/`)

**Key Features:**
- Period analysis (2024H2, 2025H1, 2025H2, 2026H1, 2026H2)
- CSI 300 composition analysis
- Factor IC analysis
- Trend prediction
- Strategy backtesting
- Macro scenario analysis

### Research Analysis (`research/`)

**Key Features:**
- Multi-format document parsing
- Financial keyword extraction
- Table and chart analysis
- Report fetching and management

### Notification Service (`notification/`)

**Key Features:**
- PushPlus message sending
- Scheduled tasks (daily, weekly)
- Message queue management
- Market notifications (daily/weekly/monthly/half-yearly reports)

## Workflow Example

```python
async def main():
    scheduler = CentralScheduler()
    harness = Harness(scheduler)
    
    harness.register_agent("AlphaAgent", AlphaAgent())
    harness.register_agent("FactorAgent", FactorAgent())
    harness.register_agent("RiskAgent", RiskAgent())
    harness.register_agent("ReviewAgent", ReviewAgent())
    
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
    
    harness.create_workflow("trading_workflow", workflow_steps)
    results = await harness.execute_workflow("trading_workflow", {"timestamp": "2024-01-15"})
```

## Architecture Principles

1. **Human-in-the-Loop**: User as central scheduler and direction controller
2. **Multi-Agent Collaboration**: Specialized vertical agents for different domains
3. **Beyond RAG**: Structured knowledge management with wiki pages
4. **Heuristic Learning**: Rule-based reasoning with LLM enhancement
5. **Risk-Aware**: Comprehensive risk management at every step
6. **Factor-Driven**: AQRA-style factor research and evaluation
7. **Research-Enabled**: Comprehensive report analysis capabilities
8. **Notification-Ready**: Automated market notifications

## Running the System

```bash
cd super_agent
pip install -r requirements.txt
python main.py
```

## Environment Variables

```bash
export OPENAI_API_KEY=your_key
export DEEPSEEK_API_KEY=your_key
export KIMI_API_KEY=your_key
export GLM_API_KEY=your_key
```

## Key Features

- ✅ Centralized task scheduler with priority queue
- ✅ Multi-agent workflow orchestration
- ✅ Comprehensive factor library with 15+ factors
- ✅ Factor IC/IR analysis and deduplication
- ✅ Beyond RAG knowledge base with structured wiki
- ✅ Risk management with multiple constraints
- ✅ Real-time market data simulation
- ✅ LLM integration for enhanced reasoning
- ✅ Async workflow execution
- ✅ Detailed logging and metrics
- ✅ Multi-format document parsing (PDF/DOCX/TXT)
- ✅ Financial keyword extraction and entity recognition
- ✅ Table and chart analysis
- ✅ Report fetching and management
- ✅ Quantitative analysis (periods, CSI300, factors)
- ✅ Macro scenario analysis
- ✅ Statistical chart generation
- ✅ PushPlus notification service
- ✅ Scheduled tasks (daily/weekly)
- ✅ Message queue management

## Test Scripts

| Script | Description |
|--------|-------------|
| `test_quant_analysis.py` | Quantitative analysis tests |
| `test_research.py` | Research report analysis tests |
| `test_scenario_analysis.py` | Macro scenario analysis tests |
| `test_notification.py` | Notification service tests |

## Output Files

| File | Description |
|------|-------------|
| `output/period_returns.png` | Period return comparison chart |
| `output/equity_curve.png` | Equity curve chart |
| `output/factor_ic.png` | Factor IC analysis chart |
| `output/csi300_composition.png` | CSI 300 composition chart |
| `output/sector_distribution.png` | Sector distribution chart |
| `output/statistics_summary.png` | Statistics summary table |
| `output/daily_report_YYYY-MM-DD.json` | Daily report data |
| `output/scenario_analysis_2026H2.json` | Scenario analysis report |