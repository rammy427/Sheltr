from flask import (Blueprint, g, render_template)
from sheltr.auth import manager_required
bp = Blueprint('admin', __name__, url_prefix='/admin')

@bp.route('/')
@manager_required
def view():
    return render_template('admin.html')

@bp.route('/shelters')
@manager_required
def shelters():
    return render_template('admin-shelters.html')