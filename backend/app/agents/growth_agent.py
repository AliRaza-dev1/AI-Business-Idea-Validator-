"""
Growth Potential Agent
"""
from typing import Dict, Any, List
from app.agents.base_agent import BaseAgent

class GrowthAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_name="Growth Potential Agent",
            prompt_filename="growth_analysis.txt"
        )
