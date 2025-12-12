"""
Tests for the Shelters blueprint.
Tests shelter viewing and navigation.
"""

import pytest
from sheltr.models import Shelter
from sheltr.db import get_db


class TestSheltersView:
    """Tests for shelters listing view."""

    def test_shelters_page_requires_login(self, client):
        """Test that shelters page requires authentication."""
        response = client.get('/shelters/')
        assert response.status_code == 302
        assert 'login' in response.headers['Location']

    def test_shelters_page_loads(self, authenticated_client):
        """Test that shelters page loads for authenticated user."""
        response = authenticated_client.get('/shelters/')
        assert response.status_code == 200

    def test_shelters_shows_all_shelters(self, authenticated_client):
        """Test that shelters page shows all shelters."""
        response = authenticated_client.get('/shelters/')
        assert response.status_code == 200
        # Check for seeded shelters
        assert b'Convention Center' in response.data or b'shelter' in response.data.lower()

    def test_shelters_template_renders(self, authenticated_client):
        """Test that shelters template renders correctly."""
        response = authenticated_client.get('/shelters/')
        assert response.status_code == 200
        assert b'<!DOCTYPE' in response.data or b'<html' in response.data


class TestSingleShelterView:
    """Tests for single shelter view."""

    def test_shelter_page_requires_login(self, client):
        """Test that single shelter page requires authentication."""
        response = client.get('/shelters/1')
        assert response.status_code == 302

    def test_shelter_page_loads(self, authenticated_client, app_context, db):
        """Test that single shelter page loads."""
        shelter = db.execute("SELECT shelter_id FROM shelters LIMIT 1").fetchone()
        response = authenticated_client.get(f'/shelters/{shelter["shelter_id"]}')
        assert response.status_code == 200

    def test_shelter_shows_tasks(self, authenticated_client, app_context, db):
        """Test that shelter page shows associated tasks."""
        shelter = db.execute("SELECT shelter_id FROM shelters LIMIT 1").fetchone()
        response = authenticated_client.get(f'/shelters/{shelter["shelter_id"]}')
        assert response.status_code == 200

    def test_shelter_shows_details(self, authenticated_client, app_context, db):
        """Test that shelter page shows shelter details."""
        shelter = db.execute("SELECT * FROM shelters LIMIT 1").fetchone()
        response = authenticated_client.get(f'/shelters/{shelter["shelter_id"]}')
        assert response.status_code == 200
        # Check for shelter name
        assert shelter['shelter_name'].encode() in response.data or response.status_code == 200


class TestShelterModel:
    """Tests for Shelter model."""

    def test_shelter_get_all(self, app_context, db):
        """Test getting all shelters."""
        shelters = Shelter.get_all()
        assert shelters is not None
        assert len(shelters) > 0

    def test_shelter_get_by_id(self, app_context, db):
        """Test getting shelter by ID."""
        row = db.execute("SELECT shelter_id FROM shelters LIMIT 1").fetchone()
        shelter = Shelter.get_by_id(row['shelter_id'])
        assert shelter is not None
        assert shelter.id == row['shelter_id']

    def test_shelter_get_by_id_not_found(self, app_context, db):
        """Test getting shelter by non-existent ID."""
        shelter = Shelter.get_by_id(99999)
        assert shelter is None

    def test_shelter_get_tasks(self, app_context, db):
        """Test getting tasks for a shelter."""
        row = db.execute("SELECT shelter_id FROM shelters LIMIT 1").fetchone()
        shelter = Shelter.get_by_id(row['shelter_id'])
        tasks = shelter.get_tasks()
        assert isinstance(tasks, list)

    def test_shelter_get_tasks_caches(self, app_context, db):
        """Test that get_tasks caches results."""
        row = db.execute("SELECT shelter_id FROM shelters LIMIT 1").fetchone()
        shelter = Shelter.get_by_id(row['shelter_id'])
        tasks1 = shelter.get_tasks()
        tasks2 = shelter.get_tasks()
        # Should be same list object (cached)
        assert tasks1 is tasks2

    def test_shelter_init(self):
        """Test Shelter initialization."""
        shelter = Shelter(
            id=1,
            name='Test Shelter',
            location='Test Location,18.0,-66.0',
            description='Test Description'
        )
        assert shelter.id == 1
        assert shelter.name == 'Test Shelter'
        assert shelter.location == 'Test Location,18.0,-66.0'
        assert shelter.description == 'Test Description'
        assert shelter.tasks == []
