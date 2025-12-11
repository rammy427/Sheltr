from flask import (Blueprint, render_template, g, flash)
from sheltr.models import Emergency, Shelter
from sheltr.auth import manager_required
from sheltr.auth import login_required

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

@bp.route('<int:e_id>/<int:s_id>/add', methods=["POST"])
@manager_required

def link_shelter(e_id, s_id):
    """Link a given shelter to the given emergency."""
    emergency = Emergency.get_one_by_id(e_id)
    if not emergency:
        flash('Emergency not found.')
        return 'Emergency not found.', 404
    
    shelter = Shelter.get_by_id(s_id)
    if not shelter:
        flash('Shelter not found.')
        return 'Shelter not found.', 404
    
    success, error = emergency.assign_shelter(s_id)
    if success:
        flash('Shelter has been linked!', 'success')
        return '', 204
    else:
        flash(error, 'danger')
        return error, 500
    
@bp.route('/<int:e_id>/<int:s_id>/remove', methods=["DELETE"])
@manager_required
def remove_shelter(e_id, s_id):
    """Unlink a given shelter from the given emergency."""
    emergency = Emergency.get_one_by_id(e_id)
    if not emergency:
        flash('Emergency not found.')
        return 'Emergency not found.', 404
    
    shelter = Shelter.get_by_id(s_id)
    if not shelter:
        flash('Shelter not found.')
        return 'Shelter not found.', 404
    
    success, error = emergency.remove_shelter(s_id)
    if success:
        flash('Shelter has been removed.', 'success')
        return '', 204
    else:
        flash(error, 'danger')
        return error, 500