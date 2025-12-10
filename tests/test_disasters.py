"""
Tests for the Emergency blueprint disaster-related functionality.
Note: The original 'disasters' blueprint was merged into 'emergency'.
These tests now verify the emergency routes work correctly.
"""

import pytest


class TestEmergencyDisasterRoutes:
    """Tests for emergency/disaster routes."""

    def test_emergency_page_requires_login(self, client):
        """Test that emergency page requires authentication."""
        response = client.get('/emergency/')
        assert response.status_code == 302
        assert 'login' in response.headers['Location']

    def test_emergency_page_loads_when_authenticated(self, authenticated_client):
        """Test that authenticated user can access emergency page."""
        response = authenticated_client.get('/emergency/')
        assert response.status_code == 200

    def test_emergency_page_renders_template(self, authenticated_client):
        """Test that emergency page renders correctly."""
        response = authenticated_client.get('/emergency/')
        assert response.status_code == 200
        # The template should have been rendered (check for common HTML)
        assert b'<!DOCTYPE' in response.data or b'<html' in response.data or b'<div' in response.data
