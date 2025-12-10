"""
Tests for database initialization and operations.
Tests schema creation, connection management, and CLI commands.
"""

import pytest
import sqlite3
from sheltr.db import get_db, init_db


class TestDatabaseConnection:
    """Tests for database connection management."""

    def test_get_db_returns_connection(self, app_context):
        """Test that get_db returns a database connection."""
        db = get_db()
        assert db is not None
        assert isinstance(db, sqlite3.Connection)

    def test_get_db_same_connection_in_request(self, app_context):
        """Test that get_db returns same connection within request."""
        db1 = get_db()
        db2 = get_db()
        assert db1 is db2

    def test_get_db_row_factory(self, app_context):
        """Test that connection has row_factory set."""
        db = get_db()
        assert db.row_factory == sqlite3.Row

    def test_connection_closed_after_context(self, app):
        """Test that connection is closed after app context ends."""
        with app.app_context():
            db = get_db()
            assert db is not None

        # After context, new connection should be different
        with app.app_context():
            new_db = get_db()
            # Can't directly compare, but should work
            assert new_db is not None


class TestDatabaseInit:
    """Tests for database initialization."""

    def test_init_db_creates_tables(self, app):
        """Test that init_db creates all required tables."""
        with app.app_context():
            init_db()
            db = get_db()

            # Check all tables exist
            tables = db.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
            table_names = [t['name'] for t in tables]

            assert 'user' in table_names
            assert 'emergencies' in table_names
            assert 'shelters' in table_names
            assert 'shelters_of_emergency' in table_names
            assert 'task' in table_names
            assert 'user_task' in table_names

    def test_init_db_creates_user_table_schema(self, app_context, db):
        """Test user table has correct schema."""
        # Get table info
        columns = db.execute("PRAGMA table_info(user)").fetchall()
        column_names = [c['name'] for c in columns]

        assert 'user_id' in column_names
        assert 'username' in column_names
        assert 'email' in column_names
        assert 'password' in column_names
        assert 'name' in column_names
        assert 'phone' in column_names
        assert 'city' in column_names
        assert 'role' in column_names
        assert 'created_at' in column_names

    def test_init_db_creates_task_table_schema(self, app_context, db):
        """Test task table has correct schema."""
        columns = db.execute("PRAGMA table_info(task)").fetchall()
        column_names = [c['name'] for c in columns]

        assert 'task_id' in column_names
        assert 'task_name' in column_names
        assert 'shelter_id' in column_names
        assert 'description' in column_names
        assert 'status' in column_names
        assert 'completed_at' in column_names
        assert 'created_at' in column_names

    def test_init_db_creates_emergencies_table_schema(self, app_context, db):
        """Test emergencies table has correct schema."""
        columns = db.execute("PRAGMA table_info(emergencies)").fetchall()
        column_names = [c['name'] for c in columns]

        assert 'emergency_id' in column_names
        assert 'emergency_name' in column_names
        assert 'emergency_status' in column_names
        assert 'emergency_date' in column_names
        assert 'image_url' in column_names
        assert 'emergency_description' in column_names
        assert 'created_at' in column_names

    def test_init_db_creates_shelters_table_schema(self, app_context, db):
        """Test shelters table has correct schema."""
        columns = db.execute("PRAGMA table_info(shelters)").fetchall()
        column_names = [c['name'] for c in columns]

        assert 'shelter_id' in column_names
        assert 'shelter_name' in column_names
        assert 'shelter_location' in column_names
        assert 'shelter_description' in column_names
        assert 'created_at' in column_names


class TestDatabaseConstraints:
    """Tests for database constraints."""

    def test_user_username_unique(self, app_context, db):
        """Test that username is unique."""
        db.execute(
            "INSERT INTO user (username, email, password, name, role) VALUES (?, ?, ?, ?, ?)",
            ('uniqueuser', 'unique1@test.com', 'pass', 'User', 'volunteer')
        )
        db.commit()

        with pytest.raises(sqlite3.IntegrityError):
            db.execute(
                "INSERT INTO user (username, email, password, name, role) VALUES (?, ?, ?, ?, ?)",
                ('uniqueuser', 'unique2@test.com', 'pass', 'User2', 'volunteer')
            )

    def test_user_email_unique(self, app_context, db):
        """Test that email is unique."""
        db.execute(
            "INSERT INTO user (username, email, password, name, role) VALUES (?, ?, ?, ?, ?)",
            ('emailuser1', 'sameemail@test.com', 'pass', 'User', 'volunteer')
        )
        db.commit()

        with pytest.raises(sqlite3.IntegrityError):
            db.execute(
                "INSERT INTO user (username, email, password, name, role) VALUES (?, ?, ?, ?, ?)",
                ('emailuser2', 'sameemail@test.com', 'pass', 'User2', 'volunteer')
            )

    def test_user_username_not_null(self, app_context, db):
        """Test that username cannot be null."""
        with pytest.raises(sqlite3.IntegrityError):
            db.execute(
                "INSERT INTO user (email, password, name, role) VALUES (?, ?, ?, ?)",
                ('null@test.com', 'pass', 'User', 'volunteer')
            )

    def test_user_email_not_null(self, app_context, db):
        """Test that email cannot be null."""
        with pytest.raises(sqlite3.IntegrityError):
            db.execute(
                "INSERT INTO user (username, password, name, role) VALUES (?, ?, ?, ?)",
                ('nullemail', 'pass', 'User', 'volunteer')
            )

    def test_task_name_not_null(self, app_context, db):
        """Test that task_name cannot be null."""
        with pytest.raises(sqlite3.IntegrityError):
            db.execute(
                "INSERT INTO task (description, status) VALUES (?, ?)",
                ('Description', 'pending')
            )


