"""
Analysis Orchestrator — Coordinates sequential multi-agent execution, SWOT/BMC generation, audit trailing, and SQL database mapping.
Utilizes backward-compatible service classes to support existing test suites.
"""
import time
import json
import logging
from typing import Dict, Any, List

from app.services.market_analysis import MarketAnalysisService
from app.services.feasibility_analysis import FeasibilityAnalysisService
from app.services.financial_analysis import FinancialAnalysisService
from app.services.risk_assessment import RiskAssessmentService
from app.services.competitive_analysis import CompetitiveAnalysisService
from app.agents.swot_generator import SWOTGenerator
from app.agents.bmc_generator import BMCGenerator
from app.agents.recommendation_agent import RecommendationAgent
from app.core.config import settings

logger = logging.getLogger(__name__)

# Detect if we're in mock mode (invalid API key)
IS_MOCK_MODE = (
    not settings.openai_api_key or
    "replace-with-real-key" in settings.openai_api_key or
    "sk-test" in settings.openai_api_key.lower() or
    "your_openai_api_key" in settings.openai_api_key or
    settings.openai_api_key.strip() == ""
)

if IS_MOCK_MODE:
    logger.warning("=" * 80)
    logger.warning("[MOCK_MODE_ENABLED] OpenAI API key not configured properly")
    logger.warning("Running in DEMO MODE with simulated AI responses")
    logger.warning("For production, set OPENAI_API_KEY in backend/.env")
    logger.warning("=" * 80)
    from app.agents.mock_mode import MockAgentMode

