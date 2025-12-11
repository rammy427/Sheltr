"""
Unit tests for the Emergency model.
Tests Emergency creation, status, and database operations.
"""

import pytest
from sheltr.models import Emergency
from sheltr.db import get_db


class TestEmergencyInitialization:
    """Tests for Emergency initialization."""

    def test_emergency_init_defaults(self):
        """Test Emergency initialization with defaults."""
        emergency = Emergency()
        assert emergency.id is None
        assert emergency.name is None
        assert emergency.status is None
        assert emergency.date is None
        assert emergency.img_url is None
        assert emergency.description is None

    def test_emergency_init_with_values(self):
        """Test Emergency initialization with values."""
        emergency = Emergency(
            id=1,
            name='Test Emergency',
            status=True,
            date='2025-01-15',
            img_url='https://example.com/img.jpg',
            description='Test description'
        )
        assert emergency.id == 1
        assert emergency.name == 'Test Emergency'
        assert emergency.status is True
        assert emergency.date == '2025-01-15'
        assert emergency.img_url == 'https://example.com/img.jpg'
        assert emergency.description == 'Test description'


class TestEmergencyCreation:
    """Tests for Emergency creation."""

    def test_new_emergency_success(self, app_context, db):
        """Test successful emergency creation."""
        Emergency.new_emergency(
            name='Test Emergency',
            status=True,
            date='2025-01-15',
            img_url='https://example.com/test.jpg',
            description='Test emergency description'
        )

        # Verify in database
        row = db.execute(
            "SELECT * FROM emergencies WHERE emergency_name = 'Test Emergency'"
        ).fetchone()

        assert row is not None
        assert row['emergency_name'] == 'Test Emergency'
        assert row['emergency_status'] == 1  # True in SQLite
        # Date may be returned as datetime.date or string depending on SQLite config
        assert str(row['emergency_date']) == '2025-01-15'
        assert row['image_url'] == 'https://example.com/test.jpg'
        assert row['emergency_description'] == 'Test emergency description'

    def test_new_emergency_without_optional_fields(self, app_context, db):
        """Test emergency creation without optional fields."""
        Emergency.new_emergency(
            name='Minimal Emergency',
            status=False,
            date='2025-02-20'
        )

        row = db.execute(
            "SELECT * FROM emergencies WHERE emergency_name = 'Minimal Emergency'"
        ).fetchone()

        assert row is not None
        assert row['emergency_name'] == 'Minimal Emergency'
        assert row['emergency_status'] == 0  # False in SQLite
        assert row['image_url'] is None
        assert row['emergency_description'] is None

    def test_new_emergency_trims_whitespace(self, app_context, db):
        """Test that emergency creation trims whitespace from fields."""
        Emergency.new_emergency(
            name='  Whitespace Emergency  ',
            status=True,
            date='2025-03-10',
            img_url='  https://example.com/img.jpg  ',
            description='  Description with spaces  '
        )

        row = db.execute(
            "SELECT * FROM emergencies WHERE emergency_name = 'Whitespace Emergency'"
        ).fetchone()

        assert row is not None
        assert row['emergency_name'] == 'Whitespace Emergency'
        assert row['image_url'] == 'https://example.com/img.jpg'
        assert row['emergency_description'] == 'Description with spaces'

    def test_new_emergency_active_status(self, app_context, db):
        """Test creating an active emergency."""
        Emergency.new_emergency(
            name='Active Emergency',
            status=True,
            date='2025-01-01'
        )

        row = db.execute(
            "SELECT emergency_status FROM emergencies WHERE emergency_name = 'Active Emergency'"
        ).fetchone()

        assert row['emergency_status'] == 1  # True/Active

    def test_new_emergency_inactive_status(self, app_context, db):
        """Test creating an inactive emergency."""
        Emergency.new_emergency(
            name='Inactive Emergency',
            status=False,
            date='2025-01-01'
        )

        row = db.execute(
            "SELECT emergency_status FROM emergencies WHERE emergency_name = 'Inactive Emergency'"
        ).fetchone()

        assert row['emergency_status'] == 0  # False/Inactive


