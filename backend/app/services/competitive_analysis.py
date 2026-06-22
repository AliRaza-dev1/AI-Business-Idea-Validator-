"""
Competitive Analysis Service — Upgraded wrapper executing CompetitionAgent and preserving legacy keys.
"""
from typing import Dict, Any
from app.agents.competition_agent import CompetitionAgent

class CompetitiveAnalysisService:
    def __init__(self):
        self.agent = CompetitionAgent()
        
    async def analyze_competition(self, idea_context: str) -> Dict[str, Any]:
        """Runs the competition agent pipeline"""
        result = await self.agent.execute(
            idea_context=idea_context,
            query_text="Competitors, unique value proposition, positioning, moats and barriers"
        )
        score_val = result.get("score", 12)
        # Convert 20-point scale to 10-point scale
        legacy_score = float(score_val) / 2.0
        
        result["competitive_score"] = legacy_score
        result["competitor_landscape"] = result.get("competitor_landscape", "Uncalculated competitor landscape.")
        result["competitive_advantages"] = result.get("competitive_advantages", "Uncalculated advantages.")
        result["market_positioning"] = result.get("market_positioning", "Uncalculated positioning.")
        result["differentiation"] = result.get("differentiation", "Uncalculated differentiation.")
        return result
