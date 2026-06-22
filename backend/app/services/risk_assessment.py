"""
Risk Assessment Service — Upgraded wrapper executing RiskAgent and preserving legacy keys.
"""
from typing import Dict, Any
from app.agents.risk_agent import RiskAgent

class RiskAssessmentService:
    def __init__(self):
        self.agent = RiskAgent()
        
    async def assess_risks(self, idea_context: str) -> Dict[str, Any]:
        """Runs the risk agent pipeline"""
        result = await self.agent.execute(
            idea_context=idea_context,
            query_text="Startup failure patterns, market risks, regulatory risks, operational bottlenecks"
        )
        score_val = result.get("score", 12)
        # Convert 20-point scale to 10-point scale
        legacy_score = float(score_val) / 2.0
        
        categories = result.get("risk_categories", {})
        
        result["overall_risk_score"] = legacy_score
        result["market_risks"] = categories.get("market_risks", "Uncalculated market risks.")
        result["technical_risks"] = categories.get("technical_risks", "Uncalculated technical risks.")
        result["financial_risks"] = categories.get("financial_risks", "Uncalculated financial risks.")
        result["operational_risks"] = categories.get("operational_risks", "Uncalculated operational risks.")
        result["mitigation_strategies"] = result.get("mitigation_strategies", ["Uncalculated mitigation strategies."])
        return result
