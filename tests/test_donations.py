"""
Tests for the Donations blueprint.
Tests the donations route and template rendering.
"""

import pytest


class TestDonationsRoute:
    """Tests for donations route."""

    def test_donations_page_requires_login(self, client):
        """Test that donations page requires authentication."""
        response = client.get('/donations/')
        assert response.status_code == 302
        assert 'login' in response.headers['Location']

    def test_donations_page_loads_when_authenticated(self, authenticated_client):
        """Test that authenticated user can access donations page."""
        response = authenticated_client.get('/donations/')
        assert response.status_code == 200
        assert b'Donations' in response.data or b'donations' in response.data

    def test_donations_page_renders_template(self, authenticated_client):
        """Test that donations page renders the donations template."""
        response = authenticated_client.get('/donations/')
        assert response.status_code == 200
        # The template should have been rendered (check for common HTML)
        assert b'<!DOCTYPE' in response.data or b'<html' in response.data or b'<div' in response.data
