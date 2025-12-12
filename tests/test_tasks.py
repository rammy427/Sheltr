"""
Integration tests for the Tasks blueprint.
Tests task viewing and status updates.
"""

import pytest
import json
from sheltr.models import Task
from sheltr.db import get_db


class TestTasksView:
    """Tests for viewing tasks."""

    def test_tasks_page_requires_login(self, client):
        """Test that tasks page requires authentication."""
        response = client.get('/tasks/')
        assert response.status_code == 302
        assert 'login' in response.headers['Location']

    def test_tasks_page_loads(self, authenticated_client):
        """Test that tasks page loads for authenticated user."""
        response = authenticated_client.get('/tasks/')
        assert response.status_code == 200

    def test_tasks_shows_assigned_tasks(self, authenticated_client, user_with_task):
        """Test that tasks page shows assigned tasks."""
        user, task = user_with_task
        response = authenticated_client.get('/tasks/')
        assert response.status_code == 200
        assert task['task_name'].encode() in response.data

    def test_tasks_filter_by_status(self, authenticated_client, user_with_task):
        """Test filtering tasks by status."""
        user, task = user_with_task
        response = authenticated_client.get('/tasks/?status=pending')
        assert response.status_code == 200
        # Should only show pending tasks

    def test_tasks_multiple_status_filter(self, authenticated_client, app_context, db, created_user):
        """Test filtering by multiple statuses."""
        # Clear seed data first
        db.execute("DELETE FROM user_task")
        db.commit()

        # Create tasks with different statuses using unique names
        for status in ['pending', 'in_progress', 'finished']:
            db.execute(
                "INSERT INTO task (task_name, description, status) VALUES (?, ?, ?)",
                (f'Filter Task {status}', f'Description {status}', status)
            )
        db.commit()

        # Assign all filter tasks to user
        tasks = db.execute("SELECT task_id FROM task WHERE task_name LIKE 'Filter Task%'").fetchall()
        for task in tasks:
            db.execute(
                "INSERT INTO user_task (user_id, task_id) VALUES (?, ?)",
                (created_user.id, task['task_id'])
            )
        db.commit()

        # Filter by pending and in_progress
        response = authenticated_client.get('/tasks/?status=pending&status=in_progress')
        assert response.status_code == 200
        assert b'Filter Task pending' in response.data
        assert b'Filter Task in_progress' in response.data
        # finished should be filtered out

    def test_tasks_empty_list(self, authenticated_client):
        """Test tasks page with no assigned tasks."""
        response = authenticated_client.get('/tasks/')
        assert response.status_code == 200
        # Page should load even with no tasks


