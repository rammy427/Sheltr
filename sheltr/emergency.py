from flask import (Blueprint, render_template, g)
from sheltr.models import Emergency
from sheltr.auth import login_required
from sheltr.db import get_db

bp = Blueprint('emergency', __name__, url_prefix = '/emergency')

@bp.route('/')
@login_required

def view():
    """ View of all the emergencies saved in the database. """
    
    # Dummy test to check that the values are being inserted to the database
    Emergency.new_emergency(name = "Fire", status = True, date = "2020-10-10", img_url = None, description = None)

    # Access the database
    db = get_db()

    list_emergencies = db.execute('SELECT * FROM emergencies').fetchall()
    return render_template('emergency.html', emergency = list_emergencies)