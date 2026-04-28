"""
test_ideas.py — Unit tests for all idea CRUD endpoints.

Endpoints covered:
  POST   /api/v1/ideas/           — create idea
  GET    /api/v1/ideas/           — list ideas
  GET    /api/v1/ideas/{idea_id}  — get single idea
  PUT    /api/v1/ideas/{idea_id}  — update idea
  DELETE /api/v1/ideas/{idea_id}  — delete idea
"""

import pytest
from tests.conftest import IDEA_PAYLOAD

IDEAS_PREFIX = "/api/v1/ideas"


# ─── Create ───────────────────────────────────────────────────────────────────

class TestCreateIdea:
    """POST /api/v1/ideas/"""

    def test_create_idea_returns_201(self, client):
        response = client.post(f"{IDEAS_PREFIX}/", json=IDEA_PAYLOAD)
        assert response.status_code == 201

    def test_create_idea_returns_correct_title(self, client):
        response = client.post(f"{IDEAS_PREFIX}/", json=IDEA_PAYLOAD)
        assert response.json()["title"] == IDEA_PAYLOAD["title"]

    def test_create_idea_returns_correct_description(self, client):
        response = client.post(f"{IDEAS_PREFIX}/", json=IDEA_PAYLOAD)
        assert response.json()["description"] == IDEA_PAYLOAD["description"]

    def test_create_idea_has_id(self, client):
        response = client.post(f"{IDEAS_PREFIX}/", json=IDEA_PAYLOAD)
        data = response.json()
        assert "id" in data
        assert isinstance(data["id"], int)
        assert data["id"] > 0

    def test_create_idea_status_is_pending(self, client):
        response = client.post(f"{IDEAS_PREFIX}/", json=IDEA_PAYLOAD)
        assert response.json()["status"] == "pending"

    def test_create_idea_has_user_id(self, client):
        response = client.post(f"{IDEAS_PREFIX}/", json=IDEA_PAYLOAD)
        data = response.json()
        assert "user_id" in data
        assert data["user_id"] > 0

    def test_create_idea_has_timestamps(self, client):
        response = client.post(f"{IDEAS_PREFIX}/", json=IDEA_PAYLOAD)
        data = response.json()
        assert "created_at" in data
        assert "updated_at" in data

    def test_create_idea_stores_optional_fields(self, client):
        response = client.post(f"{IDEAS_PREFIX}/", json=IDEA_PAYLOAD)
        data = response.json()
        assert data["problem_statement"] == IDEA_PAYLOAD["problem_statement"]
        assert data["target_market"] == IDEA_PAYLOAD["target_market"]
        assert data["proposed_solution"] == IDEA_PAYLOAD["proposed_solution"]
        assert data["value_proposition"] == IDEA_PAYLOAD["value_proposition"]
        assert data["business_model"] == IDEA_PAYLOAD["business_model"]

    def test_create_idea_without_optional_fields(self, client):
        minimal = {"title": "Minimal Idea", "description": "Just the basics"}
        response = client.post(f"{IDEAS_PREFIX}/", json=minimal)
        assert response.status_code == 201

    def test_create_idea_missing_title_returns_422(self, client):
        payload = {k: v for k, v in IDEA_PAYLOAD.items() if k != "title"}
        response = client.post(f"{IDEAS_PREFIX}/", json=payload)
        assert response.status_code == 422

    def test_create_idea_missing_description_returns_422(self, client):
        payload = {k: v for k, v in IDEA_PAYLOAD.items() if k != "description"}
        response = client.post(f"{IDEAS_PREFIX}/", json=payload)
        assert response.status_code == 422


# ─── Get Single Idea ──────────────────────────────────────────────────────────

class TestGetIdea:
    """GET /api/v1/ideas/{idea_id}"""

    def test_get_idea_returns_200(self, client, test_idea):
        response = client.get(f"{IDEAS_PREFIX}/{test_idea.id}")
        assert response.status_code == 200

    def test_get_idea_returns_correct_id(self, client, test_idea):
        response = client.get(f"{IDEAS_PREFIX}/{test_idea.id}")
        assert response.json()["id"] == test_idea.id

    def test_get_idea_returns_correct_title(self, client, test_idea):
        response = client.get(f"{IDEAS_PREFIX}/{test_idea.id}")
        assert response.json()["title"] == test_idea.title

    def test_get_idea_not_found_returns_404(self, client):
        response = client.get(f"{IDEAS_PREFIX}/999999")
        assert response.status_code == 404

    def test_get_idea_not_found_error_detail(self, client):
        response = client.get(f"{IDEAS_PREFIX}/999999")
        assert "not found" in response.json()["detail"].lower()


# ─── List Ideas ───────────────────────────────────────────────────────────────

