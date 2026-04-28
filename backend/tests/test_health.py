"""
test_health.py — Unit tests for the health check and root endpoints.
"""

import pytest


class TestHealthEndpoint:
    """Tests for GET /health"""

    def test_health_returns_200(self, client):
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_returns_healthy_status(self, client):
        response = client.get("/health")
        data = response.json()
        assert data["status"] == "healthy"

    def test_health_returns_app_name(self, client):
        response = client.get("/health")
        data = response.json()
        assert "app" in data
        assert isinstance(data["app"], str)
        assert len(data["app"]) > 0


class TestRootEndpoint:
    """Tests for GET /"""

    def test_root_returns_200(self, client):
        response = client.get("/")
        assert response.status_code == 200

    def test_root_contains_app_name(self, client):
        response = client.get("/")
        data = response.json()
        assert "app" in data

    def test_root_contains_version(self, client):
        response = client.get("/")
        data = response.json()
        assert "version" in data

    def test_root_contains_docs_url(self, client):
        response = client.get("/")
        data = response.json()
        assert "docs" in data
        assert data["docs"] == "/docs"

    def test_root_contains_api_prefix(self, client):
        response = client.get("/")
        data = response.json()
        assert "api_prefix" in data
        assert "/api/v1" in data["api_prefix"]
