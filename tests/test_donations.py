"""
Tests for the Donations blueprint.
Tests the donations route and template rendering.
"""

import pytest
from sheltr.models.donation import Donation


class TestDonationsRoute:
    """Tests for donations route."""

    def test_donations_page_requires_login(self, client):
        """Test that donations page requires authentication."""
        response = client.get('/donations/')
        assert response.status_code == 302
        assert 'login' in response.headers['Location']

    def test_donations_page_loads_when_authenticated(self, authenticated_client):
        """Test that authenticated user can access donations page."""
        response = authenticated_client.get('/donations/')
        assert response.status_code == 200
        assert b'Donations' in response.data or b'donations' in response.data

    def test_donations_page_renders_template(self, authenticated_client):
        """Test that donations page renders the donations template."""
        response = authenticated_client.get('/donations/')
        assert response.status_code == 200
        # The template should have been rendered (check for common HTML)
        assert b'<!DOCTYPE' in response.data or b'<html' in response.data or b'<div' in response.data


class TestMakeDonation:
    """Tests for make donation route."""

    def test_make_donation_page_loads(self, authenticated_client):
        """Test that make donation page loads."""
        response = authenticated_client.get('/donations/make-donation')
        assert response.status_code == 200

    def test_make_donation_success(self, authenticated_client, sample_emergency):
        """Test successful donation submission."""
        response = authenticated_client.post('/donations/make-donation', data={
            'emergency_id': sample_emergency['emergency_id'],
            'amount': '50.00',
            'provider': 'Paypal',
            'msg': 'Test donation message'
        })
        # Should redirect to payment mockup on success
        assert response.status_code == 302 or response.status_code == 200

    def test_make_donation_missing_emergency(self, authenticated_client):
        """Test donation without emergency selection."""
        response = authenticated_client.post('/donations/make-donation', data={
            'amount': '50.00',
            'provider': 'Paypal'
        })
        assert response.status_code == 200  # Re-renders form with error

    def test_make_donation_missing_amount(self, authenticated_client, sample_emergency):
        """Test donation without amount."""
        response = authenticated_client.post('/donations/make-donation', data={
            'emergency_id': sample_emergency['emergency_id'],
            'provider': 'Paypal'
        })
        assert response.status_code == 200

    def test_make_donation_missing_provider(self, authenticated_client, sample_emergency):
        """Test donation without provider."""
        response = authenticated_client.post('/donations/make-donation', data={
            'emergency_id': sample_emergency['emergency_id'],
            'amount': '50.00'
        })
        assert response.status_code == 200


class TestDonationHistory:
    """Tests for donation history route."""

    def test_donation_history_requires_login(self, client):
        """Test that donation history requires login."""
        response = client.get('/donations/user-donation-history.html')
        assert response.status_code == 302

    def test_donation_history_loads(self, authenticated_client):
        """Test that donation history page loads."""
        response = authenticated_client.get('/donations/user-donation-history.html')
        assert response.status_code == 200

    def test_donation_history_shows_user_donations(self, authenticated_client, app_context, db, created_user, sample_emergency):
        """Test that history shows user donations."""
        # Create a donation for this user
        Donation.create(
            emergency_id=sample_emergency['emergency_id'],
            user_id=created_user.id,
            amount='100.00',
            message='History test',
            provider='Paypal'
        )
        response = authenticated_client.get('/donations/user-donation-history.html')
        assert response.status_code == 200


class TestPaymentMockup:
    """Tests for payment mockup route."""

    def test_payment_mockup_requires_login(self, client):
        """Test that payment mockup requires login."""
        response = client.get('/donations/payment-mockup')
        assert response.status_code == 302

    def test_payment_mockup_loads(self, authenticated_client):
        """Test that payment mockup page loads."""
        response = authenticated_client.get('/donations/payment-mockup?provider=Paypal&amount=50.00&donation_id=1')
        assert response.status_code == 200

    def test_payment_mockup_with_params(self, authenticated_client):
        """Test payment mockup with parameters."""
        response = authenticated_client.get(
            '/donations/payment-mockup?provider=Venmo&amount=100.00&donation_id=123'
        )
        assert response.status_code == 200


class TestCompletePayment:
    """Tests for complete payment route."""

    def test_complete_payment_requires_login(self, client):
        """Test that complete payment requires login."""
        response = client.post('/donations/complete-payment')
        assert response.status_code == 302

    def test_complete_payment_success(self, authenticated_client):
        """Test successful payment completion."""
        response = authenticated_client.post('/donations/complete-payment')
        # Should redirect to donations view with success message
        assert response.status_code == 302
