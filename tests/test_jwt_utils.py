"""
Unit tests for JWT utility functions.
Tests token generation, verification, expiration, and refresh.
"""

import pytest
import jwt
import time
from datetime import datetime, timedelta
from sheltr.jwt_utils import (
    generate_token,
    decode_token,
    verify_token,
    is_token_expiring_soon,
    refresh_token
)


class TestGenerateToken:
    """Tests for token generation."""

    def test_generate_token_success(self, app_context):
        """Test successful token generation."""
        token = generate_token(user_id=1)
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    def test_generate_token_encodes_user_id(self, app_context):
        """Test that token contains user_id."""
        token = generate_token(user_id=42)
        decoded = decode_token(token)
        assert decoded['user_id'] == 42

    def test_generate_token_contains_exp(self, app_context):
        """Test that token contains expiration."""
        token = generate_token(user_id=1)
        decoded = decode_token(token)
        assert 'exp' in decoded

    def test_generate_token_contains_iat(self, app_context):
        """Test that token contains issued-at time."""
        token = generate_token(user_id=1)
        decoded = decode_token(token)
        assert 'iat' in decoded

    def test_generate_token_custom_expiration(self, app_context):
        """Test token generation with custom expiration."""
        token = generate_token(user_id=1, expiration_hours=48)
        decoded = decode_token(token)

        iat = decoded['iat']
        exp = decoded['exp']

        # Expiration should be ~48 hours after issued
        diff = exp - iat
        assert 47 * 3600 <= diff <= 49 * 3600  # Allow some tolerance

    def test_generate_token_default_expiration(self, app_context):
        """Test token has default 24 hour expiration."""
        token = generate_token(user_id=1)
        decoded = decode_token(token)

        iat = decoded['iat']
        exp = decoded['exp']

        diff = exp - iat
        assert 23 * 3600 <= diff <= 25 * 3600  # ~24 hours

    def test_generate_token_different_users(self, app_context):
        """Test tokens for different users are different."""
        token1 = generate_token(user_id=1)
        token2 = generate_token(user_id=2)
        assert token1 != token2


class TestDecodeToken:
    """Tests for token decoding."""

    def test_decode_valid_token(self, app_context):
        """Test decoding a valid token."""
        token = generate_token(user_id=1)
        decoded = decode_token(token)

        assert decoded is not None
        assert 'user_id' in decoded
        assert 'exp' in decoded
        assert 'iat' in decoded

    def test_decode_invalid_token(self, app_context):
        """Test decoding an invalid token returns None."""
        decoded = decode_token('invalid.token.string')
        assert decoded is None

    def test_decode_expired_token(self, app_context):
        """Test decoding an expired token returns None."""
        # Create a token that expires immediately
        token = generate_token(user_id=1, expiration_hours=0)
        time.sleep(0.1)  # Wait a bit
        decoded = decode_token(token)
        # Should return None for expired token
        assert decoded is None

    def test_decode_tampered_token(self, app):
        """Test decoding a tampered token returns None."""
        with app.app_context():
            token = generate_token(user_id=1)
            # Tamper with the token
            parts = token.split('.')
            parts[1] = 'tampered' + parts[1][8:]
            tampered_token = '.'.join(parts)

            decoded = decode_token(tampered_token)
            assert decoded is None

    def test_decode_empty_token(self, app_context):
        """Test decoding empty string returns None."""
        decoded = decode_token('')
        assert decoded is None


class TestVerifyToken:
    """Tests for token verification."""

    def test_verify_valid_token(self, app_context):
        """Test verifying a valid token returns user_id."""
        token = generate_token(user_id=123)
        user_id = verify_token(token)
        assert user_id == 123

    def test_verify_invalid_token(self, app_context):
        """Test verifying invalid token returns None."""
        user_id = verify_token('invalid.token.string')
        assert user_id is None

    def test_verify_expired_token(self, app_context):
        """Test verifying expired token returns None."""
        # Create token that expires immediately
        token = generate_token(user_id=1, expiration_hours=0)
        time.sleep(0.1)
        user_id = verify_token(token)
        assert user_id is None

    def test_verify_none_token(self, app_context):
        """Test verifying None token returns None."""
        # This would typically raise an error, but we handle it gracefully
        user_id = verify_token('')
        assert user_id is None


