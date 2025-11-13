from flask import (Blueprint, render_template)
bp = Blueprint('donations', __name__, url_prefix='/donations')

@bp.route('/')
def view_donations():
    return render_template('donations.html')