from flask import (Blueprint, render_template)
from sheltr.auth import login_required
from  sheltr.db import get_db

bp = Blueprint('donations', __name__, url_prefix='/donations')

@bp.route('/')
@login_required
def view():
    db = get_db()

    return render_template('donations.html')

@bp.route('/donate')