class TestIsTokenExpiringSoon:
    """Tests for token expiration check."""

    def test_token_not_expiring_soon(self, app_context):
        """Test fresh token is not expiring soon."""
        token = generate_token(user_id=1, expiration_hours=24)
        assert is_token_expiring_soon(token) is False

    def test_token_expiring_within_threshold(self, app_context):
        """Test token expiring within threshold is detected."""
        # Create token that expires in 1 hour
        token = generate_token(user_id=1, expiration_hours=1)
        # Default threshold is 2 hours, so 1 hour should be "soon"
        assert is_token_expiring_soon(token, hours_threshold=2) is True

    def test_token_expiring_custom_threshold(self, app_context):
        """Test custom threshold for expiration check."""
        # Token expires in 10 hours
        token = generate_token(user_id=1, expiration_hours=10)
        # With 3 hour threshold, not expiring soon
        assert is_token_expiring_soon(token, hours_threshold=3) is False
        # With 12 hour threshold, expiring soon
        assert is_token_expiring_soon(token, hours_threshold=12) is True

    def test_invalid_token_not_expiring_soon(self, app_context):
        """Test invalid token returns False for expiring soon."""
        assert is_token_expiring_soon('invalid.token') is False

    def test_token_missing_exp_claim(self, app_context, app):
        """Test token with missing exp claim returns False."""
        # Create a valid JWT but without the 'exp' claim
        payload = {'user_id': 1, 'iat': datetime.utcnow()}
        token = jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')
        assert is_token_expiring_soon(token) is False


class TestRefreshToken:
    """Tests for token refresh."""

    def test_refresh_valid_token(self, app_context):
        """Test refreshing a valid token."""
        original_token = generate_token(user_id=1)
        time.sleep(1.1)  # Delay to ensure different timestamp (1 second granularity)
        new_token = refresh_token(original_token)

        assert new_token is not None
        # Both should decode to same user_id
        assert verify_token(original_token) == verify_token(new_token)

    def test_refresh_preserves_user_id(self, app_context):
        """Test that refresh preserves user_id."""
        original_token = generate_token(user_id=42)
        new_token = refresh_token(original_token)

        assert verify_token(new_token) == 42

    def test_refresh_extends_expiration(self, app_context):
        """Test that refresh extends expiration."""
        # Create token expiring in 1 hour
        original_token = generate_token(user_id=1, expiration_hours=1)
        original_decoded = decode_token(original_token)

        time.sleep(0.1)

        # Refresh should create new token with fresh 24 hour expiration
        new_token = refresh_token(original_token)
        new_decoded = decode_token(new_token)

        # New expiration should be later than original
        assert new_decoded['exp'] > original_decoded['exp']

    def test_refresh_invalid_token(self, app_context):
        """Test refreshing invalid token returns None."""
        new_token = refresh_token('invalid.token.string')
        assert new_token is None

    def test_refresh_expired_token(self, app_context):
        """Test refreshing expired token returns None."""
        # Create immediately expiring token
        token = generate_token(user_id=1, expiration_hours=0)
        time.sleep(0.1)
        new_token = refresh_token(token)
        assert new_token is None


class TestTokenSecurity:
    """Tests for token security properties."""

    def test_tokens_are_signed(self, app_context):
        """Test that tokens have signatures."""
        token = generate_token(user_id=1)
        parts = token.split('.')
        # JWT has 3 parts: header, payload, signature
        assert len(parts) == 3
        assert len(parts[2]) > 0  # Signature present

    def test_different_secret_fails_verification(self, app):
        """Test that token from different secret fails."""
        with app.app_context():
            token = generate_token(user_id=1)

        # Try to decode with different secret
        try:
            payload = jwt.decode(token, 'different-secret', algorithms=['HS256'])
            # Should not reach here
            assert False, "Should have raised exception"
        except jwt.InvalidSignatureError:
            pass  # Expected

    def test_token_algorithm_hs256(self, app_context):
        """Test that tokens use HS256 algorithm."""
        token = generate_token(user_id=1)
        # Decode header (base64 without verification)
        import base64
        import json
        header_b64 = token.split('.')[0]
        # Add padding if needed
        header_b64 += '=' * (4 - len(header_b64) % 4)
        header = json.loads(base64.urlsafe_b64decode(header_b64))
        assert header['alg'] == 'HS256'


class TestTokenEdgeCases:
    """Tests for edge cases in token handling."""

    def test_token_with_large_user_id(self, app_context):
        """Test token with large user_id."""
        token = generate_token(user_id=999999999)
        assert verify_token(token) == 999999999

    def test_token_with_zero_user_id(self, app_context):
        """Test token with zero user_id."""
        token = generate_token(user_id=0)
        user_id = verify_token(token)
        # 0 is falsy but should still be returned
        assert user_id == 0

    def test_multiple_sequential_tokens(self, app_context):
        """Test generating multiple tokens sequentially."""
        tokens = [generate_token(user_id=i) for i in range(10)]
        # All should be unique
        assert len(tokens) == len(set(tokens))
        # All should be valid
        for i, token in enumerate(tokens):
            assert verify_token(token) == i
