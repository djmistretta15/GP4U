"""
Tests for Authentication API endpoints
"""
import pytest
from httpx import AsyncClient

from app.models import User


@pytest.mark.asyncio
class TestAuthAPI:
    """Test authentication endpoints"""

    async def test_signup(self, client: AsyncClient):
        """Test user registration"""
        response = await client.post(
            "/api/v1/auth/signup",
            json={
                "email": "newuser@example.com",
                "password": "securepass123"
            }
        )

        assert response.status_code == 201
        data = response.json()

        assert data["email"] == "newuser@example.com"
        assert "id" in data
        assert "hashed_password" not in data  # Password should not be returned

    async def test_signup_duplicate_email(
        self,
        client: AsyncClient,
        test_user: User
    ):
        """Test registering with existing email fails"""
        response = await client.post(
            "/api/v1/auth/signup",
            json={
                "email": "test@example.com",
                "password": "password123"
            }
        )

        assert response.status_code == 400
        assert "already registered" in response.json()["detail"]

    async def test_signup_short_password(self, client: AsyncClient):
        """Test registration with short password fails"""
        response = await client.post(
            "/api/v1/auth/signup",
            json={
                "email": "newuser@example.com",
                "password": "short"
            }
        )

        assert response.status_code == 422  # Validation error

    async def test_login_success(self, client: AsyncClient, test_user: User):
        """Test successful login"""
        response = await client.post(
            "/api/v1/auth/login",
            data={
                "username": "test@example.com",
                "password": "testpassword123"
            }
        )

        assert response.status_code == 200
        data = response.json()

        assert "access_token" in data
        assert data["token_type"] == "bearer"

    async def test_login_wrong_password(
        self,
        client: AsyncClient,
        test_user: User
    ):
        """Test login with wrong password fails"""
        response = await client.post(
            "/api/v1/auth/login",
            data={
                "username": "test@example.com",
                "password": "wrongpassword"
            }
        )

        assert response.status_code == 401
        assert "Incorrect email or password" in response.json()["detail"]

    async def test_login_nonexistent_user(self, client: AsyncClient):
        """Test login with non-existent user fails"""
        response = await client.post(
            "/api/v1/auth/login",
            data={
                "username": "nonexistent@example.com",
                "password": "password123"
            }
        )

        assert response.status_code == 401

    async def test_get_current_user(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_user: User
    ):
        """Test getting current user profile"""
        response = await client.get(
            "/api/v1/auth/me",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        assert data["email"] == "test@example.com"
        assert data["id"] == str(test_user.id)

    async def test_update_profile(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        """Test updating user profile"""
        response = await client.patch(
            "/api/v1/auth/me",
            headers=auth_headers,
            json={
                "skill_level": "EXPERT",
                "theme_preference": "DARK"
            }
        )

        assert response.status_code == 200
        data = response.json()

        assert data["skill_level"] == "EXPERT"
        assert data["theme_preference"] == "DARK"

    async def test_get_current_user_unauthorized(self, client: AsyncClient):
        """Test accessing profile without authentication"""
        response = await client.get("/api/v1/auth/me")

        assert response.status_code == 401
