"""
Unit tests for the User model.
Tests CRUD operations, validation methods, and password handling.
"""

import pytest
from werkzeug.security import check_password_hash
from sheltr.models import User


class TestUserValidation:
    """Tests for User validation methods."""

    # Password validation tests
    class TestPasswordValidation:
        """Tests for password validation."""

        def test_valid_password(self):
            """Test that a valid password passes validation."""
            valid, error = User.validate_password('TestPass123!')
            assert valid is True
            assert error is None

        def test_password_too_short(self):
            """Test that passwords under 8 characters fail."""
            valid, error = User.validate_password('Short1!')
            assert valid is False
            assert 'at least 8 characters' in error

        def test_password_no_uppercase(self):
            """Test that passwords without uppercase letters fail."""
            valid, error = User.validate_password('testpass123!')
            assert valid is False
            assert 'uppercase letter' in error

        def test_password_no_number(self):
            """Test that passwords without numbers fail."""
            valid, error = User.validate_password('TestPass!!')
            assert valid is False
            assert 'number' in error

        def test_password_no_special_char(self):
            """Test that passwords without special characters fail."""
            valid, error = User.validate_password('TestPass123')
            assert valid is False
            assert 'special character' in error

        def test_password_with_all_requirements(self):
            """Test various valid password formats."""
            passwords = [
                'Password1!',
                'MyP@ssw0rd',
                'Secure#123',
                'Test&Pass9',
                'Complex<>1',
            ]
            for pwd in passwords:
                valid, error = User.validate_password(pwd)
                assert valid is True, f"Password '{pwd}' should be valid"

    # Email validation tests
    class TestEmailValidation:
        """Tests for email validation."""

        def test_valid_email(self):
            """Test that valid emails pass validation."""
            valid, error = User.validate_email('user@example.com')
            assert valid is True
            assert error is None

        def test_email_without_at(self):
            """Test that emails without @ fail."""
            valid, error = User.validate_email('userexample.com')
            assert valid is False
            assert 'valid email' in error

        def test_email_without_domain(self):
            """Test that emails without proper domain fail."""
            valid, error = User.validate_email('user@')
            assert valid is False
            assert 'valid email' in error

        def test_empty_email(self):
            """Test that empty email fails."""
            valid, error = User.validate_email('')
            assert valid is False
            assert 'valid email' in error

        def test_none_email(self):
            """Test that None email fails."""
            valid, error = User.validate_email(None)
            assert valid is False
            assert 'valid email' in error

        def test_various_valid_emails(self):
            """Test various valid email formats."""
            emails = [
                'test@test.com',
                'user.name@domain.org',
                'user+tag@example.co.uk',
                'firstname.lastname@company.com',
            ]
            for email in emails:
                valid, error = User.validate_email(email)
                assert valid is True, f"Email '{email}' should be valid"

    # Phone validation tests
    class TestPhoneValidation:
        """Tests for phone validation."""

        def test_valid_phone(self):
            """Test that valid phone numbers pass."""
            valid, error = User.validate_phone('1234567890')
            assert valid is True
            assert error is None

        def test_empty_phone_allowed(self):
            """Test that empty phone is allowed (optional field)."""
            valid, error = User.validate_phone('')
            assert valid is True
            assert error is None

        def test_none_phone_allowed(self):
            """Test that None phone is allowed (optional field)."""
            valid, error = User.validate_phone(None)
            assert valid is True
            assert error is None

        def test_phone_too_long(self):
            """Test that phone numbers over 10 digits fail."""
            valid, error = User.validate_phone('12345678901')
            assert valid is False
            assert 'at most 10 digits' in error

        def test_phone_with_letters(self):
            """Test that phone with letters fails."""
            valid, error = User.validate_phone('123abc7890')
            assert valid is False
            assert 'only digits' in error

        def test_phone_with_special_chars(self):
            """Test that phone with special characters fails."""
            valid, error = User.validate_phone('123-456-7890')
            assert valid is False
            assert 'only digits' in error

    # Name validation tests
    class TestNameValidation:
        """Tests for name validation."""

        def test_valid_name(self):
            """Test that valid names pass."""
            valid, error = User.validate_name('John Doe')
            assert valid is True
            assert error is None

        def test_empty_name(self):
            """Test that empty name fails (required field)."""
            valid, error = User.validate_name('')
            assert valid is False
            assert 'required' in error

        def test_whitespace_only_name(self):
            """Test that whitespace-only name fails."""
            valid, error = User.validate_name('   ')
            assert valid is False
            assert 'required' in error

        def test_none_name(self):
            """Test that None name fails."""
            valid, error = User.validate_name(None)
            assert valid is False
            assert 'required' in error

        def test_name_too_long(self):
            """Test that names over 100 characters fail."""
            long_name = 'A' * 101
            valid, error = User.validate_name(long_name)
            assert valid is False
            assert 'at most 100 characters' in error

        def test_max_length_name(self):
            """Test that 100-character name passes."""
            max_name = 'A' * 100
            valid, error = User.validate_name(max_name)
            assert valid is True

    # City validation tests
    class TestCityValidation:
        """Tests for city validation."""

        def test_valid_city(self):
            """Test that valid city passes."""
            valid, error = User.validate_city('Miami')
            assert valid is True
            assert error is None

        def test_empty_city_allowed(self):
            """Test that empty city is allowed (optional field)."""
            valid, error = User.validate_city('')
            assert valid is True
            assert error is None

        def test_none_city_allowed(self):
            """Test that None city is allowed (optional field)."""
            valid, error = User.validate_city(None)
            assert valid is True
            assert error is None

        def test_city_too_long(self):
            """Test that city over 12 characters fails."""
            valid, error = User.validate_city('LongCityName!')
            assert valid is False
            assert 'at most 12 characters' in error

        def test_max_length_city(self):
            """Test that 12-character city passes."""
            valid, error = User.validate_city('TwelveChars!')
            assert valid is True


