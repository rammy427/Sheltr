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

    # Volunteer-specific methods.
    @classmethod
    def get_all(cls):
        """Get all volunteers."""
        db = get_db()
        rows = db.execute("SELECT * FROM user WHERE role = 'volunteer'").fetchall()
        if rows is None:
            return None
        return [cls._from_db_row(row) for row in rows]

    def get_tasks(self):
        """Get all tasks that are assigned to a volunteer."""
        if not self.tasks:
            db = get_db()
            rows = db.execute('''SELECT *
                            FROM user JOIN user_task JOIN task
                            WHERE user.user_id = user_task.user_id
                            AND task.task_id = user_task.task_id
                            AND user.user_id = ?''', (self.id,)).fetchall()
            for row in rows:
                self.tasks.append(Task._from_db_row(row))
        
        return self.tasks