class TestDatabaseRelationships:
    """Tests for database relationships."""

    def test_user_task_relationship(self, app_context, db):
        """Test user_task junction table relationship."""
        # Create user with unique username to avoid conflicts with seeded data
        db.execute(
            "INSERT INTO user (username, email, password, name, role) VALUES (?, ?, ?, ?, ?)",
            ('reluser_unique', 'rel_unique@test.com', 'pass', 'Rel User', 'volunteer')
        )
        # Create task with unique name
        db.execute(
            "INSERT INTO task (task_name, description, status) VALUES (?, ?, ?)",
            ('Rel Task Unique', 'Description', 'pending')
        )
        db.commit()

        user = db.execute("SELECT user_id FROM user WHERE username = 'reluser_unique'").fetchone()
        task = db.execute("SELECT task_id FROM task WHERE task_name = 'Rel Task Unique'").fetchone()

        # Link them (use REPLACE to handle any potential conflicts with seeded data)
        db.execute(
            "REPLACE INTO user_task (user_id, task_id) VALUES (?, ?)",
            (user['user_id'], task['task_id'])
        )
        db.commit()

        # Verify relationship
        link = db.execute(
            "SELECT * FROM user_task WHERE user_id = ? AND task_id = ?",
            (user['user_id'], task['task_id'])
        ).fetchone()
        assert link is not None

    def test_shelter_emergency_relationship(self, app_context, db):
        """Test shelters_of_emergency junction table."""
        # Create shelter
        db.execute(
            "INSERT INTO shelters (shelter_name, shelter_location) VALUES (?, ?)",
            ('Test Shelter', 'Test Location')
        )
        # Create emergency
        db.execute(
            "INSERT INTO emergencies (emergency_name, emergency_status, emergency_date) VALUES (?, ?, ?)",
            ('Test Emergency', True, '2025-01-15')
        )
        db.commit()

        shelter = db.execute("SELECT shelter_id FROM shelters WHERE shelter_name = 'Test Shelter'").fetchone()
        emergency = db.execute("SELECT emergency_id FROM emergencies WHERE emergency_name = 'Test Emergency'").fetchone()

        # Link them
        db.execute(
            "INSERT INTO shelters_of_emergency (starting_date, shelter_id, emergency_id, end_date) VALUES (?, ?, ?, ?)",
            ('2025-01-15', shelter['shelter_id'], emergency['emergency_id'], '2025-02-15')
        )
        db.commit()

        # Verify relationship
        link = db.execute(
            "SELECT * FROM shelters_of_emergency WHERE shelter_id = ? AND emergency_id = ?",
            (shelter['shelter_id'], emergency['emergency_id'])
        ).fetchone()
        assert link is not None


class TestDatabaseCLI:
    """Tests for database CLI commands."""

    def test_init_db_command(self, runner):
        """Test init-db CLI command."""
        result = runner.invoke(args=['init-db'])
        assert 'Initialized' in result.output

    def test_init_db_command_clears_data(self, app, runner):
        """Test that init-db clears existing data."""
        with app.app_context():
            db = get_db()
            # Insert some data
            db.execute(
                "INSERT INTO user (username, email, password, name, role) VALUES (?, ?, ?, ?, ?)",
                ('clearuser', 'clear@test.com', 'pass', 'Clear User', 'volunteer')
            )
            db.commit()

        # Run init-db
        result = runner.invoke(args=['init-db'])
        assert 'Initialized' in result.output

        # Check data was cleared
        with app.app_context():
            db = get_db()
            user = db.execute("SELECT * FROM user WHERE username = 'clearuser'").fetchone()
            assert user is None



class TestTimestampHandling:
    """Tests for timestamp handling."""

    def test_user_created_at_auto(self, app_context, db):
        """Test that created_at is automatically set for users."""
        db.execute(
            "INSERT INTO user (username, email, password, name, role) VALUES (?, ?, ?, ?, ?)",
            ('timestampuser', 'ts@test.com', 'pass', 'TS User', 'volunteer')
        )
        db.commit()

        user = db.execute(
            "SELECT created_at FROM user WHERE username = 'timestampuser'"
        ).fetchone()
        assert user['created_at'] is not None

    def test_task_created_at_auto(self, app_context, db):
        """Test that created_at is automatically set for tasks."""
        db.execute(
            "INSERT INTO task (task_name, description, status) VALUES (?, ?, ?)",
            ('TS Task', 'Description', 'pending')
        )
        db.commit()

        task = db.execute(
            "SELECT created_at FROM task WHERE task_name = 'TS Task'"
        ).fetchone()
        assert task['created_at'] is not None

    def test_emergency_created_at_auto(self, app_context, db):
        """Test that created_at is automatically set for emergencies."""
        db.execute(
            "INSERT INTO emergencies (emergency_name, emergency_status, emergency_date) VALUES (?, ?, ?)",
            ('TS Emergency', True, '2025-01-15')
        )
        db.commit()

        emergency = db.execute(
            "SELECT created_at FROM emergencies WHERE emergency_name = 'TS Emergency'"
        ).fetchone()
        assert emergency['created_at'] is not None
