"""
Financial Analysis Module - Projects financial performance and requirements
"""

from typing import Dict, Any
from openai import OpenAI
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class FinancialAnalysisService:
    """Service for financial analysis"""
    
    def __init__(self):
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model
    
    async def analyze_financials(self, idea_context: str) -> Dict[str, Any]:
        """
        Comprehensive financial analysis
        
        Args:
            idea_context: Context about the business idea
            
        Returns:
            Dictionary with financial analysis results
        """
        try:
            # Revenue Model
            revenue_model = await self._analyze_revenue_model(idea_context)
            
            # Cost Structure
            cost_structure = await self._analyze_cost_structure(idea_context)
            
            # Break-even Analysis
            break_even = await self._analyze_break_even(idea_context)
            
            # Profitability Projection
            profitability = await self._project_profitability(idea_context)
            
            # Funding Requirements
            funding_req = await self._estimate_funding_requirements(idea_context)
            
            # Financial Score
            financial_score = await self._calculate_financial_score(
                revenue_model, cost_structure, break_even, profitability, funding_req
            )
            
            return {
                "revenue_model": revenue_model,
                "cost_structure": cost_structure,
                "break_even_analysis": break_even,
                "profitability_projection": profitability,
                "funding_requirements": funding_req,
                "financial_score": financial_score,
                "full_analysis": {
                    "revenue": revenue_model,
                    "costs": cost_structure,
                    "break_even": break_even,
                    "profitability": profitability,
                    "funding": funding_req
                }
            }
        
        except Exception as e:
            logger.error(f"Financial analysis error: {str(e)}")
            raise
    
    async def _analyze_revenue_model(self, idea_context: str) -> str:
        """Analyze revenue streams and pricing"""
        prompt = f"""
Analyze the revenue model for this business:

{idea_context}

Provide:
1. Primary revenue streams
2. Pricing strategy recommendations
3. Average revenue per customer (ARPU) estimates
4. Revenue projections for Year 1, 2, 3
5. Pricing competitive analysis

Use specific numbers and ranges. Keep response concise (100-150 words).
        """
        return await self._call_openai(prompt)
    
    async def _analyze_cost_structure(self, idea_context: str) -> str:
        """Analyze cost structure and variable vs fixed costs"""
        prompt = f"""
Analyze the cost structure for this business:

{idea_context}

Provide:
1. Major cost categories (COGS, operations, marketing, etc.)
2. Fixed vs variable costs breakdown
3. Cost per customer/unit estimates
4. Gross margin expectations
5. Operating expense projections

Use specific dollar amounts or percentages. Keep response concise (100-150 words).
        """
        return await self._call_openai(prompt)
    
    async def _analyze_break_even(self, idea_context: str) -> str:
        """Calculate break-even point"""
        prompt = f"""
Calculate the break-even analysis for this business:

{idea_context}

Provide:
1. Break-even point (units/revenue required)
2. Time to break-even estimate
3. Customer acquisition cost (CAC)
4. Customer lifetime value (LTV)
5. LTV:CAC ratio and implications

Use specific numbers. Keep response concise (100-150 words).
        """
        return await self._call_openai(prompt)
    
    async def _project_profitability(self, idea_context: str) -> str:
        """Project profitability over time"""
        prompt = f"""
Project profitability for this business over 3-5 years:

{idea_context}

Provide:
1. Year 1, Year 2, Year 3 profit/loss projections
2. Profitability timeline and when profitability is reached
3. Profit margin targets
4. Path to profitability
5. Key assumptions behind projections

Use specific dollar amounts. Keep response concise (100-150 words).
        """
        return await self._call_openai(prompt)
    
    async def _estimate_funding_requirements(self, idea_context: str) -> str:
        """Estimate capital needs"""
        prompt = f"""
Estimate funding requirements for this business:

{idea_context}

Provide:
1. Initial capital required to launch
2. Funding breakdown across categories
3. Operating capital requirements (burn rate)
4. Runway estimates with different funding scenarios
5. Recommended funding timeline and sources

Use specific dollar amounts. Keep response concise (100-150 words).
        """
        return await self._call_openai(prompt)
    
    async def _calculate_financial_score(self, revenue: str, costs: str, 
                                        break_even: str, profitability: str, 
                                        funding: str) -> float:
        """Calculate financial viability score 1-10"""
        prompt = f"""
Based on this financial analysis, score the financial viability from 1-10 where:
1 = Poor financial prospects
5 = Average financial potential
10 = Excellent financial opportunity

Revenue Model: {revenue[:150]}
Cost Structure: {costs[:150]}
Break-even: {break_even[:150]}
Profitability: {profitability[:150]}
Funding: {funding[:150]}

Respond with ONLY a single number between 1 and 10.
        """
        
        try:
            response = await self._call_openai(prompt)
            score = float(response.strip().split()[0])
            return max(1.0, min(10.0, score))
        except Exception as e:
            logger.error(f"Score calculation error: {str(e)}")
            return 5.0
    
    async def _call_openai(self, prompt: str) -> str:
        """Call OpenAI API"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional financial analyst with expertise in business modeling, financial projections, and startup finance."
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
