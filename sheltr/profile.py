"""
Profile blueprint for user profile management.
Handles profile viewing, editing, and password changes.
"""

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from sheltr.auth import login_required
from sheltr.models import User

bp = Blueprint('profile', __name__, url_prefix='/profile')


@bp.route('/')
@login_required
def view():
    """Display the current user's profile."""
    return render_template('profile/view.html', user=g.user)


@bp.route('/edit', methods=('GET', 'POST'))
@login_required
def edit():
    """Edit the current user's profile."""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        phone = request.form.get('phone', '').strip()
        city = request.form.get('city', '').strip()

        # Update user profile using model method
        success, error = g.user.update(
            name=name,
            phone=phone if phone else None,
            city=city if city else None
        )

        if success:
            flash('Profile updated successfully!', 'success')
            return redirect(url_for('profile.view'))
        else:
            flash(error, 'error')

    return render_template('profile/edit.html', user=g.user)


@bp.route('/password', methods=('GET', 'POST'))
@login_required
def change_password():
    """Change the current user's password."""
    if request.method == 'POST':
        current_password = request.form.get('current_password', '')
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')

        error = None

        if not current_password:
            error = 'Current password is required.'
        elif not new_password:
            error = 'New password is required.'
        elif new_password != confirm_password:
            error = 'New passwords must match.'
        else:
            # Update password using model method
            success, error = g.user.update_password(current_password, new_password)

            if success:
                flash('Password changed successfully!', 'success')
                return redirect(url_for('profile.view'))

        if error:
            flash(error, 'error')

    return render_template('profile/password.html')