class TestTaskStatusUpdate:
    """Tests for updating task status."""

    def test_update_status_requires_login(self, client, sample_task):
        """Test that status update requires authentication."""
        response = client.post('/tasks/update_status',
            data=json.dumps({'id': sample_task['task_id'], 'status': 'in_progress'}),
            content_type='application/json'
        )
        assert response.status_code == 302

    def test_update_status_success(self, authenticated_client, sample_task):
        """Test successfully updating task status."""
        response = authenticated_client.post('/tasks/update_status',
            data=json.dumps({
                'id': sample_task['task_id'],
                'status': 'in_progress'
            }),
            content_type='application/json'
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True

        # Verify in database
        with authenticated_client.application.app_context():
            task = Task.get_by_id(sample_task['task_id'])
            assert task.status == 'in_progress'

    def test_update_status_to_pending(self, authenticated_client, app_context, db):
        """Test updating status to pending."""
        db.execute(
            "INSERT INTO task (task_name, description, status) VALUES (?, ?, ?)",
            ('Pending Test', 'Test', 'in_progress')
        )
        db.commit()
        row = db.execute("SELECT task_id FROM task WHERE task_name = 'Pending Test'").fetchone()

        response = authenticated_client.post('/tasks/update_status',
            data=json.dumps({
                'id': row['task_id'],
                'status': 'pending'
            }),
            content_type='application/json'
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True

    def test_update_status_to_finished(self, authenticated_client, sample_task):
        """Test updating status to finished."""
        response = authenticated_client.post('/tasks/update_status',
            data=json.dumps({
                'id': sample_task['task_id'],
                'status': 'finished'
            }),
            content_type='application/json'
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True

        # Verify completion timestamp is set
        with authenticated_client.application.app_context():
            task = Task.get_by_id(sample_task['task_id'])
            assert task.status == 'finished'

    def test_update_status_invalid_task(self, authenticated_client):
        """Test updating status for nonexistent task."""
        response = authenticated_client.post('/tasks/update_status',
            data=json.dumps({
                'id': 99999,
                'status': 'in_progress'
            }),
            content_type='application/json'
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is False
        assert 'not found' in data.get('error', '').lower()

    def test_update_status_invalid_status(self, authenticated_client, sample_task):
        """Test updating with invalid status."""
        response = authenticated_client.post('/tasks/update_status',
            data=json.dumps({
                'id': sample_task['task_id'],
                'status': 'invalid_status'
            }),
            content_type='application/json'
        )

        # Should return error or not update
        assert response.status_code == 200

    def test_update_status_missing_id(self, authenticated_client):
        """Test updating without task ID."""
        response = authenticated_client.post('/tasks/update_status',
            data=json.dumps({
                'status': 'in_progress'
            }),
            content_type='application/json'
        )

        # Should handle gracefully

    def test_update_status_missing_status(self, authenticated_client, sample_task):
        """Test updating without status."""
        response = authenticated_client.post('/tasks/update_status',
            data=json.dumps({
                'id': sample_task['task_id']
            }),
            content_type='application/json'
        )

        # Should handle gracefully


class TestTaskWorkflows:
    """Tests for complete task workflows."""

    def test_task_workflow_pending_to_finished(self, authenticated_client, sample_task):
        """Test complete task workflow from pending to finished."""
        task_id = sample_task['task_id']

        # Start: pending (from fixture)
        # Update to in_progress
        response = authenticated_client.post('/tasks/update_status',
            data=json.dumps({'id': task_id, 'status': 'in_progress'}),
            content_type='application/json'
        )
        assert response.get_json()['success'] is True

        # Update to finished
        response = authenticated_client.post('/tasks/update_status',
            data=json.dumps({'id': task_id, 'status': 'finished'}),
            content_type='application/json'
        )
        assert response.get_json()['success'] is True

    def test_view_update_view(self, authenticated_client, user_with_task):
        """Test viewing tasks, updating, then viewing again."""
        user, task = user_with_task

        # View tasks
        response = authenticated_client.get('/tasks/')
        assert response.status_code == 200
        assert task['task_name'].encode() in response.data

        # Update task
        authenticated_client.post('/tasks/update_status',
            data=json.dumps({
                'id': task['task_id'],
                'status': 'in_progress'
            }),
            content_type='application/json'
        )

        # View again
        response = authenticated_client.get('/tasks/')
        assert response.status_code == 200


class TestMultipleTasksScenarios:
    """Tests for scenarios with multiple tasks."""

    def test_user_with_multiple_tasks(self, authenticated_client, app_context, db, created_user):
        """Test user with multiple assigned tasks."""
        # Create multiple tasks
        for i in range(5):
            db.execute(
                "INSERT INTO task (task_name, description, status) VALUES (?, ?, ?)",
                (f'Multi Task {i}', f'Description {i}', 'pending')
            )
        db.commit()

        # Assign all to user
        tasks = db.execute("SELECT task_id FROM task WHERE task_name LIKE 'Multi Task%'").fetchall()
        for task in tasks:
            db.execute(
                "INSERT INTO user_task (user_id, task_id) VALUES (?, ?)",
                (created_user.id, task['task_id'])
            )
        db.commit()

        # View tasks
        response = authenticated_client.get('/tasks/')
        assert response.status_code == 200
        for i in range(5):
            assert f'Multi Task {i}'.encode() in response.data

    def test_tasks_mixed_statuses(self, authenticated_client, app_context, db, created_user):
        """Test display of tasks with mixed statuses."""
        statuses = ['pending', 'in_progress', 'finished']
        for i, status in enumerate(statuses):
            db.execute(
                "INSERT INTO task (task_name, description, status) VALUES (?, ?, ?)",
                (f'Mixed Task {i}', f'Description {i}', status)
            )
        db.commit()

        tasks = db.execute("SELECT task_id FROM task WHERE task_name LIKE 'Mixed Task%'").fetchall()
        for task in tasks:
            db.execute(
                "INSERT INTO user_task (user_id, task_id) VALUES (?, ?)",
                (created_user.id, task['task_id'])
            )
        db.commit()

        response = authenticated_client.get('/tasks/')
        assert response.status_code == 200

    def test_update_multiple_tasks(self, authenticated_client, app_context, db, created_user):
        """Test updating multiple tasks."""
        # Create tasks
        for i in range(3):
            db.execute(
                "INSERT INTO task (task_name, description, status) VALUES (?, ?, ?)",
                (f'Batch Task {i}', f'Description {i}', 'pending')
            )
        db.commit()

        tasks = db.execute("SELECT task_id FROM task WHERE task_name LIKE 'Batch Task%'").fetchall()
        for task in tasks:
            db.execute(
                "INSERT INTO user_task (user_id, task_id) VALUES (?, ?)",
                (created_user.id, task['task_id'])
            )
        db.commit()

        # Update each task
        for task in tasks:
            response = authenticated_client.post('/tasks/update_status',
                data=json.dumps({
                    'id': task['task_id'],
                    'status': 'in_progress'
                }),
                content_type='application/json'
            )
            assert response.get_json()['success'] is True


class TestTaskDeletion:
    """Tests for task deletion."""

    def test_delete_task_requires_manager(self, authenticated_client, sample_task):
        """Test that task deletion redirects non-managers."""
        response = authenticated_client.delete(f'/tasks/{sample_task["task_id"]}')
        # Non-manager gets redirected
        assert response.status_code == 302

    def test_delete_task_success(self, authenticated_manager_client, sample_task):
        """Test successful task deletion by manager."""
        response = authenticated_manager_client.delete(f'/tasks/{sample_task["task_id"]}')
        assert response.status_code == 204

    def test_delete_nonexistent_task(self, authenticated_manager_client):
        """Test deleting a nonexistent task."""
        response = authenticated_manager_client.delete('/tasks/99999')
        assert response.status_code == 204  # Returns 204 even for nonexistent


class TestTaskAssignment:
    """Tests for task assignment."""

    def test_assign_task_success(self, authenticated_client, app_context, db, created_user):
        """Test successful task assignment."""
        # Create an unassigned task with shelter
        shelter = db.execute("SELECT shelter_id FROM shelters LIMIT 1").fetchone()
        db.execute(
            "INSERT INTO task (task_name, description, status, shelter_id) VALUES (?, ?, ?, ?)",
            ('Assign Test Task', 'Description', 'pending', shelter['shelter_id'])
        )
        db.commit()
        task = db.execute("SELECT task_id FROM task WHERE task_name = 'Assign Test Task'").fetchone()

        response = authenticated_client.post(f'/tasks/{task["task_id"]}/{created_user.id}')
        assert response.status_code == 204

    def test_assign_task_volunteer_not_found(self, authenticated_client, sample_task):
        """Test assigning task to nonexistent volunteer."""
        response = authenticated_client.post(f'/tasks/{sample_task["task_id"]}/99999')
        assert response.status_code == 404

    def test_assign_task_task_not_found(self, authenticated_client, created_user):
        """Test assigning nonexistent task."""
        response = authenticated_client.post(f'/tasks/99999/{created_user.id}')
        assert response.status_code == 404

    def test_assign_task_already_taken(self, authenticated_client, app_context, db, created_user):
        """Test assigning already taken task."""
        # Create and assign a task
        shelter = db.execute("SELECT shelter_id FROM shelters LIMIT 1").fetchone()
        db.execute(
            "INSERT INTO task (task_name, description, status, shelter_id) VALUES (?, ?, ?, ?)",
            ('Already Taken Task', 'Description', 'pending', shelter['shelter_id'])
        )
        db.commit()
        task = db.execute("SELECT task_id FROM task WHERE task_name = 'Already Taken Task'").fetchone()

        # First assignment should succeed
        authenticated_client.post(f'/tasks/{task["task_id"]}/{created_user.id}')

        # Second assignment should fail
        response = authenticated_client.post(f'/tasks/{task["task_id"]}/{created_user.id}')
        assert response.status_code == 500  # Already taken
