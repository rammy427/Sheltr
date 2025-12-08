from flask import (Blueprint, render_template, request, flash, redirect, url_for)
from sheltr.models import Donation
from sheltr.auth import login_required
from  sheltr.db import get_db

bp = Blueprint('donations', __name__, url_prefix='/donations')

@bp.route('/')
@login_required
def view():
    """View the 10 most recent donations"""
    db = get_db()

    donation_list = db.execute('SELECT  FROM donation ORDER BY donation_date DESC LIMIT 10').fetchall()

    return render_template('donations/donations.html', donations = donation_list)


"""

@bp.route('/make-donation', methods = ('GET', 'POST'))
@login_required
def make_donation():
    if request.method == 'POST':
        emergency_selection = request.form.get['emergency_id']
        amount = request.form.get['amount']
        provider = request.form.get['provider']
        msg = request.form.get['msg']
        error = None

        if not emergency_selection:
            error = 'Required: Select emergency to donate'
        if not amount:
            error = 'Required: Select an amount to donate'
        if not provider:
            error = 'Required: Select payment service provider'
        
        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute('INSERT INTO donation (emergency_id, user_id, donation_quantity, donation_message) VALUES(?, ?, ?, ?)', (emergency_selection, g.user['id'], amount, msg))

            db.commit()
            return(redirect(url_for('donations.view')))
        
    return render_template('donations/make-donation.html')


"""


    