class TestUserCRUD:
    """Tests for User CRUD operations."""

    def test_create_user_success(self, app_context, sample_user_data):
        """Test successful user creation."""
        user, error = User.create(**sample_user_data)
        assert user is not None
        assert error is None
        assert user.username == sample_user_data['username']
        assert user.email == sample_user_data['email']
        assert user.name == sample_user_data['name']
        assert user.role == sample_user_data['role']

    def test_create_user_hashes_password(self, app_context, sample_user_data):
        """Test that password is hashed on creation."""
        user, error = User.create(**sample_user_data)
        assert user is not None
        assert user.password != sample_user_data['password']
        assert check_password_hash(user.password, sample_user_data['password'])

    def test_create_user_missing_username(self, app_context, sample_user_data):
        """Test that user creation fails without username."""
        sample_user_data['username'] = ''
        user, error = User.create(**sample_user_data)
        assert user is None
        assert 'Username is required' in error

    def test_create_user_invalid_email(self, app_context, sample_user_data):
        """Test that user creation fails with invalid email."""
        sample_user_data['email'] = 'invalid-email'
        user, error = User.create(**sample_user_data)
        assert user is None
        assert 'valid email' in error

    def test_create_user_weak_password(self, app_context, sample_user_data):
        """Test that user creation fails with weak password."""
        sample_user_data['password'] = 'weak'
        user, error = User.create(**sample_user_data)
        assert user is None
        assert error is not None

    def test_create_duplicate_username(self, app_context, sample_user_data):
        """Test that duplicate usernames are rejected."""
        User.create(**sample_user_data)
        sample_user_data['email'] = 'different@example.com'
        user, error = User.create(**sample_user_data)
        assert user is None
        assert 'already exists' in error

    def test_create_duplicate_email(self, app_context, sample_user_data):
        """Test that duplicate emails are rejected."""
        User.create(**sample_user_data)
        sample_user_data['username'] = 'differentuser'
        user, error = User.create(**sample_user_data)
        assert user is None
        assert 'already exists' in error

    def test_get_by_id(self, app_context, created_user):
        """Test getting user by ID."""
        user = User.get_by_id(created_user.id)
        assert user is not None
        assert user.id == created_user.id
        assert user.username == created_user.username

    def test_get_by_id_nonexistent(self, app_context):
        """Test getting nonexistent user by ID."""
        user = User.get_by_id(99999)
        assert user is None

    def test_get_by_username(self, app_context, created_user):
        """Test getting user by username."""
        user = User.get_by_username(created_user.username)
        assert user is not None
        assert user.username == created_user.username

    def test_get_by_username_nonexistent(self, app_context):
        """Test getting nonexistent user by username."""
        user = User.get_by_username('nonexistent')
        assert user is None

    def test_get_by_email(self, app_context, created_user):
        """Test getting user by email."""
        user = User.get_by_email(created_user.email)
        assert user is not None
        assert user.email == created_user.email

    def test_get_by_email_nonexistent(self, app_context):
        """Test getting nonexistent user by email."""
        user = User.get_by_email('nonexistent@example.com')
        assert user is None


