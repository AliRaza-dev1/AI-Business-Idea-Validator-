"""
Financial Feasibility Agent
"""
from typing import Dict, Any, List
from app.agents.base_agent import BaseAgent

class FinancialAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_name="Financial Feasibility Agent",
            prompt_filename="financial_analysis.txt"
        )