class TestEmergencyIsActive:
    """Tests for Emergency isActive method."""

    def test_is_active_true(self):
        """Test isActive returns True for active emergency."""
        emergency = Emergency(status=True)
        assert emergency.isActive() is True

    def test_is_active_false(self):
        """Test isActive returns False for inactive emergency."""
        emergency = Emergency(status=False)
        assert emergency.isActive() is False

    def test_is_active_with_int_true(self):
        """Test isActive with integer 1 (from database)."""
        emergency = Emergency(status=1)
        assert emergency.isActive() == 1  # Truthy

    def test_is_active_with_int_false(self):
        """Test isActive with integer 0 (from database)."""
        emergency = Emergency(status=0)
        assert emergency.isActive() == 0  # Falsy


class TestEmergencyMultiple:
    """Tests for multiple emergencies."""

    def test_create_multiple_emergencies(self, app_context, db):
        """Test creating multiple emergencies."""
        for i in range(5):
            Emergency.new_emergency(
                name=f'Emergency {i}',
                status=i % 2 == 0,  # Alternate active/inactive
                date=f'2025-01-{10 + i:02d}'
            )

        rows = db.execute("SELECT * FROM emergencies WHERE emergency_name LIKE 'Emergency%'").fetchall()
        assert len(rows) == 5

    def test_emergencies_have_unique_ids(self, app_context, db):
        """Test that emergencies get unique IDs."""
        Emergency.new_emergency(name='Unique 1', status=True, date='2025-01-01')
        Emergency.new_emergency(name='Unique 2', status=True, date='2025-01-02')
        Emergency.new_emergency(name='Unique 3', status=True, date='2025-01-03')

        rows = db.execute(
            "SELECT emergency_id FROM emergencies WHERE emergency_name LIKE 'Unique%'"
        ).fetchall()

        ids = [row['emergency_id'] for row in rows]
        assert len(ids) == len(set(ids))  # All unique


class TestEmergencyDates:
    """Tests for Emergency date handling."""

    def test_emergency_various_date_formats(self, app_context, db):
        """Test emergencies with various date formats."""
        dates = [
            '2025-01-01',
            '2025-12-31',
            '2020-06-15',
        ]

        for i, date in enumerate(dates):
            Emergency.new_emergency(
                name=f'Date Emergency {i}',
                status=True,
                date=date
            )

        for i, date in enumerate(dates):
            row = db.execute(
                "SELECT emergency_date FROM emergencies WHERE emergency_name = ?",
                (f'Date Emergency {i}',)
            ).fetchone()
            # Date may be returned as datetime.date or string
            assert str(row['emergency_date']) == date


class TestEmergencyDescriptions:
    """Tests for Emergency description handling."""

    def test_emergency_long_description(self, app_context, db):
        """Test emergency with long description."""
        long_desc = 'A' * 1000  # 1000 character description
        Emergency.new_emergency(
            name='Long Desc Emergency',
            status=True,
            date='2025-01-01',
            description=long_desc
        )

        row = db.execute(
            "SELECT emergency_description FROM emergencies WHERE emergency_name = 'Long Desc Emergency'"
        ).fetchone()
        assert row['emergency_description'] == long_desc

    def test_emergency_multiline_description(self, app_context, db):
        """Test emergency with multiline description."""
        multiline = """This is a multiline
        description with
        several lines."""

        Emergency.new_emergency(
            name='Multiline Emergency',
            status=True,
            date='2025-01-01',
            description=multiline
        )

        row = db.execute(
            "SELECT emergency_description FROM emergencies WHERE emergency_name = 'Multiline Emergency'"
        ).fetchone()
        assert 'multiline' in row['emergency_description']


