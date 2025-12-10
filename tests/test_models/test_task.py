"""
Unit tests for the Task model.
Tests Task CRUD operations and status management.
"""

import pytest
from datetime import datetime
from sheltr.models import Task
from sheltr.db import get_db


class TestTaskValidation:
    """Tests for Task validation methods."""

    class TestStatusValidation:
        """Tests for status validation."""

        def test_valid_status_pending(self):
            """Test that 'pending' status is valid."""
            valid, error = Task.validate_status('pending')
            assert valid is True
            assert error is None

        def test_valid_status_in_progress(self):
            """Test that 'in_progress' status is valid."""
            valid, error = Task.validate_status('in_progress')
            assert valid is True
            assert error is None

        def test_valid_status_finished(self):
            """Test that 'finished' status is valid."""
            valid, error = Task.validate_status('finished')
            assert valid is True
            assert error is None

        def test_invalid_status(self):
            """Test that invalid status fails validation."""
            valid, error = Task.validate_status('invalid')
            assert valid is False
            assert 'Invalid status' in error

        def test_empty_status(self):
            """Test that empty status fails validation."""
            valid, error = Task.validate_status('')
            assert valid is False
            assert 'Invalid status' in error

    class TestCompletionDateValidation:
        """Tests for completion date validation."""

        def test_valid_date_format(self):
            """Test that valid date format passes validation."""
            valid, error = Task.validate_completion_date('2025-01-15 10:30:45')
            assert valid is True
            assert error is None

        def test_invalid_date_format(self):
            """Test that invalid date format fails validation."""
            valid, error = Task.validate_completion_date('01-15-2025')
            assert valid is False
            assert 'Invalid date' in error

        def test_invalid_date_string(self):
            """Test that non-date string fails validation."""
            valid, error = Task.validate_completion_date('not a date')
            assert valid is False
            assert 'Invalid date' in error

        def test_custom_date_format(self):
            """Test validation with custom format."""
            valid, error = Task.validate_completion_date('15/01/2025', format_str='%d/%m/%Y')
            assert valid is True
            assert error is None


class TestTaskRetrieval:
    """Tests for Task retrieval operations."""

    def test_get_by_id_success(self, app_context, db):
        """Test getting task by ID."""
        db.execute(
            "INSERT INTO task (task_name, description, status) VALUES (?, ?, ?)",
            ('Test Task', 'Test description', 'pending')
        )
        db.commit()

        row = db.execute("SELECT task_id FROM task WHERE task_name = 'Test Task'").fetchone()
        task = Task.get_by_id(row['task_id'])

        assert task is not None
        assert task.name == 'Test Task'
        assert task.description == 'Test description'
        assert task.status == 'pending'

    def test_get_by_id_nonexistent(self, app_context):
        """Test getting nonexistent task by ID."""
        task = Task.get_by_id(99999)
        assert task is None

    def test_task_from_db_row(self, app_context, db):
        """Test creating Task from database row."""
        db.execute(
            "INSERT INTO task (task_name, description, status) VALUES (?, ?, ?)",
            ('DB Row Task', 'From database', 'in_progress')
        )
        db.commit()

        row = db.execute(
            "SELECT * FROM task WHERE task_name = 'DB Row Task'"
        ).fetchone()
        task = Task._from_db_row(row)

        assert task.id == row['task_id']
        assert task.name == 'DB Row Task'
        assert task.description == 'From database'
        assert task.status == 'in_progress'


