"""
JWT utilities for token-based authentication.
Handles token generation, verification, and refresh.
"""

import jwt
from datetime import datetime, timedelta
from flask import current_app


def generate_token(user_id, expiration_hours=24):
    """
    Generate a JWT token for the given user ID.

    Args:
        user_id: The user's ID to encode in the token
        expiration_hours: Hours until token expires (default 24)

    Returns:
        str: The encoded JWT token
    """
    now = datetime.utcnow()
    payload = {
        'user_id': user_id,
        'iat': now,  # Issued at
        'exp': now + timedelta(hours=expiration_hours)  # Expiration
    }

    token = jwt.encode(
        payload,
        current_app.config['SECRET_KEY'],
        algorithm='HS256'
    )

    return token


def decode_token(token):
    """
    Decode and verify a JWT token.

    Args:
        token: The JWT token string to decode

    Returns:
        dict: The decoded payload if valid, None if invalid/expired
    """
    try:
        payload = jwt.decode(
            token,
            current_app.config['SECRET_KEY'],
            algorithms=['HS256']
        )
        return payload
    except jwt.ExpiredSignatureError:
        # Token has expired
        return None
    except jwt.InvalidTokenError:
        # Token is invalid
        return None


def verify_token(token):
    """
    Verify a token and return the user_id if valid.

    Args:
        token: The JWT token string to verify

    Returns:
        int: The user_id if token is valid, None otherwise
    """
    payload = decode_token(token)
    if payload:
        return payload.get('user_id')
    return None


def is_token_expiring_soon(token, hours_threshold=2):
    """
    Check if a token is expiring within the threshold.

    Args:
        token: The JWT token string to check
        hours_threshold: Hours before expiration to consider "soon" (default 2)

    Returns:
        bool: True if token expires within threshold, False otherwise
    """
    payload = decode_token(token)
    if not payload:
        return False

    exp_timestamp = payload.get('exp')
    if not exp_timestamp:
        return False

    exp_datetime = datetime.fromtimestamp(exp_timestamp)
    time_until_expiry = exp_datetime - datetime.utcnow()

    return time_until_expiry < timedelta(hours=hours_threshold)


def refresh_token(old_token):
    """
    Generate a new token from an existing valid token.

    Args:
        old_token: The existing JWT token

    Returns:
        str: New token if old token is valid, None otherwise
    """
    user_id = verify_token(old_token)
    if user_id:
        return generate_token(user_id)
    return None
