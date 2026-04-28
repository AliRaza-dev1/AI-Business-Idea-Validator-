"""
Analysis Orchestrator - Coordinates all analysis modules
"""

from typing import Dict, Any
from app.services.market_analysis import MarketAnalysisService
from app.services.feasibility_analysis import FeasibilityAnalysisService
from app.services.financial_analysis import FinancialAnalysisService
from app.services.risk_assessment import RiskAssessmentService
from app.services.competitive_analysis import CompetitiveAnalysisService
import logging

logger = logging.getLogger(__name__)


class AnalysisOrchestrator:
    """Orchestrates all analysis modules"""
    
    def __init__(self):
        self.market_service = MarketAnalysisService()
        self.feasibility_service = FeasibilityAnalysisService()
        self.financial_service = FinancialAnalysisService()
        self.risk_service = RiskAssessmentService()
        self.competitive_service = CompetitiveAnalysisService()
    
    async def run_full_analysis(self, 
                               idea_title: str,
                               idea_description: str,
                               problem_statement: str,
                               target_market: str,
                               proposed_solution: str,
                               value_proposition: str,
                               business_model: str) -> Dict[str, Any]:
        """
        Run comprehensive analysis on a business idea
        
        Args:
            idea_title: Title of the business idea
            idea_description: Detailed description
            problem_statement: Problem being solved
            target_market: Target market description
            proposed_solution: Proposed solution
            value_proposition: Unique value proposition
            business_model: Business model description
            
        Returns:
            Complete analysis results with all scores and insights
        """
        try:
            # Build context for all modules
            idea_context = f"""
Business Idea: {idea_title}

Description: {idea_description}

Problem Statement: {problem_statement}

Target Market: {target_market}

Proposed Solution: {proposed_solution}

Value Proposition: {value_proposition}

Business Model: {business_model}
            """
            
            logger.info(f"Starting comprehensive analysis for idea: {idea_title}")
            
            # Run all analyses concurrently-ready format (can be parallelized)
            market_results = await self.market_service.analyze_market(idea_context)
            feasibility_results = await self.feasibility_service.analyze_feasibility(idea_context)
            financial_results = await self.financial_service.analyze_financials(idea_context)
            risk_results = await self.risk_service.assess_risks(idea_context)
            competitive_results = await self.competitive_service.analyze_competition(idea_context)
            
            # Calculate overall scores
            overall_score = self._calculate_overall_score(
                market_results["market_score"],
                feasibility_results["feasibility_score"],
                financial_results["financial_score"],
                risk_results["overall_risk_score"],
                competitive_results["competitive_score"]
            )
            
            # Compile comprehensive report
            analysis_report = {
                "idea_title": idea_title,
                "idea_description": idea_description,
                
                # Individual Analysis Results
                "market_analysis": {
                    "score": market_results["market_score"],
                    "analysis": market_results["full_analysis"],
                    "summary": market_results["market_size"]
                },
                
                "feasibility_analysis": {
                    "score": feasibility_results["feasibility_score"],
                    "analysis": feasibility_results["full_analysis"],
                    "summary": feasibility_results["technical_requirements"]
                },
                
                "financial_analysis": {
                    "score": financial_results["financial_score"],
                    "analysis": financial_results["full_analysis"],
                    "revenue_model": financial_results["revenue_model"],
                    "funding_requirements": financial_results["funding_requirements"]
                },
                
                "risk_analysis": {
                    "score": risk_results["overall_risk_score"],
                    "market_risks": risk_results["market_risks"],
                    "technical_risks": risk_results["technical_risks"],
                    "financial_risks": risk_results["financial_risks"],
                    "operational_risks": risk_results["operational_risks"],
                    "mitigation_strategies": risk_results["mitigation_strategies"]
                },
                
                "competitive_analysis": {
                    "score": competitive_results["competitive_score"],
                    "competitors": competitive_results["competitor_landscape"],
                    "advantages": competitive_results["competitive_advantages"],
                    "positioning": competitive_results["market_positioning"],
                    "differentiation": competitive_results["differentiation"]
                },
                
                # Aggregate Scores
                "scores": {
                    "market_score": market_results["market_score"],
                    "feasibility_score": feasibility_results["feasibility_score"],
                    "financial_score": financial_results["financial_score"],
                    "risk_score": risk_results["overall_risk_score"],
                    "competitive_score": competitive_results["competitive_score"],
                    "overall_score": overall_score
                },
                
                # Recommendations and Insights
                "recommendations": await self._generate_recommendations(
                    market_results, feasibility_results, financial_results,
                    risk_results, competitive_results
                ),
                
                "strengths": await self._extract_strengths(
                    market_results, feasibility_results, financial_results,
                    risk_results, competitive_results
                ),
                
                "weaknesses": await self._extract_weaknesses(
                    market_results, feasibility_results, financial_results,
                    risk_results, competitive_results
                ),
                
                "next_steps": await self._generate_next_steps(overall_score),
                
                "viability_assessment": self._assess_viability(overall_score)
            }
            
            logger.info(f"Analysis complete. Overall score: {overall_score}")
            
            return analysis_report
        
        except Exception as e:
            logger.error(f"Analysis orchestration error: {str(e)}")
            raise
    
    def _calculate_overall_score(self, market: float, feasibility: float, 
                                financial: float, risk: float, 
                                competitive: float) -> float:
        """Calculate weighted overall score"""
        # Weights: Market (25%), Feasibility (20%), Financial (20%), Risk (20%), Competitive (15%)
        overall = (
            market * 0.25 +
            feasibility * 0.20 +
            financial * 0.20 +
            risk * 0.20 +
            competitive * 0.15
        )
        return round(overall, 1)
    
    async def _generate_recommendations(self, market, feasibility, financial, risk, competitive) -> list:
        """Generate consolidated recommendations"""
        recommendations = []
        
        # High-priority recommendations based on scores
        if market["market_score"] < 6:
            recommendations.append({
                "priority": "high",
                "category": "market",
                "text": "Focus on market validation and customer interviews to better understand market demand."
            })
        
        if feasibility["feasibility_score"] < 6:
            recommendations.append({
                "priority": "high",
                "category": "technical",
                "text": "Conduct detailed technical feasibility study and consider hiring technical experts."
            })
        
        if financial["financial_score"] < 6:
            recommendations.append({
                "priority": "high",
                "category": "financial",
                "text": "Refine financial projections with more detailed cost/revenue analysis."
            })
        
        if risk["overall_risk_score"] < 6:
            recommendations.append({
                "priority": "high",
                "category": "risk",
                "text": "Develop comprehensive risk mitigation plan before launch."
            })
        
        if competitive["competitive_score"] < 6:
            recommendations.append({
                "priority": "high",
                "category": "competitive",
                "text": "Strengthen differentiation strategy and competitive positioning."
            })
        
        return recommendations
    
    async def _extract_strengths(self, market, feasibility, financial, risk, competitive) -> list:
        """Extract key strengths from analysis"""
        strengths = []
        
        if market["market_score"] >= 7:
            strengths.append(f"Strong market opportunity with positive growth trends")
        if feasibility["feasibility_score"] >= 7:
            strengths.append(f"Highly feasible implementation with clear technical path")
        if financial["financial_score"] >= 7:
            strengths.append(f"Attractive financial model with strong profit potential")
        if risk["overall_risk_score"] >= 7:
            strengths.append(f"Manageable risk profile with clear mitigation strategies")
        if competitive["competitive_score"] >= 7:
            strengths.append(f"Strong competitive positioning and differentiation")
        
        return strengths if strengths else ["Review analysis for specific strengths"]
    
    async def _extract_weaknesses(self, market, feasibility, financial, risk, competitive) -> list:
        """Extract key weaknesses from analysis"""
        weaknesses = []
        
        if market["market_score"] < 6:
            weaknesses.append(f"Market opportunity concerns - insufficient market size or growth")
        if feasibility["feasibility_score"] < 6:
            weaknesses.append(f"Feasibility challenges - high technical or operational complexity")
        if financial["financial_score"] < 6:
            weaknesses.append(f"Financial concerns - tight margins or high capital requirements")
        if risk["overall_risk_score"] < 4:
            weaknesses.append(f"Significant risk factors - multiple high-risk areas")
        if competitive["competitive_score"] < 6:
            weaknesses.append(f"Weak competitive positioning - unclear differentiation")
        
        return weaknesses if weaknesses else ["No significant weaknesses identified"]
    
    async def _generate_next_steps(self, overall_score: float) -> list:
        """Generate recommended next steps based on viability"""
        if overall_score >= 8:
            return [
                "Proceed with business plan development",
                "Assemble core team",
                "Begin fundraising preparation",
                "Develop detailed go-to-market strategy"
            ]
        elif overall_score >= 6:
            return [
                "Validate key assumptions through market research",
                "Refine business model based on feedback",
                "Address identified gaps and risks",
                "Create detailed implementation plan"
            ]
        elif overall_score >= 4:
            return [
                "Conduct deeper market validation",
                "Consider pivoting approach based on analysis",
                "Get expert feedback on key areas",
                "Reassess after making changes"
            ]
        else:
            return [
                "Reconsider business model fundamentals",
                "Explore alternative market segments",
                "Consider pivoting or combining ideas",
                "Revisit assumptions with fresh perspective"
            ]
    
    def _assess_viability(self, overall_score: float) -> Dict[str, Any]:
        """Assess overall business viability"""
        if overall_score >= 8:
            return {
                "status": "Highly Viable",
                "description": "Strong business potential with positive indicators across all dimensions",
                "recommendation": "Proceed with business planning and implementation"
            }
        elif overall_score >= 6:
            return {
                "status": "Viable",
                "description": "Good business potential with some areas needing refinement",
                "recommendation": "Address identified gaps and refine strategy before launch"
            }
        elif overall_score >= 4:
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
