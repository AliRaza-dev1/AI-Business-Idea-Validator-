"""
Tests for Analysis Modules - Market, Feasibility, Financial, Risk, Competitive
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from app.services.market_analysis import MarketAnalysisService
from app.services.feasibility_analysis import FeasibilityAnalysisService
from app.services.financial_analysis import FinancialAnalysisService
from app.services.risk_assessment import RiskAssessmentService
from app.services.competitive_analysis import CompetitiveAnalysisService
from app.services.analysis_orchestrator import AnalysisOrchestrator


# Test fixtures
@pytest.fixture
def market_service():
    """Market analysis service fixture"""
    return MarketAnalysisService()


@pytest.fixture
def feasibility_service():
    """Feasibility analysis service fixture"""
    return FeasibilityAnalysisService()


@pytest.fixture
def financial_service():
    """Financial analysis service fixture"""
    return FinancialAnalysisService()


@pytest.fixture
def risk_service():
    """Risk assessment service fixture"""
    return RiskAssessmentService()


@pytest.fixture
def competitive_service():
    """Competitive analysis service fixture"""
    return CompetitiveAnalysisService()


@pytest.fixture
def orchestrator():
    """Analysis orchestrator fixture"""
    return AnalysisOrchestrator()


@pytest.fixture
def sample_idea_context():
    """Sample business idea context"""
    return """
Business Idea: AI Email Management Assistant

Description: An AI-powered email management tool that automatically categorizes, 
prioritizes, and summarizes emails, helping professionals save 2+ hours daily.

Problem Statement: Professionals spend excessive time managing email overload

Target Market: Corporate professionals, executives (B2B, enterprise focus)

Proposed Solution: SaaS application with AI-powered email intelligence

Value Proposition: Save 2+ hours daily through intelligent email automation

