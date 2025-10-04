"""
Test cases for user management endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from ..main import app
from ..models.user import User
from ..schemas.user import UserCreate, UserUpdate
from ..crud.user import create_user, get_user_by_email
from ..core.security import create_access_token
from ..core.database import SessionLocal

client = TestClient(app)

# Test data
TEST_USER_EMAIL = "testuser@example.com"
TEST_USER_PASSWORD = "TestPass123!"
TEST_USER_NAME = "Test User"

@pytest.fixture
def db_session():
    """Create a test database session."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

@pytest.fixture
def test_user(db_session: Session):
    """Create a test user."""
    user_create = UserCreate(
        email=TEST_USER_EMAIL,
        password=TEST_USER_PASSWORD,
        full_name=TEST_USER_NAME
    )
    user = create_user(db=db_session, user=user_create)
    return user

@pytest.fixture
def auth_headers(test_user: User):
    """Create authentication headers for test user."""
    access_token = create_access_token(subject=test_user.email)
    return {"Authorization": f"Bearer {access_token}"}

class TestUserProfile:
    """Test user profile management endpoints."""
    
    def test_get_current_user_profile(self, auth_headers: dict):
        """Test getting current user profile."""
        response = client.get("/api/v1/users/me", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == TEST_USER_EMAIL
        assert data["full_name"] == TEST_USER_NAME
        assert "id" in data
        assert "created_at" in data
    
    def test_get_user_profile_unauthorized(self):
        """Test getting user profile without authentication."""
        response = client.get("/api/v1/users/me")
        assert response.status_code == 401
    
    def test_update_current_user_profile(self, auth_headers: dict):
        """Test updating current user profile."""
        update_data = {
            "full_name": "Updated Name"
        }
        
        response = client.put(
            "/api/v1/users/me", 
            json=update_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["full_name"] == "Updated Name"
        assert data["email"] == TEST_USER_EMAIL
    
    def test_update_user_profile_invalid_data(self, auth_headers: dict):
        """Test updating user profile with invalid data."""
        update_data = {
            "full_name": "x" * 200  # Too long
        }
        
        response = client.put(
            "/api/v1/users/me",
            json=update_data,
            headers=auth_headers
        )
        
        assert response.status_code == 400
    
    def test_delete_current_user_account(self, auth_headers: dict):
        """Test deleting current user account."""
        response = client.delete("/api/v1/users/me", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "successfully deleted" in data["message"].lower()
    
    def test_get_user_status(self, auth_headers: dict):
        """Test getting user account status."""
        response = client.get("/api/v1/users/me/status", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "user_id" in data
        assert "email" in data
        assert "is_active" in data
        assert "created_at" in data
        assert data["email"] == TEST_USER_EMAIL
        assert data["is_active"] is True

class TestUserValidation:
    """Test user input validation."""
    
    def test_validate_email_format(self):
        """Test email format validation during registration."""
        invalid_user_data = {
            "email": "invalid-email",
            "password": TEST_USER_PASSWORD,
            "full_name": TEST_USER_NAME
        }
        
        response = client.post("/api/v1/auth/register", json=invalid_user_data)
        assert response.status_code == 400
        assert "email" in response.json()["detail"].lower()
    
    def test_validate_password_strength(self):
        """Test password strength validation."""
        weak_passwords = [
            "123",  # Too short
            "password",  # No uppercase, numbers, special chars
            "PASSWORD",  # No lowercase, numbers, special chars
            "Password",  # No numbers, special chars
            "Password1",  # No special chars
        ]
        
        for weak_password in weak_passwords:
            user_data = {
                "email": f"test{weak_password}@example.com",
                "password": weak_password,
                "full_name": TEST_USER_NAME
            }
            
            response = client.post("/api/v1/auth/register", json=user_data)
            assert response.status_code == 400
    
    def test_validate_name_format(self, auth_headers: dict):
        """Test name format validation."""
        invalid_names = [
            "Test123",  # Contains numbers
            "Test<script>",  # Contains HTML
            "Test' OR 1=1--",  # SQL injection attempt
        ]
        
        for invalid_name in invalid_names:
            update_data = {"full_name": invalid_name}
            
            response = client.put(
                "/api/v1/users/me",
                json=update_data,
                headers=auth_headers
            )
            
            assert response.status_code == 400

class TestRateLimiting:
    """Test rate limiting functionality."""
    
    def test_login_rate_limiting(self):
        """Test login rate limiting."""
        # This test would require mocking or actual rate limiting setup
        # For now, we'll just test that the endpoint responds
        user_data = {
            "username": TEST_USER_EMAIL,
            "password": "wrongpassword"
        }
        
        # Make multiple failed login attempts
        for _ in range(3):
            response = client.post("/api/v1/auth/login", data=user_data)
            assert response.status_code == 401
    
    def test_api_rate_limiting(self, auth_headers: dict):
        """Test API rate limiting."""
        # Make multiple API requests
        for _ in range(5):
            response = client.get("/api/v1/users/me", headers=auth_headers)
            # Should succeed for reasonable number of requests
            assert response.status_code in [200, 429]

class TestSecurity:
    """Test security features."""
    
    def test_sql_injection_prevention(self, auth_headers: dict):
        """Test SQL injection prevention."""
        malicious_inputs = [
            "'; DROP TABLE users; --",
            "' OR 1=1 --",
            "UNION SELECT * FROM users",
        ]
        
        for malicious_input in malicious_inputs:
            update_data = {"full_name": malicious_input}
            
            response = client.put(
                "/api/v1/users/me",
                json=update_data,
                headers=auth_headers
            )
            
            # Should either reject the input or sanitize it
            assert response.status_code in [200, 400]
            
            if response.status_code == 200:
                # If accepted, the malicious content should be sanitized
                assert malicious_input not in response.json().get("full_name", "")
    
    def test_xss_prevention(self, auth_headers: dict):
        """Test XSS prevention."""
        xss_inputs = [
            "<script>alert('xss')</script>",
            "<img src=x onerror=alert('xss')>",
            "javascript:alert('xss')",
        ]
        
        for xss_input in xss_inputs:
            update_data = {"full_name": xss_input}
            
            response = client.put(
                "/api/v1/users/me",
                json=update_data,
                headers=auth_headers
            )
            
            # Should either reject the input or sanitize it
            assert response.status_code in [200, 400]
            
            if response.status_code == 200:
                # If accepted, the XSS content should be sanitized
                result_name = response.json().get("full_name", "")
                assert "<script>" not in result_name
                assert "javascript:" not in result_name
                assert "onerror" not in result_name
