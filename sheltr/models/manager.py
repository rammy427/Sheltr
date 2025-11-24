"""
Manager model for Sheltr application.
Extends User model with manager-specific functionality.
"""

from .user import User


class Manager(User):
    """Manager user type."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.role = 'manager'

    @classmethod
    def create(cls, username, email, password, name, phone=None, city=None):
        """Create a new manager user."""
        return super().create(username, email, password, name, phone, city, role='manager')

    # Manager-specific methods can be added here
    # For example: manage_volunteers(), manage_shelters(), view_reports()
