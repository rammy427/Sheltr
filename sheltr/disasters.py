from flask import (Blueprint, render_template)
from sheltr.auth import login_required
bp = Blueprint('disasters', __name__, url_prefix='/disasters')

@bp.route('/')
@login_required

def view():
    return render_template('disasters.html')