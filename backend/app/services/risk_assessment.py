"""
Risk Assessment Module - Identifies and mitigates business risks
"""

from typing import Dict, Any, List
from openai import OpenAI
from app.core.config import settings
import logging
import json

logger = logging.getLogger(__name__)


class RiskAssessmentService:
    """Service for risk assessment and mitigation"""
    
    def __init__(self):
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model
    
    async def assess_risks(self, idea_context: str) -> Dict[str, Any]:
        """
        Comprehensive risk assessment
        
        Args:
            idea_context: Context about the business idea
            
        Returns:
            Dictionary with risk assessment results
        """
        try:
            # Market Risks
            market_risks = await self._identify_market_risks(idea_context)
            
            # Technical Risks
            technical_risks = await self._identify_technical_risks(idea_context)
            
            # Financial Risks
            financial_risks = await self._identify_financial_risks(idea_context)
            
            # Operational Risks
            operational_risks = await self._identify_operational_risks(idea_context)
            
            # Mitigation Strategies
            mitigations = await self._generate_mitigation_strategies(idea_context)
            
            # Risk Score (lower is better)
            risk_score = await self._calculate_risk_score(
                market_risks, technical_risks, financial_risks, operational_risks
            )
            
            return {
                "market_risks": market_risks,
                "technical_risks": technical_risks,
                "financial_risks": financial_risks,
                "operational_risks": operational_risks,
                "mitigation_strategies": mitigations,
                "overall_risk_score": risk_score,  # Lower is better
                "full_analysis": {
                    "market": market_risks,
                    "technical": technical_risks,
                    "financial": financial_risks,
                    "operational": operational_risks,
                    "mitigations": mitigations
                }
            }
        
        except Exception as e:
            logger.error(f"Risk assessment error: {str(e)}")
            raise
    
    async def _identify_market_risks(self, idea_context: str) -> str:
        """Identify market-related risks"""
        prompt = f"""
Identify market-related risks for this business:

{idea_context}

List 4-6 specific market risks including:
1. Market demand uncertainty
2. Market saturation risks
3. Competitor responses
4. Customer acquisition challenges
5. Market volatility
6. Regulatory changes affecting market

For each risk, rate severity (high/medium/low) and likelihood (high/medium/low).
Keep response concise (100-150 words).
        """
        return await self._call_openai(prompt)
    
    async def _identify_technical_risks(self, idea_context: str) -> str:
        """Identify technical and operational risks"""
        prompt = f"""
Identify technical and operational risks for this business:

{idea_context}

List 4-6 specific technical/operational risks including:
1. Technology obsolescence
2. Technical complexity challenges
3. Infrastructure/scalability issues
4. Integration challenges
5. Data security/privacy risks
6. Performance and reliability concerns

For each risk, rate severity (high/medium/low) and likelihood (high/medium/low).
Keep response concise (100-150 words).
        """
        return await self._call_openai(prompt)
    
    async def _identify_financial_risks(self, idea_context: str) -> str:
        """Identify financial risks"""
        prompt = f"""
Identify financial risks for this business:

{idea_context}

List 4-6 specific financial risks including:
1. Burn rate and runway risks
2. Funding availability risks
3. Revenue uncertainty
4. Cost overrun risks
5. Cash flow timing issues
6. Foreign exchange or external economic risks

For each risk, rate severity (high/medium/low) and likelihood (high/medium/low).
Keep response concise (100-150 words).
        """
        return await self._call_openai(prompt)
    
    async def _identify_operational_risks(self, idea_context: str) -> str:
        """Identify operational and organizational risks"""
        prompt = f"""
Identify operational and organizational risks for this business:

{idea_context}

List 4-6 specific operational/organizational risks including:
1. Team skill gaps
2. Key person dependencies
3. Organizational scaling challenges
4. Vendor/supplier dependencies
5. Supply chain disruptions
6. Geographical or external dependencies

For each risk, rate severity (high/medium/low) and likelihood (high/medium/low).
Keep response concise (100-150 words).
        """
        return await self._call_openai(prompt)
    
    async def _generate_mitigation_strategies(self, idea_context: str) -> str:
        """Generate risk mitigation strategies"""
        prompt = f"""
Based on this business idea, propose specific mitigation strategies for key risks:

{idea_context}

For 5-7 key risks, provide:
1. Risk description
2. Mitigation strategy
3. Owner/responsibility
4. Timeline for implementation
5. Success metrics

Format as clear, actionable strategies. Keep response concise (150-200 words).
        """
        return await self._call_openai(prompt)
    
    async def _calculate_risk_score(self, market: str, technical: str, 
                                   financial: str, operational: str) -> float:
        """
        Calculate overall risk score (1-10, where 10 is highest risk)
        Returns a viability score (10 minus risk) for consistency
        """
        prompt = f"""
Based on these identified risks, provide an overall risk rating from 1-10 where:
1 = Very low risk / highly viable
5 = Medium risk / moderate viability
10 = Very high risk / low viability

Market Risks: {market[:150]}
Technical Risks: {technical[:150]}
Financial Risks: {financial[:150]}
Operational Risks: {operational[:150]}

Respond with ONLY a single number between 1 and 10.
        """
        
        try:
            response = await self._call_openai(prompt)
            risk_score = float(response.strip().split()[0])
            # Convert risk score to viability score (10 = low risk, 1 = high risk)
            viability_score = 11 - max(1.0, min(10.0, risk_score))
            return viability_score
        except Exception as e:
            logger.error(f"Risk score calculation error: {str(e)}")
            return 5.0
    
    async def _call_openai(self, prompt: str) -> str:
        """Call OpenAI API"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert risk management consultant with extensive experience in identifying and mitigating business risks across all categories."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=settings.openai_temperature,
                max_tokens=settings.openai_max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise
