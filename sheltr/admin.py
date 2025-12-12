from flask import (Blueprint, g, render_template, request, flash, redirect, url_for)
from sheltr.auth import manager_required
from sheltr.models import Shelter, Task, Volunteer, Emergency
from sheltr.db import get_db
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

@bp.route('/shelters/add', methods=('GET', 'POST'))
@manager_required
def add_emergency():
    # If POST request, or form was submitted, update the emergency.
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        status = request.form.get('status', '').strip()

        # Update emergency using model method.
        success, error = Emergency.new_emergency(name=name, description=description, status=status)

        if success:
            flash('Emergency updated successfully!', 'success')
            return redirect(url_for('admin.emergencies'))
        else:
            flash(error, 'error')

    return render_template('admin/admin-emergency.html')

@bp.route('/reports')
@manager_required
def reports():
    db = get_db()

    # Query emergency statistics
    total_emergencies = db.execute('SELECT COUNT(*) as count FROM emergencies').fetchone()['count']
    active_emergencies = db.execute('SELECT COUNT(*) as count FROM emergencies WHERE emergency_status = 1').fetchone()['count']
    inactive_emergencies = total_emergencies - active_emergencies

    # Query shelter statistics
    total_shelters = db.execute('SELECT COUNT(*) as count FROM shelters').fetchone()['count']

    # Query user statistics
    total_volunteers = db.execute("SELECT COUNT(*) as count FROM user WHERE role = 'volunteer'").fetchone()['count']
    total_managers = db.execute("SELECT COUNT(*) as count FROM user WHERE role = 'manager'").fetchone()['count']

    # Query task statistics
    total_tasks = db.execute('SELECT COUNT(*) as count FROM task').fetchone()['count']
    completed_tasks = db.execute("SELECT COUNT(*) as count FROM task WHERE status = 'completed'").fetchone()['count']
    pending_tasks = db.execute("SELECT COUNT(*) as count FROM task WHERE status = 'pending'").fetchone()['count']
    in_progress_tasks = db.execute("SELECT COUNT(*) as count FROM task WHERE status = 'in_progress'").fetchone()['count']

    # Query donation statistics
    total_donations = db.execute('SELECT COUNT(*) as count FROM donation').fetchone()['count']
    total_donation_amount = db.execute('SELECT COALESCE(SUM(donation_quantity), 0) as total FROM donation').fetchone()['total']

    # Query recent donations with donor username and emergency name
    recent_donations = db.execute('''
        SELECT d.donation_quantity, d.donation_date, u.username, e.emergency_name
        FROM donation d
        JOIN user u ON d.user_id = u.user_id
        JOIN emergencies e ON d.emergency_id = e.emergency_id
        ORDER BY d.donation_date DESC
        LIMIT 5
    ''').fetchall()

    # Query top emergencies by donation amount
    top_emergencies = db.execute('''
        SELECT e.emergency_name, COUNT(d.donation_id) as donation_count,
               COALESCE(SUM(d.donation_quantity), 0) as total_amount
        FROM emergencies e
        LEFT JOIN donation d ON e.emergency_id = d.emergency_id
        GROUP BY e.emergency_id, e.emergency_name
        ORDER BY total_amount DESC
        LIMIT 5
    ''').fetchall()

    return render_template('admin/reports.html',
        total_emergencies=total_emergencies,
        active_emergencies=active_emergencies,
        inactive_emergencies=inactive_emergencies,
        total_shelters=total_shelters,
        total_volunteers=total_volunteers,
        total_managers=total_managers,
        total_tasks=total_tasks,
        completed_tasks=completed_tasks,
        pending_tasks=pending_tasks,
        in_progress_tasks=in_progress_tasks,
        total_donations=total_donations,
        total_donation_amount=total_donation_amount,
        recent_donations=recent_donations,
        top_emergencies=top_emergencies
    )