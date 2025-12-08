from flask import (Blueprint, g, render_template, request, flash, redirect, url_for)
from sheltr.auth import manager_required
from sheltr.models import Shelter, Task, Volunteer
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

@bp.route('/shelters/<int:shelter_id>/<int:task_id>', methods=('GET', 'POST'))
@manager_required
def task(shelter_id, task_id):
    # Get all information for the task selected.
    task = Task.get_by_id(task_id)
    # Get all available volunteers.
    volunteers = Volunteer.get_all()

    # If POST request, or form was submitted, update the task.
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        volunteer = request.form.get('volunteer', '').strip()

        # Update task using model method.
        success, error = task.update(name=name, description=description, volunteer_id=volunteer)
        if success:
            flash('Task updated successfully!', 'success')
            return redirect(url_for('admin.shelter', shelter_id=shelter_id))
        else:
            flash(error, 'error')

    return render_template('admin/admin-task.html', shelter_id=shelter_id, task=task, volunteers=volunteers)