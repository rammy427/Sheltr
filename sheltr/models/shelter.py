"""
Shelter model for Sheltr application.
Handles all shelter database operations.
"""

from sheltr.db import get_db

class Shelter:
    def __init__(self, id=None, name=None, location=None, description=None):
        self.id = id
        self.name = name
        self.location = location
        self.description = description

    @classmethod
    def get_all(cls):
        """Get all shelters."""
        db = get_db()
        rows = db.execute("SELECT * FROM shelters")
        return [cls._from_db_row(row) for row in rows]

    @classmethod
    def _from_db_row(cls, row):
        """Create Shelter object from database row."""
        return cls(
            id = row['shelter_id'],
            name = row['shelter_name'],
            location = row['shelter_location'],
            description = row['shelter_description']
        )