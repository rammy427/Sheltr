"""
Tests for the Flask application factory.
Tests create_app function and application configuration.
"""

import os
import pytest
from sheltr import create_app


class TestCreateApp:
    """Tests for create_app factory function."""

    def test_create_app_without_config(self, tmp_path, monkeypatch):
        """Test creating app without test_config loads instance config."""
        # Set a temporary instance path
        instance_path = tmp_path / 'instance'
        instance_path.mkdir()

        # Create a config.py in the instance folder
        config_file = instance_path / 'config.py'
        config_file.write_text("CUSTOM_SETTING = 'test_value'")

        # Monkeypatch to use tmp_path as instance path
        monkeypatch.setenv('SECRET_KEY', 'test-secret-key')

        app = create_app()
        # App should be created successfully
        assert app is not None
        assert app.config['SECRET_KEY'] == 'test-secret-key'

    def test_create_app_with_test_config(self):
        """Test creating app with test_config."""
        app = create_app(test_config={
            'TESTING': True,
            'SECRET_KEY': 'test-key',
            'DATABASE': ':memory:'
        })

        assert app is not None
        assert app.config['TESTING'] is True
        assert app.config['SECRET_KEY'] == 'test-key'

    def test_create_app_instance_folder_created(self, tmp_path, monkeypatch):
        """Test that instance folder is created if it doesn't exist."""
        monkeypatch.setenv('SECRET_KEY', 'test-secret-key')

        app = create_app(test_config={'TESTING': True})
        # The instance_path should exist after app creation
        assert os.path.exists(app.instance_path)

    def test_create_app_generates_secret_key_if_not_set(self, monkeypatch):
        """Test that a random secret key is generated if not provided."""
        # Remove SECRET_KEY from environment
        monkeypatch.delenv('SECRET_KEY', raising=False)

        app = create_app(test_config={'TESTING': True})
        # A secret key should have been generated
        assert app.config['SECRET_KEY'] is not None
        assert len(app.config['SECRET_KEY']) > 0

    def test_create_app_uses_environment_secret_key(self, monkeypatch):
        """Test that SECRET_KEY from environment is used."""
        monkeypatch.setenv('SECRET_KEY', 'my-env-secret-key')

        app = create_app(test_config={'TESTING': True})
        assert app.config['SECRET_KEY'] == 'my-env-secret-key'

    def test_create_app_registers_blueprints(self):
        """Test that all blueprints are registered."""
        app = create_app(test_config={'TESTING': True, 'SECRET_KEY': 'test'})

        blueprint_names = [bp for bp in app.blueprints]
        assert 'auth' in blueprint_names
        assert 'tasks' in blueprint_names
        assert 'donations' in blueprint_names
        assert 'emergency' in blueprint_names
        assert 'profile' in blueprint_names
        assert 'shelters' in blueprint_names
        assert 'admin' in blueprint_names

    def test_create_app_has_index_route(self):
        """Test that index route is registered."""
        app = create_app(test_config={'TESTING': True, 'SECRET_KEY': 'test'})

        # Check that '/' route exists
        rules = [rule.rule for rule in app.url_map.iter_rules()]
        assert '/' in rules


class TestAppConfiguration:
    """Tests for application configuration."""

    def test_session_cookie_settings(self, monkeypatch):
        """Test session cookie security settings."""
        monkeypatch.setenv('SECRET_KEY', 'test-key')

        app = create_app(test_config={'TESTING': True})

        assert app.config['SESSION_COOKIE_HTTPONLY'] is True
        assert app.config['SESSION_COOKIE_SAMESITE'] == 'Lax'
        assert app.config['PERMANENT_SESSION_LIFETIME'] == 86400

    def test_session_cookie_secure_in_production(self, monkeypatch):
        """Test that session cookie is secure in production."""
        monkeypatch.setenv('SECRET_KEY', 'test-key')
        monkeypatch.setenv('FLASK_ENV', 'production')

        app = create_app(test_config={'TESTING': True})

        assert app.config['SESSION_COOKIE_SECURE'] is True

    def test_session_cookie_not_secure_in_development(self, monkeypatch):
        """Test that session cookie is not secure in development."""
        monkeypatch.setenv('SECRET_KEY', 'test-key')
        monkeypatch.delenv('FLASK_ENV', raising=False)

        app = create_app(test_config={'TESTING': True})

        assert app.config['SESSION_COOKIE_SECURE'] is False