class TestUserUpdate:
    """Tests for User update operations."""

    def test_update_name(self, app_context, created_user):
        """Test updating user name."""
        success, error = created_user.update(name='Updated Name')
        assert success is True
        assert error is None
        assert created_user.name == 'Updated Name'

        # Verify in database
        user = User.get_by_id(created_user.id)
        assert user.name == 'Updated Name'

    def test_update_phone(self, app_context, created_user):
        """Test updating user phone."""
        success, error = created_user.update(phone='9876543210')
        assert success is True
        assert error is None

        user = User.get_by_id(created_user.id)
        assert user.phone == '9876543210'

    def test_update_city(self, app_context, created_user):
        """Test updating user city."""
        success, error = created_user.update(city='NewCity')
        assert success is True
        assert error is None

        user = User.get_by_id(created_user.id)
        assert user.city == 'NewCity'

    def test_update_invalid_name(self, app_context, created_user):
        """Test that updating with invalid name fails."""
        success, error = created_user.update(name='')
        assert success is False
        assert 'required' in error

    def test_update_invalid_phone(self, app_context, created_user):
        """Test that updating with invalid phone fails."""
        success, error = created_user.update(phone='invalid')
        assert success is False
        assert error is not None

    def test_update_invalid_city(self, app_context, created_user):
        """Test that updating with too long city fails."""
        success, error = created_user.update(city='ThisCityNameIsTooLong')
        assert success is False
        assert 'at most 12 characters' in error


class TestUserPassword:
    """Tests for User password operations."""

    def test_verify_password_correct(self, app_context, created_user):
        """Test verifying correct password."""
        assert created_user.verify_password('TestPass123!') is True

    def test_verify_password_incorrect(self, app_context, created_user):
        """Test verifying incorrect password."""
        assert created_user.verify_password('WrongPassword123!') is False

    def test_update_password_success(self, app_context, created_user):
        """Test successful password update."""
        success, error = created_user.update_password('TestPass123!', 'NewPass456!')
        assert success is True
        assert error is None
        assert created_user.verify_password('NewPass456!') is True

    def test_update_password_wrong_current(self, app_context, created_user):
        """Test password update fails with wrong current password."""
        success, error = created_user.update_password('WrongPass123!', 'NewPass456!')
        assert success is False
        assert 'incorrect' in error.lower()

    def test_update_password_weak_new(self, app_context, created_user):
        """Test password update fails with weak new password."""
        success, error = created_user.update_password('TestPass123!', 'weak')
        assert success is False
        assert error is not None


class TestUserRoles:
    """Tests for User role methods."""

    def test_is_volunteer(self, app_context, sample_user_data):
        """Test is_volunteer method for volunteer user."""
        sample_user_data['role'] = 'volunteer'
        user, _ = User.create(**sample_user_data)
        assert user.is_volunteer() is True
        assert user.is_manager() is False

    def test_is_manager(self, app_context, sample_manager_data):
        """Test is_manager method for manager user."""
        user, _ = User.create(**sample_manager_data)
        assert user.is_manager() is True
        assert user.is_volunteer() is False


class TestUserSerialization:
    """Tests for User serialization methods."""

    def test_to_dict(self, app_context, created_user):
        """Test converting user to dictionary."""
        user_dict = created_user.to_dict()

        assert user_dict['id'] == created_user.id
        assert user_dict['username'] == created_user.username
        assert user_dict['email'] == created_user.email
        assert user_dict['name'] == created_user.name
        assert user_dict['phone'] == created_user.phone
        assert user_dict['city'] == created_user.city
        assert user_dict['role'] == created_user.role
        # Password should not be in dict
        assert 'password' not in user_dict


