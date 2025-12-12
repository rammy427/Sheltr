import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, make_response
)
from sheltr.models import User
from sheltr.models.shelter import Shelter
from sheltr.jwt_utils import generate_token, verify_token, is_token_expiring_soon, refresh_token

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        name = request.form.get('name', '').strip()
        phone = request.form.get('phone', '').strip()
        city = request.form.get('city', '').strip()
        role = request.form.get('role', 'volunteer')

        # Extract volunteer-specific fields
        availability = request.form.get('availability', '')
        skills = request.form.get('skills', '')
        preferred_shelter_id = request.form.get('preferred_shelter_id', '')
        latitude = request.form.get('latitude', '')
        longitude = request.form.get('longitude', '')

        error = None

        if not username:
            error = 'Username is required.'
        elif password != confirm_password:
            error = 'Passwords must match.'
        else:
            # Use User model to create user (includes all validation)
            user, error = User.create(
                username=username,
                email=email,
                password=password,
                name=name,
                phone=phone if phone else None,
                city=city if city else None,
                role=role,
                availability=availability if availability else None,
                skills=skills if skills else None,
                preferred_shelter_id=preferred_shelter_id if preferred_shelter_id else None,
                latitude=latitude if latitude else None,
                longitude=longitude if longitude else None
            )

            if user:
                flash('Account created! Please log in.', 'success')
                return redirect(url_for("auth.login"))

        if error:
            flash(error, 'error')

    # GET request - fetch shelters for dropdown
    shelters = Shelter.get_all()
    return render_template('auth/register.html', shelters=shelters)

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        error = None

        # Use User model to get user
        user = User.get_by_username(username)

        if user is None:
            error = 'Incorrect username.'
        elif not user.verify_password(password):
            error = 'Incorrect password.'

        if error is None:
            # Generate JWT token
            token = generate_token(user.id)

            # Create response and set JWT in HTTP-only cookie
            response = make_response(redirect(url_for('index')))
            response.set_cookie(
                'auth_token',
                token,
                httponly=True,
                secure=False,  # Set to True in production with HTTPS
                samesite='Strict',
                max_age=24*60*60  # 24 hours in seconds
            )

            # Also keep session for backward compatibility
            session.clear()
            session['user_id'] = user.id

            return response

        if error:
            flash(error, 'error')

    return render_template('auth/login.html')

@bp.before_app_request
def load_logged_in_user():
    # Try to get user_id from JWT token first, then fall back to session
    user_id = None

    # Check for JWT token in cookie
    token = request.cookies.get('auth_token')
    if token:
        user_id = verify_token(token)

    # Fall back to session if no valid JWT
    if user_id is None:
        user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        # Use User model to get user
        g.user = User.get_by_id(user_id)

@bp.route('/logout')
def logout():
    session.clear()

    # Clear JWT token cookie
    response = make_response(redirect(url_for('index')))
    response.set_cookie('auth_token', '', expires=0)

    return response


@bp.route('/refresh', methods=('POST',))
def refresh():
    """Refresh JWT token if it's expiring soon."""
    token = request.cookies.get('auth_token')

    if not token:
        return {'error': 'No token provided'}, 401

    if is_token_expiring_soon(token):
        new_token = refresh_token(token)
        if new_token:
            response = make_response({'message': 'Token refreshed'})
            response.set_cookie(
                'auth_token',
                new_token,
                httponly=True,
                secure=False,  # Set to True in production with HTTPS
                samesite='Strict',
                max_age=24*60*60
            )
            return response

    return {'message': 'Token still valid'}, 200


@bp.route('/forgot', methods=('GET', 'POST'))
def forgot_password():
    if request.method == 'POST':
        identifier = request.form['identifier'].strip()
        if not identifier:
            flash('Please enter the username or email tied to your account.')
        else:
            flash('If an account exists, password reset instructions will arrive shortly.')
            return redirect(url_for('auth.login'))

    return render_template('auth/forgot_password.html')

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        return view(**kwargs)
    return wrapped_view

def manager_required(view):
    """Decorator to require manager role for a view."""
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        if not g.user.is_manager():
            flash('You must be a manager to access this page.', 'error')
            return redirect(url_for('index'))
        return view(**kwargs)
    return wrapped_view
