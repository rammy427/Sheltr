from flask import (Blueprint, g, render_template, request)
from sheltr.auth import login_required
from sheltr.models import Volunteer
bp = Blueprint('donations', __name__, url_prefix='/donations')

@bp.route('/')
@login_required
def view():
    # Get all the current tasks assigned to the user.
    tasks = Volunteer.get_by_username(g.user.username).get_tasks()

    # Filter tasks by status if specified.
    status = request.args.getlist("status")
    if status:
        tasks = [t for t in tasks if t.status in status]

    return render_template('donations.html', tasks=tasks, status=status)