class TestTaskStatusUpdate:
    """Tests for Task status update operations."""

    def test_update_status_to_pending(self, app_context, db):
        """Test updating task status to pending."""
        db.execute(
            "INSERT INTO task (task_name, description, status) VALUES (?, ?, ?)",
            ('Status Task 1', 'Test', 'in_progress')
        )
        db.commit()

        row = db.execute("SELECT task_id FROM task WHERE task_name = 'Status Task 1'").fetchone()
        task = Task.get_by_id(row['task_id'])

        success, error = task.update_status('pending')
        assert success is True
        assert error is None
        assert task.status == 'pending'

    def test_update_status_to_in_progress(self, app_context, db):
        """Test updating task status to in_progress."""
        db.execute(
            "INSERT INTO task (task_name, description, status) VALUES (?, ?, ?)",
            ('Status Task 2', 'Test', 'pending')
        )
        db.commit()

        row = db.execute("SELECT task_id FROM task WHERE task_name = 'Status Task 2'").fetchone()
        task = Task.get_by_id(row['task_id'])

        success, error = task.update_status('in_progress')
        assert success is True
        assert error is None
        assert task.status == 'in_progress'

    def test_update_status_to_finished(self, app_context, db):
        """Test updating task status to finished sets completion time."""
        db.execute(
            "INSERT INTO task (task_name, description, status) VALUES (?, ?, ?)",
            ('Status Task 3', 'Test', 'in_progress')
        )
        db.commit()

        row = db.execute("SELECT task_id FROM task WHERE task_name = 'Status Task 3'").fetchone()
        task = Task.get_by_id(row['task_id'])

        success, error = task.update_status('finished')
        assert success is True
        assert error is None
        assert task.status == 'finished'
        assert task.completed_at is not None

    def test_update_status_invalid(self, app_context, db):
        """Test updating task with invalid status fails."""
        db.execute(
            "INSERT INTO task (task_name, description, status) VALUES (?, ?, ?)",
            ('Status Task 4', 'Test', 'pending')
        )
        db.commit()

        row = db.execute("SELECT task_id FROM task WHERE task_name = 'Status Task 4'").fetchone()
        task = Task.get_by_id(row['task_id'])

        success, error = task.update_status('invalid_status')
        assert success is False
        assert 'Invalid status' in error

    def test_update_status_persists_in_db(self, app_context, db):
        """Test that status update persists in database."""
        db.execute(
            "INSERT INTO task (task_name, description, status) VALUES (?, ?, ?)",
            ('Status Task 5', 'Test', 'pending')
        )
        db.commit()

        row = db.execute("SELECT task_id FROM task WHERE task_name = 'Status Task 5'").fetchone()
        task_id = row['task_id']
        task = Task.get_by_id(task_id)

        task.update_status('in_progress')

        # Retrieve fresh from database
        row = db.execute("SELECT status FROM task WHERE task_id = ?", (task_id,)).fetchone()
        assert row['status'] == 'in_progress'

    def test_finished_status_sets_completion_timestamp(self, app_context, db):
        """Test that finishing task sets completion timestamp in database."""
        db.execute(
            "INSERT INTO task (task_name, description, status) VALUES (?, ?, ?)",
            ('Finish Task', 'Test', 'in_progress')
        )
        db.commit()

        row = db.execute("SELECT task_id FROM task WHERE task_name = 'Finish Task'").fetchone()
        task_id = row['task_id']
        task = Task.get_by_id(task_id)

        task.update_status('finished')

        # Verify in database
        row = db.execute(
            "SELECT completed_at FROM task WHERE task_id = ?", (task_id,)
        ).fetchone()
        assert row['completed_at'] is not None


class TestTaskInitialization:
    """Tests for Task initialization."""

    def test_task_init_defaults(self):
        """Test Task initialization with defaults."""
        task = Task()
        assert task.id is None
        assert task.name is None
        assert task.description is None
        assert task.status is None
        assert task.completed_at is None

    def test_task_init_with_values(self):
        """Test Task initialization with values."""
        task = Task(
            id=1,
            name='Test Task',
            description='Description',
            status='pending',
            completed_at='2025-01-15 10:30:00'
        )
        assert task.id == 1
        assert task.name == 'Test Task'
        assert task.description == 'Description'
        assert task.status == 'pending'
        assert task.completed_at == '2025-01-15 10:30:00'


class TestTaskWorkflow:
    """Tests for complete task workflow scenarios."""

    def test_task_workflow_pending_to_finished(self, app_context, db):
        """Test complete workflow from pending to finished."""
        # Create task
        db.execute(
            "INSERT INTO task (task_name, description, status) VALUES (?, ?, ?)",
            ('Workflow Task', 'Test workflow', 'pending')
        )
        db.commit()

        row = db.execute("SELECT task_id FROM task WHERE task_name = 'Workflow Task'").fetchone()
        task_id = row['task_id']

        # Start task
        task = Task.get_by_id(task_id)
        assert task.status == 'pending'

        success, _ = task.update_status('in_progress')
        assert success is True
        assert task.status == 'in_progress'

        # Complete task
        success, _ = task.update_status('finished')
        assert success is True
        assert task.status == 'finished'
        assert task.completed_at is not None

    def test_task_can_revert_status(self, app_context, db):
        """Test that task status can be reverted."""
        db.execute(
            "INSERT INTO task (task_name, description, status) VALUES (?, ?, ?)",
            ('Revert Task', 'Test revert', 'in_progress')
        )
        db.commit()

        row = db.execute("SELECT task_id FROM task WHERE task_name = 'Revert Task'").fetchone()
        task = Task.get_by_id(row['task_id'])

        # Move to finished
        task.update_status('finished')
        assert task.status == 'finished'

        # Revert to in_progress
        success, _ = task.update_status('in_progress')
        assert success is True
        assert task.status == 'in_progress'

    def test_multiple_tasks_independent(self, app_context, db):
        """Test that multiple tasks operate independently."""
        # Create multiple tasks
        for i in range(3):
            db.execute(
                "INSERT INTO task (task_name, description, status) VALUES (?, ?, ?)",
                (f'Multi Task {i}', f'Task {i}', 'pending')
            )
        db.commit()

        # Get tasks
        rows = db.execute("SELECT task_id FROM task WHERE task_name LIKE 'Multi Task%'").fetchall()
        tasks = [Task.get_by_id(row['task_id']) for row in rows]

        # Update one task
        tasks[0].update_status('in_progress')

        # Verify others unchanged
        assert tasks[0].status == 'in_progress'
        for task in tasks[1:]:
            refreshed = Task.get_by_id(task.id)
            assert refreshed.status == 'pending'
