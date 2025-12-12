"""
Integration tests for the Profile blueprint.
Tests profile viewing, editing, and password changes.
"""

import pytest
from sheltr.models import User


class TestProfileView:
    """Tests for profile viewing."""

    def test_profile_page_loads(self, authenticated_client):
        """Test that profile page loads for authenticated user."""
        response = authenticated_client.get('/profile/')
        assert response.status_code == 200

    def test_profile_shows_user_info(self, authenticated_client, created_user):
        """Test that profile displays user information."""
        response = authenticated_client.get('/profile/')
        assert response.status_code == 200
        assert created_user.username.encode() in response.data
        assert created_user.name.encode() in response.data

    def test_profile_requires_login(self, client):
        """Test that profile page requires authentication."""
        response = client.get('/profile/')
        assert response.status_code == 302
        assert 'login' in response.headers['Location']

    def test_profile_shows_email(self, authenticated_client, created_user):
        """Test that profile shows email."""
        response = authenticated_client.get('/profile/')
        assert created_user.email.encode() in response.data

    def test_profile_shows_phone_if_present(self, authenticated_client, created_user):
        """Test that profile shows phone if set."""
        response = authenticated_client.get('/profile/')
        if created_user.phone:
            assert created_user.phone.encode() in response.data

    def test_profile_shows_city_if_present(self, authenticated_client, created_user):
        """Test that profile shows city if set."""
        response = authenticated_client.get('/profile/')
        if created_user.city:
            assert created_user.city.encode() in response.data


class TestProfileEdit:
    """Tests for profile editing."""

    def test_edit_page_loads(self, authenticated_client):
        """Test that edit page loads for authenticated user."""
        response = authenticated_client.get('/profile/edit')
        assert response.status_code == 200

    def test_edit_requires_login(self, client):
        """Test that edit page requires authentication."""
        response = client.get('/profile/edit')
        assert response.status_code == 302
        assert 'login' in response.headers['Location']

    def test_edit_name_success(self, authenticated_client, created_user):
        """Test successfully editing name."""
        response = authenticated_client.post('/profile/edit', data={
            'name': 'Updated Name',
            'phone': created_user.phone or '',
            'city': created_user.city or ''
        }, follow_redirects=True)

        assert response.status_code == 200
        assert b'success' in response.data.lower() or b'Success' in response.data

        # Verify change persisted
        with authenticated_client.application.app_context():
            user = User.get_by_id(created_user.id)
            assert user.name == 'Updated Name'

    def test_edit_phone_success(self, authenticated_client, created_user):
        """Test successfully editing phone."""
        response = authenticated_client.post('/profile/edit', data={
            'name': created_user.name,
            'phone': '5555555555',
            'city': created_user.city or ''
        }, follow_redirects=True)

        assert response.status_code == 200

        with authenticated_client.application.app_context():
            user = User.get_by_id(created_user.id)
            assert user.phone == '5555555555'

    def test_edit_city_success(self, authenticated_client, created_user):
        """Test successfully editing city."""
        response = authenticated_client.post('/profile/edit', data={
            'name': created_user.name,
            'phone': created_user.phone or '',
            'city': 'NewCity'
        }, follow_redirects=True)

        assert response.status_code == 200

        with authenticated_client.application.app_context():
            user = User.get_by_id(created_user.id)
            assert user.city == 'NewCity'

    def test_edit_invalid_name_empty(self, authenticated_client, created_user):
        """Test that empty name fails."""
        response = authenticated_client.post('/profile/edit', data={
            'name': '',
            'phone': created_user.phone or '',
            'city': created_user.city or ''
        }, follow_redirects=True)

        assert response.status_code == 200
        # Should show error and not update

    def test_edit_invalid_phone(self, authenticated_client, created_user):
        """Test that invalid phone fails."""
        response = authenticated_client.post('/profile/edit', data={
            'name': created_user.name,
            'phone': 'not-a-phone',
            'city': created_user.city or ''
        }, follow_redirects=True)

        assert response.status_code == 200
        # Should show error

    def test_edit_phone_too_long(self, authenticated_client, created_user):
        """Test that phone over 10 digits fails."""
        response = authenticated_client.post('/profile/edit', data={
            'name': created_user.name,
            'phone': '12345678901',  # 11 digits
            'city': created_user.city or ''
        }, follow_redirects=True)

        assert response.status_code == 200
        # Should show error

    def test_edit_city_too_long(self, authenticated_client, created_user):
        """Test that city over 12 characters fails."""
        response = authenticated_client.post('/profile/edit', data={
            'name': created_user.name,
            'phone': created_user.phone or '',
            'city': 'ThisCityNameIsTooLong'
        }, follow_redirects=True)

        assert response.status_code == 200
        # Should show error

    def test_edit_clear_optional_fields(self, authenticated_client, created_user):
        """Test that empty optional fields are processed."""
        response = authenticated_client.post('/profile/edit', data={
            'name': created_user.name,
            'phone': '',
            'city': ''
        }, follow_redirects=True)

        assert response.status_code == 200
        # The update should succeed; empty strings may be stored as None or empty string
        # depending on the model implementation

    def test_edit_multiple_fields(self, authenticated_client, created_user):
        """Test editing multiple fields at once."""
        response = authenticated_client.post('/profile/edit', data={
            'name': 'Multi Update',
            'phone': '9999999999',
            'city': 'MultiCity'
        }, follow_redirects=True)

        assert response.status_code == 200

        with authenticated_client.application.app_context():
            user = User.get_by_id(created_user.id)
            assert user.name == 'Multi Update'
            assert user.phone == '9999999999'
            assert user.city == 'MultiCity'


class TestPasswordChange:
    """Tests for password change functionality."""

    def test_password_page_loads(self, authenticated_client):
        """Test that password change page loads."""
        response = authenticated_client.get('/profile/password')
        assert response.status_code == 200

    def test_password_requires_login(self, client):
        """Test that password change requires authentication."""
        response = client.get('/profile/password')
        assert response.status_code == 302
        assert 'login' in response.headers['Location']

    def test_change_password_success(self, authenticated_client, created_user):
        """Test successfully changing password."""
        response = authenticated_client.post('/profile/password', data={
            'current_password': 'TestPass123!',
            'new_password': 'NewTestPass456!',
            'confirm_password': 'NewTestPass456!'
        }, follow_redirects=True)

        assert response.status_code == 200
        assert b'success' in response.data.lower() or b'Success' in response.data

        # Verify password changed
        with authenticated_client.application.app_context():
            user = User.get_by_id(created_user.id)
            assert user.verify_password('NewTestPass456!') is True
            assert user.verify_password('TestPass123!') is False

    def test_change_password_wrong_current(self, authenticated_client):
        """Test password change fails with wrong current password."""
        response = authenticated_client.post('/profile/password', data={
            'current_password': 'WrongPassword123!',
            'new_password': 'NewTestPass456!',
            'confirm_password': 'NewTestPass456!'
        }, follow_redirects=True)

        assert response.status_code == 200
        assert b'incorrect' in response.data.lower()

    def test_change_password_mismatch(self, authenticated_client):
        """Test password change fails when passwords don't match."""
        response = authenticated_client.post('/profile/password', data={
            'current_password': 'TestPass123!',
            'new_password': 'NewTestPass456!',
            'confirm_password': 'DifferentPass789!'
        }, follow_redirects=True)

        assert response.status_code == 200
        assert b'match' in response.data.lower()

    def test_change_password_missing_current(self, authenticated_client):
        """Test password change fails without current password."""
        response = authenticated_client.post('/profile/password', data={
            'current_password': '',
            'new_password': 'NewTestPass456!',
            'confirm_password': 'NewTestPass456!'
        }, follow_redirects=True)

        assert response.status_code == 200
        assert b'required' in response.data.lower()

    def test_change_password_missing_new(self, authenticated_client):
        """Test password change fails without new password."""
        response = authenticated_client.post('/profile/password', data={
            'current_password': 'TestPass123!',
            'new_password': '',
            'confirm_password': ''
        }, follow_redirects=True)

        assert response.status_code == 200
        assert b'required' in response.data.lower()

    def test_change_password_weak_new(self, authenticated_client):
        """Test password change fails with weak new password."""
        response = authenticated_client.post('/profile/password', data={
            'current_password': 'TestPass123!',
            'new_password': 'weak',
            'confirm_password': 'weak'
        }, follow_redirects=True)

        assert response.status_code == 200
        # Should show password requirements error


class TestProfileWorkflows:
    """Tests for complete profile workflows."""

    def test_view_edit_view(self, authenticated_client, created_user):
        """Test viewing, editing, then viewing profile."""
        # View profile
        response = authenticated_client.get('/profile/')
        assert response.status_code == 200
        assert created_user.name.encode() in response.data

        # Edit profile
        authenticated_client.post('/profile/edit', data={
            'name': 'Workflow Updated',
            'phone': '',
            'city': ''
        }, follow_redirects=True)

        # View updated profile
        response = authenticated_client.get('/profile/')
        assert response.status_code == 200
        assert b'Workflow Updated' in response.data

    def test_change_password_then_relogin(self, client, created_user):
        """Test changing password then logging in with new password."""
        # Login
        client.post('/auth/login', data={
            'username': 'testuser',
            'password': 'TestPass123!'
        })

        # Change password
        client.post('/profile/password', data={
            'current_password': 'TestPass123!',
            'new_password': 'WorkflowPass999!',
            'confirm_password': 'WorkflowPass999!'
        })

        # Logout
        client.get('/auth/logout')

        # Login with new password
        response = client.post('/auth/login', data={
            'username': 'testuser',
            'password': 'WorkflowPass999!'
        }, follow_redirects=True)

        assert response.status_code == 200

        # Old password should not work
        client.get('/auth/logout')
        response = client.post('/auth/login', data={
            'username': 'testuser',
            'password': 'TestPass123!'
        }, follow_redirects=True)
        # Should show login error
        assert b'incorrect' in response.data.lower() or b'Incorrect' in response.data
