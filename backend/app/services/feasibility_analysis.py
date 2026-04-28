"""
Feasibility Analysis Module - Evaluates technical and operational feasibility
"""

from typing import Dict, Any
from openai import OpenAI
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class FeasibilityAnalysisService:
    """Service for feasibility analysis"""
    
    def __init__(self):
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model
    
    async def analyze_feasibility(self, idea_context: str) -> Dict[str, Any]:
        """
        Comprehensive feasibility analysis
        
        Args:
            idea_context: Context about the business idea
            
        Returns:
            Dictionary with feasibility analysis results
        """
        try:
            # Technical Requirements
            technical_reqs = await self._analyze_technical_requirements(idea_context)
            
            # Resource Requirements
            resource_reqs = await self._analyze_resource_requirements(idea_context)
            
            # Timeline Estimation
            timeline = await self._estimate_timeline(idea_context)
            
            # Operational Challenges
            challenges = await self._identify_operational_challenges(idea_context)
            
            # Feasibility Score
            feasibility_score = await self._calculate_feasibility_score(
                technical_reqs, resource_reqs, timeline, challenges
            )
            
            return {
                "technical_requirements": technical_reqs,
                "resource_requirements": resource_reqs,
                "timeline": timeline,
                "operational_challenges": challenges,
                "feasibility_score": feasibility_score,
                "full_analysis": {
                    "technical": technical_reqs,
                    "resources": resource_reqs,
                    "timeline": timeline,
                    "challenges": challenges
                }
            }
        
        except Exception as e:
            logger.error(f"Feasibility analysis error: {str(e)}")
            raise
    
    async def _analyze_technical_requirements(self, idea_context: str) -> str:
        """Analyze technical infrastructure and requirements"""
        prompt = f"""
Analyze the technical requirements for this business idea:

{idea_context}

Provide:
1. Technology stack recommendations
2. Infrastructure requirements (servers, cloud, etc.)
3. Technical complexity level (simple/medium/complex)
4. Security and compliance requirements
5. Scalability considerations

Keep response concise (100-150 words).
        """
        return await self._call_openai(prompt)
    
    async def _analyze_resource_requirements(self, idea_context: str) -> str:
        """Analyze resource needs"""
        prompt = f"""
Analyze the resource requirements for this business:

{idea_context}

Provide:
1. Team size and composition needed
2. Key roles required
3. Budget estimate for launch
4. Tools and software requirements
5. Infrastructure and equipment costs

Keep response concise (100-150 words).
        """
        return await self._call_openai(prompt)
    
    async def _estimate_timeline(self, idea_context: str) -> str:
        """Estimate implementation timeline"""
        prompt = f"""
Create a realistic implementation timeline for this business:

{idea_context}

Provide:
1. MVP (Minimum Viable Product) timeline
2. Full launch timeline
3. Key milestones and phases
4. Critical path items
5. Potential delays and buffers

Keep response concise (100-150 words).
        """
        return await self._call_openai(prompt)
    
    async def _identify_operational_challenges(self, idea_context: str) -> str:
        """Identify operational and execution challenges"""
        prompt = f"""
Identify key operational and execution challenges for this business:

{idea_context}

Provide:
1. Main execution challenges
2. Operational complexity areas
3. Risk areas in implementation
4. Supply chain or logistics considerations
5. Recommended mitigation strategies

Keep response concise (100-150 words).
        """
        return await self._call_openai(prompt)
    
    async def _calculate_feasibility_score(self, technical: str, resources: str, 
                                          timeline: str, challenges: str) -> float:
        """Calculate feasibility score 1-10"""
        prompt = f"""
Based on this feasibility analysis, score the overall feasibility of implementation from 1-10 where:
1 = Very difficult/infeasible
5 = Moderately feasible
10 = Highly feasible

Technical: {technical[:200]}
Resources: {resources[:200]}
Timeline: {timeline[:200]}
Challenges: {challenges[:200]}

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
                        "content": "You are an expert technical architect and operational consultant with deep expertise in feasibility assessment."
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
