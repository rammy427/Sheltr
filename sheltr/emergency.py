from flask import (Blueprint, render_template)
from sheltr.auth import login_required
bp = Blueprint('emergency', __name__, url_prefix = '/emergency')

@bp.route('/')
@login_required

def view():
    return render_template('emergency.html')