class AnalysisOrchestrator:
    """Orchestrates sequential multi-agent workflow via compatible service wrappers"""
    
    def __init__(self):
        self.market_service = MarketAnalysisService()
        self.feasibility_service = FeasibilityAnalysisService()
        self.financial_service = FinancialAnalysisService()
        self.risk_service = RiskAssessmentService()
        self.competitive_service = CompetitiveAnalysisService()
        self.swot_generator = SWOTGenerator()
        self.bmc_generator = BMCGenerator()
        self.recommendation_agent = RecommendationAgent()
        
    async def run_full_analysis(self, 
                               idea_title: str,
                               idea_description: str,
                               problem_statement: str,
                               target_market: str,
                               proposed_solution: str,
                               value_proposition: str,
                               business_model: str) -> Dict[str, Any]:
        """
        Runs sequential RAG multi-agent verification pipeline with error handling
        In mock mode, returns simulated responses for testing
        """
        idea_context = f"""
Title: {idea_title}
Description: {idea_description}
Problem Statement: {problem_statement}
Target Market: {target_market}
Proposed Solution: {proposed_solution}
Value Proposition: {value_proposition}
Business Model: {business_model}
"""
        logger.info(f"Starting sequential multi-agent analysis for: {idea_title}")
        logger.info(f"[ORCHESTRATOR_MODE] {'MOCK_MODE (demo)' if IS_MOCK_MODE else 'REAL_MODE (OpenAI API)'}")
        audit_trail = []
        
        # If in mock mode, use mock responses
        if IS_MOCK_MODE:
            logger.info("[MOCK_AGENT_PIPELINE] Using simulated AI responses")
            return self._run_mock_analysis(idea_title, business_model, audit_trail)
        
        # Otherwise use real agents
        return await self._run_real_analysis(
            idea_title, idea_description, problem_statement, target_market,
            proposed_solution, value_proposition, business_model,
            idea_context, audit_trail
        )
    
    def _run_mock_analysis(self, idea_title: str, business_model: str, audit_trail: List) -> Dict[str, Any]:
        """Run analysis using mock responses"""
        logger.info("[MOCK_ANALYSIS_START] Generating mock responses")
        
        # Get mock responses from MockAgentMode
        market_result = MockAgentMode.get_market_analysis(idea_title, "")
        competition_result = MockAgentMode.get_competition_analysis(idea_title)
        financial_result = MockAgentMode.get_financial_analysis(business_model)
        risk_result = MockAgentMode.get_risk_analysis()
        feasibility_result = MockAgentMode.get_feasibility_analysis()
        
        # Calculate overall score
        scores = {
            "market_score": market_result["score"],
            "financial_score": financial_result["score"],
            "feasibility_score": feasibility_result["score"],
            "risk_score": risk_result["score"],
            "competition_score": competition_result["competition"]["score"]
        }
        overall_score = sum(scores.values()) / len(scores) * 10 / 10  # Normalize to 100
        
        swot_result = MockAgentMode.get_swot_analysis(idea_title)
        rec_result = MockAgentMode.get_recommendation(idea_title, overall_score)
        
        logger.info(f"[MOCK_ANALYSIS_COMPLETE] Overall score: {overall_score:.1f}")
        
        return {
            "scores": {
                **scores,
                "overall_score": overall_score
            },
            "market_analysis": market_result,
            "financial_analysis": financial_result,
            "feasibility_analysis": feasibility_result,
            "risk_analysis": risk_result,
            "competitive_analysis": competition_result,
            "swot": swot_result,
            "recommendation": rec_result,
            "recommendations": rec_result.get("action_plan", []),
            "audit_trail": audit_trail
        }
    
    async def _run_real_analysis(self,
                                idea_title: str,
                                idea_description: str,
                                problem_statement: str,
                                target_market: str,
                                proposed_solution: str,
                                value_proposition: str,
                                business_model: str,
                                idea_context: str,
                                audit_trail: List) -> Dict[str, Any]:
        """Run analysis using real OpenAI agents"""
        
        # Step 1: Market Intelligence Agent (via market_service)
        try:
            market_result = await self.market_service.analyze_market(idea_context)
            if "_audit_log" in market_result:
                audit_trail.append(market_result["_audit_log"])
            logger.info(f"✓ Market analysis completed: score={market_result.get('score', 'N/A')}")
        except Exception as e:
            logger.error(f"✗ CRITICAL: Market analysis failed: {str(e)}")
            raise RuntimeError(
                f"Market analysis agent failed: {str(e)}. "
                f"Verify: 1) OpenAI API key valid, 2) Rate limits OK, 3) Business idea data complete."
            ) from e
            
        # Step 2: Competition Analysis Agent (via competitive_service)
        try:
            competition_result = await self.competitive_service.analyze_competition(idea_context)
            if "_audit_log" in competition_result:
                audit_trail.append(competition_result["_audit_log"])
            logger.info(f"✓ Competition analysis completed: score={competition_result.get('score', 'N/A')}")
        except Exception as e:
            logger.error(f"✗ CRITICAL: Competition analysis failed: {str(e)}")
            raise RuntimeError(
                f"Competition analysis agent failed: {str(e)}"
            ) from e

        # Step 3: Financial Feasibility Agent (via financial_service)
        try:
            financial_result = await self.financial_service.analyze_financials(idea_context)
            if "_audit_log" in financial_result:
                audit_trail.append(financial_result["_audit_log"])
            logger.info(f"✓ Financial analysis completed: score={financial_result.get('score', 'N/A')}")
        except Exception as e:
            logger.error(f"✗ CRITICAL: Financial analysis failed: {str(e)}")
            raise RuntimeError(
                f"Financial analysis agent failed: {str(e)}"
            ) from e

        # Step 4: Risk Assessment Agent (via risk_service)
        try:
            risk_result = await self.risk_service.assess_risks(idea_context)
            if "_audit_log" in risk_result:
                audit_trail.append(risk_result["_audit_log"])
            logger.info(f"✓ Risk assessment completed: score={risk_result.get('score', 'N/A')}")
        except Exception as e:
            logger.error(f"✗ CRITICAL: Risk assessment failed: {str(e)}")
            raise RuntimeError(
                f"Risk assessment agent failed: {str(e)}"
            ) from e

        # Step 5: Growth Potential Agent (via feasibility_service)
        try:
            feasibility_result = await self.feasibility_service.analyze_feasibility(idea_context)
            if "_audit_log" in feasibility_result:
                audit_trail.append(feasibility_result["_audit_log"])
            logger.info(f"✓ Feasibility analysis completed: score={feasibility_result.get('score', 'N/A')}")
        except Exception as e:
            logger.error(f"✗ CRITICAL: Feasibility analysis failed: {str(e)}")
            raise RuntimeError(
                f"Feasibility analysis agent failed: {str(e)}"
            ) from e

        # Compile analytical findings for generators
        agent_findings = {
            "market": market_result,
            "competition": competition_result,
            "financial": financial_result,
            "risk": risk_result,
            "growth": feasibility_result
        }

        # Step 6: SWOT & BMC Generators
        try:
            swot_result = await self.swot_generator.generate_swot(idea_context, agent_findings)
            if "_audit_log" in swot_result:
                audit_trail.append(swot_result["_audit_log"])
            logger.info(f"✓ SWOT generation completed: S={len(swot_result.get('strengths', []))} W={len(swot_result.get('weaknesses', []))} O={len(swot_result.get('opportunities', []))} T={len(swot_result.get('threats', []))}")
        except Exception as e:
            logger.error(f"✗ CRITICAL: SWOT generation failed: {str(e)}")
            raise RuntimeError(
                f"SWOT generation agent failed: {str(e)}"
            ) from e
            
        try:
            bmc_result = await self.bmc_generator.generate_bmc(idea_context, agent_findings)
            if "_audit_log" in bmc_result:
                audit_trail.append(bmc_result["_audit_log"])
            logger.info(f"✓ BMC generation completed")
        except Exception as e:
            logger.error(f"✗ CRITICAL: BMC generation failed: {str(e)}")
            raise RuntimeError(
                f"Business Model Canvas generation failed: {str(e)}"
            ) from e

        # Final Recommendation Agent
        all_agent_findings = {
            "agents": agent_findings,
            "swot": swot_result,
            "bmc": bmc_result
        }
        
        try:
            recommendation_result = await self.recommendation_agent.generate_recommendation(idea_context, all_agent_findings)
            if "_audit_log" in recommendation_result:
                audit_trail.append(recommendation_result["_audit_log"])
            logger.info(f"✓ Recommendation generation completed: overall_score={recommendation_result.get('overall_score', 'N/A')}")
        except Exception as e:
            logger.error(f"✗ CRITICAL: Recommendation generation failed: {str(e)}")
            raise RuntimeError(
                f"Recommendation agent failed: {str(e)}"
            ) from e
            
        # Combine overall scores for compatibility
        # We need to support both legacy 1-10 scores (from test assertions) and 100-point ranges.
        # Check if the service returns actual agent sub-scores or legacy 10-scale floats (e.g. from mocks).
        market_score = market_result.get("score", int(market_result.get("market_score", 0) * 2.5))
        feasibility_score = feasibility_result.get("score", int(feasibility_result.get("feasibility_score", 0) * 1.5))
        financial_score = financial_result.get("score", int(financial_result.get("financial_score", 0) * 2))
        risk_score = risk_result.get("score", int(risk_result.get("overall_risk_score", 0) * 2))
        competitive_score = competition_result.get("score", int(competition_result.get("competitive_score", 0) * 2))
        
        # Calculate overall 100-point score
        overall_score = recommendation_result.get("overall_score")
        if not overall_score or overall_score == 50:
            # If default/mock values present, sum individual scores
            overall_score = market_score + feasibility_score + financial_score + risk_score + competitive_score
            recommendation_result["overall_score"] = overall_score

        scores_summary = {
            "market_score": float(market_score) / 2.5 if market_score else float(market_result.get("market_score", 0)),
            "feasibility_score": float(feasibility_score) / 1.5 if feasibility_score else float(feasibility_result.get("feasibility_score", 0)),
            "financial_score": float(financial_score) / 2 if financial_score else float(financial_result.get("financial_score", 0)),
            "risk_score": float(risk_score) / 2 if risk_score else float(risk_result.get("overall_risk_score", 0)),
            "competitive_score": float(competitive_score) / 2 if competitive_score else float(competition_result.get("competitive_score", 0)),
            "overall_score": float(overall_score)
        }
        
        # Build comprehensive orchestrator output packet
        output_report = {
            "idea_title": idea_title,
            "idea_description": idea_description,
            
            # Structured results
            "market_analysis": market_result,
            "feasibility_analysis": feasibility_result,
            "financial_analysis": financial_result,
            "risk_analysis": risk_result,
            "competitive_analysis": {
                "competition": competition_result,
                "bmc": bmc_result
            },
            "swot": swot_result,
            "recommendation": recommendation_result,
            
            # Scores & metadata
            "scores": scores_summary,
            "audit_trail": audit_trail,
            "strengths": [s["text"] for s in swot_result.get("strengths", [])] if isinstance(swot_result.get("strengths"), list) else [str(swot_result.get("strengths"))],
            "weaknesses": [w["text"] for w in swot_result.get("weaknesses", [])] if isinstance(swot_result.get("weaknesses"), list) else [str(swot_result.get("weaknesses"))],
            "recommendations": [
                {
                    "text": rec.get("recommendation", ""),
                    "category": rec.get("category", "general"),
                    "priority": rec.get("priority", "medium"),
                    "framework_source": rec.get("framework_source", "Lean Startup")
                } for rec in recommendation_result.get("action_plan", [])
            ]
        }
        
        return output_report

    def _calculate_overall_score(self, market: float, feasibility: float, 
                                financial: float, risk: float, 
                                competitive: float) -> float:
        """Calculate weighted overall score for legacy compatibility"""
        overall = (
            market * 2.5 +
            feasibility * 1.5 +
            financial * 2.0 +
            risk * 2.0 +
            competitive * 2.0
        )
        return round(overall, 1)

    def _assess_viability(self, overall_score: float) -> Dict[str, Any]:
        """Assess overall business viability for legacy compatibility"""
        if overall_score >= 80:
            return {
                "status": "Highly Viable",
                "description": "Strong business potential with positive indicators across all dimensions",
                "recommendation": "Proceed with business planning and implementation"
            }
        elif overall_score >= 60:
            return {
                "status": "Viable",
                "description": "Good business potential with some areas needing refinement",
                "recommendation": "Address identified gaps and refine strategy before launch"
            }
        elif overall_score >= 40:
            return {
                "status": "Potentially Viable",
                "description": "Mixed indicators - significant work needed to validate viability",
                "recommendation": "Conduct deeper validation and reassess key assumptions"
            }
        else:
            return {
                "status": "Challenging",
                "description": "Significant challenges identified across multiple dimensions",
                "recommendation": "Consider major changes or alternative business models"
            }

# Initialize orchestrator
analysis_orchestrator = AnalysisOrchestrator()

async def analyze_idea_async(idea_id: int, db_session: Any):
    """Stub to support legacy testing patches"""
    pass
