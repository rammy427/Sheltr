from flask import (Blueprint, render_template, g, request, flash, redirect, url_for)
from sheltr.models import Donation
from sheltr.auth import login_required
from  sheltr.db import get_db

bp = Blueprint('donations', __name__, url_prefix='/donations')

@bp.route('/')
@login_required
def view():
    """View the 10 most recent donations"""
    db = get_db()

    donation_list = db.execute('SELECT user.username, emergencies.emergency_name, donation.donation_date, donation.donation_quantity, donation.donation_message  FROM ((donation JOIN user ON donation.user_id = user.user_id) JOIN emergencies ON donation.emergency_id = emergencies.emergency_id) ORDER BY donation.donation_date DESC LIMIT 10').fetchall()

    return render_template('donations/donations.html', donations = donation_list)


@bp.route('/make-donation', methods = ('GET', 'POST'))
@login_required
def make_donation():

    db = get_db()
    emergencies = db.execute("SELECT emergency_id, emergency_name FROM emergencies WHERE emergency_status = 1 ORDER BY emergency_name").fetchall()

    if request.method == 'POST':
        emergency_selection = request.form.get('emergency_id')
        amount = request.form.get('amount')
        provider = request.form.get('provider')
        msg = request.form.get('msg')
        error = None

        if not emergency_selection:
            error = 'Required: Select emergency to donate'
        if not amount:
            error = 'Required: Select an amount to donate'
        if not provider:
            error = 'Required: Select payment service provider'
        else:
             donation, error = Donation.create(
                emergency_id=emergency_selection,
                user_id=g.user.id,
                amount=amount,
                message=msg,
            )
           
        if error:
            flash(error)
        else:
            flash('Thanks for donating!', 'success')
            return redirect(url_for('donations.view'))
           

    return render_template('donations/make-donation.html', emergencies = emergencies)

@bp.route('/user-donation-history.html')
@login_required
def donation_history():
    """View of 50 most recent donations done by the user"""
    user_id = g.user.id

    donation_hist = Donation.user_donation_history(user_id)
    total_donations = Donation.count_by_donations(user_id)
    sum_total = Donation.sum_by_user_donation(user_id)

    return render_template('donations/user-donation-history.html', donations = donation_hist, total_donations = total_donations, sum = sum_total)


    