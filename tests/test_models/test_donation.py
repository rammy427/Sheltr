"""
Unit tests for the Donation model.
Tests donation creation, validation, and retrieval.
"""

import pytest
from decimal import Decimal
from sheltr.models.donation import Donation
from sheltr.db import get_db


class TestDonationInit:
    """Tests for Donation initialization."""

    def test_donation_init_defaults(self):
        """Test Donation initialization with defaults."""
        donation = Donation()
        assert donation.id is None
        assert donation.emergency_id is None
        assert donation.user_id is None
        assert donation.quantity is None

    def test_donation_init_with_values(self):
        """Test Donation initialization with values."""
        donation = Donation(
            donation_id=1,
            emergency_id=1,
            user_id=1,
            donation_quantity=Decimal('50.00'),
            donation_message='Test message',
            payment_process_provider='Paypal'
        )
        assert donation.id == 1
        assert donation.emergency_id == 1
        assert donation.quantity == Decimal('50.00')
        assert donation.message == 'Test message'
        assert donation.provider == 'Paypal'


class TestDonationValidation:
    """Tests for Donation validation methods."""

    def test_validate_quantity_valid(self):
        """Test validation of valid quantity."""
        valid, error, amount = Donation.validate_quantity('50.00')
        assert valid is True
        assert error is None
        assert amount == Decimal('50.00')

    def test_validate_quantity_minimum(self):
        """Test validation of minimum quantity."""
        valid, error, amount = Donation.validate_quantity('1.00')
        assert valid is True
        assert amount == Decimal('1.00')

    def test_validate_quantity_below_minimum(self):
        """Test validation rejects below minimum."""
        valid, error, amount = Donation.validate_quantity('0.50')
        assert valid is False
        assert 'Minimum' in error

    def test_validate_quantity_empty(self):
        """Test validation rejects empty quantity."""
        valid, error, amount = Donation.validate_quantity('')
        assert valid is False
        assert 'required' in error.lower()

    def test_validate_quantity_none(self):
        """Test validation rejects None quantity."""
        valid, error, amount = Donation.validate_quantity(None)
        assert valid is False

    def test_validate_quantity_invalid_string(self):
        """Test validation rejects non-numeric string."""
        valid, error, amount = Donation.validate_quantity('abc')
        assert valid is False
        assert 'number' in error.lower()

    def test_validate_quantity_rounds_correctly(self):
        """Test that quantity is rounded to 2 decimal places."""
        valid, error, amount = Donation.validate_quantity('50.999')
        assert valid is True
        assert amount == Decimal('51.00')

    def test_validate_msg_valid(self):
        """Test validation of valid message."""
        valid, error, msg = Donation.validate_msg('Thank you for helping!')
        assert valid is True
        assert msg == 'Thank you for helping!'

    def test_validate_msg_empty(self):
        """Test validation allows empty message."""
        valid, error, msg = Donation.validate_msg('')
        assert valid is True
        assert msg is None

    def test_validate_msg_whitespace_only(self):
        """Test validation handles whitespace-only message."""
        valid, error, msg = Donation.validate_msg('   ')
        assert valid is True
        assert msg is None

    def test_validate_msg_too_long(self):
        """Test validation rejects too long message."""
        long_msg = 'a' * 500
        valid, error, msg = Donation.validate_msg(long_msg)
        assert valid is False
        assert '400' in error

    def test_validate_msg_invalid_characters(self):
        """Test validation rejects invalid characters."""
        valid, error, msg = Donation.validate_msg('Test <script>alert("xss")</script>')
        assert valid is False
        assert 'invalid characters' in error.lower()

    def test_validate_provider_valid(self):
        """Test validation of valid providers."""
        for provider in ['Paypal', 'Venmo', 'Apple Pay', 'Credit Card']:
            valid, error = Donation.validate_provider(provider)
            assert valid is True
            assert error is None

    def test_validate_provider_invalid(self):
        """Test validation rejects invalid provider."""
        valid, error = Donation.validate_provider('Bitcoin')
        assert valid is False
        assert 'Invalid' in error

    def test_validate_provider_empty(self):
        """Test validation rejects empty provider."""
        valid, error = Donation.validate_provider('')
        assert valid is False
        assert 'required' in error.lower()

    def test_validate_provider_none(self):
        """Test validation rejects None provider."""
        valid, error = Donation.validate_provider(None)
        assert valid is False

    def test_validate_ids_valid(self):
        """Test validation of valid IDs."""
        valid, error = Donation.validate_ids(1, 1)
        assert valid is True

    def test_validate_ids_zero(self):
        """Test validation rejects zero IDs."""
        valid, error = Donation.validate_ids(0, 1)
        assert valid is False

    def test_validate_ids_negative(self):
        """Test validation rejects negative IDs."""
        valid, error = Donation.validate_ids(-1, 1)
        assert valid is False

    def test_validate_ids_none(self):
        """Test validation rejects None IDs."""
        valid, error = Donation.validate_ids(None, 1)
        assert valid is False

    def test_validate_ids_invalid_type(self):
        """Test validation rejects invalid type IDs."""
        valid, error = Donation.validate_ids('abc', 1)
        assert valid is False


