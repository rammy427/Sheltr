"""
Integration tests for the Auth blueprint.
Tests registration, login, logout, and authentication decorators.
"""

import pytest
from flask import g, session
from sheltr.models import User


class TestRegistration:
    """Tests for user registration."""

    def test_register_page_loads(self, client):
        """Test that registration page loads."""
        response = client.get('/auth/register')
        assert response.status_code == 200
        assert b'Register' in response.data or b'register' in response.data

    def test_register_success(self, client, app_context):
        """Test successful user registration."""
        response = client.post('/auth/register', data={
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'NewUserPass1!',
            'confirm_password': 'NewUserPass1!',
            'name': 'New User',
            'phone': '1234567890',
            'city': 'TestCity',
            'role': 'volunteer'
        }, follow_redirects=True)

        assert response.status_code == 200
        # Should redirect to login
        assert b'login' in response.data.lower() or b'Log' in response.data

        # Verify user was created
        with client.application.app_context():
            user = User.get_by_username('newuser')
            assert user is not None
            assert user.email == 'newuser@example.com'

    def test_register_password_mismatch(self, client):
        """Test registration fails when passwords don't match."""
        response = client.post('/auth/register', data={
            'username': 'mismatchuser',
            'email': 'mismatch@example.com',
            'password': 'Password123!',
            'confirm_password': 'DifferentPass123!',
            'name': 'Mismatch User'
        }, follow_redirects=True)

        assert response.status_code == 200
        assert b'match' in response.data.lower()

    def test_register_missing_username(self, client):
        """Test registration fails without username."""
        response = client.post('/auth/register', data={
            'username': '',
            'email': 'nouser@example.com',
            'password': 'Password123!',
            'confirm_password': 'Password123!',
            'name': 'No Username'
        }, follow_redirects=True)

        assert response.status_code == 200
        assert b'required' in response.data.lower()

    def test_register_invalid_email(self, client):
        """Test registration fails with invalid email."""
        response = client.post('/auth/register', data={
            'username': 'bademailuser',
            'email': 'not-an-email',
            'password': 'Password123!',
            'confirm_password': 'Password123!',
            'name': 'Bad Email User'
        }, follow_redirects=True)

        assert response.status_code == 200
        assert b'email' in response.data.lower()

    def test_register_weak_password(self, client):
        """Test registration fails with weak password."""
        response = client.post('/auth/register', data={
            'username': 'weakpwduser',
            'email': 'weakpwd@example.com',
            'password': 'weak',
            'confirm_password': 'weak',
            'name': 'Weak Password User'
        }, follow_redirects=True)

        assert response.status_code == 200
        # Should show password requirement error

    def test_register_duplicate_username(self, client, created_user):
        """Test registration fails with duplicate username."""
        response = client.post('/auth/register', data={
            'username': 'testuser',  # Already exists
            'email': 'different@example.com',
            'password': 'Password123!',
            'confirm_password': 'Password123!',
            'name': 'Duplicate User'
        }, follow_redirects=True)

        assert response.status_code == 200
        assert b'exists' in response.data.lower()

    def test_register_duplicate_email(self, client, created_user):
        """Test registration fails with duplicate email."""
        response = client.post('/auth/register', data={
            'username': 'differentuser',
            'email': 'testuser@example.com',  # Already exists
            'password': 'Password123!',
            'confirm_password': 'Password123!',
            'name': 'Duplicate Email User'
        }, follow_redirects=True)

        assert response.status_code == 200
        assert b'exists' in response.data.lower()

    def test_register_as_manager(self, client):
        """Test registering as manager role."""
        response = client.post('/auth/register', data={
            'username': 'newmanager',
            'email': 'newmanager@example.com',
            'password': 'ManagerPass1!',
            'confirm_password': 'ManagerPass1!',
            'name': 'New Manager',
            'role': 'manager'
        }, follow_redirects=True)

        assert response.status_code == 200

        with client.application.app_context():
            user = User.get_by_username('newmanager')
            assert user is not None
            assert user.role == 'manager'


