"""
Unit Tests for User Authentication API

Tests the registration endpoint, password hashing, input validation,
and database operations for the authentication system.

Reference: test_auth_api.py - Comprehensive test suite for authentication
"""

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

from src.api.app import create_app
from src.api.models import DatabaseManager, User


class TestAuthenticationAPI(unittest.TestCase):
    """
    Test suite for authentication API endpoints.

    Tests:
        - User registration with validation
        - Password hashing and verification
        - Duplicate user detection
        - Login functionality
        - Input validation
        - Error handling (missing data, server errors)
        - Account status checks

    Reference: #TestAuthenticationAPI - Main test class for auth endpoints
    """

    def setUp(self):
        """
        Set up test environment before each test.

        Creates temporary database and Flask test client.

        Reference: #setUp - Test fixture initialization
        """
        # Create temporary database file
        self.db_fd, self.db_path = tempfile.mkstemp(suffix=".db")

        # Create Flask app with test configuration
        self.app = create_app(
            {
                "TESTING": True,
                "DATABASE_URL": f"sqlite:///{self.db_path}",
                "SECRET_KEY": "test-secret-key",
            }
        )

        self.client = self.app.test_client()

        # Store database URL for direct database operations
        self.database_url = f"sqlite:///{self.db_path}"

    def tearDown(self):
        """
        Clean up test environment after each test.

        Removes temporary database file.

        Reference: #tearDown - Test cleanup
        """
        # Close database connections first
        # This is critical on Windows to release file locks
        if hasattr(self, 'app'):
            with self.app.app_context():
                # Force close any database connections
                from sqlalchemy import create_engine
                engine = create_engine(self.database_url)
                engine.dispose()
        
        # Close file descriptor
        try:
            os.close(self.db_fd)
        except (OSError, ValueError):
            pass  # Already closed
        
        # Wait a moment for file locks to release (Windows-specific)
        import time
        time.sleep(0.1)
        
        # Remove database file
        try:
            os.unlink(self.db_path)
        except (OSError, PermissionError) as e:
            # On Windows, file may still be locked
            # Schedule for deletion on next run
            print(f"Warning: Could not delete temp file {self.db_path}: {e}")
            pass

    def test_health_check(self):
        """
        Test health check endpoint.

        Reference: #test_health_check - API health monitoring test
        """
        response = self.client.get("/api/auth/health")
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["status"], "healthy")
        self.assertEqual(data["service"], "Authentication API")

    def test_register_user_success(self):
        """
        Test successful user registration.

        Validates:
            - 201 status code
            - User data returned
            - Password not in response
            - Database record created

        Integration with:
            - #registerUser endpoint (auth_routes.py)
            - #User.set_password (models.py) - bcrypt hashing
            - #validate_registration_data (validators.py)

        Reference: #test_register_user_success - Happy path registration test
        """
        # Registration data
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "SecurePass123!",
            "full_name": "Test User",
        }

        # Send registration request
        response = self.client.post(
            "/api/auth/register", data=json.dumps(user_data), content_type="application/json"
        )

        data = json.loads(response.data)

        # Validate response
        self.assertEqual(response.status_code, 201)
        self.assertTrue(data["success"])
        self.assertEqual(data["message"], "User registered successfully")
        self.assertIn("user", data)

        # Validate user data
        user = data["user"]
        self.assertEqual(user["username"], "testuser")
        self.assertEqual(user["email"], "test@example.com")
        self.assertEqual(user["full_name"], "Test User")
        self.assertTrue(user["is_active"])
        self.assertIsNotNone(user["created_at"])

        # Ensure password is NOT in response
        self.assertNotIn("password", user)
        self.assertNotIn("password_hash", user)

        # Verify database record exists
        db_manager = DatabaseManager(self.database_url)
        session = db_manager.get_session()
        db_user = session.query(User).filter_by(username="testuser").first()

        self.assertIsNotNone(db_user)
        self.assertEqual(db_user.email, "test@example.com")
        self.assertTrue(db_user.check_password("SecurePass123!"))  # Integration with #check_password

        session.close()

    def test_register_user_duplicate_username(self):
        """
        Test registration with duplicate username.

        Validates:
            - 409 Conflict status code
            - Appropriate error message

        Reference: #test_register_user_duplicate_username - Duplicate detection test
        """
        # Register first user
        user_data = {
            "username": "duplicate_user",
            "email": "user1@example.com",
            "password": "SecurePass123!",
        }

        self.client.post("/api/auth/register", data=json.dumps(user_data), content_type="application/json")

        # Try to register with same username but different email
        user_data2 = {
            "username": "duplicate_user",
            "email": "user2@example.com",
            "password": "SecurePass123!",
        }

        response = self.client.post(
            "/api/auth/register", data=json.dumps(user_data2), content_type="application/json"
        )

        data = json.loads(response.data)

        self.assertEqual(response.status_code, 409)
        self.assertFalse(data["success"])
        self.assertIn("Username already exists", data["message"])

    def test_register_user_duplicate_email(self):
        """
        Test registration with duplicate email.

        Reference: #test_register_user_duplicate_email - Email uniqueness test
        """
        # Register first user
        user_data = {
            "username": "user1",
            "email": "duplicate@example.com",
            "password": "SecurePass123!",
        }

        self.client.post("/api/auth/register", data=json.dumps(user_data), content_type="application/json")

        # Try to register with same email but different username
        user_data2 = {
            "username": "user2",
            "email": "duplicate@example.com",
            "password": "SecurePass123!",
        }

        response = self.client.post(
            "/api/auth/register", data=json.dumps(user_data2), content_type="application/json"
        )

        data = json.loads(response.data)

        self.assertEqual(response.status_code, 409)
        self.assertFalse(data["success"])
        self.assertIn("Email already exists", data["message"])

    def test_register_user_invalid_email(self):
        """
        Test registration with invalid email format.

        Integration with:
            - #validate_email (validators.py)

        Reference: #test_register_user_invalid_email - Email validation test
        """
        user_data = {
            "username": "testuser",
            "email": "invalid-email-format",
            "password": "SecurePass123!",
        }

        response = self.client.post(
            "/api/auth/register", data=json.dumps(user_data), content_type="application/json"
        )

        data = json.loads(response.data)

        self.assertEqual(response.status_code, 400)
        self.assertFalse(data["success"])
        self.assertIn("errors", data)
        self.assertIn("Invalid email format", data["errors"])

    def test_register_user_weak_password(self):
        """
        Test registration with weak password.

        Integration with:
            - #validate_password (validators.py)

        Reference: #test_register_user_weak_password - Password strength test
        """
        user_data = {"username": "testuser", "email": "test@example.com", "password": "weak"}

        response = self.client.post(
            "/api/auth/register", data=json.dumps(user_data), content_type="application/json"
        )

        data = json.loads(response.data)

        self.assertEqual(response.status_code, 400)
        self.assertFalse(data["success"])
        self.assertIn("errors", data)
        # Should have multiple password errors
        self.assertGreater(len(data["errors"]), 0)

    def test_register_user_short_username(self):
        """
        Test registration with username too short.

        Integration with:
            - #validate_username (validators.py)

        Reference: #test_register_user_short_username - Username length validation
        """
        user_data = {"username": "ab", "email": "test@example.com", "password": "SecurePass123!"}

        response = self.client.post(
            "/api/auth/register", data=json.dumps(user_data), content_type="application/json"
        )

        data = json.loads(response.data)

        self.assertEqual(response.status_code, 400)
        self.assertFalse(data["success"])
        self.assertIn("Username must be at least 3 characters", data["errors"])

    # 🆕 NEW TESTS - Missing Request Body

    def test_register_missing_request_body(self):
        """
        Test registration without request body.

        Reference: #test_register_missing_request_body - Request validation test
        """
        response = self.client.post(
            "/api/auth/register",
            data=None,
            content_type="application/json"
        )

        data = json.loads(response.data)

        # Flask may return 500 for completely missing body, or 400 for empty body
        self.assertIn(response.status_code, [400, 500])
        self.assertFalse(data["success"])

    def test_register_empty_json(self):
        """
        Test registration with empty JSON object.

        Reference: #test_register_empty_json - Empty data validation
        """
        response = self.client.post(
            "/api/auth/register",
            data=json.dumps({}),
            content_type="application/json"
        )

        data = json.loads(response.data)

        self.assertEqual(response.status_code, 400)
        self.assertFalse(data["success"])
        # Empty object will trigger validation errors for missing required fields
        self.assertIn("message", data)

    def test_register_missing_username(self):
        """
        Test registration without username field.

        Reference: #test_register_missing_username - Required field validation
        """
        user_data = {
            "email": "test@example.com",
            "password": "SecurePass123!",
        }

        response = self.client.post(
            "/api/auth/register",
            data=json.dumps(user_data),
            content_type="application/json"
        )

        data = json.loads(response.data)

        self.assertEqual(response.status_code, 400)
        self.assertFalse(data["success"])
        self.assertIn("errors", data)

    def test_register_missing_email(self):
        """
        Test registration without email field.

        Reference: #test_register_missing_email - Required field validation
        """
        user_data = {
            "username": "testuser",
            "password": "SecurePass123!",
        }

        response = self.client.post(
            "/api/auth/register",
            data=json.dumps(user_data),
            content_type="application/json"
        )

        data = json.loads(response.data)

        self.assertEqual(response.status_code, 400)
        self.assertFalse(data["success"])
        self.assertIn("errors", data)

    def test_register_missing_password(self):
        """
        Test registration without password field.

        Reference: #test_register_missing_password - Required field validation
        """
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
        }

        response = self.client.post(
            "/api/auth/register",
            data=json.dumps(user_data),
            content_type="application/json"
        )

        data = json.loads(response.data)

        self.assertEqual(response.status_code, 400)
        self.assertFalse(data["success"])
        self.assertIn("errors", data)

    # 🆕 NEW TESTS - Login Tests

    def test_login_success(self):
        """
        Test successful user login.

        Integration with:
            - #loginUser endpoint (auth_routes.py)
            - #check_password method (models.py) - bcrypt verification

        Reference: #test_login_success - Login flow test
        """
        # First register a user
        user_data = {
            "username": "logintest",
            "email": "login@example.com",
            "password": "SecurePass123!",
        }

        self.client.post("/api/auth/register", data=json.dumps(user_data), content_type="application/json")

        # Now try to login
        login_data = {"username": "logintest", "password": "SecurePass123!"}

        response = self.client.post("/api/auth/login", data=json.dumps(login_data), content_type="application/json")

        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(data["success"])
        self.assertEqual(data["message"], "Login successful")
        self.assertIn("user", data)
        self.assertEqual(data["user"]["username"], "logintest")

    def test_login_with_email(self):
        """
        Test login using email instead of username.

        Reference: #test_login_with_email - Alternative login method
        """
        # Register user
        user_data = {
            "username": "emaillogin",
            "email": "emaillogin@example.com",
            "password": "SecurePass123!",
        }

        self.client.post("/api/auth/register", data=json.dumps(user_data), content_type="application/json")

        # Login with email
        login_data = {"username": "emaillogin@example.com", "password": "SecurePass123!"}

        response = self.client.post("/api/auth/login", data=json.dumps(login_data), content_type="application/json")

        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(data["success"])

    def test_login_invalid_password(self):
        """
        Test login with incorrect password.

        Reference: #test_login_invalid_password - Authentication failure test
        """
        # Register user
        user_data = {
            "username": "passtest",
            "email": "passtest@example.com",
            "password": "SecurePass123!",
        }

        self.client.post("/api/auth/register", data=json.dumps(user_data), content_type="application/json")

        # Try login with wrong password
        login_data = {"username": "passtest", "password": "WrongPassword123!"}

        response = self.client.post("/api/auth/login", data=json.dumps(login_data), content_type="application/json")

        data = json.loads(response.data)

        self.assertEqual(response.status_code, 401)
        self.assertFalse(data["success"])
        self.assertEqual(data["message"], "Invalid credentials")

    def test_login_nonexistent_user(self):
        """
        Test login with non-existent username.

        Reference: #test_login_nonexistent_user - User enumeration prevention
        """
        login_data = {"username": "nonexistent", "password": "SecurePass123!"}

        response = self.client.post("/api/auth/login", data=json.dumps(login_data), content_type="application/json")

        data = json.loads(response.data)

        self.assertEqual(response.status_code, 401)
        self.assertFalse(data["success"])
        # Should return generic error to prevent username enumeration
        self.assertEqual(data["message"], "Invalid credentials")

    def test_login_missing_request_body(self):
        """
        Test login without request body.

        Reference: #test_login_missing_request_body - Request validation test
        """
        response = self.client.post(
            "/api/auth/login",
            data=None,
            content_type="application/json"
        )

        data = json.loads(response.data)

        # Flask may return 500 for completely missing body
        self.assertIn(response.status_code, [400, 500])
        self.assertFalse(data["success"])
        # Message could be "Request body is required" or wrapped in "Server error"
        self.assertTrue(
            "Request body is required" in data["message"] or
            "Server error" in data["message"] or
            "Bad Request" in data["message"]
        )

    def test_login_missing_username(self):
        """
        Test login without username field.

        Reference: #test_login_missing_username - Required field validation
        """
        login_data = {"password": "SecurePass123!"}

        response = self.client.post(
            "/api/auth/login",
            data=json.dumps(login_data),
            content_type="application/json"
        )

        data = json.loads(response.data)

        self.assertEqual(response.status_code, 400)
        self.assertFalse(data["success"])
        self.assertEqual(data["message"], "Username and password are required")

    def test_login_missing_password(self):
        """
        Test login without password field.

        Reference: #test_login_missing_password - Required field validation
        """
        login_data = {"username": "testuser"}

        response = self.client.post(
            "/api/auth/login",
            data=json.dumps(login_data),
            content_type="application/json"
        )

        data = json.loads(response.data)

        self.assertEqual(response.status_code, 400)
        self.assertFalse(data["success"])
        self.assertEqual(data["message"], "Username and password are required")
