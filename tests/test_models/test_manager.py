"""
Unit tests for the Manager model.
Tests Manager-specific functionality and inheritance from User.
"""

import pytest
from sheltr.models import Manager, User


class TestManagerCreation:
    """Tests for Manager creation."""

    def test_create_manager_success(self, app_context):
        """Test successful manager creation."""
        manager, error = Manager.create(
            username='new_manager1',
            email='new_manager1@example.com',
            password='ManagerPass1!',
            name='Test Manager'
        )
        assert manager is not None
        assert error is None
        assert manager.role == 'manager'

    def test_manager_inherits_user_validation(self, app_context):
        """Test that Manager inherits User validation."""
        # Should fail due to weak password
        manager, error = Manager.create(
            username='manager2',
            email='manager2@example.com',
            password='weak',
            name='Test Manager'
        )
        assert manager is None
        assert error is not None

    def test_manager_role_set_automatically(self, app_context):
        """Test that role is set to manager automatically."""
        manager, _ = Manager.create(
            username='manager3',
            email='manager3@example.com',
            password='ManagerPass1!',
            name='Test Manager'
        )
        assert manager is not None
        assert manager.is_manager() is True
        assert manager.is_volunteer() is False


class TestManagerInheritance:
    """Tests for Manager inheritance from User."""

    def test_manager_has_user_methods(self, app_context):
        """Test that Manager has all User methods."""
        manager, _ = Manager.create(
            username='inherit_manager',
            email='inherit_manager@example.com',
            password='InheritPass1!',
            name='Inherit Manager'
        )

        # Test inherited methods
        assert hasattr(manager, 'verify_password')
        assert hasattr(manager, 'update')
        assert hasattr(manager, 'update_password')
        assert hasattr(manager, 'to_dict')

    def test_manager_verify_password(self, app_context):
        """Test that Manager can verify password."""
        manager, _ = Manager.create(
            username='pwd_manager',
            email='pwd_manager@example.com',
            password='PwdManager1!',
            name='Pwd Manager'
        )

        assert manager.verify_password('PwdManager1!') is True
        assert manager.verify_password('WrongPassword!') is False

    def test_manager_update_profile(self, app_context):
        """Test that Manager can update profile."""
        manager, _ = Manager.create(
            username='update_manager',
            email='update_manager@example.com',
            password='UpdatePass1!',
            name='Update Manager'
        )

        success, error = manager.update(name='Updated Manager', city='Tampa')
        assert success is True
        assert manager.name == 'Updated Manager'
        assert manager.city == 'Tampa'

    def test_manager_update_password(self, app_context):
        """Test that Manager can update password."""
        manager, _ = Manager.create(
            username='pwdupdate_manager',
            email='pwdupdate_manager@example.com',
            password='OldPass123!',
            name='Password Manager'
        )

        success, error = manager.update_password('OldPass123!', 'NewPass456!')
        assert success is True
        assert manager.verify_password('NewPass456!') is True

    def test_manager_to_dict(self, app_context):
        """Test that Manager can be serialized to dict."""
        manager, _ = Manager.create(
            username='dict_manager',
            email='dict_manager@example.com',
            password='DictManager1!',
            name='Dict Manager',
            city='Orlando'
        )

        mgr_dict = manager.to_dict()
        assert mgr_dict['username'] == 'dict_manager'
        assert mgr_dict['email'] == 'dict_manager@example.com'
        assert mgr_dict['name'] == 'Dict Manager'
        assert mgr_dict['role'] == 'manager'
        assert 'password' not in mgr_dict


class TestManagerVsVolunteer:
    """Tests comparing Manager and Volunteer roles."""

    def test_manager_is_not_volunteer(self, app_context):
        """Test that manager is not identified as volunteer."""
        manager, _ = Manager.create(
            username='role_manager',
            email='role_manager@example.com',
            password='RoleManager1!',
            name='Role Manager'
        )

        assert manager.is_manager() is True
        assert manager.is_volunteer() is False

    def test_role_persistence(self, app_context):
        """Test that manager role persists in database."""
        manager, _ = Manager.create(
            username='persist_manager',
            email='persist_manager@example.com',
            password='PersistManager1!',
            name='Persist Manager'
        )

        # Retrieve from database
        retrieved = User.get_by_id(manager.id)
        assert retrieved.role == 'manager'
        assert retrieved.is_manager() is True