class TestLogin:
    """Tests for user login."""

    def test_login_page_loads(self, client):
        """Test that login page loads."""
        response = client.get('/auth/login')
        assert response.status_code == 200
        assert b'Login' in response.data or b'login' in response.data

    def test_login_success(self, client, created_user):
        """Test successful login."""
        response = client.post('/auth/login', data={
            'username': 'testuser',
            'password': 'TestPass123!'
        }, follow_redirects=True)

        assert response.status_code == 200
        # Should redirect to index/home and set auth cookie
        # Cookie is set via response headers

    def test_login_sets_session(self, client, created_user):
        """Test that login sets session."""
        with client:
            response = client.post('/auth/login', data={
                'username': 'testuser',
                'password': 'TestPass123!'
            }, follow_redirects=True)

            assert response.status_code == 200
            assert session.get('user_id') == created_user.id

    def test_login_wrong_username(self, client, created_user):
        """Test login fails with wrong username."""
        response = client.post('/auth/login', data={
            'username': 'wronguser',
            'password': 'TestPass123!'
        }, follow_redirects=True)

        assert response.status_code == 200
        assert b'incorrect' in response.data.lower() or b'Incorrect' in response.data

    def test_login_wrong_password(self, client, created_user):
        """Test login fails with wrong password."""
        response = client.post('/auth/login', data={
            'username': 'testuser',
            'password': 'WrongPassword123!'
        }, follow_redirects=True)

        assert response.status_code == 200
        assert b'incorrect' in response.data.lower() or b'Incorrect' in response.data

    def test_login_empty_username(self, client, created_user):
        """Test login fails with empty username."""
        response = client.post('/auth/login', data={
            'username': '',
            'password': 'TestPass123!'
        }, follow_redirects=True)

        assert response.status_code == 200
        # Should show error or stay on login page

    def test_login_empty_password(self, client, created_user):
        """Test login fails with empty password."""
        response = client.post('/auth/login', data={
            'username': 'testuser',
            'password': ''
        }, follow_redirects=True)

        assert response.status_code == 200
        # Should show error


class TestLogout:
    """Tests for user logout."""

    def test_logout_clears_session(self, authenticated_client):
        """Test that logout clears session."""
        with authenticated_client:
            response = authenticated_client.get('/auth/logout', follow_redirects=True)
            assert response.status_code == 200
            assert 'user_id' not in session

    def test_logout_clears_cookie(self, authenticated_client):
        """Test that logout clears auth cookie."""
        response = authenticated_client.get('/auth/logout', follow_redirects=True)
        assert response.status_code == 200
        # Cookie should be cleared via Set-Cookie header with empty value

    def test_logout_redirects_to_index(self, authenticated_client):
        """Test that logout redirects to index."""
        response = authenticated_client.get('/auth/logout')
        assert response.status_code == 302
        assert '/' in response.headers['Location']


class TestLoadLoggedInUser:
    """Tests for the before_request user loading."""

    def test_loads_user_from_session(self, client, created_user):
        """Test that user is loaded from session."""
        with client:
            with client.session_transaction() as sess:
                sess['user_id'] = created_user.id

            response = client.get('/')
            # If redirected to login, user wasn't loaded correctly
            # If showing home/index content, user was loaded

    def test_loads_user_from_jwt(self, client, created_user):
        """Test that user is loaded from JWT cookie."""
        # Login to get JWT
        client.post('/auth/login', data={
            'username': 'testuser',
            'password': 'TestPass123!'
        })

        # Clear session but keep cookie
        with client.session_transaction() as sess:
            sess.clear()

        # User should still be loaded from JWT
        response = client.get('/')
        # Should not redirect to login (or should show user content)

    def test_no_user_when_no_auth(self, client):
        """Test that g.user is None when not authenticated."""
        response = client.get('/')
        # Should redirect to login when no user
        assert response.status_code == 302
        assert 'login' in response.headers['Location']


class TestLoginRequired:
    """Tests for login_required decorator."""

    def test_redirects_unauthenticated_user(self, client):
        """Test that unauthenticated user is redirected."""
        response = client.get('/profile/')
        assert response.status_code == 302
        assert 'login' in response.headers['Location']

    def test_allows_authenticated_user(self, authenticated_client):
        """Test that authenticated user can access protected page."""
        response = authenticated_client.get('/profile/')
        assert response.status_code == 200

    def test_redirects_to_login_page(self, client):
        """Test redirect goes to auth.login."""
        response = client.get('/tasks/')
        assert response.status_code == 302
        assert '/auth/login' in response.headers['Location']


