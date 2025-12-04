"""
User model for Sheltr application.
Handles all user-related database operations.
"""

import re
from werkzeug.security import generate_password_hash, check_password_hash
from sheltr.db import get_db


class User:
    """Base User model with CRUD operations."""

    def __init__(self, id=None, username=None, email=None, password=None,
                 name=None, phone=None, city=None, role='volunteer'):
        self.id = id
        self.username = username
        self.email = email
        self.password = password  # This should be hashed
        self.name = name
        self.phone = phone
        self.city = city
        self.role = role

    @staticmethod
    def validate_password(password):
        """
        Validate password meets requirements:
        - Minimum 8 characters
        - At least 1 uppercase letter
        - At least 1 number
        - At least 1 special character
        """
        if len(password) < 8:
            return False, "Password must be at least 8 characters long."
        if not re.search(r'[A-Z]', password):
            return False, "Password must contain at least one uppercase letter."
        if not re.search(r'\d', password):
            return False, "Password must contain at least one number."
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return False, "Password must contain at least one special character."
        return True, None

    @staticmethod
    def validate_email(email):
        """Validate email format."""
        if not email or '@' not in email:
            return False, "Please provide a valid email address."
        # Basic email regex
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email):
            return False, "Please provide a valid email address."
        return True, None

    @staticmethod
    def validate_phone(phone):
        """Validate phone number (max 10 digits, optional)."""
        if phone is None or phone == '':
            return True, None  # Phone is optional
        if not phone.isdigit():
            return False, "Phone number must contain only digits."
        if len(phone) > 10:
            return False, "Phone number must be at most 10 digits."
        return True, None

    @staticmethod
    def validate_name(name):
        """Validate name (required, max 100 characters)."""
        if not name or not name.strip():
            return False, "Name is required."
        if len(name) > 100:
            return False, "Name must be at most 100 characters."
        return True, None

    @staticmethod
    def validate_city(city):
        """Validate city (optional, max 12 characters)."""
        if city is None or city == '':
            return True, None  # City is optional
        if len(city) > 12:
            return False, "City must be at most 12 characters."
        return True, None

    @classmethod
    def create(cls, username, email, password, name, phone=None, city=None, role='volunteer'):
        """
        Create a new user in the database.
        Returns (user_object, error_message).
        """
        # Validate all fields
        valid, error = cls.validate_name(name)
        if not valid:
            return None, error

        valid, error = cls.validate_email(email)
        if not valid:
            return None, error

        valid, error = cls.validate_password(password)
        if not valid:
            return None, error

        valid, error = cls.validate_phone(phone)
        if not valid:
            return None, error

        valid, error = cls.validate_city(city)
        if not valid:
            return None, error

        if not username or not username.strip():
            return None, "Username is required."

        # Hash password
        hashed_password = generate_password_hash(password)

        # Insert into database
        db = get_db()
        try:
            cursor = db.execute(
                "INSERT INTO user (username, email, password, name, phone, city, role) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (username.strip(), email.strip(), hashed_password, name.strip(),
                 phone.strip() if phone else None, city.strip() if city else None, role)
            )
            db.commit()

            # Return created user
            user = cls.get_by_id(cursor.lastrowid)
            return user, None
        except db.IntegrityError:
            return None, f"User with username '{username}' or email '{email}' already exists."

    @classmethod
    def get_by_id(cls, user_id):
        """Get user by ID."""
        db = get_db()
        row = db.execute('SELECT * FROM user WHERE user_id = ?', (user_id,)).fetchone()
        if row is None:
            return None
        return cls._from_db_row(row)

    @classmethod
    def get_by_username(cls, username):
        """Get user by username."""
        db = get_db()
        row = db.execute('SELECT * FROM user WHERE username = ?', (username,)).fetchone()
        if row is None:
            return None
        return cls._from_db_row(row)

    @classmethod
    def get_by_email(cls, email):
        """Get user by email."""
        db = get_db()
        row = db.execute('SELECT * FROM user WHERE email = ?', (email,)).fetchone()
        if row is None:
            return None
        return cls._from_db_row(row)

    def verify_password(self, password):
        """Check if provided password matches hashed password."""
        return check_password_hash(self.password, password)

    def update(self, name=None, phone=None, city=None):
        """
        Update user profile fields.
        Returns (success, error_message).
        """
        # Validate fields
        if name is not None:
            valid, error = self.validate_name(name)
            if not valid:
                return False, error
            self.name = name.strip()

        if phone is not None:
            valid, error = self.validate_phone(phone)
            if not valid:
                return False, error
            self.phone = phone.strip() if phone else None

        if city is not None:
            valid, error = self.validate_city(city)
            if not valid:
                return False, error
            self.city = city.strip() if city else None

        # Update database
        db = get_db()
        db.execute(
            "UPDATE user SET name = ?, phone = ?, city = ? WHERE user_id = ?",
            (self.name, self.phone, self.city, self.id)
        )
        db.commit()
        return True, None

    def update_password(self, old_password, new_password):
        """
        Update user password after verifying old password.
        Returns (success, error_message).
        """
        # Verify old password
        if not self.verify_password(old_password):
            return False, "Current password is incorrect."

        # Validate new password
        valid, error = self.validate_password(new_password)
        if not valid:
            return False, error

        # Hash and update
        self.password = generate_password_hash(new_password)
        db = get_db()
        db.execute(
            "UPDATE user SET password = ? WHERE user_id = ?",
            (self.password, self.id)
        )
        db.commit()
        return True, None

    def is_volunteer(self):
        """Check if user is a volunteer."""
        return self.role == 'volunteer'

    def is_manager(self):
        """Check if user is a manager."""
        return self.role == 'manager'

    @classmethod
    def _from_db_row(cls, row):
        """Create User object from database row."""
        return cls(
            id=row['user_id'],
            username=row['username'],
            email=row['email'],
            password=row['password'],
            name=row['name'] if 'name' in row.keys() else None,
            phone=row['phone'] if 'phone' in row.keys() else None,
            city=row['city'] if 'city' in row.keys() else None,
            role=row['role'] if 'role' in row.keys() else 'volunteer'
        )

    def to_dict(self):
        """Convert user to dictionary (excluding password)."""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'name': self.name,
            'phone': self.phone,
            'city': self.city,
            'role': self.role
        }
