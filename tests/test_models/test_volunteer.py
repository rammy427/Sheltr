"""
Unit tests for the Volunteer model.
Tests Volunteer-specific functionality and inheritance from User.
"""

import pytest
from sheltr.models import Volunteer, User
from sheltr.db import get_db


class TestVolunteerCreation:
    """Tests for Volunteer creation."""

    def test_create_volunteer_success(self, app_context):
        """Test successful volunteer creation."""
        volunteer, error = Volunteer.create(
            username='volunteer1',
            email='volunteer1@example.com',
            password='VolunteerPass1!',
            name='Test Volunteer'
        )
        assert volunteer is not None
        assert error is None
        assert volunteer.role == 'volunteer'

    def test_volunteer_inherits_user_validation(self, app_context):
        """Test that Volunteer inherits User validation."""
        # Should fail due to weak password
        volunteer, error = Volunteer.create(
            username='volunteer2',
            email='volunteer2@example.com',
            password='weak',
            name='Test Volunteer'
        )
        assert volunteer is None
        assert error is not None

    def test_volunteer_role_set_automatically(self, app_context):
        """Test that role is set to volunteer automatically."""
        volunteer, _ = Volunteer.create(
            username='volunteer3',
            email='volunteer3@example.com',
            password='VolunteerPass1!',
            name='Test Volunteer'
        )
        assert volunteer is not None
        assert volunteer.is_volunteer() is True
        assert volunteer.is_manager() is False


class TestVolunteerTasks:
    """Tests for Volunteer task retrieval."""

    def test_get_tasks_empty(self, app_context, db):
        """Test getting tasks for volunteer with no assigned tasks."""
        # Clear any seed data assignments first
        db.execute("DELETE FROM user_task")
        db.commit()

        volunteer, _ = Volunteer.create(
            username='taskless_volunteer',
            email='taskless@example.com',
            password='TasklessPass1!',
            name='Taskless Volunteer'
        )
        tasks = volunteer.get_tasks()
        assert tasks == []

    def test_get_tasks_with_assigned_tasks(self, app_context, db):
        """Test getting tasks for volunteer with assigned tasks."""
        # Clear seed data first
        db.execute("DELETE FROM user_task")
        db.execute("DELETE FROM task WHERE task_name LIKE 'Volunteer%'")
        db.commit()

        # Create volunteer
        volunteer, _ = Volunteer.create(
            username='task_volunteer',
            email='task_volunteer@example.com',
            password='TaskVolunteer1!',
            name='Task Volunteer'
        )

        # Create new tasks with unique names
        db.execute(
            "INSERT INTO task (task_name, description, status) VALUES (?, ?, ?)",
            ('Volunteer Task 1', 'First task', 'pending')
        )
        db.execute(
            "INSERT INTO task (task_name, description, status) VALUES (?, ?, ?)",
            ('Volunteer Task 2', 'Second task', 'in_progress')
        )
        db.commit()

        # Assign tasks to volunteer
        task1 = db.execute("SELECT task_id FROM task WHERE task_name = 'Volunteer Task 1'").fetchone()
        task2 = db.execute("SELECT task_id FROM task WHERE task_name = 'Volunteer Task 2'").fetchone()

        db.execute(
            "INSERT INTO user_task (user_id, task_id) VALUES (?, ?)",
            (volunteer.id, task1['task_id'])
        )
        db.execute(
            "INSERT INTO user_task (user_id, task_id) VALUES (?, ?)",
            (volunteer.id, task2['task_id'])
        )
        db.commit()

        # Fetch tasks via volunteer model
        vol = Volunteer.get_by_username('task_volunteer')
        # Need to set up volunteer instance properly
        vol_instance = Volunteer(
            id=vol.id,
            username=vol.username,
            email=vol.email,
            password=vol.password,
            name=vol.name,
            phone=vol.phone,
            city=vol.city,
            role=vol.role
        )
        tasks = vol_instance.get_tasks()

        assert len(tasks) == 2
        task_names = [t.name for t in tasks]
        assert 'Volunteer Task 1' in task_names
        assert 'Volunteer Task 2' in task_names

    def test_get_tasks_caches_results(self, app_context, db):
        """Test that get_tasks caches results."""
        volunteer, _ = Volunteer.create(
            username='cache_volunteer',
            email='cache@example.com',
            password='CacheVolunteer1!',
            name='Cache Volunteer'
        )

        vol_instance = Volunteer(
            id=volunteer.id,
            username=volunteer.username,
            email=volunteer.email,
            password=volunteer.password,
            name=volunteer.name
        )

        # First call
        tasks1 = vol_instance.get_tasks()
        # Second call should return cached results
        tasks2 = vol_instance.get_tasks()

        assert tasks1 is tasks2  # Same object reference


class TestVolunteerInheritance:
    """Tests for Volunteer inheritance from User."""

    def test_volunteer_has_user_methods(self, app_context):
        """Test that Volunteer has all User methods."""
        volunteer, _ = Volunteer.create(
            username='inherit_volunteer',
            email='inherit@example.com',
            password='InheritPass1!',
            name='Inherit Volunteer'
        )

        # Test inherited methods
        assert hasattr(volunteer, 'verify_password')
        assert hasattr(volunteer, 'update')
        assert hasattr(volunteer, 'update_password')
        assert hasattr(volunteer, 'to_dict')

    def test_volunteer_verify_password(self, app_context):
        """Test that Volunteer can verify password."""
        volunteer, _ = Volunteer.create(
            username='pwd_volunteer',
            email='pwd@example.com',
            password='PwdVolunteer1!',
            name='Pwd Volunteer'
        )

        assert volunteer.verify_password('PwdVolunteer1!') is True
        assert volunteer.verify_password('WrongPassword!') is False

    def test_volunteer_update_profile(self, app_context):
        """Test that Volunteer can update profile."""
        volunteer, _ = Volunteer.create(
            username='update_volunteer',
            email='update@example.com',
            password='UpdatePass1!',
            name='Update Volunteer'
        )

        success, error = volunteer.update(name='Updated Volunteer', city='Miami')
        assert success is True
        assert volunteer.name == 'Updated Volunteer'
        assert volunteer.city == 'Miami'

    def test_volunteer_to_dict(self, app_context):
        """Test that Volunteer can be serialized to dict."""
        volunteer, _ = Volunteer.create(
            username='dict_volunteer',
            email='dict@example.com',
            password='DictVolunteer1!',
            name='Dict Volunteer',
            city='TestCity'
        )

        vol_dict = volunteer.to_dict()
        assert vol_dict['username'] == 'dict_volunteer'
        assert vol_dict['email'] == 'dict@example.com'
        assert vol_dict['name'] == 'Dict Volunteer'
        assert vol_dict['role'] == 'volunteer'
        assert 'password' not in vol_dict