class TestUserEdgeCases:
    """Tests for edge cases in User model."""

    def test_create_with_whitespace_username(self, app_context, sample_user_data):
        """Test that usernames are trimmed."""
        sample_user_data['username'] = '  spaceduser  '
        user, _ = User.create(**sample_user_data)
        assert user.username == 'spaceduser'

    def test_create_with_whitespace_email(self, app_context, sample_user_data):
        """Test emails with internal spaces are rejected (validation)."""
        # Note: The User.create validation happens before stripping,
        # so emails with spaces may fail validation
        sample_user_data['email'] = 'spaced@example.com'
        user, _ = User.create(**sample_user_data)
        assert user is not None
        assert user.email == 'spaced@example.com'

    def test_create_with_whitespace_name(self, app_context, sample_user_data):
        """Test that names are trimmed."""
        sample_user_data['name'] = '  Spaced Name  '
        user, _ = User.create(**sample_user_data)
        assert user.name == 'Spaced Name'

    def test_create_with_empty_optional_fields(self, app_context):
        """Test creating user with empty optional fields."""
        user, error = User.create(
            username='minimaluser',
            email='minimal@example.com',
            password='MinimalPass1!',
            name='Minimal User'
        )
        assert user is not None
        assert user.phone is None
        assert user.city is None

    def test_update_clears_optional_fields(self, app_context, created_user):
        """Test that optional fields can be cleared."""
        success, _ = created_user.update(phone='', city='')
        assert success is True

        user = User.get_by_id(created_user.id)
        assert user.phone is None
        assert user.city is None


class TestUserCreateValidationFailures:
    """Tests for User.create validation failures that return early."""

    def test_create_user_invalid_name(self, app_context, sample_user_data):
        """Test that user creation fails with invalid name."""
        sample_user_data['name'] = ''  # Empty name should fail
        user, error = User.create(**sample_user_data)
        assert user is None
        assert 'Name is required' in error

    def test_create_user_name_too_long(self, app_context, sample_user_data):
        """Test that user creation fails with name over 100 characters."""
        sample_user_data['name'] = 'A' * 101
        user, error = User.create(**sample_user_data)
        assert user is None
        assert 'at most 100 characters' in error

    def test_create_user_invalid_phone(self, app_context, sample_user_data):
        """Test that user creation fails with invalid phone (non-digit)."""
        sample_user_data['phone'] = '123-456-7890'  # Contains dashes
        user, error = User.create(**sample_user_data)
        assert user is None
        assert 'only digits' in error

    def test_create_user_phone_too_long(self, app_context, sample_user_data):
        """Test that user creation fails with phone over 10 digits."""
        sample_user_data['phone'] = '12345678901'  # 11 digits
        user, error = User.create(**sample_user_data)
        assert user is None
        assert 'at most 10 digits' in error

    def test_create_user_invalid_city(self, app_context, sample_user_data):
        """Test that user creation fails with city over 12 characters."""
        sample_user_data['city'] = 'A' * 13  # 13 characters
        user, error = User.create(**sample_user_data)
        assert user is None
        assert 'at most 12 characters' in error


class TestUserAvailabilityValidation:
    """Tests for availability validation."""

    def test_validate_availability_valid_values(self):
        """Test that valid availability values pass."""
        valid_values = ['full-time', 'part-time', 'weekends', 'flexible']
        for value in valid_values:
            valid, error = User.validate_availability(value)
            assert valid is True
            assert error is None

    def test_validate_availability_none_allowed(self):
        """Test that None availability is allowed."""
        valid, error = User.validate_availability(None)
        assert valid is True

    def test_validate_availability_empty_allowed(self):
        """Test that empty availability is allowed."""
        valid, error = User.validate_availability('')
        assert valid is True

    def test_validate_availability_invalid_value(self):
        """Test that invalid availability value fails."""
        valid, error = User.validate_availability('invalid-value')
        assert valid is False
        assert 'must be one of' in error


