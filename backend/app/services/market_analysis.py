"""
Market Analysis Service — Upgraded wrapper that executes Market Intelligence Agent and preserves legacy mock structures.
"""
from typing import Dict, Any
from app.agents.market_agent import MarketAgent

class MarketAnalysisService:
    def __init__(self):
        self.agent = MarketAgent()
        
    async def analyze_market(self, idea_context: str) -> Dict[str, Any]:
        """Runs the market intelligence agent pipeline"""
        result = await self.agent.execute(
            idea_context=idea_context,
            query_text="Market size, TAM, SAM, SOM, demographics and target demand"
        )
        # Inject legacy fields to ensure full compatibility with tests and old report layouts
        score_val = result.get("score", 15)
        # Convert 25-point scale to 10-point scale for legacy compatibility
        legacy_score = float(score_val) / 2.5
        
        result["market_score"] = legacy_score
        result["market_size"] = result.get("tam_sam_som", {}).get("tam", "TAM estimation uncalculated.")
        result["full_analysis"] = result.get("reasoning", "Detailed analysis.")
        return result
