"""
Task model for Sheltr application.
Handles all task database operations.
"""

from sheltr.db import get_db

class Task:
    def __init__(self, id=None, name=None, description=None, state=None):
        self.id = id
        self.name = name
        self.description = description
        self.state = state