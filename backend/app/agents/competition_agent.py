"""
Competition Analysis Agent
"""
from typing import Dict, Any, List
from app.agents.base_agent import BaseAgent

class CompetitionAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_name="Competition Analysis Agent",
            prompt_filename="competition_analysis.txt"
        )
