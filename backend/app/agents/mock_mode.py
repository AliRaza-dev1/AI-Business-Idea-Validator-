"""
Mock Agent Mode - For testing without OpenAI API key
This module provides simulated AI responses for development and testing
"""

import json
import logging

logger = logging.getLogger(__name__)

class MockAgentMode:
    """Provides mock responses for all agents when API key is invalid"""
    
    @staticmethod
    def get_market_analysis(idea_title: str, description: str) -> dict:
        """Mock market analysis response"""
        logger.info(f"[MOCK_AGENT] Generating mock market analysis for: {idea_title}")
        return {
            "score": 22,
            "confidence": 85,
            "confidence_reason": "Strong market indicators based on idea description",
            "reasoning": f"The {idea_title} addresses a significant market gap in the industry.",
            "tam_sam_som": {
                "tam": "$5-10B",
                "sam": "$1-2B",
                "som": "$200-500M"
            },
            "target_audience": "Enterprise and SMB segments",
            "market_trends": "Growing demand for AI-powered solutions in this vertical",
            "retrieved_knowledge_sources": ["Market Research", "Industry Reports"]
        }
    
    @staticmethod
    def get_competition_analysis(idea_title: str) -> dict:
        """Mock competition analysis response"""
        logger.info(f"[MOCK_AGENT] Generating mock competition analysis for: {idea_title}")
        return {
            "competition": {
                "score": 18,
                "confidence": 80,
                "confidence_reason": "Clear competitive landscape identified",
                "reasoning": f"{idea_title} has moderate competition with differentiation opportunity",
                "competitor_landscape": "Moderate fragmentation with 3-5 major players",
                "competitive_advantage": "Unique approach to problem solving",
                "defensibility": "Strong IP potential",
                "market_positioning": "Clear differentiation possible"
            },
            "bmc": {
                "value_proposition": {"details": "Delivers unique value through innovation", "framework_source": "Business Model Canvas"},
                "key_activities": "Product development, customer acquisition",
                "revenue_streams": ["Subscription", "Premium features"]
            }
        }
    
    @staticmethod
    def get_financial_analysis(business_model: str) -> dict:
        """Mock financial analysis response"""
        logger.info(f"[MOCK_AGENT] Generating mock financial analysis")
        return {
            "score": 17,
            "confidence": 82,
            "confidence_reason": "Clear SaaS economics demonstrated",
            "reasoning": f"Financial model shows strong unit economics with {business_model} approach",
            "revenue_model": business_model or "SaaS Subscription",
            "cost_structure": ["R&D", "Infrastructure", "Customer Acquisition", "Operations"],
            "gross_margin": "75-80%",
            "payback_period": "12-18 months",
            "break_even_timeline": "18-24 months",
            "funding_requirement": "$500K-1M for MVP",
            "capital_efficiency": "High"
        }
    
    @staticmethod
    def get_risk_analysis() -> dict:
        """Mock risk analysis response"""
        logger.info(f"[MOCK_AGENT] Generating mock risk analysis")
        return {
            "score": 16,
            "confidence": 78,
            "confidence_reason": "Standard startup risks identified and mitigated",
            "reasoning": "Primary risks are market adoption and competitive response - manageable with proper strategy",
            "key_risks": [
                "Market adoption slower than expected",
                "Competitive response from incumbents",
                "Regulatory changes"
            ],
            "mitigation_strategies": [
                "Pre-sell MVP to validate demand",
                "Build strong IP moat early",
                "Engage regulatory bodies proactively"
            ],
            "failure_patterns": "Avoided through clear differentiation and market validation"
        }
    
    @staticmethod
    def get_feasibility_analysis() -> dict:
        """Mock feasibility analysis response"""
        logger.info(f"[MOCK_AGENT] Generating mock feasibility analysis")
        return {
            "score": 13,
            "confidence": 80,
            "confidence_reason": "Technical feasibility proven with MVP blueprint",
            "reasoning": "Solution can be built with current technology stack",
            "technical_complexity": "Moderate",
            "required_expertise": ["Full-stack development", "AI/ML", "Product management"],
            "scalability_factors": "90% gross margins enable rapid scaling",
            "time_to_market": "6-12 months for MVP",
            "investor_readiness": {
                "investor_score": 75,
                "funding_stage_recommendation": "Seed ($500K-1M)"
            }
        }
    
    @staticmethod
    def get_swot_analysis(idea_title: str) -> dict:
        """Mock SWOT analysis response"""
        logger.info(f"[MOCK_AGENT] Generating mock SWOT analysis for: {idea_title}")
        return {
            "strengths": [
                {"text": "Innovative approach to market problem", "framework_source": "SWOT Analysis", "impact": "high"},
                {"text": "Strong founder-market fit", "framework_source": "SWOT Analysis", "impact": "high"},
                {"text": "Clear value proposition", "framework_source": "SWOT Analysis", "impact": "medium"}
            ],
            "weaknesses": [
                {"text": "Early stage - limited brand recognition", "framework_source": "SWOT Analysis", "impact": "medium"},
                {"text": "Requires significant initial investment", "framework_source": "SWOT Analysis", "impact": "medium"}
            ],
            "opportunities": [
                {"text": "Rapidly growing market segment", "framework_source": "Market Research", "impact": "high"},
                {"text": "Potential for international expansion", "framework_source": "Market Research", "impact": "high"},
                {"text": "Partnership with larger players", "framework_source": "Strategic Analysis", "impact": "medium"}
            ],
            "threats": [
                {"text": "Established competitors may enter market", "framework_source": "Competitive Analysis", "impact": "high"},
                {"text": "Economic downturn could impact adoption", "framework_source": "Market Analysis", "impact": "medium"}
            ]
        }
    
    @staticmethod
    def get_recommendation(idea_title: str, overall_score: float) -> dict:
        """Mock recommendation response"""
        logger.info(f"[MOCK_AGENT] Generating mock recommendation for: {idea_title}")
        
        viability_verdict = "Highly Viable"
        if overall_score < 50:
            viability_verdict = "Moderate Viability"
        elif overall_score < 60:
            viability_verdict = "Good Viability"
        elif overall_score >= 70:
            viability_verdict = "Highly Viable"
        
        return {
            "overall_score": overall_score,
            "overall_confidence": 81,
            "overall_confidence_reason": "Comprehensive analysis validated against Lean Startup and SWOT frameworks",
            "viability_verdict": viability_verdict,
            "summary": f"{idea_title} demonstrates strong potential with manageable risks",
            "score_breakdown": {
                "market_demand": {"score": 22, "max_score": 25, "reasoning": "Strong TAM and clear target market"},
                "competition": {"score": 18, "max_score": 20, "reasoning": "Differentiated positioning possible"},
                "revenue_potential": {"score": 17, "max_score": 20, "reasoning": "Solid SaaS economics"},
                "scalability": {"score": 13, "max_score": 15, "reasoning": "High-margin business model"},
                "risk_management": {"score": 16, "max_score": 20, "reasoning": "Manageable startup risks"}
            },
            "action_plan": [
                {"recommendation": "Validate market demand with 20-30 customer interviews", "framework_source": "Lean Startup", "priority": "high", "category": "market"},
                {"recommendation": "Build MVP with core features in 3 months", "framework_source": "Lean Startup", "priority": "high", "category": "product"},
                {"recommendation": "Establish IP protection strategy", "framework_source": "Strategic Planning", "priority": "high", "category": "legal"},
                {"recommendation": "Prepare seed round pitch deck", "framework_source": "Fundraising", "priority": "medium", "category": "finance"}
            ],
            "next_steps": [
                "Conduct customer discovery interviews",
                "Build functional MVP",
                "Establish advisory board",
                "Prepare for seed fundraising"
            ],
            "key_metrics": {
                "customer_acquisition_cost": "$200-500",
                "lifetime_value": "$5,000-10,000",
                "payback_period_months": 12
            }
        }
