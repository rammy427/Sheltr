from flask import (Blueprint, render_template)
from sheltr.auth import login_required
bp = Blueprint('donations', __name__, url_prefix='/donations')

@bp.route('/')
@login_required
def view():
    return render_template('donations.html')