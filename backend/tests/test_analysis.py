"""
test_analysis.py — Unit tests for all analysis endpoints.

Endpoints covered:
  POST /api/v1/analysis/{idea_id}/analyze      — trigger analysis
  GET  /api/v1/analysis/{idea_id}              — get analysis results
  GET  /api/v1/analysis/{idea_id}/report       — get full report
"""

import pytest
from unittest.mock import patch, AsyncMock

ANALYSIS_PREFIX = "/api/v1/analysis"


# ─── Trigger Analysis ─────────────────────────────────────────────────────────

class TestTriggerAnalysis:
    """POST /api/v1/analysis/{idea_id}/analyze"""

    def test_trigger_analysis_returns_202(self, client, test_idea):
        response = client.post(f"{ANALYSIS_PREFIX}/{test_idea.id}/analyze")
        assert response.status_code == 202

    def test_trigger_analysis_returns_message(self, client, test_idea):
        response = client.post(f"{ANALYSIS_PREFIX}/{test_idea.id}/analyze")
        data = response.json()
        assert "message" in data
        assert "started" in data["message"].lower()

    def test_trigger_analysis_returns_idea_id(self, client, test_idea):
        response = client.post(f"{ANALYSIS_PREFIX}/{test_idea.id}/analyze")
        data = response.json()
        assert data["idea_id"] == test_idea.id

    def test_trigger_analysis_returns_status_analyzing(self, client, test_idea):
        response = client.post(f"{ANALYSIS_PREFIX}/{test_idea.id}/analyze")
        data = response.json()
        assert data["status"] == "analyzing"

    def test_trigger_analysis_nonexistent_idea_returns_404(self, client):
        response = client.post(f"{ANALYSIS_PREFIX}/999999/analyze")
        assert response.status_code == 404

    def test_trigger_analysis_nonexistent_idea_error_detail(self, client):
        response = client.post(f"{ANALYSIS_PREFIX}/999999/analyze")
        assert "not found" in response.json()["detail"].lower()

    def test_trigger_analysis_duplicate_returns_400(self, client, test_idea, test_analysis):
        """If analysis already exists for this idea, must return 400."""
        response = client.post(f"{ANALYSIS_PREFIX}/{test_idea.id}/analyze")
        assert response.status_code == 400

    def test_trigger_analysis_duplicate_error_detail(self, client, test_idea, test_analysis):
        response = client.post(f"{ANALYSIS_PREFIX}/{test_idea.id}/analyze")
        assert "already exists" in response.json()["detail"].lower()


# ─── Get Analysis Results ─────────────────────────────────────────────────────

class TestGetAnalysis:
    """GET /api/v1/analysis/{idea_id}"""

    def test_get_analysis_returns_200(self, client, test_idea):
        """Even with no real analysis, the endpoint returns demo data (200)."""
        response = client.get(f"{ANALYSIS_PREFIX}/{test_idea.id}")
        assert response.status_code == 200

    def test_get_analysis_demo_contains_scores(self, client, test_idea):
        """Demo fallback must return all 5 scores."""
        response = client.get(f"{ANALYSIS_PREFIX}/{test_idea.id}")
        data = response.json()
        assert "market_score" in data
        assert "feasibility_score" in data
        assert "financial_score" in data
        assert "risk_score" in data
        assert "overall_score" in data

    def test_get_analysis_demo_scores_are_numbers(self, client, test_idea):
        response = client.get(f"{ANALYSIS_PREFIX}/{test_idea.id}")
        data = response.json()
        for key in ("market_score", "feasibility_score", "financial_score",
                    "risk_score", "overall_score"):
            assert isinstance(data[key], (int, float))

    def test_get_analysis_demo_contains_idea_id(self, client, test_idea):
        response = client.get(f"{ANALYSIS_PREFIX}/{test_idea.id}")
        assert response.json()["idea_id"] == test_idea.id

    def test_get_analysis_demo_contains_text_fields(self, client, test_idea):
        response = client.get(f"{ANALYSIS_PREFIX}/{test_idea.id}")
        data = response.json()
        assert "market_analysis" in data
        assert "feasibility_analysis" in data
        assert "financial_analysis" in data
        assert "risk_analysis" in data
        assert "competitive_analysis" in data

    def test_get_analysis_with_real_db_result(self, client, test_idea, test_analysis):
        """When a real AnalysisResult exists, it should be returned."""
        response = client.get(f"{ANALYSIS_PREFIX}/{test_idea.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["market_score"] == pytest.approx(test_analysis.market_score)
        assert data["overall_score"] == pytest.approx(test_analysis.overall_score)

    def test_get_analysis_real_result_contains_strengths(self, client, test_idea, test_analysis):
        response = client.get(f"{ANALYSIS_PREFIX}/{test_idea.id}")
        assert response.json()["strengths"] == test_analysis.strengths

    def test_get_analysis_real_result_contains_weaknesses(self, client, test_idea, test_analysis):
        response = client.get(f"{ANALYSIS_PREFIX}/{test_idea.id}")
        assert response.json()["weaknesses"] == test_analysis.weaknesses

    def test_get_analysis_contains_recommendations_list(self, client, test_idea):
        response = client.get(f"{ANALYSIS_PREFIX}/{test_idea.id}")
        data = response.json()
        assert "recommendations" in data
        assert isinstance(data["recommendations"], list)

    def test_get_analysis_contains_timestamps(self, client, test_idea):
        response = client.get(f"{ANALYSIS_PREFIX}/{test_idea.id}")
        data = response.json()
        assert "created_at" in data
        assert "updated_at" in data


# ─── Get Report ───────────────────────────────────────────────────────────────

class TestGetReport:
    """GET /api/v1/analysis/{idea_id}/report"""

    def test_get_report_returns_200(self, client, test_idea, test_analysis):
        response = client.get(f"{ANALYSIS_PREFIX}/{test_idea.id}/report")
        assert response.status_code == 200

    def test_get_report_contains_idea(self, client, test_idea, test_analysis):
        response = client.get(f"{ANALYSIS_PREFIX}/{test_idea.id}/report")
        data = response.json()
        assert "idea" in data
        assert data["idea"]["id"] == test_idea.id

    def test_get_report_idea_has_title(self, client, test_idea, test_analysis):
        response = client.get(f"{ANALYSIS_PREFIX}/{test_idea.id}/report")
        assert response.json()["idea"]["title"] == test_idea.title

    def test_get_report_contains_analysis(self, client, test_idea, test_analysis):
        response = client.get(f"{ANALYSIS_PREFIX}/{test_idea.id}/report")
        data = response.json()
        assert "analysis" in data
        assert data["analysis"]["idea_id"] == test_idea.id

    def test_get_report_analysis_has_scores(self, client, test_idea, test_analysis):
        response = client.get(f"{ANALYSIS_PREFIX}/{test_idea.id}/report")
        analysis = response.json()["analysis"]
        assert "overall_score" in analysis
        assert "market_score" in analysis

    def test_get_report_nonexistent_idea_returns_404(self, client):
        response = client.get(f"{ANALYSIS_PREFIX}/999999/report")
        assert response.status_code == 404

    def test_get_report_nonexistent_idea_error_detail(self, client):
        response = client.get(f"{ANALYSIS_PREFIX}/999999/report")
        assert "not found" in response.json()["detail"].lower()

    def test_get_report_no_analysis_returns_404(self, client, test_idea):
        """Idea exists but has no analysis yet — report must be 404."""
        response = client.get(f"{ANALYSIS_PREFIX}/{test_idea.id}/report")
        assert response.status_code == 404