Business Model: Freemium with premium enterprise plans
    """


# Market Analysis Tests
@pytest.mark.asyncio
async def test_market_analysis_structure(market_service, sample_idea_context):
    """Test that market analysis returns expected structure"""
    with patch.object(market_service, '_call_openai', new_callable=AsyncMock) as mock_call:
        mock_call.return_value = "Market size: $50B TAM, Growing 20% annually"
        
        result = await market_service.analyze_market(sample_idea_context)
        
        assert "market_score" in result
        assert "market_size" in result
        assert "growth_trends" in result
        assert "target_audience" in result
        assert "entry_strategy" in result
        assert 1.0 <= result["market_score"] <= 10.0


@pytest.mark.asyncio
async def test_market_score_bounds(market_service):
    """Test market score is within valid bounds"""
    with patch.object(market_service, '_call_openai', new_callable=AsyncMock) as mock_call:
        mock_call.return_value = "8"
        
        score = await market_service._calculate_market_score("test", "test", "test", "test")
        assert 1.0 <= score <= 10.0


# Feasibility Analysis Tests
@pytest.mark.asyncio
async def test_feasibility_analysis_structure(feasibility_service, sample_idea_context):
    """Test that feasibility analysis returns expected structure"""
    with patch.object(feasibility_service, '_call_openai', new_callable=AsyncMock) as mock_call:
        mock_call.return_value = "Moderate complexity, 6-month development timeline"
        
        result = await feasibility_service.analyze_feasibility(sample_idea_context)
        
        assert "feasibility_score" in result
        assert "technical_requirements" in result
        assert "resource_requirements" in result
        assert "timeline" in result
        assert "operational_challenges" in result
        assert 1.0 <= result["feasibility_score"] <= 10.0


@pytest.mark.asyncio
async def test_feasibility_score_bounds(feasibility_service):
    """Test feasibility score is within valid bounds"""
    with patch.object(feasibility_service, '_call_openai', new_callable=AsyncMock) as mock_call:
        mock_call.return_value = "6.5"
        
        score = await feasibility_service._calculate_feasibility_score("test", "test", "test", "test")
        assert 1.0 <= score <= 10.0


# Financial Analysis Tests
@pytest.mark.asyncio
async def test_financial_analysis_structure(financial_service, sample_idea_context):
    """Test that financial analysis returns expected structure"""
    with patch.object(financial_service, '_call_openai', new_callable=AsyncMock) as mock_call:
        mock_call.return_value = "Strong revenue potential with $50K MRR by year 2"
        
        result = await financial_service.analyze_financials(sample_idea_context)
        
        assert "financial_score" in result
        assert "revenue_model" in result
        assert "cost_structure" in result
        assert "break_even_analysis" in result
        assert "profitability_projection" in result
        assert "funding_requirements" in result
        assert 1.0 <= result["financial_score"] <= 10.0


@pytest.mark.asyncio
async def test_financial_score_bounds(financial_service):
    """Test financial score is within valid bounds"""
    with patch.object(financial_service, '_call_openai', new_callable=AsyncMock) as mock_call:
        mock_call.return_value = "7"
        
        score = await financial_service._calculate_financial_score("test", "test", "test", "test", "test")
        assert 1.0 <= score <= 10.0


# Risk Assessment Tests
@pytest.mark.asyncio
async def test_risk_assessment_structure(risk_service, sample_idea_context):
    """Test that risk assessment returns expected structure"""
    with patch.object(risk_service, '_call_openai', new_callable=AsyncMock) as mock_call:
        mock_call.return_value = "Moderate risks with clear mitigation strategies"
        
        result = await risk_service.assess_risks(sample_idea_context)
        
        assert "overall_risk_score" in result
        assert "market_risks" in result
        assert "technical_risks" in result
        assert "financial_risks" in result
        assert "operational_risks" in result
        assert "mitigation_strategies" in result
        assert 1.0 <= result["overall_risk_score"] <= 10.0


@pytest.mark.asyncio
async def test_risk_score_bounds(risk_service):
    """Test risk score is within valid bounds"""
    with patch.object(risk_service, '_call_openai', new_callable=AsyncMock) as mock_call:
        mock_call.return_value = "6"
        
        score = await risk_service._calculate_risk_score("test", "test", "test", "test")
        assert 1.0 <= score <= 10.0


# Competitive Analysis Tests
@pytest.mark.asyncio
async def test_competitive_analysis_structure(competitive_service, sample_idea_context):
    """Test that competitive analysis returns expected structure"""
    with patch.object(competitive_service, '_call_openai', new_callable=AsyncMock) as mock_call:
        mock_call.return_value = "Strong differentiation vs competitors"
        
        result = await competitive_service.analyze_competition(sample_idea_context)
        
        assert "competitive_score" in result
        assert "competitor_landscape" in result
        assert "competitive_advantages" in result
        assert "market_positioning" in result
        assert "differentiation" in result
        assert "competitive_threats" in result
        assert 1.0 <= result["competitive_score"] <= 10.0


@pytest.mark.asyncio
async def test_competitive_score_bounds(competitive_service):
    """Test competitive score is within valid bounds"""
    with patch.object(competitive_service, '_call_openai', new_callable=AsyncMock) as mock_call:
        mock_call.return_value = "8"
        
        score = await competitive_service._calculate_competitive_score("test", "test", "test", "test")
        assert 1.0 <= score <= 10.0


# Orchestrator Tests
@pytest.mark.asyncio
async def test_orchestrator_full_analysis(orchestrator):
    """Test orchestrator runs full analysis"""
    with patch.object(orchestrator.market_service, 'analyze_market', new_callable=AsyncMock) as mock_market, \
         patch.object(orchestrator.feasibility_service, 'analyze_feasibility', new_callable=AsyncMock) as mock_feasibility, \
         patch.object(orchestrator.financial_service, 'analyze_financials', new_callable=AsyncMock) as mock_financial, \
         patch.object(orchestrator.risk_service, 'assess_risks', new_callable=AsyncMock) as mock_risk, \
         patch.object(orchestrator.competitive_service, 'analyze_competition', new_callable=AsyncMock) as mock_competitive:
        
        # Setup mock returns
        mock_market.return_value = {
            "market_score": 7.5,
            "full_analysis": {"market_size": "test"}
        }
        mock_feasibility.return_value = {
            "feasibility_score": 8.0,
            "full_analysis": {"technical": "test"}
        }
        mock_financial.return_value = {
            "financial_score": 7.0,
            "full_analysis": {"revenue": "test"},
            "revenue_model": "test",
            "funding_requirements": "test"
        }
        mock_risk.return_value = {
            "overall_risk_score": 7.5,
            "market_risks": "test",
            "technical_risks": "test",
            "financial_risks": "test",
            "operational_risks": "test",
            "mitigation_strategies": "test"
        }
        mock_competitive.return_value = {
            "competitive_score": 8.5,
            "competitor_landscape": "test",
            "competitive_advantages": "test",
            "market_positioning": "test",
            "differentiation": "test"
        }
        
        result = await orchestrator.run_full_analysis(
            idea_title="Test Idea",
            idea_description="Test Description",
            problem_statement="Test Problem",
            target_market="Test Market",
            proposed_solution="Test Solution",
            value_proposition="Test Value",
            business_model="Test Model"
        )
        
        assert "scores" in result
        assert "overall_score" in result["scores"]
        assert result["scores"]["overall_score"] > 0
        assert "recommendations" in result
        assert "strengths" in result or "weaknesses" in result


@pytest.mark.asyncio
async def test_overall_score_calculation(orchestrator):
    """Test overall score calculation logic"""
    score = orchestrator._calculate_overall_score(8, 7, 6, 8, 9)
    
    # Expected: (8*0.25 + 7*0.20 + 6*0.20 + 8*0.20 + 9*0.15) = 2 + 1.4 + 1.2 + 1.6 + 1.35 = 7.55
    assert 7.5 <= score <= 7.6


@pytest.mark.asyncio
async def test_orchestrator_viability_assessment(orchestrator):
    """Test viability assessment logic"""
    # Highly viable
    assessment = orchestrator._assess_viability(8.5)
    assert assessment["status"] == "Highly Viable"
    
    # Viable
    assessment = orchestrator._assess_viability(6.5)
    assert assessment["status"] == "Viable"
    
    # Potentially viable
    assessment = orchestrator._assess_viability(4.5)
    assert assessment["status"] == "Potentially Viable"
    
    # Challenging
    assessment = orchestrator._assess_viability(2.5)
    assert assessment["status"] == "Challenging"


# Integration Tests
@pytest.mark.asyncio
async def test_all_services_initialized(orchestrator):
    """Test all service instances are properly initialized"""
    assert orchestrator.market_service is not None
    assert orchestrator.feasibility_service is not None
    assert orchestrator.financial_service is not None
    assert orchestrator.risk_service is not None
    assert orchestrator.competitive_service is not None


@pytest.mark.asyncio
async def test_analysis_error_handling(market_service):
    """Test error handling in analysis"""
    with patch.object(market_service, '_call_openai', side_effect=Exception("API Error")):
        with pytest.raises(Exception):
            await market_service.analyze_market("test context")
