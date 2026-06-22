"""
Financial Analysis Service — Upgraded wrapper executing FinancialAgent and preserving legacy keys.
"""
from typing import Dict, Any
from app.agents.financial_agent import FinancialAgent

class FinancialAnalysisService:
    def __init__(self):
        self.agent = FinancialAgent()
        
    async def analyze_financials(self, idea_context: str) -> Dict[str, Any]:
        """Runs the financial agent pipeline"""
        result = await self.agent.execute(
            idea_context=idea_context,
            query_text="Cost structure, revenue streams, breakeven and pricing model"
        )
        score_val = result.get("score", 12)
        # Convert 20-point scale to 10-point scale
        legacy_score = float(score_val) / 2.0
        
        result["financial_score"] = legacy_score
        result["revenue_model"] = ", ".join(result.get("revenue_streams", ["N/A"]))
        result["funding_requirements"] = result.get("breakeven_projection", "Funding projection uncalculated.")
        result["cost_structure"] = ", ".join(result.get("cost_structure", ["N/A"]))
        result["full_analysis"] = result.get("reasoning", "Detailed analysis.")
        return result