class TestDonationCreate:
    """Tests for Donation creation."""

    def test_create_donation_success(self, app_context, db, created_user, sample_emergency):
        """Test successful donation creation."""
        donation, error = Donation.create(
            emergency_id=sample_emergency['emergency_id'],
            user_id=created_user.id,
            amount='50.00',
            message='Test donation',
            provider='Paypal'
        )
        assert donation is not None
        assert error is None
        assert donation.quantity == Decimal('50.00')

    def test_create_donation_without_message(self, app_context, db, created_user, sample_emergency):
        """Test donation creation without message."""
        donation, error = Donation.create(
            emergency_id=sample_emergency['emergency_id'],
            user_id=created_user.id,
            amount='25.00',
            message='',
            provider='Venmo'
        )
        assert donation is not None
        assert error is None

    def test_create_donation_invalid_amount(self, app_context, created_user, sample_emergency):
        """Test donation creation with invalid amount."""
        donation, error = Donation.create(
            emergency_id=sample_emergency['emergency_id'],
            user_id=created_user.id,
            amount='0.50',
            provider='Paypal'
        )
        assert donation is None
        assert error is not None

    def test_create_donation_invalid_provider(self, app_context, created_user, sample_emergency):
        """Test donation creation with invalid provider."""
        donation, error = Donation.create(
            emergency_id=sample_emergency['emergency_id'],
            user_id=created_user.id,
            amount='50.00',
            message='Test message',
            provider='InvalidProvider'
        )
        assert donation is None
        assert error is not None

    def test_create_donation_invalid_ids(self, app_context):
        """Test donation creation with invalid IDs."""
        donation, error = Donation.create(
            emergency_id=0,
            user_id=0,
            amount='50.00',
            message='Test message',
            provider='Paypal'
        )
        assert donation is None
        assert error is not None


