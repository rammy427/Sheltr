from flask import (Blueprint, g, render_template, request, flash, redirect, url_for)
from sheltr.auth import manager_required
from sheltr.models import Shelter, Task, Volunteer, Emergency
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

@bp.route('/shelters/<int:shelter_id>/add', methods=('GET', 'POST'))
@manager_required
def add_task(shelter_id):
    # Get all available volunteers.
    volunteers = Volunteer.get_all()

     # If POST request, or form was submitted, add the new task.
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        volunteer = request.form.get('volunteer', '').strip()

        # Create task using model method.
        success, error = Task.create(name=name, description=description, volunteer_id=volunteer, shelter_id=shelter_id)

        if success:
            flash('Task created successfully!', 'success')
            return redirect(url_for('admin.shelter', shelter_id=shelter_id))
        else:
            flash(error, 'error')

    return render_template('admin/admin-task.html', shelter_id=shelter_id, volunteers=volunteers)

@bp.route('/emergencies')
@manager_required
def emergencies():
    emergencies = Emergency.get_all()
    return render_template('admin/admin-emergencies.html', emergencies=emergencies)

@bp.route('/emergencies/<int:e_id>', methods=('GET', 'POST'))
@manager_required
def manage_emergency(e_id):
    emergency = Emergency.get_one_by_id(e_id)

    # If POST request, or form was submitted, update the emergency.
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        status = request.form.get('status', '').strip()

        # Update emergency using model method.
        success, error = emergency.edit_em(name=name, description=description, status=status)

        if success:
            flash('Emergency updated successfully!', 'success')
            return redirect(url_for('admin.emergencies'))
        else:
            flash(error, 'error')

    assigned_shelters = Emergency.assigned_shelters(e_id)
    shelters = Shelter.get_all()
    return render_template('admin/admin-emergency.html', emergency = emergency, assigned_shelters = assigned_shelters, shelters = shelters)
