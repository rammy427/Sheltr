from flask import (Blueprint, render_template, g)
from sheltr.models import Emergency
from sheltr.auth import login_required
from sheltr.db import get_db

bp = Blueprint('emergency', __name__, url_prefix = '/emergency')

@bp.route('/')
@login_required

def view():
    """ View of all the emergencies saved in the database. """
    
    # Access the database
    db = get_db()

    list_emergencies = db.execute('SELECT * FROM emergencies').fetchall()
    return render_template('emergency.html', emergency = list_emergencies)

@bp.route('/<int:emergency_id>')
@login_required

def specific_emergency(emergency_id):
    """ Display the specific emergency that was clicked on. """
    print("hola")
