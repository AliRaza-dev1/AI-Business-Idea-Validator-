"""
SWOT Generator
"""
import time
import json
import logging
from typing import Dict, Any, List
from app.agents.base_agent import BaseAgent
from app.core.config import settings

logger = logging.getLogger(__name__)

class SWOTGenerator(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_name="SWOT Generator",
            prompt_filename="swot_generation.txt"
        )
        
    async def generate_swot(self, idea_context: str, agent_findings: Dict[str, Any]) -> Dict[str, Any]:
        """Custom execution method taking previous agent findings and generating SWOT details"""
        start_time = time.time()
        try:
            prompt_template = self._load_prompt_template()
            full_prompt = prompt_template.format(
                idea_context=idea_context,
                agent_findings=json.dumps(agent_findings, indent=2)
            )
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system", 
                        "content": "You are a professional business strategist. You respond with raw JSON only. Never wrap responses in markdown code blocks."
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
                
            duration = time.time() - start_time
            parsed_json["_audit_log"] = {
                "agent_name": self.agent_name,
                "retrieved_frameworks": ["SWOT Analysis"],
                "input_summary": f"Findings for SWOT Generation",
                "output_summary": {
                    "strengths_count": len(parsed_json.get("strengths", [])),
                    "weaknesses_count": len(parsed_json.get("weaknesses", []))
                },
                "processing_time": round(duration, 3),
                "confidence": 90
            }
            return parsed_json
            
        except Exception as e:
            logger.error(f"SWOT generation failed: {str(e)}")
            fallback = self.get_fallback_response([])
            fallback["_audit_log"] = {
                "agent_name": self.agent_name,
                "error": str(e)
            }
            return fallback

    def get_fallback_response(self, retrieved_sources: List[str]) -> Dict[str, Any]:
        """Provide a minimal structured fallback when SWOT JSON parsing fails."""
        return {
            "strengths": [
                {
                    "text": "Unable to extract strengths from the model response.",
                    "framework_source": "SWOT Generator"
                }
            ],
            "weaknesses": [
                {
                    "text": "Unable to extract weaknesses from the model response.",
                    "framework_source": "SWOT Generator"
                }
            ],
            "opportunities": [
                {
                    "text": "Unable to identify opportunities from the model response.",
                    "framework_source": "SWOT Generator"
                }
            ],
            "threats": [
                {
                    "text": "Unable to identify threats from the model response.",
                    "framework_source": "SWOT Generator"
                }
            ]
        }
