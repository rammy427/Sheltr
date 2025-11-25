"""
Volunteer model for Sheltr application.
Extends User model with volunteer-specific functionality.
"""

from .user import User
from .task import Task
from sheltr.db import get_db

class Volunteer(User):
    """Volunteer user type."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.role = 'volunteer'
        self.tasks = []

    @classmethod
    def create(cls, username, email, password, name, phone=None, city=None):
        """Create a new volunteer user."""
        return super().create(username, email, password, name, phone, city, role='volunteer')

    # Volunteer-specific methods can be added here
    # For example: get_tasks(), get_shelters(), get_donations()
    def get_tasks(cls):
        db = get_db()
        rows = db.execute('SELECT * FROM user JOIN user_task JOIN task WHERE user.user_', (cls.id,)).fetchall()
        return rows
        