class TestDonationRetrieval:
    """Tests for Donation retrieval methods."""

    def test_get_by_id_exists(self, app_context, db, created_user, sample_emergency):
        """Test getting donation by ID that exists."""
        donation, _ = Donation.create(
            emergency_id=sample_emergency['emergency_id'],
            user_id=created_user.id,
            amount='75.00',
            message='Test message',
            provider='Credit Card'
        )
        retrieved = Donation.get_by_id(donation.id)
        assert retrieved is not None
        assert retrieved.id == donation.id

    def test_get_by_id_not_exists(self, app_context, db):
        """Test getting donation by ID that doesn't exist."""
        retrieved = Donation.get_by_id(99999)
        assert retrieved is None

    def test_list_recent(self, app_context, db, created_user, sample_emergency):
        """Test listing recent donations."""
        # Create some donations
        for i in range(3):
            Donation.create(
                emergency_id=sample_emergency['emergency_id'],
                user_id=created_user.id,
                amount=str(10 * (i + 1)),
                message=f'Donation {i}',
                provider='Paypal'
            )
        donations = Donation.list_recent(limit=5)
        assert len(donations) >= 3

    def test_user_donation_history(self, app_context, db, created_user, sample_emergency):
        """Test getting user donation history."""
        # Create donations for user
        for i in range(2):
            Donation.create(
                emergency_id=sample_emergency['emergency_id'],
                user_id=created_user.id,
                amount=str(20 * (i + 1)),
                message=f'Donation {i}',
                provider='Venmo'
            )
        history = Donation.user_donation_history(created_user.id)
        assert len(history) >= 2
        assert 'emergency_name' in history[0]

    def test_emergency_donation_history(self, app_context, db, created_user, sample_emergency):
        """Test getting emergency donation history."""
        # Create donations for emergency
        for i in range(2):
            Donation.create(
                emergency_id=sample_emergency['emergency_id'],
                user_id=created_user.id,
                amount=str(15 * (i + 1)),
                message=f'Emergency donation {i}',
                provider='Apple Pay'
            )
        history = Donation.emergency_donation_history(sample_emergency['emergency_id'])
        assert len(history) >= 2

    def test_sum_by_emergency(self, app_context, db, created_user, sample_emergency):
        """Test summing donations by emergency."""
        # Create known donations
        Donation.create(
            emergency_id=sample_emergency['emergency_id'],
            user_id=created_user.id,
            amount='100.00',
            message='Sum test 1',
            provider='Paypal'
        )
        Donation.create(
            emergency_id=sample_emergency['emergency_id'],
            user_id=created_user.id,
            amount='50.00',
            message='Sum test 2',
            provider='Paypal'
        )
        total = Donation.sum_by_emergency(sample_emergency['emergency_id'])
        assert total >= Decimal('150.00')

    def test_sum_by_user_donation(self, app_context, db, created_user, sample_emergency):
        """Test summing donations by user."""
        Donation.create(
            emergency_id=sample_emergency['emergency_id'],
            user_id=created_user.id,
            amount='75.00',
            message='User sum test',
            provider='Venmo'
        )
        total = Donation.sum_by_user_donation(created_user.id)
        assert total >= Decimal('75.00')

    def test_count_by_emergency(self, app_context, db, created_user, sample_emergency):
        """Test counting donations by emergency."""
        initial_count = Donation.count_by_emergency(sample_emergency['emergency_id'])
        Donation.create(
            emergency_id=sample_emergency['emergency_id'],
            user_id=created_user.id,
            amount='25.00',
            message='Count test',
            provider='Credit Card'
        )
        new_count = Donation.count_by_emergency(sample_emergency['emergency_id'])
        assert new_count == initial_count + 1

    def test_count_by_donations(self, app_context, db, created_user, sample_emergency):
        """Test counting donations by user."""
        initial_count = Donation.count_by_donations(created_user.id)
        Donation.create(
            emergency_id=sample_emergency['emergency_id'],
            user_id=created_user.id,
            amount='30.00',
            message='User count test',
            provider='Paypal'
        )
        new_count = Donation.count_by_donations(created_user.id)
        assert new_count == initial_count + 1


class TestDonationSerialization:
    """Tests for Donation serialization."""

    def test_to_dict(self, app_context, db, created_user, sample_emergency):
        """Test converting donation to dictionary."""
        donation, _ = Donation.create(
            emergency_id=sample_emergency['emergency_id'],
            user_id=created_user.id,
            amount='100.00',
            message='Test dict conversion',
            provider='Paypal'
        )
        d = donation.to_dict()
        assert d['donation_id'] == donation.id
        assert d['emergency_id'] == sample_emergency['emergency_id']
        assert d['donation_quantity'] == '100.00'
        assert d['donation_message'] == 'Test dict conversion'

    def test_from_row(self, app_context, db, created_user, sample_emergency):
        """Test creating donation from database row."""
        donation, _ = Donation.create(
            emergency_id=sample_emergency['emergency_id'],
            user_id=created_user.id,
            amount='55.00',
            message='From row test',
            provider='Venmo'
        )
        row = db.execute(
            "SELECT * FROM donation WHERE donation_id = ?",
            (donation.id,)
        ).fetchone()
        from_row = Donation.from_row(row)
        assert from_row.id == donation.id