class TestEmergencyImageUrls:
    """Tests for Emergency image URL handling."""

    def test_emergency_with_http_url(self, app_context, db):
        """Test emergency with HTTP image URL."""
        Emergency.new_emergency(
            name='HTTP Image Emergency',
            status=True,
            date='2025-01-01',
            img_url='http://example.com/image.jpg'
        )

        row = db.execute(
            "SELECT image_url FROM emergencies WHERE emergency_name = 'HTTP Image Emergency'"
        ).fetchone()
        assert row['image_url'] == 'http://example.com/image.jpg'

    def test_emergency_with_https_url(self, app_context, db):
        """Test emergency with HTTPS image URL."""
        Emergency.new_emergency(
            name='HTTPS Image Emergency',
            status=True,
            date='2025-01-01',
            img_url='https://example.com/image.jpg'
        )

        row = db.execute(
            "SELECT image_url FROM emergencies WHERE emergency_name = 'HTTPS Image Emergency'"
        ).fetchone()
        assert row['image_url'] == 'https://example.com/image.jpg'

    def test_emergency_with_long_url(self, app_context, db):
        """Test emergency with long image URL."""
        long_url = 'https://example.com/' + 'a' * 400 + '.jpg'
        Emergency.new_emergency(
            name='Long URL Emergency',
            status=True,
            date='2025-01-01',
            img_url=long_url
        )

        row = db.execute(
            "SELECT image_url FROM emergencies WHERE emergency_name = 'Long URL Emergency'"
        ).fetchone()
        assert row['image_url'] == long_url


