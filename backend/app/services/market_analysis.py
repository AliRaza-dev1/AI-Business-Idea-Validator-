"""
Market Analysis Module - Analyzes market viability of business ideas
"""

from typing import Dict, Any
from openai import OpenAI
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class MarketAnalysisService:
    """Service for market analysis"""
    
    def __init__(self):
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model
    
    async def analyze_market(self, idea_context: str) -> Dict[str, Any]:
        """
        Comprehensive market analysis
        
        Args:
            idea_context: Context about the business idea
            
        Returns:
            Dictionary with market analysis results
        """
        try:
            # Market Size Estimation
            market_size = await self._estimate_market_size(idea_context)
            
            # Growth Trends
            growth_trends = await self._analyze_growth_trends(idea_context)
            
            # Target Audience
            target_audience = await self._identify_target_audience(idea_context)
            
            # Market Entry Strategy
            entry_strategy = await self._market_entry_strategy(idea_context)
            
            # Market Score
            market_score = await self._calculate_market_score(
                market_size, growth_trends, target_audience, entry_strategy
            )
            
            return {
                "market_size": market_size,
                "growth_trends": growth_trends,
                "target_audience": target_audience,
                "entry_strategy": entry_strategy,
                "market_score": market_score,
                "full_analysis": {
                    "market_size": market_size,
                    "growth_trends": growth_trends,
                    "target_audience": target_audience,
                    "entry_strategy": entry_strategy
                }
            }
        
        except Exception as e:
            logger.error(f"Market analysis error: {str(e)}")
            raise
    
    async def _estimate_market_size(self, idea_context: str) -> str:
        """Estimate total addressable market (TAM)"""
        prompt = f"""
Based on this business idea, estimate the Total Addressable Market (TAM):

{idea_context}

Provide:
1. Total Addressable Market (TAM) estimate with size in $ or units
2. Serviceable Available Market (SAM) estimate
3. Serviceable Obtainable Market (SOM) for first 3-5 years
4. Market growth rate projection

Be specific with numbers and ranges where possible. Keep response concise (100-150 words).
        """
        return await self._call_openai(prompt)
    
    async def _analyze_growth_trends(self, idea_context: str) -> str:
        """Analyze current market growth trends"""
        prompt = f"""
Analyze the growth trends and opportunities for this market:

{idea_context}

Provide:
1. Current market growth rate
2. Emerging trends benefiting this idea
3. Market drivers and catalysts
4. Economic factors
5. 3-5 year market outlook

Keep response concise (100-150 words).
        """
        return await self._call_openai(prompt)
    
    async def _identify_target_audience(self, idea_context: str) -> str:
        """Identify and describe target customers"""
        prompt = f"""
Identify the ideal target audience/customers for this idea:

{idea_context}

Provide:
1. Primary customer segments
2. Customer demographics and psychographics
3. Customer pain points this solves
4. Customer acquisition strategy
5. Willingness to pay estimates

Keep response concise (100-150 words).
        """
        return await self._call_openai(prompt)
    
    async def _market_entry_strategy(self, idea_context: str) -> str:
        """Develop market entry strategy"""
        prompt = f"""
Develop a market entry strategy for this business:

{idea_context}

Provide:
1. Go-to-market strategy
2. Entry barriers and how to overcome them
3. Competitive positioning
4. Key partnerships needed
5. First 12-month milestones

Keep response concise (100-150 words).
        """
        return await self._call_openai(prompt)
    
    async def _calculate_market_score(self, market_size: str, growth: str, 
                                     audience: str, strategy: str) -> float:
        """Calculate market viability score 1-10"""
        prompt = f"""
Based on this market analysis, score the market opportunity from 1-10 where:
1 = Poor market opportunity
5 = Average market opportunity
10 = Excellent market opportunity

Market Size: {market_size[:200]}
Growth Trends: {growth[:200]}
Target Audience: {audience[:200]}
Entry Strategy: {strategy[:200]}

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
                        "content": "You are an expert market analyst with deep knowledge of market dynamics and trends."
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
