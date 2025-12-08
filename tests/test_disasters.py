"""
Tests for the Disasters blueprint.
Tests the disasters route and template rendering.
"""

import pytest


class TestDisastersRoute:
    """Tests for disasters route."""

    def test_disasters_page_requires_login(self, client):
        """Test that disasters page requires authentication."""
        response = client.get('/disasters/')
        assert response.status_code == 302
        assert 'login' in response.headers['Location']

    def test_disasters_page_loads_when_authenticated(self, authenticated_client):
        """Test that authenticated user can access disasters page."""
        response = authenticated_client.get('/disasters/')
        assert response.status_code == 200
        assert b'Disasters' in response.data or b'disasters' in response.data

    def test_disasters_page_renders_template(self, authenticated_client):
        """Test that disasters page renders the disasters template."""
        response = authenticated_client.get('/disasters/')
        assert response.status_code == 200
        # The template should have been rendered (check for common HTML)
        assert b'<!DOCTYPE' in response.data or b'<html' in response.data or b'<div' in response.data