class TestEmergencyEditEm:
    """Tests for Emergency edit_em method."""

    def test_edit_em_update_name(self, app_context, db):
        """Test editing emergency name."""
        # Create an emergency
        Emergency.new_emergency(
            name='Original Name',
            status=True,
            date='2025-01-15'
        )

        # Get the emergency from DB
        row = db.execute(
            "SELECT * FROM emergencies WHERE emergency_name = 'Original Name'"
        ).fetchone()

        emergency = Emergency(
            id=row['emergency_id'],
            name=row['emergency_name'],
            status=row['emergency_status'],
            date=row['emergency_date'],
            img_url=row['image_url'],
            description=row['emergency_description']
        )

        # Edit the name
        success, error = emergency.edit_em(name='Updated Name')

        assert success is True
        assert error is None
        assert emergency.name == 'Updated Name'

        # Verify in database
        row = db.execute(
            "SELECT emergency_name FROM emergencies WHERE emergency_id = ?",
            (emergency.id,)
        ).fetchone()
        assert row['emergency_name'] == 'Updated Name'

    def test_edit_em_update_date(self, app_context, db):
        """Test editing emergency date."""
        Emergency.new_emergency(
            name='Date Edit Test',
            status=True,
            date='2025-01-15'
        )

        row = db.execute(
            "SELECT * FROM emergencies WHERE emergency_name = 'Date Edit Test'"
        ).fetchone()

        emergency = Emergency(
            id=row['emergency_id'],
            name=row['emergency_name'],
            status=row['emergency_status'],
            date=row['emergency_date']
        )

        success, error = emergency.edit_em(date='2025-12-25')

        assert success is True
        assert emergency.date == '2025-12-25'

        row = db.execute(
            "SELECT emergency_date FROM emergencies WHERE emergency_id = ?",
            (emergency.id,)
        ).fetchone()
        assert str(row['emergency_date']) == '2025-12-25'

    def test_edit_em_update_img_url(self, app_context, db):
        """Test editing emergency image URL."""
        Emergency.new_emergency(
            name='Image Edit Test',
            status=True,
            date='2025-01-15',
            img_url='https://old.com/img.jpg'
        )

        row = db.execute(
            "SELECT * FROM emergencies WHERE emergency_name = 'Image Edit Test'"
        ).fetchone()

        emergency = Emergency(
            id=row['emergency_id'],
            name=row['emergency_name'],
            status=row['emergency_status'],
            date=row['emergency_date'],
            img_url=row['image_url']
        )

        success, error = emergency.edit_em(img_url='https://new.com/img.jpg')

        assert success is True
        assert emergency.img_url == 'https://new.com/img.jpg'

        row = db.execute(
            "SELECT image_url FROM emergencies WHERE emergency_id = ?",
            (emergency.id,)
        ).fetchone()
        assert row['image_url'] == 'https://new.com/img.jpg'

    def test_edit_em_update_description(self, app_context, db):
        """Test editing emergency description."""
        Emergency.new_emergency(
            name='Desc Edit Test',
            status=True,
            date='2025-01-15',
            description='Original description'
        )

        row = db.execute(
            "SELECT * FROM emergencies WHERE emergency_name = 'Desc Edit Test'"
        ).fetchone()

        emergency = Emergency(
            id=row['emergency_id'],
            name=row['emergency_name'],
            status=row['emergency_status'],
            date=row['emergency_date'],
            description=row['emergency_description']
        )

        success, error = emergency.edit_em(description='Updated description')

        assert success is True
        assert emergency.description == 'Updated description'

        row = db.execute(
            "SELECT emergency_description FROM emergencies WHERE emergency_id = ?",
            (emergency.id,)
        ).fetchone()
        assert row['emergency_description'] == 'Updated description'

    def test_edit_em_update_multiple_fields(self, app_context, db):
        """Test editing multiple emergency fields at once."""
        Emergency.new_emergency(
            name='Multi Edit Test',
            status=True,
            date='2025-01-15',
            img_url='https://old.com/img.jpg',
            description='Old description'
        )

        row = db.execute(
            "SELECT * FROM emergencies WHERE emergency_name = 'Multi Edit Test'"
        ).fetchone()

        emergency = Emergency(
            id=row['emergency_id'],
            name=row['emergency_name'],
            status=row['emergency_status'],
            date=row['emergency_date'],
            img_url=row['image_url'],
            description=row['emergency_description']
        )

        success, error = emergency.edit_em(
            name='New Name',
            date='2025-06-30',
            img_url='https://new.com/new.jpg',
            description='New description'
        )

        assert success is True
        assert emergency.name == 'New Name'
        assert emergency.date == '2025-06-30'
        assert emergency.img_url == 'https://new.com/new.jpg'
        assert emergency.description == 'New description'

    def test_edit_em_trims_whitespace(self, app_context, db):
        """Test that edit_em trims whitespace from fields."""
        Emergency.new_emergency(
            name='Whitespace Test',
            status=True,
            date='2025-01-15'
        )

        row = db.execute(
            "SELECT * FROM emergencies WHERE emergency_name = 'Whitespace Test'"
        ).fetchone()

        emergency = Emergency(
            id=row['emergency_id'],
            name=row['emergency_name'],
            status=row['emergency_status'],
            date=row['emergency_date']
        )

        success, error = emergency.edit_em(
            name='  Trimmed Name  ',
            img_url='  https://trimmed.com/img.jpg  ',
            description='  Trimmed description  '
        )

        assert success is True
        assert emergency.name == 'Trimmed Name'
        assert emergency.img_url == 'https://trimmed.com/img.jpg'
        assert emergency.description == 'Trimmed description'

    def test_edit_em_clear_img_url_with_empty_string(self, app_context, db):
        """Test clearing image URL with empty string."""
        Emergency.new_emergency(
            name='Clear Image Test',
            status=True,
            date='2025-01-15',
            img_url='https://example.com/img.jpg'
        )

        row = db.execute(
            "SELECT * FROM emergencies WHERE emergency_name = 'Clear Image Test'"
        ).fetchone()

        emergency = Emergency(
            id=row['emergency_id'],
            name=row['emergency_name'],
            status=row['emergency_status'],
            date=row['emergency_date'],
            img_url=row['image_url']
        )

        success, error = emergency.edit_em(img_url='')

        assert success is True
        assert emergency.img_url is None

    def test_edit_em_no_changes(self, app_context, db):
        """Test edit_em with no changes."""
        Emergency.new_emergency(
            name='No Change Test',
            status=True,
            date='2025-01-15'
        )

        row = db.execute(
            "SELECT * FROM emergencies WHERE emergency_name = 'No Change Test'"
        ).fetchone()

        emergency = Emergency(
            id=row['emergency_id'],
            name=row['emergency_name'],
            status=row['emergency_status'],
            date=row['emergency_date']
        )

        # Call edit_em with no arguments
        success, error = emergency.edit_em()

        assert success is True
        assert error is None