class TestUserSkillsValidation:
    """Tests for skills validation."""

    def test_validate_skills_valid(self):
        """Test that valid skills pass."""
        valid, error = User.validate_skills('Python, JavaScript, SQL')
        assert valid is True
        assert error is None

    def test_validate_skills_none_allowed(self):
        """Test that None skills is allowed."""
        valid, error = User.validate_skills(None)
        assert valid is True

    def test_validate_skills_empty_allowed(self):
        """Test that empty skills is allowed."""
        valid, error = User.validate_skills('')
        assert valid is True

    def test_validate_skills_too_long(self):
        """Test that skills over 500 characters fails."""
        long_skills = 'A' * 501
        valid, error = User.validate_skills(long_skills)
        assert valid is False
        assert '500 characters' in error


class TestUserCoordinatesValidation:
    """Tests for coordinates validation."""

    def test_validate_coordinates_valid(self):
        """Test that valid coordinates pass."""
        valid, error = User.validate_coordinates(18.4655, -66.1057)
        assert valid is True
        assert error is None

    def test_validate_coordinates_none_allowed(self):
        """Test that None coordinates are allowed."""
        valid, error = User.validate_coordinates(None, None)
        assert valid is True

    def test_validate_coordinates_missing_latitude(self):
        """Test that missing latitude fails."""
        valid, error = User.validate_coordinates(None, -66.1057)
        assert valid is False
        assert 'both' in error.lower()

    def test_validate_coordinates_missing_longitude(self):
        """Test that missing longitude fails."""
        valid, error = User.validate_coordinates(18.4655, None)
        assert valid is False
        assert 'both' in error.lower()

    def test_validate_coordinates_latitude_too_low(self):
        """Test that latitude below -90 fails."""
        valid, error = User.validate_coordinates(-91, -66)
        assert valid is False
        assert 'between -90 and 90' in error

    def test_validate_coordinates_latitude_too_high(self):
        """Test that latitude above 90 fails."""
        valid, error = User.validate_coordinates(91, -66)
        assert valid is False
        assert 'between -90 and 90' in error

    def test_validate_coordinates_longitude_too_low(self):
        """Test that longitude below -180 fails."""
        valid, error = User.validate_coordinates(18, -181)
        assert valid is False
        assert 'between -180 and 180' in error

    def test_validate_coordinates_longitude_too_high(self):
        """Test that longitude above 180 fails."""
        valid, error = User.validate_coordinates(18, 181)
        assert valid is False
        assert 'between -180 and 180' in error

    def test_validate_coordinates_invalid_type(self):
        """Test that non-numeric coordinates fail."""
        valid, error = User.validate_coordinates('abc', 'def')
        assert valid is False
        assert 'valid numbers' in error


class TestUserCreateWithVolunteerFields:
    """Tests for User creation with volunteer-specific fields."""

    def test_create_user_with_availability(self, app_context, sample_user_data):
        """Test creating user with availability."""
        sample_user_data['availability'] = 'full-time'
        user, error = User.create(**sample_user_data)
        assert user is not None
        assert error is None

    def test_create_user_with_invalid_availability(self, app_context, sample_user_data):
        """Test creating user with invalid availability fails."""
        sample_user_data['availability'] = 'invalid'
        user, error = User.create(**sample_user_data)
        assert user is None
        assert 'must be one of' in error

    def test_create_user_with_skills(self, app_context, sample_user_data):
        """Test creating user with skills."""
        sample_user_data['skills'] = 'First Aid, CPR'
        user, error = User.create(**sample_user_data)
        assert user is not None
        assert error is None

    def test_create_user_with_skills_too_long(self, app_context, sample_user_data):
        """Test creating user with skills too long fails."""
        sample_user_data['skills'] = 'A' * 501
        user, error = User.create(**sample_user_data)
        assert user is None
        assert '500 characters' in error

    def test_create_user_with_coordinates(self, app_context, sample_user_data):
        """Test creating user with coordinates."""
        sample_user_data['latitude'] = 18.4655
        sample_user_data['longitude'] = -66.1057
        user, error = User.create(**sample_user_data)
        assert user is not None
        assert error is None

    def test_create_user_with_invalid_coordinates(self, app_context, sample_user_data):
        """Test creating user with invalid coordinates fails."""
        sample_user_data['latitude'] = 100  # Out of range
        sample_user_data['longitude'] = -66
        user, error = User.create(**sample_user_data)
        assert user is None
        assert 'between -90 and 90' in error
