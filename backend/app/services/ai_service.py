from openai import OpenAI
from app.core.config import settings
import json
import logging

logger = logging.getLogger(__name__)


class AIAnalysisService:
    """Service for AI-powered analysis using OpenAI"""
    
    def __init__(self):
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model
    
    def analyze_idea(self, idea_title: str, description: str, problem: str, 
                    market: str, solution: str, value_prop: str, business_model: str) -> dict:
        """
        Comprehensive analysis of a business idea using AI
        Returns a dictionary with all analysis metrics and insights
        """
        
        idea_context = f"""
Title: {idea_title}
Description: {description}
Problem Statement: {problem}
Target Market: {market}
Proposed Solution: {solution}
Value Proposition: {value_prop}
Business Model: {business_model}
        """
        
        try:
            # Market Analysis
            market_analysis = self._analyze_market(idea_context)
            
            # Feasibility Analysis
            feasibility_analysis = self._analyze_feasibility(idea_context)
            
            # Financial Analysis
            financial_analysis = self._analyze_financial(idea_context)
            
            # Risk Assessment
            risk_analysis = self._analyze_risks(idea_context)
            
            # Competitive Analysis
            competitive_analysis = self._analyze_competition(idea_context)
            
            # Generate Scores and Recommendations
            scores = self._calculate_scores(
                market_analysis, feasibility_analysis, financial_analysis, risk_analysis
            )
            
            recommendations = self._generate_recommendations(
                market_analysis, feasibility_analysis, financial_analysis, risk_analysis, competitive_analysis
            )
            
            strengths = self._extract_strengths(idea_context, scores)
            weaknesses = self._extract_weaknesses(idea_context, scores)
            
            return {
                "market_score": scores["market_score"],
                "feasibility_score": scores["feasibility_score"],
                "financial_score": scores["financial_score"],
                "risk_score": scores["risk_score"],
                "overall_score": scores["overall_score"],
                "market_analysis": market_analysis,
                "feasibility_analysis": feasibility_analysis,
                "financial_analysis": financial_analysis,
                "risk_analysis": risk_analysis,
                "competitive_analysis": competitive_analysis,
                "strengths": strengths,
                "weaknesses": weaknesses,
                "recommendations": recommendations
            }
        
        except Exception as e:
            logger.error(f"Error in AI analysis: {str(e)}")
            raise
    
    def _analyze_market(self, idea_context: str) -> str:
        """Analyze market viability"""
        prompt = f"""
Analyze the market viability of this business idea:

{idea_context}

Provide a detailed market analysis covering:
1. Market size estimation
2. Growth trends and opportunities
3. Target audience identification
4. Market entry barriers
5. Competitive landscape overview

Format your response as a clear, structured analysis in 200-300 words.
        """
        return self._call_openai(prompt)
    
    def _analyze_feasibility(self, idea_context: str) -> str:
        """Analyze technical and operational feasibility"""
        prompt = f"""
Analyze the feasibility of this business idea:

{idea_context}

Provide a detailed feasibility assessment covering:
1. Technical requirements and complexity
2. Resource requirements (team, tools, infrastructure)
3. Timeline for implementation
4. Operational challenges
5. Required expertise and skill gaps

Format your response as a clear, structured analysis in 200-300 words.
        """
        return self._call_openai(prompt)
    
    def _analyze_financial(self, idea_context: str) -> str:
        """Analyze financial projections"""
        prompt = f"""
Analyze the financial potential of this business idea:

{idea_context}

Provide a detailed financial analysis covering:
1. Potential revenue streams
2. Cost structure estimation
3. Break-even point calculation
4. Profitability projection (3-year)
5. Funding requirements

Format your response as a clear, structured analysis in 200-300 words with specific numbers/ranges where possible.
        """
        return self._call_openai(prompt)
    
    def _analyze_risks(self, idea_context: str) -> str:
        """Assess risks and challenges"""
        prompt = f"""
Analyze the risks and challenges for this business idea:

{idea_context}

Provide a detailed risk assessment covering:
1. Market risks and uncertainties
2. Technical or operational risks
3. Financial risks
4. Competitive risks
5. Regulatory or compliance risks
6. Suggested mitigation strategies

Format your response as a clear, structured analysis in 200-300 words.
        """
        return self._call_openai(prompt)
    
    def _analyze_competition(self, idea_context: str) -> str:
        """Analyze competitive landscape"""
        prompt = f"""
Analyze the competitive landscape for this business idea:

{idea_context}

Provide a detailed competitive analysis covering:
1. Existing competitors in this space
2. Competitive advantages of this idea
3. Unique value proposition vs. competitors
4. Market positioning strategy
5. Differentiation factors

Format your response as a clear, structured analysis in 200-300 words.
        """
        return self._call_openai(prompt)
    
    def _calculate_scores(self, market: str, feasibility: str, financial: str, risk: str) -> dict:
        """Calculate numerical scores based on analyses"""
        prompt = f"""
Based on these analyses, provide numerical viability scores from 1-10 for each category:

Market Analysis: {market[:500]}...

Feasibility Analysis: {feasibility[:500]}...

Financial Analysis: {financial[:500]}...

Risk Analysis: {risk[:500]}...

Please respond with ONLY a JSON object in this exact format:
{{
    "market_score": <number>,
    "feasibility_score": <number>,
    "financial_score": <number>,
    "risk_score": <number>
}}

Calculate overall_score as the average of all four scores.
        """
        
        response = self._call_openai(prompt)
        try:
            scores = json.loads(response)
            scores["overall_score"] = (
                scores["market_score"] + scores["feasibility_score"] + 
                scores["financial_score"] + scores["risk_score"]
            ) / 4
            return scores
        except json.JSONDecodeError:
            logger.warning("Failed to parse scores, using defaults")
            return {
                "market_score": 5.0,
                "feasibility_score": 5.0,
                "financial_score": 5.0,
                "risk_score": 5.0,
                "overall_score": 5.0
            }
    
    def _generate_recommendations(self, market: str, feasibility: str, financial: str, 
                                 risk: str, competitive: str) -> list:
        """Generate actionable recommendations"""
        prompt = f"""
Based on these business analyses, provide 5-7 specific, actionable recommendations:

Market: {market[:300]}...
Feasibility: {feasibility[:300]}...
Financial: {financial[:300]}...
Risk: {risk[:300]}...
Competitive: {competitive[:300]}...

For each recommendation provide:
- The recommendation text
- Category (market, financial, technical, or operational)
- Priority (high, medium, or low)

Format as JSON array.
        """
        
        response = self._call_openai(prompt)
        try:
            # Extract JSON if embedded in text
            import re
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                recommendations = json.loads(json_match.group())
                return recommendations
            return []
        except (json.JSONDecodeError, AttributeError):
            logger.warning("Failed to parse recommendations")
            return []
    
    def _extract_strengths(self, idea_context: str, scores: dict) -> str:
        """Extract key strengths"""
        prompt = f"""
Based on this idea and its scores, provide 3-4 key strengths in bullet point format:

Idea: {idea_context}

Scores: {scores}

Be specific and actionable. Keep response under 150 words.
        """
        return self._call_openai(prompt)
    
    def _extract_weaknesses(self, idea_context: str, scores: dict) -> str:
        """Extract key weaknesses"""
        prompt = f"""
Based on this idea and its scores, provide 3-4 key weaknesses/challenges in bullet point format:

Idea: {idea_context}

Scores: {scores}

Be specific and constructive. Keep response under 150 words.
        """
        return self._call_openai(prompt)
    
    def _call_openai(self, prompt: str) -> str:
        """Call OpenAI API"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert business analyst and consultant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=settings.openai_temperature,
                max_tokens=settings.openai_max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise
