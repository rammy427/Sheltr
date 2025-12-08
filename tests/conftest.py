"""
Pytest configuration and shared fixtures for Sheltr application tests.
"""

import os
import tempfile
import pytest
from sheltr import create_app
from sheltr.db import get_db, init_db


@pytest.fixture
def app():
    """Create and configure a test application instance."""
    db_fd, db_path = tempfile.mkstemp()

    app = create_app({
        'TESTING': True,
        'DATABASE': db_path,
        'SECRET_KEY': 'test-secret-key-for-testing',
        'WTF_CSRF_ENABLED': False,
        'SESSION_COOKIE_SECURE': False,
    })

    with app.app_context():
        init_db()
        yield app

    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    """Create a test client for the application."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Create a test CLI runner for the application."""
    return app.test_cli_runner()


@pytest.fixture
def app_context(app):
    """Provide an application context for tests."""
    with app.app_context():
        yield app


@pytest.fixture
def db(app_context):
    """Provide database connection within app context."""
    return get_db()


@pytest.fixture
def sample_user_data():
    """Provide sample valid user data for tests."""
    return {
        'username': 'testuser',
        'email': 'testuser@example.com',
        'password': 'TestPass123!',
        'name': 'Test User',
        'phone': '1234567890',
        'city': 'TestCity',
        'role': 'volunteer'
    }


@pytest.fixture
def sample_manager_data():
    """Provide sample valid manager data for tests."""
    return {
        'username': 'testmanager',
        'email': 'testmanager@example.com',
        'password': 'Manager123!',
        'name': 'Test Manager',
        'phone': '0987654321',
        'city': 'ManagerCity',
        'role': 'manager'
    }


@pytest.fixture
def created_user(app_context, sample_user_data):
    """Create and return a test user in the database."""
    from sheltr.models import User
    user, error = User.create(**sample_user_data)
    assert user is not None, f"Failed to create user: {error}"
    return user


@pytest.fixture
def created_manager(app_context, sample_manager_data):
    """Create and return a test manager in the database."""
    from sheltr.models import User
    user, error = User.create(**sample_manager_data)
    assert user is not None, f"Failed to create manager: {error}"
    return user


@pytest.fixture
def authenticated_client(client, created_user):
    """Provide a client that is logged in as a regular user."""
    client.post('/auth/login', data={
        'username': 'testuser',
        'password': 'TestPass123!'
    })
    return client


@pytest.fixture
def authenticated_manager_client(client, created_manager):
    """Provide a client that is logged in as a manager."""
    client.post('/auth/login', data={
        'username': 'testmanager',
        'password': 'Manager123!'
    })
    return client


@pytest.fixture
def sample_task(app_context, db):
    """Create and return a sample task in the database."""
    db.execute(
        "INSERT INTO task (task_name, description, status) VALUES (?, ?, ?)",
        ('Test Task', 'A test task description', 'pending')
    )
    db.commit()
    row = db.execute("SELECT * FROM task WHERE task_name = 'Test Task'").fetchone()
    return dict(row)


@pytest.fixture
def sample_emergency(app_context, db):
    """Create and return a sample emergency in the database."""
    db.execute(
        """INSERT INTO emergencies
           (emergency_name, emergency_status, emergency_date, image_url, emergency_description)
           VALUES (?, ?, ?, ?, ?)""",
        ('Test Emergency', True, '2025-01-15', 'https://example.com/img.jpg', 'Test emergency description')
    )
    db.commit()
    row = db.execute("SELECT * FROM emergencies WHERE emergency_name = 'Test Emergency'").fetchone()
    return dict(row)


@pytest.fixture
def user_with_task(app_context, db, created_user, sample_task):
    """Create a user with an assigned task."""
    db.execute(
        "INSERT INTO user_task (user_id, task_id) VALUES (?, ?)",
        (created_user.id, sample_task['task_id'])
    )
    db.commit()
    return created_user, sample_task


class AuthActions:
    """Helper class for authentication actions in tests."""

    def __init__(self, client):
        self._client = client

    def login(self, username='testuser', password='TestPass123!'):
        return self._client.post(
            '/auth/login',
            data={'username': username, 'password': password}
        )

    def logout(self):
        return self._client.get('/auth/logout')

    def register(self, username='newuser', email='newuser@example.com',
                 password='NewPass123!', confirm_password='NewPass123!',
                 name='New User', phone='5551234567', city='NewCity', role='volunteer'):
        return self._client.post(
            '/auth/register',
            data={
                'username': username,
                'email': email,
                'password': password,
                'confirm_password': confirm_password,
                'name': name,
                'phone': phone,
                'city': city,
                'role': role
            }
        )


@pytest.fixture
def auth(client):
    """Provide authentication helper for tests."""
    return AuthActions(client)
