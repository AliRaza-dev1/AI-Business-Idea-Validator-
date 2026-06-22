"""
Risk Assessment Agent
"""
from typing import Dict, Any, List
from app.agents.base_agent import BaseAgent

class RiskAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_name="Risk Assessment Agent",
            prompt_filename="risk_analysis.txt"
        )
