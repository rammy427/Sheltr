from flask import (Blueprint, render_template)
from sheltr.auth import login_required
from sheltr.models import Volunteer
bp = Blueprint('donations', __name__, url_prefix='/donations')

@bp.route('/')
@login_required
def view():
    volunteer = Volunteer.get_by_username('admin')
    print(volunteer.get_tasks())
    return render_template('donations.html')