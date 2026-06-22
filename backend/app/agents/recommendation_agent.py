"""
Final Recommendation Agent
"""
import time
import json
import logging
from typing import Dict, Any, List
from app.agents.base_agent import BaseAgent
from app.core.config import settings

logger = logging.getLogger(__name__)

class RecommendationAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_name="Final Recommendation Agent",
            prompt_filename="final_recommendation.txt"
        )
        
    async def generate_recommendation(self, idea_context: str, all_agent_findings: Dict[str, Any]) -> Dict[str, Any]:
        """Custom execution method taking all previous results and aggregating a final assessment"""
        start_time = time.time()
        try:
            prompt_template = self._load_prompt_template()
            full_prompt = prompt_template.format(
                idea_context=idea_context,
                all_agent_findings=json.dumps(all_agent_findings, indent=2)
            )
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system", 
                        "content": "You are a professional Startup Incubator Director and Venture Capital Partner. You respond with raw JSON only. Never wrap responses in markdown code blocks."
                    },
                    {"role": "user", "content": full_prompt}
                ],
                temperature=settings.openai_temperature,
                max_tokens=settings.openai_max_tokens
            )
            
            raw_content = response.choices[0].message.content.strip()
            
            if raw_content.startswith("```"):
                lines = raw_content.split("\n")
                if lines[0].startswith("```"):
                    lines = lines[1:]
                if lines[-1].startswith("```"):
                    lines = lines[:-1]
                raw_content = "\n".join(lines).strip()
                
            try:
                parsed_json = json.loads(raw_content)
            except json.JSONDecodeError:
                parsed_json = self.get_fallback_response([])
                
            # Double-check score calculations (Market Demand [25], Competition [20], Revenue Potential [20], Scalability [15], Risk Management [20])
            score_breakdown = parsed_json.get("score_breakdown", {})
            computed_score = 0
            for key in ["market_demand", "competition", "revenue_potential", "scalability", "risk_management"]:
                sub = score_breakdown.get(key, {})
                computed_score += sub.get("score", 0)
                
            # If computed_score is zero (e.g. failed parsing), set score directly or default it
            if computed_score > 0:
                parsed_json["overall_score"] = computed_score
                
            duration = time.time() - start_time
            parsed_json["_audit_log"] = {
                "agent_name": self.agent_name,
                "retrieved_frameworks": ["Lean Startup", "SWOT Analysis", "Business Model Canvas", "Porter Five Forces"],
                "input_summary": "Aggregated agent findings",
                "output_summary": {
                    "overall_score": parsed_json.get("overall_score"),
                    "verdict": parsed_json.get("viability_verdict")
                },
                "processing_time": round(duration, 3),
                "confidence": parsed_json.get("overall_confidence", 85)
            }
            return parsed_json
            
        except Exception as e:
            logger.error(f"Final recommendation failed: {str(e)}")
            fallback = self.get_fallback_response([])
            fallback["_audit_log"] = {
                "agent_name": self.agent_name,
                "error": str(e)
            }
            return fallback

    def get_fallback_response(self, retrieved_sources: List[str]) -> Dict[str, Any]:
        """Provide a minimal structured fallback when recommendation JSON parsing fails."""
        return {
            "overall_score": 0,
            "overall_confidence": 0,
            "overall_confidence_reason": "Recommendation agent output could not be parsed.",
            "executive_summary": "The final summary could not be generated due to an internal parsing failure.",
            "score_breakdown": {
                "market_demand": {"score": 0, "max_score": 25, "reasoning": "Market assessment unavailable."},
                "competition": {"score": 0, "max_score": 20, "reasoning": "Competition assessment unavailable."},
                "revenue_potential": {"score": 0, "max_score": 20, "reasoning": "Financial assessment unavailable."},
                "scalability": {"score": 0, "max_score": 15, "reasoning": "Growth potential unavailable."},
                "risk_management": {"score": 0, "max_score": 20, "reasoning": "Risk assessment unavailable."}
            },
            "action_plan": [
                {
                    "recommendation": "Retry analysis with a valid OpenAI API key and review idea inputs.",
                    "framework_source": "Fallback",
                    "priority": "medium",
                    "category": "operational"
                }
            ],
            "next_steps": [
                "Verify your OpenAI API key is configured properly.",
                "Retry the idea analysis once the service is available."
            ],
            "viability_verdict": "Challenging"
        }
