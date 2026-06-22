"""
Base Agent Class — Coordinates prompt template loading, RAG retrieval, OpenAI execution, structured JSON parsing, and audit trails.
"""
import os
import time
import json
import logging
from typing import Dict, Any, List
from openai import OpenAI
from app.core.config import settings

logger = logging.getLogger(__name__)

class BaseAgent:
    """Base class for all business validation agents"""
    
    def __init__(self, agent_name: str, prompt_filename: str):
        self.agent_name = agent_name
        self.prompt_filename = prompt_filename
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model
        
    def _load_prompt_template(self) -> str:
        """Loads prompt text from file system"""
        prompt_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "prompts",
            self.prompt_filename
        )
        if not os.path.exists(prompt_path):
            raise FileNotFoundError(f"Prompt template {prompt_path} not found.")
            
        with open(prompt_path, "r", encoding="utf-8") as f:
            return f.read()

    async def execute(self, idea_context: str, query_text: str) -> Dict[str, Any]:
        """Runs the complete RAG + agent execution pipeline"""
        start_time = time.time()
        retrieved_sources = []
        retrieved_content = ""
        
        # Log execution start with context
        logger.info(f"\n{'='*80}")
        logger.info(f"AGENT EXECUTION START: {self.agent_name}")
        logger.info(f"{'='*80}")
        logger.info(f"Business Idea Context (first 500 chars):\n{idea_context[:500]}")
        logger.info(f"Query: {query_text}")
        logger.info(f"Prompt File: {self.prompt_filename}")
        logger.info(f"API Model: {self.model}")
        logger.info(f"{'='*80}")
        
        try:
            # 1. RAG Search (Lazy initialized)
            logger.info("Step 1: RAG Retrieval Starting...")
            from app.services.knowledge_base import get_rag_service
            rag_svc = get_rag_service()
            search_results = rag_svc.search_similarity(query_text, top_k=2)
            if search_results:
                retrieved_sources = list(set(res["framework_name"] for res in search_results))
                retrieved_content = "\n\n".join(
                    f"[{res['framework_name']}]:\n{res['chunk_text']}" for res in search_results
                )
                logger.info(f"RAG Retrieved {len(search_results)} chunks from {len(retrieved_sources)} frameworks")
                logger.info(f"Retrieved Frameworks: {retrieved_sources}")
                logger.info(f"Retrieved Context Length: {len(retrieved_content)} characters")
                logger.info(f"Retrieved Content (first 500 chars):\n{retrieved_content[:500]}")
            else:
                logger.warning("RAG: No matching frameworks retrieved - using general business principles")
                retrieved_content = "No matching frameworks retrieved. Use general business principles."
            
            # 2. Render Prompt
            logger.info("Step 2: Prompt Rendering...")
            prompt_template = self._load_prompt_template()
            logger.info(f"Loaded prompt template ({len(prompt_template)} chars)")
            full_prompt = prompt_template.format(
                idea_context=idea_context,
                retrieved_context=retrieved_content
            )
            logger.info(f"Full prompt with context ({len(full_prompt)} chars)")
            logger.info(f"Full Prompt (first 1000 chars):\n{full_prompt[:1000]}")
            
            # 3. OpenAI Call
            logger.info(f"Step 3: OpenAI API Call...")
            logger.info(f"Calling {self.model} with temperature={settings.openai_temperature}, max_tokens={settings.openai_max_tokens}")
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system", 
                        "content": "You are a professional business analysis assistant. You respond with raw JSON only. Never write explanations or wrap your response in markdown code blocks."
                    },
                    {"role": "user", "content": full_prompt}
                ],
                temperature=settings.openai_temperature,
                max_tokens=settings.openai_max_tokens
            )
            logger.info(f"OpenAI response received successfully")
            
            raw_content = response.choices[0].message.content.strip()
            logger.info(f"Raw Response Length: {len(raw_content)} characters")
            logger.info(f"Raw Response (first 1000 chars):\n{raw_content[:1000]}")
            
            # Remove any markdown wrapping if LLM ignored system instructions
            if raw_content.startswith("```"):
                logger.warning("Response wrapped in markdown code blocks - removing wrapper")
                lines = raw_content.split("\n")
                if lines[0].startswith("```"):
                    lines = lines[1:]
                if lines[-1].startswith("```"):
                    lines = lines[:-1]
                raw_content = "\n".join(lines).strip()
            
            # 4. JSON Validation - STRICT (no fallback)
            logger.info("Step 4: JSON Parsing...")
            try:
                parsed_json = json.loads(raw_content)
                logger.info(f"JSON parsed successfully - {len(parsed_json)} top-level keys")
                logger.info(f"Parsed JSON: {json.dumps(parsed_json, indent=2)[:1500]}")
            except json.JSONDecodeError as e:
                logger.error(f"{self.agent_name} returned invalid JSON. Response: {raw_content[:500]}")
                raise ValueError(
                    f"Agent {self.agent_name} failed to return valid JSON. "
                    f"Raw response: {raw_content[:200]}... "
                    f"Error: {str(e)}"
                )
            
            # Verify required fields are present
            if not parsed_json.get("score") and parsed_json.get("score") != 0:
                raise ValueError(f"Agent {self.agent_name} response missing required 'score' field")
            
            # Attach metadata
            parsed_json.setdefault("retrieved_knowledge_sources", retrieved_sources)
            parsed_json.setdefault("confidence", parsed_json.get("confidence", None))
            
            duration = time.time() - start_time
            
            # 5. Compile Audit Log Entry
            audit_log = {
                "agent_name": self.agent_name,
                "retrieved_frameworks": retrieved_sources,
                "input_summary": idea_context[:300] + "...",
                "output_summary": {
                    "score": parsed_json.get("score"),
                    "confidence": parsed_json.get("confidence"),
                    "key_findings": parsed_json.get("key_findings", [])[:2]
                },
                "processing_time": round(duration, 3),
                "confidence": parsed_json.get("confidence")
            }
            
            # Write audit log to internal logger
            logger.info(f"Audit Trail for {self.agent_name}: {json.dumps(audit_log)}")
            logger.info(f"{'='*80}")
            logger.info(f"AGENT EXECUTION SUCCESSFUL: {self.agent_name}")
            logger.info(f"Duration: {duration:.2f}s")
            logger.info(f"Score: {parsed_json.get('score')}")
            logger.info(f"Confidence: {parsed_json.get('confidence')}")
            logger.info(f"Retrieved Frameworks: {retrieved_sources}")
            logger.info(f"Final Output (first 1500 chars):\n{json.dumps(parsed_json, indent=2)[:1500]}")
            logger.info(f"{'='*80}\n")
            
            # Attach audit details to payload
            parsed_json["_audit_log"] = audit_log
            
            return parsed_json
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"AGENT EXECUTION FAILED: {self.agent_name}")
            logger.error(f"Error Type: {type(e).__name__}")
            logger.error(f"Error Message: {str(e)}")
            logger.error(f"Idea Context: {idea_context[:300]}")
            logger.error(f"Query: {query_text}")
            
            # Do NOT return fallback - let error propagate
            # This forces the orchestrator to handle the failure explicitly
            raise RuntimeError(
                f"Agent {self.agent_name} execution failed: {str(e)}. "
                f"Please check: 1) OpenAI API key validity, 2) API rate limits, "
                f"3) Business idea data completeness"
            ) from e

    def get_fallback_response(self, retrieved_sources: List[str]) -> Dict[str, Any]:
        """NO LONGER USED - Fallbacks disabled to prevent generic report generation"""
        raise NotImplementedError(
            f"Agent {self.agent_name} does not support fallback responses. "
            "If execution fails, the error must be handled explicitly by the orchestrator. "
            "This ensures no generic/fake data is ever returned to users."
        )
