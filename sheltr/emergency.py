from flask import (Blueprint, render_template, g)
from sheltr.models import Emergency
from sheltr.auth import manager_required
from sheltr.auth import login_required
from sheltr.db import get_db

bp = Blueprint('emergency', __name__, url_prefix = '/emergency')

@bp.route('/')
@login_required

def view():
    """ View of all the emergencies saved in the database. """
    
    list_emergencies = Emergency.get_all()
    return render_template('emergency.html', emergency = list_emergencies)



@bp.route('/<int:e_id>')
@login_required

def specific_emergency(e_id):
    """ Display the specific emergency that was clicked on. """

    emergency = Emergency.get_one_by_id(e_id)
    shelters = Emergency.assigned_shelters(e_id)
    return render_template('single_emergency.html', emergency = emergency, shelters = shelters)