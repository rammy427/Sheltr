"""
Task model for Sheltr application.
Handles all task database operations.
"""

from flask import flash
from sheltr.db import get_db
from datetime import datetime, timezone

class Task:
    def __init__(self, id=None, name=None, description=None, status=None, completed_at=None):
        self.id = id
        self.name = name
        self.description = description
        self.status = status
        self.completed_at = completed_at
    
    @staticmethod
    def validate_status(status):
        """Validate status (must be 'pending', 'in_progress', or 'finished')."""
        if status not in ('pending', 'in_progress', 'finished'):
            return False, "Invalid status."
        return True, None
    
    @staticmethod
    def validate_completion_date(completion_date, format_str="%Y-%m-%d %H:%M:%S"):
        """Validate completion date (timestamp). Use YYYY-MM-DD HH:MM:SS as default."""
        try:
            datetime.strptime(completion_date, format_str)
            return True, None
        except ValueError:
            return False, "Invalid date."
    
    @classmethod
    def get_by_id(cls, task_id):
        """Get task by ID."""
        db = get_db()
        row = db.execute('SELECT * FROM task WHERE task_id = ?', (task_id,)).fetchone()
        if row is None:
            return None
        return cls._from_db_row(row)
    
    def update_status(self, status=None):
        # Validate the status.
        if status is not None:
            valid, error = self.validate_status(status)
            if not valid:
                return False, error
            # Update this model.
            self.status = status
        
        # Update the database.
        db = get_db()
        if status == 'finished':
            cur_time = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
            valid, error = self.validate_completion_date(cur_time)
            if not valid:  # pragma: no cover - defensive code, datetime.now() always valid
                flash("Error!")
                return False, error
            self.completed_at = cur_time
            db.execute("UPDATE task SET status = ?, completed_at = ? WHERE task_id = ?", (self.status, cur_time, self.id))
        else:
            db.execute("UPDATE task SET status = ? WHERE task_id = ?", (self.status, self.id))
        db.commit()
        return True, None
    
    @classmethod
    def _from_db_row(cls, row):
        """Create Task object from database row."""
        return cls(
            id = row['task_id'],
            name = row['task_name'],
            description = row['description'],
            status = row['status']
        )