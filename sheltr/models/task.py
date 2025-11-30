"""
Task model for Sheltr application.
Handles all task database operations.
"""

from sheltr.db import get_db

class Task:
    def __init__(self, id=None, name=None, description=None, status=None):
        self.id = id
        self.name = name
        self.description = description
        self.status = status

    @classmethod
    def _from_db_row(cls, row):
        """Create Task object from database row."""
        return cls(
            id = row['task_id'],
            name = row['task_name'],
            description = row['description'],
            status = row['status']
        )