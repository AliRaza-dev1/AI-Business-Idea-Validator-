"""
Feasibility Analysis Service — Upgraded wrapper executing GrowthAgent and preserving legacy keys.
"""
from typing import Dict, Any
from app.agents.growth_agent import GrowthAgent

class FeasibilityAnalysisService:
    def __init__(self):
        self.agent = GrowthAgent()
        
    async def analyze_feasibility(self, idea_context: str) -> Dict[str, Any]:
        """Runs the growth agent pipeline"""
        result = await self.agent.execute(
            idea_context=idea_context,
            query_text="Scalability, viral factors and investor readiness"
        )
        score_val = result.get("score", 10)
        # Convert 15-point scale to 10-point scale
        legacy_score = float(score_val) / 1.5
        
        result["feasibility_score"] = legacy_score
        result["technical_requirements"] = result.get("scalability_factors", "Scalability factors uncalculated.")
        result["full_analysis"] = result.get("reasoning", "Detailed analysis.")
        return result
