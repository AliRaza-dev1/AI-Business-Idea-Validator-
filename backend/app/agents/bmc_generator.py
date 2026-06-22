"""
Business Model Canvas Generator
"""
import time
import json
import logging
from typing import Dict, Any, List
from app.agents.base_agent import BaseAgent
from app.core.config import settings

logger = logging.getLogger(__name__)

class BMCGenerator(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_name="BMC Generator",
            prompt_filename="bmc_generation.txt"
        )
        
    async def generate_bmc(self, idea_context: str, agent_findings: Dict[str, Any]) -> Dict[str, Any]:
        """Custom execution method taking previous findings and compiling Business Model Canvas blocks"""
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
                        "content": "You are a professional business architect. You respond with raw JSON only. Never wrap responses in markdown code blocks."
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
                "retrieved_frameworks": ["Business Model Canvas"],
                "input_summary": "Findings for BMC Generation",
                "output_summary": {
                    "blocks_compiled": len(parsed_json.keys())
                },
                "processing_time": round(duration, 3),
                "confidence": 95
            }
            return parsed_json
            
        except Exception as e:
            logger.error(f"BMC generation failed: {str(e)}")
            fallback = self.get_fallback_response([])
            fallback["_audit_log"] = {
                "agent_name": self.agent_name,
                "error": str(e)
            }
            return fallback

    def get_fallback_response(self, retrieved_sources: List[str]) -> Dict[str, Any]:
        """Fallback responses disabled - do not use"""
        raise NotImplementedError(
            "Fallback responses are not supported. "
            "If BMC generation fails, the error must be handled by the orchestrator."
        )
