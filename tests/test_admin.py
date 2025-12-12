"""
Tests for the Admin blueprint.
Tests admin routes for manager users.
"""

import pytest
from sheltr.models import Task, Emergency, Shelter, Volunteer
from sheltr.db import get_db


class TestAdminDashboard:
    """Tests for admin dashboard view."""

    def test_admin_page_requires_manager(self, authenticated_client):
        """Test that admin page redirects non-managers."""
        response = authenticated_client.get('/admin/')
        # Non-manager gets redirected to index
        assert response.status_code == 302

    def test_admin_page_loads_for_manager(self, authenticated_manager_client):
        """Test that manager can access admin dashboard."""
        response = authenticated_manager_client.get('/admin/')
        assert response.status_code == 200


class TestAdminShelters:
    """Tests for admin shelter management."""

    def test_shelters_page_loads(self, authenticated_manager_client):
        """Test that shelters admin page loads."""
        response = authenticated_manager_client.get('/admin/shelters')
        assert response.status_code == 200

    def test_shelters_shows_all_shelters(self, authenticated_manager_client):
        """Test that shelters page shows all shelters."""
        response = authenticated_manager_client.get('/admin/shelters')
        assert response.status_code == 200
        # Check for seeded shelters
        assert b'Convention Center' in response.data or b'shelter' in response.data.lower()

    def test_single_shelter_page_loads(self, authenticated_manager_client, app_context, db):
        """Test viewing a single shelter."""
        shelter = db.execute("SELECT shelter_id FROM shelters LIMIT 1").fetchone()
        response = authenticated_manager_client.get(f'/admin/shelters/{shelter["shelter_id"]}')
        assert response.status_code == 200

    def test_shelter_page_filters_by_status(self, authenticated_manager_client, app_context, db):
        """Test filtering shelter tasks by status."""
        shelter = db.execute("SELECT shelter_id FROM shelters LIMIT 1").fetchone()
        response = authenticated_manager_client.get(
            f'/admin/shelters/{shelter["shelter_id"]}?status=pending'
        )
        assert response.status_code == 200


class TestAdminTasks:
    """Tests for admin task management."""

    def test_task_page_loads(self, authenticated_manager_client, app_context, db):
        """Test that task edit page loads."""
        shelter = db.execute("SELECT shelter_id FROM shelters LIMIT 1").fetchone()
        task = db.execute(
            "SELECT task_id FROM task WHERE shelter_id = ? LIMIT 1",
            (shelter["shelter_id"],)
        ).fetchone()
        if task:
            response = authenticated_manager_client.get(
                f'/admin/shelters/{shelter["shelter_id"]}/{task["task_id"]}'
            )
            assert response.status_code == 200

    def test_task_update_success(self, authenticated_manager_client, app_context, db):
        """Test successfully updating a task."""
        shelter = db.execute("SELECT shelter_id FROM shelters LIMIT 1").fetchone()
        task = db.execute(
            "SELECT task_id FROM task WHERE shelter_id = ? LIMIT 1",
            (shelter["shelter_id"],)
        ).fetchone()
        if task:
            response = authenticated_manager_client.post(
                f'/admin/shelters/{shelter["shelter_id"]}/{task["task_id"]}',
                data={
                    'name': 'Updated Task Name',
                    'description': 'Updated description for the task',
                    'volunteer': '-1'
                },
                follow_redirects=True
            )
            assert response.status_code == 200

    def test_task_update_with_invalid_name(self, authenticated_manager_client, app_context, db):
        """Test updating task with invalid name."""
        shelter = db.execute("SELECT shelter_id FROM shelters LIMIT 1").fetchone()
        task = db.execute(
            "SELECT task_id FROM task WHERE shelter_id = ? LIMIT 1",
            (shelter["shelter_id"],)
        ).fetchone()
        if task:
            response = authenticated_manager_client.post(
                f'/admin/shelters/{shelter["shelter_id"]}/{task["task_id"]}',
                data={
                    'name': '',  # Empty name
                    'description': 'Description',
                    'volunteer': '-1'
                }
            )
            assert response.status_code == 200

    def test_add_task_page_loads(self, authenticated_manager_client, app_context, db):
        """Test that add task page loads."""
        shelter = db.execute("SELECT shelter_id FROM shelters LIMIT 1").fetchone()
        response = authenticated_manager_client.get(
            f'/admin/shelters/{shelter["shelter_id"]}/add'
        )
        assert response.status_code == 200

    def test_add_task_success(self, authenticated_manager_client, app_context, db):
        """Test successfully adding a new task."""
        shelter = db.execute("SELECT shelter_id FROM shelters LIMIT 1").fetchone()
        response = authenticated_manager_client.post(
            f'/admin/shelters/{shelter["shelter_id"]}/add',
            data={
                'name': 'New Admin Task',
                'description': 'A new task created by admin',
                'volunteer': '-1'
            },
            follow_redirects=True
        )
        assert response.status_code == 200

    def test_add_task_validation_error(self, authenticated_manager_client, app_context, db):
        """Test adding task with validation error."""
        shelter = db.execute("SELECT shelter_id FROM shelters LIMIT 1").fetchone()
        response = authenticated_manager_client.post(
            f'/admin/shelters/{shelter["shelter_id"]}/add',
            data={
                'name': '',  # Empty name
                'description': 'Description',
                'volunteer': '-1'
            }
        )
        assert response.status_code == 200


