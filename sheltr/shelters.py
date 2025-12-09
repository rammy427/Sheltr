from flask import (Blueprint, g, render_template)
from sheltr.auth import login_required
from sheltr.models import Shelter, Task
bp = Blueprint('shelters', __name__, url_prefix='/shelters')

@bp.route('/')
@login_required
def view():
    # Get all available shelters.
    shelters = Shelter.get_all()
    return render_template('shelters.html', shelters=shelters)

@bp.route('/<int:shelter_id>')
@login_required
def shelter(shelter_id):
    # Get information for selected shelter.
    shelter = Shelter.get_by_id(shelter_id)
    # Get all tasks for this shelter.
    tasks = shelter.get_tasks()
    return render_template('shelter.html', shelter=shelter, tasks=tasks)