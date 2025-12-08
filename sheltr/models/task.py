"""
Task model for Sheltr application.
Handles all task database operations.
"""

from flask import flash
from sheltr.db import get_db
from datetime import datetime, timezone

class Task:
    def __init__(self, id=None, name=None, description=None, status=None, completed_at=None, volunteer=None):
        self.id = id
        self.name = name
        self.description = description
        self.status = status
        self.completed_at = completed_at
        self.volunteer = volunteer

    @staticmethod
    def validate_name(name):
        """Validate name (required, max 50 characters)."""
        if not name or not name.strip():
            return False, "Name is required."
        if len(name) > 50:
            return False, "Name must be at most 50 characters."
        return True, None
    
    @staticmethod
    def validate_description(description):
        """Validate description (required, max 1000 characters)."""
        if not description or not description.strip():
            return False, "Description is required."
        if len(description) > 1000:
            return False, "Description must be at most 1000 characters."
        return True, None
    
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
        except:
            return False, "Invalid date."
        
    @staticmethod
    def validate_volunteer(volunteer_id):
        """Validate volunteer (check if the user exists)."""
        from .volunteer import Volunteer
        # If volunteer ID is -1, remove volunteer.
        if volunteer_id == "-1":
            return True, None
        
        volunteer = Volunteer.get_by_id(volunteer_id)
        if volunteer is None:
            return False, "User not found."
        return True, None
        
    @classmethod
    def get_by_id(cls, task_id):
        """Get task by ID."""
        db = get_db()
        row = db.execute('SELECT * FROM task WHERE task_id = ?', (task_id,)).fetchone()
        if row is None:
            return None
        return cls._from_db_row(row)
    
    def get_volunteer(self):
        """Get the associated volunteer for this task."""
        from .volunteer import Volunteer
        if not self.volunteer:
            db = get_db()
            row = db.execute('''SELECT *
                            FROM user JOIN user_task JOIN task
                            WHERE user.user_id = user_task.user_id
                            AND task.task_id = user_task.task_id
                            AND task.task_id = ?''', (self.id,)).fetchone()
            if row is not None:
                self.volunteer = Volunteer._from_db_row(row)
        return self.volunteer
    
    def update(self, name=None, description=None, volunteer_id=None):
        """
        Update task fields.
        Returns (success, error_message).
        """
        from .volunteer import Volunteer
        # Validate fields.
        if name is not None:
            valid, error = self.validate_name(name)
            if not valid:
                return False, error
            self.name = name.strip()

        if description is not None:
            valid, error = self.validate_description(description)
            if not valid:
                return False, error
            self.description = description.strip()
        
        if volunteer_id is not None:
            valid, error = self.validate_volunteer(volunteer_id)
            if not valid:
                return False, error
            if volunteer_id == "-1":
                self.volunteer = None
            else:
                self.volunteer = Volunteer.get_by_id(volunteer_id)
        
        # Update task information in database.
        db = get_db()
        db.execute(
            "UPDATE task SET task_name = ?, description = ? WHERE task_id = ?",
            (self.name, self.description, self.id)
        )
        self.set_volunteer(db, volunteer_id)

        db.commit()
        return True, None
    
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
            if not valid:
                flash("Error!")
                return False, error
            self.completed_at = cur_time
            db.execute("UPDATE task SET status = ?, completed_at = ? WHERE task_id = ?", (self.status, cur_time, self.id))
        else:
            db.execute("UPDATE task SET status = ? WHERE task_id = ?", (self.status, self.id))
        db.commit()
        return True, None
    
    def set_volunteer(self, db, volunteer_id):
        # Update assigned volunteer.
        if volunteer_id != "-1":
            db.execute(
                "REPLACE INTO user_task (user_id, task_id) VALUES (?, ?)",
                (self.volunteer.id, self.id)
            )
        else:
            db.execute(
                "DELETE FROM user_task WHERE task_id = ?",
                (self.id,)
            )
    
    @classmethod
    def _from_db_row(cls, row):
        """Create Task object from database row."""
        return cls(
            id = row['task_id'],
            name = row['task_name'],
            description = row['description'],
            status = row['status']
        )