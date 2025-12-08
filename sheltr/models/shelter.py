"""
Shelter model for Sheltr application.
Handles all shelter database operations.
"""

from sheltr.db import get_db
from .task import Task

class Shelter:
    def __init__(self, id=None, name=None, location=None, description=None):
        self.id = id
        self.name = name
        self.location = location
        self.description = description
        self.tasks = []

    @classmethod
    def get_all(cls):
        """Get all shelters."""
        db = get_db()
        rows = db.execute("SELECT * FROM shelters").fetchall()
        if rows is None:
            return None
        return [cls._from_db_row(row) for row in rows]
    
    @classmethod
    def get_by_id(cls, shelter_id):
        """Get one shelter by ID."""
        db = get_db()
        row = db.execute("SELECT * FROM shelters WHERE shelter_id = ?", (shelter_id,)).fetchone()
        if row is None:
            return None
        return cls._from_db_row(row)
    
    def get_tasks(self):
        """Get all tasks that are assigned to this shelter."""
        if not self.tasks:
            db = get_db()
            rows = db.execute("SELECT * FROM task WHERE shelter_id = ?", (self.id,)).fetchall()
            for row in rows:
                self.tasks.append(Task._from_db_row(row))        
        return self.tasks

    @classmethod
    def _from_db_row(cls, row):
        """Create Shelter object from database row."""
        return cls(
            id = row['shelter_id'],
            name = row['shelter_name'],
            location = row['shelter_location'],
            description = row['shelter_description']
        )