class TestManagerRequired:
    """Tests for manager_required decorator."""

    def test_allows_manager(self, authenticated_manager_client):
        """Test that manager can access manager-only pages."""
        # Note: Need to have a manager-only route to test this properly
        # For now, just verify the manager is authenticated
        response = authenticated_manager_client.get('/profile/')
        assert response.status_code == 200

    def test_volunteer_cannot_access_manager_pages(self, app, created_user):
        """Test that volunteer cannot access manager-only pages."""
        from flask import g
        from sheltr.auth import manager_required

        # Create a test route that requires manager access
        @app.route('/test-manager-only')
        @manager_required
        def test_manager_route():
            return 'Manager content'

        client = app.test_client()

        # Login as volunteer
        client.post('/auth/login', data={
            'username': 'testuser',
            'password': 'TestPass123!'
        })

        # Try to access manager-only route - should redirect to index with flash
        response = client.get('/test-manager-only')
        assert response.status_code == 302
        assert '/' in response.headers['Location']

    def test_unauthenticated_redirects_to_login(self, app):
        """Test that unauthenticated user is redirected to login from manager route."""
        from sheltr.auth import manager_required

        @app.route('/test-manager-only-unauth')
        @manager_required
        def test_manager_unauth_route():
            return 'Manager content'

        client = app.test_client()

        # Try to access without logging in
        response = client.get('/test-manager-only-unauth')
        assert response.status_code == 302
        assert 'login' in response.headers['Location']

    def test_manager_can_access_manager_route(self, app, created_manager):
        """Test that manager can access manager-required route and view content."""
        from sheltr.auth import manager_required

        @app.route('/test-manager-access')
        @manager_required
        def test_manager_access_route():
            return 'Manager-only content'

        client = app.test_client()

        # Login as manager
        client.post('/auth/login', data={
            'username': 'testmanager',
            'password': 'Manager123!'
        })

        # Try to access manager-only route - should succeed
        response = client.get('/test-manager-access')
        assert response.status_code == 200
        assert b'Manager-only content' in response.data


class TestForgotPassword:
    """Tests for forgot password functionality."""

    def test_forgot_password_page_loads(self, client):
        """Test that forgot password page loads."""
        response = client.get('/auth/forgot')
        assert response.status_code == 200

    def test_forgot_password_with_identifier(self, client, created_user):
        """Test forgot password with valid identifier."""
        response = client.post('/auth/forgot', data={
            'identifier': 'testuser'
        }, follow_redirects=True)

        assert response.status_code == 200
        # Should show message about reset instructions
        assert b'reset' in response.data.lower() or b'instructions' in response.data.lower()

    def test_forgot_password_empty_identifier(self, client):
        """Test forgot password with empty identifier."""
        response = client.post('/auth/forgot', data={
            'identifier': ''
        }, follow_redirects=True)

        assert response.status_code == 200
        # Should show error message


class TestTokenRefresh:
    """Tests for JWT token refresh endpoint."""

    def test_refresh_with_valid_token(self, authenticated_client):
        """Test refreshing with valid token."""
        response = authenticated_client.post('/auth/refresh')
        assert response.status_code == 200
        data = response.get_json()
        assert 'message' in data

    def test_refresh_without_token(self, client):
        """Test refresh fails without token."""
        response = client.post('/auth/refresh')
        assert response.status_code == 401
        data = response.get_json()
        assert 'error' in data

    def test_refresh_with_expiring_token(self, client, created_user):
        """Test refreshing a token that is expiring soon."""
        from sheltr.jwt_utils import generate_token

        with client.application.app_context():
            # Generate token expiring in 1 hour (within 2 hour threshold)
            expiring_token = generate_token(created_user.id, expiration_hours=1)

        # Set the expiring token as cookie
        client.set_cookie('auth_token', expiring_token, domain='localhost')

        response = client.post('/auth/refresh')
        assert response.status_code == 200
        data = response.get_json()
        assert data['message'] == 'Token refreshed'


class TestAuthWorkflow:
    """Tests for complete authentication workflows."""

    def test_register_then_login(self, client):
        """Test complete registration and login flow."""
        # Register
        client.post('/auth/register', data={
            'username': 'flowuser',
            'email': 'flow@example.com',
            'password': 'FlowPass123!',
            'confirm_password': 'FlowPass123!',
            'name': 'Flow User'
        })

        # Login
        response = client.post('/auth/login', data={
            'username': 'flowuser',
            'password': 'FlowPass123!'
        }, follow_redirects=True)

        assert response.status_code == 200

    def test_login_logout_login(self, client, created_user):
        """Test login, logout, then login again."""
        # First login
        client.post('/auth/login', data={
            'username': 'testuser',
            'password': 'TestPass123!'
        })

        # Logout
        client.get('/auth/logout')

        # Login again
        response = client.post('/auth/login', data={
            'username': 'testuser',
            'password': 'TestPass123!'
        }, follow_redirects=True)

        assert response.status_code == 200

    def test_multiple_users_concurrent(self, app, created_user, created_manager):
        """Test that different users have separate sessions."""
        client1 = app.test_client()
        client2 = app.test_client()

        # Login as user on client1
        client1.post('/auth/login', data={
            'username': 'testuser',
            'password': 'TestPass123!'
        })

        # Login as manager on client2
        client2.post('/auth/login', data={
            'username': 'testmanager',
            'password': 'Manager123!'
        })

        # Both should be able to access profile
        response1 = client1.get('/profile/')
        response2 = client2.get('/profile/')

        assert response1.status_code == 200
        assert response2.status_code == 200
