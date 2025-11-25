"""
Volunteer model for Sheltr application.
Extends User model with volunteer-specific functionality.
"""

from .user import User


class Volunteer(User):
    """Volunteer user type."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.role = 'volunteer'

    @classmethod
    def create(cls, username, email, password, name, phone=None, city=None):
        """Create a new volunteer user."""
        return super().create(username, email, password, name, phone, city, role='volunteer')

    # Volunteer-specific methods can be added here
    # For example: get_tasks(), get_shelters(), get_donations()
