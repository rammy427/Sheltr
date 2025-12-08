from flask import (Blueprint, g, render_template, request)
from sheltr.auth import manager_required
from sheltr.models import Shelter
bp = Blueprint('admin', __name__, url_prefix='/admin')

@bp.route('/')
@manager_required
def view():
    return render_template('admin/admin.html')

@bp.route('/shelters')
@manager_required
def shelters():
    shelters = Shelter.get_all()
    return render_template('admin/admin-shelters.html', shelters=shelters)

@bp.route('/shelters/<int:shelter_id>')
@manager_required
def shelter(shelter_id):
    # Get all information for the shelter selected.
    shelter = Shelter.get_by_id(shelter_id)

    # Get all tasks associated to this shelter.
    tasks = shelter.get_tasks()
    # Filter tasks if specified.
    status = request.args.getlist("status")
    if status:
        tasks = [t for t in tasks if t.status in status]

    return render_template('admin/admin-shelter.html', shelter=shelter, tasks=tasks, status=status)