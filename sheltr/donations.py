from flask import (Blueprint, g, render_template, request, jsonify)
from sheltr.auth import login_required
from sheltr.models import Volunteer, Task
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

@bp.route('/update_status', methods=['POST'])
@login_required
def update_status():
    data = request.get_json()
    task_id = data.get("id")
    new_status = data.get("status")

    task = Task.get_by_id(task_id)
    if not task:
        return jsonify(success=False, error="Task not found")
    
    task.update_status(new_status)
    return jsonify(success=True)