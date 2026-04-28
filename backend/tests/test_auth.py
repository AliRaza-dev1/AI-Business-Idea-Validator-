"""
test_auth.py — Unit tests for all authentication endpoints.

Endpoints covered:
  POST /api/v1/auth/register
  POST /api/v1/auth/login
  GET  /api/v1/auth/me  (basic smoke test)
"""

import pytest


AUTH_PREFIX = "/api/v1/auth"

# ─── Reusable payloads ────────────────────────────────────────────────────────

REGISTER_PAYLOAD = {
    "email": "new_user@example.com",
    "password": "SecurePass123!",
    "full_name": "New User",
}

LOGIN_PAYLOAD = {
    "email": "test@example.com",
    "password": "TestPassword123!",
}


# ─── Registration ─────────────────────────────────────────────────────────────

class TestRegister:
    """POST /api/v1/auth/register"""

    def test_register_returns_201(self, client):
        response = client.post(f"{AUTH_PREFIX}/register", json=REGISTER_PAYLOAD)
        assert response.status_code == 201

    def test_register_returns_user_email(self, client):
        response = client.post(f"{AUTH_PREFIX}/register", json=REGISTER_PAYLOAD)
        data = response.json()
        assert data["email"] == REGISTER_PAYLOAD["email"]

    def test_register_returns_full_name(self, client):
        response = client.post(f"{AUTH_PREFIX}/register", json=REGISTER_PAYLOAD)
        data = response.json()
        assert data["full_name"] == REGISTER_PAYLOAD["full_name"]

    def test_register_returns_user_id(self, client):
        response = client.post(f"{AUTH_PREFIX}/register", json=REGISTER_PAYLOAD)
        data = response.json()
        assert "id" in data
        assert isinstance(data["id"], int)
        assert data["id"] > 0

    def test_register_user_is_active_by_default(self, client):
        response = client.post(f"{AUTH_PREFIX}/register", json=REGISTER_PAYLOAD)
        data = response.json()
        assert data["is_active"] is True

    def test_register_returns_timestamps(self, client):
        response = client.post(f"{AUTH_PREFIX}/register", json=REGISTER_PAYLOAD)
        data = response.json()
        assert "created_at" in data
        assert "updated_at" in data

    def test_register_does_not_return_password(self, client):
        response = client.post(f"{AUTH_PREFIX}/register", json=REGISTER_PAYLOAD)
        data = response.json()
        assert "password" not in data
        assert "password_hash" not in data

    def test_register_duplicate_email_returns_400(self, client, test_user):
        """Registering with an already-taken email must fail."""
        payload = {
            "email": test_user.email,
            "password": "AnotherPass123!",
            "full_name": "Duplicate",
        }
        response = client.post(f"{AUTH_PREFIX}/register", json=payload)
        assert response.status_code == 400

    def test_register_duplicate_email_error_message(self, client, test_user):
        payload = {
            "email": test_user.email,
            "password": "AnotherPass123!",
            "full_name": "Duplicate",
        }
        response = client.post(f"{AUTH_PREFIX}/register", json=payload)
        assert "already registered" in response.json()["detail"].lower()

    def test_register_invalid_email_returns_422(self, client):
        payload = {**REGISTER_PAYLOAD, "email": "not-an-email"}
        response = client.post(f"{AUTH_PREFIX}/register", json=payload)
        assert response.status_code == 422

    def test_register_missing_password_returns_422(self, client):
        payload = {"email": "missing@example.com", "full_name": "No Pass"}
        response = client.post(f"{AUTH_PREFIX}/register", json=payload)
        assert response.status_code == 422


# ─── Login ────────────────────────────────────────────────────────────────────

class TestLogin:
    """POST /api/v1/auth/login"""

    def test_login_returns_200(self, client, test_user):
        response = client.post(f"{AUTH_PREFIX}/login", json=LOGIN_PAYLOAD)
        assert response.status_code == 200

    def test_login_returns_access_token(self, client, test_user):
        response = client.post(f"{AUTH_PREFIX}/login", json=LOGIN_PAYLOAD)
        data = response.json()
        assert "access_token" in data
        assert isinstance(data["access_token"], str)
        assert len(data["access_token"]) > 0

    def test_login_token_type_is_bearer(self, client, test_user):
        response = client.post(f"{AUTH_PREFIX}/login", json=LOGIN_PAYLOAD)
        data = response.json()
        assert data["token_type"] == "bearer"

    def test_login_returns_user_info(self, client, test_user):
        response = client.post(f"{AUTH_PREFIX}/login", json=LOGIN_PAYLOAD)
        data = response.json()
        assert "user" in data
        assert data["user"]["email"] == test_user.email

    def test_login_wrong_password_returns_401(self, client, test_user):
        payload = {"email": test_user.email, "password": "WrongPassword!"}
        response = client.post(f"{AUTH_PREFIX}/login", json=payload)
        assert response.status_code == 401

    def test_login_wrong_password_error_message(self, client, test_user):
        payload = {"email": test_user.email, "password": "WrongPassword!"}
        response = client.post(f"{AUTH_PREFIX}/login", json=payload)
        assert "invalid" in response.json()["detail"].lower()

    def test_login_nonexistent_user_returns_401(self, client):
        payload = {"email": "nobody@example.com", "password": "SomePass123!"}
        response = client.post(f"{AUTH_PREFIX}/login", json=payload)
        assert response.status_code == 401

    def test_login_inactive_user_returns_403(self, client, inactive_user):
        payload = {"email": inactive_user.email, "password": "TestPassword123!"}
        response = client.post(f"{AUTH_PREFIX}/login", json=payload)
        assert response.status_code == 403

    def test_login_inactive_user_error_message(self, client, inactive_user):
        payload = {"email": inactive_user.email, "password": "TestPassword123!"}
        response = client.post(f"{AUTH_PREFIX}/login", json=payload)
        assert "inactive" in response.json()["detail"].lower()

    def test_login_missing_email_returns_422(self, client):
        response = client.post(f"{AUTH_PREFIX}/login", json={"password": "Pass123!"})
        assert response.status_code == 422

    def test_login_missing_password_returns_422(self, client):
        response = client.post(
            f"{AUTH_PREFIX}/login", json={"email": "test@example.com"}
        )
        assert response.status_code == 422