class TestListIdeas:
    """GET /api/v1/ideas/"""

    def test_list_ideas_returns_200(self, client):
        response = client.get(f"{IDEAS_PREFIX}/")
        assert response.status_code == 200

    def test_list_ideas_returns_list(self, client):
        response = client.get(f"{IDEAS_PREFIX}/")
        assert isinstance(response.json(), list)

    def test_list_ideas_includes_created_idea(self, client, test_idea):
        response = client.get(f"{IDEAS_PREFIX}/")
        ids = [i["id"] for i in response.json()]
        assert test_idea.id in ids

    def test_list_ideas_filter_by_user_id(self, client, test_idea):
        response = client.get(f"{IDEAS_PREFIX}/?user_id={test_idea.user_id}")
        assert response.status_code == 200
        data = response.json()
        assert all(i["user_id"] == test_idea.user_id for i in data)

    def test_list_ideas_filter_by_wrong_user_id_returns_empty(self, client, test_idea):
        response = client.get(f"{IDEAS_PREFIX}/?user_id=999999")
        assert response.status_code == 200
        assert response.json() == []

    def test_list_ideas_pagination_skip(self, client, test_idea):
        # Create a second idea via API
        client.post(f"{IDEAS_PREFIX}/", json={**IDEA_PAYLOAD, "title": "Second Idea"})
        response = client.get(f"{IDEAS_PREFIX}/?skip=1&limit=10")
        assert response.status_code == 200

    def test_list_ideas_pagination_limit(self, client, test_idea):
        response = client.get(f"{IDEAS_PREFIX}/?skip=0&limit=1")
        assert response.status_code == 200
        assert len(response.json()) <= 1


# ─── Update Idea ──────────────────────────────────────────────────────────────

class TestUpdateIdea:
    """PUT /api/v1/ideas/{idea_id}"""

    def test_update_idea_returns_200(self, client, test_idea):
        response = client.put(
            f"{IDEAS_PREFIX}/{test_idea.id}", json={"title": "Updated Title"}
        )
        assert response.status_code == 200

    def test_update_idea_title_changes(self, client, test_idea):
        new_title = "My Updated Title"
        response = client.put(
            f"{IDEAS_PREFIX}/{test_idea.id}", json={"title": new_title}
        )
        assert response.json()["title"] == new_title

    def test_update_idea_description_changes(self, client, test_idea):
        new_desc = "Completely new description"
        response = client.put(
            f"{IDEAS_PREFIX}/{test_idea.id}", json={"description": new_desc}
        )
        assert response.json()["description"] == new_desc

    def test_update_idea_partial_update_keeps_other_fields(self, client, test_idea):
        """Only updating 'title' should leave other fields unchanged."""
        response = client.put(
            f"{IDEAS_PREFIX}/{test_idea.id}", json={"title": "New Title Only"}
        )
        data = response.json()
        assert data["description"] == test_idea.description

    def test_update_idea_all_optional_fields(self, client, test_idea):
        update = {
            "title": "Full Update",
            "description": "New desc",
            "problem_statement": "New problem",
            "target_market": "New market",
            "proposed_solution": "New solution",
            "value_proposition": "New value",
            "business_model": "New model",
        }
        response = client.put(f"{IDEAS_PREFIX}/{test_idea.id}", json=update)
        data = response.json()
        for key, value in update.items():
            assert data[key] == value

    def test_update_nonexistent_idea_returns_404(self, client):
        response = client.put(
            f"{IDEAS_PREFIX}/999999", json={"title": "Doesn't exist"}
        )
        assert response.status_code == 404

    def test_update_nonexistent_idea_error_detail(self, client):
        response = client.put(
            f"{IDEAS_PREFIX}/999999", json={"title": "Ghost Idea"}
        )
        assert "not found" in response.json()["detail"].lower()


# ─── Delete Idea ──────────────────────────────────────────────────────────────

class TestDeleteIdea:
    """DELETE /api/v1/ideas/{idea_id}"""

    def test_delete_idea_returns_204(self, client, test_idea):
        response = client.delete(f"{IDEAS_PREFIX}/{test_idea.id}")
        assert response.status_code == 204

    def test_delete_idea_removes_from_db(self, client, test_idea):
        client.delete(f"{IDEAS_PREFIX}/{test_idea.id}")
        get_response = client.get(f"{IDEAS_PREFIX}/{test_idea.id}")
        assert get_response.status_code == 404

    def test_delete_nonexistent_idea_returns_404(self, client):
        response = client.delete(f"{IDEAS_PREFIX}/999999")
        assert response.status_code == 404

    def test_delete_nonexistent_idea_error_detail(self, client):
        response = client.delete(f"{IDEAS_PREFIX}/999999")
        assert "not found" in response.json()["detail"].lower()
