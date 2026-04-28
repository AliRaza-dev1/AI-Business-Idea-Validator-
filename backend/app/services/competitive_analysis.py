"""
Competitive Analysis Module - Analyzes competitive landscape and positioning
"""

from typing import Dict, Any
from openai import OpenAI
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class CompetitiveAnalysisService:
    """Service for competitive analysis"""
    
    def __init__(self):
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model
    
    async def analyze_competition(self, idea_context: str) -> Dict[str, Any]:
        """
        Comprehensive competitive analysis
        
        Args:
            idea_context: Context about the business idea
            
        Returns:
            Dictionary with competitive analysis results
        """
        try:
            # Competitor Identification
            competitors = await self._identify_competitors(idea_context)
            
            # Competitive Advantages
            advantages = await self._analyze_competitive_advantages(idea_context)
            
            # Market Positioning
            positioning = await self._develop_positioning_strategy(idea_context)
            
            # Differentiation Analysis
            differentiation = await self._analyze_differentiation(idea_context)
            
            # Threat Level
            threat_analysis = await self._analyze_competitive_threats(idea_context)
            
            # Competitive Score (how well positioned)
            competitive_score = await self._calculate_competitive_score(
                advantages, positioning, differentiation, threat_analysis
            )
            
            return {
                "competitor_landscape": competitors,
                "competitive_advantages": advantages,
                "market_positioning": positioning,
                "differentiation": differentiation,
                "competitive_threats": threat_analysis,
                "competitive_score": competitive_score,
                "full_analysis": {
                    "competitors": competitors,
                    "advantages": advantages,
                    "positioning": positioning,
                    "differentiation": differentiation,
                    "threats": threat_analysis
                }
            }
        
        except Exception as e:
            logger.error(f"Competitive analysis error: {str(e)}")
            raise
    
    async def _identify_competitors(self, idea_context: str) -> str:
        """Identify direct and indirect competitors"""
        prompt = f"""
Identify competitors for this business idea:

{idea_context}

Provide:
1. Direct competitors (offering similar solutions)
2. Indirect competitors (alternative solutions)
3. Competitor strengths and weaknesses
4. Market share estimates
5. Competitive intensity level (low/medium/high)

Keep response specific with competitor names where possible (100-150 words).
        """
        return await self._call_openai(prompt)
    
    async def _analyze_competitive_advantages(self, idea_context: str) -> str:
        """Analyze competitive advantages vs existing solutions"""
        prompt = f"""
Analyze the competitive advantages of this business idea:

{idea_context}

Provide:
1. Key competitive advantages vs existing solutions
2. Unique value proposition
3. Sustainable competitive advantages (defensible?)
4. Unfair advantages or moats
5. Timeline sustainability of advantages

Be specific about what makes this idea better. Keep response concise (100-150 words).
        """
        return await self._call_openai(prompt)
    
    async def _develop_positioning_strategy(self, idea_context: str) -> str:
        """Develop market positioning strategy"""
        prompt = f"""
Develop a market positioning strategy for this business:

{idea_context}

Provide:
1. Target positioning ("position as the...")
2. Key messages and brand promise
3. Competitive positioning vs main competitors
4. Pricing positioning (premium/value/economy)
5. Go-to-market positioning angles

Keep response concise (100-150 words).
        """
        return await self._call_openai(prompt)
    
    async def _analyze_differentiation(self, idea_context: str) -> str:
        """Analyze product/service differentiation"""
        prompt = f"""
Analyze differentiation opportunities for this business:

{idea_context}

Provide:
1. Product/service differentiation angles
2. Price differentiation strategy
3. Channel/distribution differentiation
4. Marketing and branding differentiation
5. Customer experience differentiation
6. Long-term differentiation strategy

Keep response concise (100-150 words).
        """
        return await self._call_openai(prompt)
    
    async def _analyze_competitive_threats(self, idea_context: str) -> str:
        """Analyze competitive threats and risks"""
        prompt = f"""
Analyze competitive threats for this business:

{idea_context}

Provide:
1. Major competitive threats
2. Likelihood of new market entrants
3. Threat from existing players expanding
4. Competitive response scenarios
5. Risk mitigation strategies

Rate overall competitive threat level (low/medium/high).
Keep response concise (100-150 words).
        """
        return await self._call_openai(prompt)
    
    async def _calculate_competitive_score(self, advantages: str, positioning: str, 
                                          differentiation: str, threats: str) -> float:
        """Calculate competitive positioning score 1-10"""
        prompt = f"""
Based on this competitive analysis, score the competitive positioning from 1-10 where:
1 = Poor competitive position, easily beaten
5 = Average competitive position
10 = Excellent competitive position, strong differentiation

Competitive Advantages: {advantages[:150]}
Market Positioning: {positioning[:150]}
Differentiation: {differentiation[:150]}
Competitive Threats: {threats[:150]}

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
                        "content": "You are a competitive strategy expert with deep expertise in market positioning, competitive advantage, and differentiation strategies."
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