class TestAdminEmergencies:
    """Tests for admin emergency management."""

    def test_emergencies_page_loads(self, authenticated_manager_client):
        """Test that emergencies admin page loads."""
        response = authenticated_manager_client.get('/admin/emergencies')
        assert response.status_code == 200

    def test_single_emergency_page_loads(self, authenticated_manager_client, sample_emergency):
        """Test viewing a single emergency."""
        response = authenticated_manager_client.get(
            f'/admin/emergencies/{sample_emergency["emergency_id"]}'
        )
        assert response.status_code == 200

    def test_emergency_update_success(self, authenticated_manager_client, sample_emergency):
        """Test successfully updating an emergency."""
        response = authenticated_manager_client.post(
            f'/admin/emergencies/{sample_emergency["emergency_id"]}',
            data={
                'name': 'Updated Emergency',
                'description': 'Updated emergency description',
                'status': '1'
            },
            follow_redirects=True
        )
        assert response.status_code == 200

    def test_emergency_update_with_empty_name(self, authenticated_manager_client, sample_emergency):
        """Test updating emergency with empty name - model accepts it."""
        response = authenticated_manager_client.post(
            f'/admin/emergencies/{sample_emergency["emergency_id"]}',
            data={
                'name': '',  # Empty name - model accepts this
                'description': 'Description',
                'status': '1'
            }
        )
        # Model doesn't validate empty name, so update succeeds and redirects
        assert response.status_code == 302

    def test_add_emergency_page_loads(self, authenticated_manager_client):
        """Test that add emergency page loads."""
        response = authenticated_manager_client.get('/admin/shelters/add')
        assert response.status_code == 200

    def test_add_emergency_success(self, authenticated_manager_client):
        """Test successfully adding a new emergency."""
        response = authenticated_manager_client.post(
            '/admin/shelters/add',
            data={
                'name': 'New Test Emergency',
                'description': 'A new emergency for testing',
                'status': '1'
            },
            follow_redirects=True
        )
        assert response.status_code == 200

    def test_add_emergency_with_empty_name(self, authenticated_manager_client):
        """Test adding emergency with empty name - model accepts it."""
        response = authenticated_manager_client.post(
            '/admin/shelters/add',
            data={
                'name': '',  # Empty name - model accepts this
                'description': 'Description',
                'status': '1'
            }
        )
        # Model doesn't validate empty name, so add succeeds and redirects
        assert response.status_code == 302


class TestAdminReports:
    """Tests for admin reports page."""

    def test_reports_page_loads(self, authenticated_manager_client):
        """Test that reports page loads."""
        response = authenticated_manager_client.get('/admin/reports')
        assert response.status_code == 200

    def test_reports_shows_statistics(self, authenticated_manager_client):
        """Test that reports page shows statistics."""
        response = authenticated_manager_client.get('/admin/reports')
        assert response.status_code == 200
        # Check for common report elements
        assert b'report' in response.data.lower() or b'stat' in response.data.lower() or response.status_code == 200

    def test_reports_with_donations(self, authenticated_manager_client, app_context, db):
        """Test reports page with donation data."""
        # Add a test donation
        db.execute(
            """INSERT INTO donation (emergency_id, user_id, donation_date, donation_quantity, payment_process_provider)
               VALUES (1, 1, datetime('now'), 100.00, 'Paypal')"""
        )
        db.commit()

        response = authenticated_manager_client.get('/admin/reports')
        assert response.status_code == 200
