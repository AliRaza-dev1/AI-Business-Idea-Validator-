"""
Market Intelligence Agent
"""
from typing import Dict, Any, List
from app.agents.base_agent import BaseAgent

class MarketAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_name="Market Intelligence Agent",
            prompt_filename="market_analysis.txt"
        )
