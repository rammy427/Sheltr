import sqlite3
from datetime import datetime

import click
from flask import current_app, g

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.execute("PRAGMA foreign_keys = ON;")
        g.db.row_factory = sqlite3.Row

    return g.db

def close_db(_e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    from werkzeug.security import generate_password_hash
    db = get_db()
    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))

    volunteers = [
        ("volunteer1", "volunteer1@test.com", generate_password_hash("Volunteer1!"), "Alice Johnson", "5551234567", "Miami", "volunteer"),
        ("volunteer2", "volunteer2@test.com", generate_password_hash("Volunteer2!"), "Bob Smith", "5552345678", "Tampa", "volunteer"),
        ("volunteer3", "volunteer3@test.com", generate_password_hash("Volunteer3!"), "Carol Davis", "5553456789", "Orlando", "volunteer"),
    ]

    for v in volunteers:
        db.execute(
            "INSERT INTO user (username, email, password, name, phone, city, role) VALUES (?, ?, ?, ?, ?, ?, ?)",
            v
        )

    managers = [
        ("manager1", "manager1@test.com", generate_password_hash("Manager1!"), "David Wilson", "5554567890", "Jacksonville", "manager"),
        ("manager2", "manager2@test.com", generate_password_hash("Manager2!"), "Emma Brown", "5555678901", "Tallahassee", "manager"),
    ]

    for m in managers:
        db.execute(
            "INSERT INTO user (username, email, password, name, phone, city, role) VALUES (?, ?, ?, ?, ?, ?, ?)",
            m
        )

    shelters = [
        ("Convention Center", "San Juan,18.452263,-66.092282", "Large shelter with 500 bed capacity. Has backup generators and medical facilities."),
        ("Casita de Bayamón", "Bayamón,18.397952,-66.142013", "Medium shelter with 300 bed capacity. Pet-friendly area available."),
        ("Bomberos", "Ponce,17.999078,-66.608709", "Large shelter with 400 bed capacity. Wheelchair accessible throughout."),
        ("Centro", "Luquillo,18.370658,-65.7206", "Small shelter with 150 bed capacity. Near major hospital."),
        ("Escuela Los Palos", "Lares,18.294432,-66.876314", "Medium shelter with 200 bed capacity. Kitchen facilities on-site."),
    ]

    for s in shelters:
        db.execute(
            "INSERT INTO shelters (shelter_name, shelter_location, shelter_description) VALUES (?, ?, ?)",
            s
        )

    emergencies = [
        ("Hurricane Maria", 1, "2024-09-15", "https://images.pexels.com/photos/1446076/pexels-photo-1446076.jpeg?auto=compress&cs=tinysrgb&w=800", "Category 4 hurricane approaching the Florida coast. Mandatory evacuations in coastal areas."),
        ("Tropical Storm Alex", 0, "2024-06-10", "https://images.pexels.com/photos/1739855/pexels-photo-1739855.jpeg?auto=compress&cs=tinysrgb&w=800", "Tropical storm that caused flooding in northern Florida. Now resolved."),
        ("Wildfire Season 2024", 1, "2024-03-01", "https://images.pexels.com/photos/51951/forest-fire-fire-smoke-conservation-51951.jpeg?auto=compress&cs=tinysrgb&w=800", "Ongoing wildfire threats in rural areas. Multiple shelters activated."),
    ]

    for e in emergencies:
        db.execute(
            "INSERT INTO emergencies (emergency_name, emergency_status, emergency_date, image_url, emergency_description) VALUES (?, ?, ?, ?, ?)",
            e
        )

    shelter_emergency_links = [
        ("2024-09-15", 1, 1, "2024-09-25"),
        ("2024-09-15", 2, 1, "2024-09-25"),
        ("2024-09-16", 3, 1, "2024-09-25"),
        ("2024-06-10", 4, 2, "2024-06-15"),
        ("2024-03-01", 5, 3, "2024-05-01"),
    ]

    for link in shelter_emergency_links:
        db.execute(
            "INSERT INTO shelters_of_emergency (starting_date, shelter_id, emergency_id, end_date) VALUES (?, ?, ?, ?)",
            link
        )

    additional_tasks = [
        ("Set up cots", "Arrange 100 cots in the main hall with proper spacing for social distancing.", "pending", 1),
        ("Stock water supplies", "Ensure each shelter station has at least 50 cases of bottled water.", "pending", 2),
        ("Coordinate food delivery", "Contact local restaurants for meal donations. Target: 500 meals/day.", "in_progress", 3),
        ("Medical station setup", "Set up first aid station with basic supplies and AED equipment.", "pending", 4),
        ("Register evacuees", "Process incoming evacuees and assign them to available spaces.", "in_progress", 5),
        ("Pet care area", "Establish designated area for evacuees with pets. Ensure supplies available.", "pending", 1),
        ("Communication center", "Set up phones and charging stations for evacuee use.", "finished", 2),
    ]

    for t in additional_tasks:
        db.execute(
            "INSERT INTO task (task_name, description, status, shelter_id) VALUES (?, ?, ?, ?)",
            t
        )

    task_assignments = [
        (1, 7), (1, 6), (2, 5), (2, 4), (3, 3), (3, 2), (1, 1),
    ]

    for assignment in task_assignments:
        db.execute(
            "INSERT INTO user_task (user_id, task_id) VALUES (?, ?)",
            assignment
        )

    db.commit()
    print("Database seeded successfully!")

@click.command('init-db')
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')

sqlite3.register_converter("timestamp", lambda v: datetime.fromisoformat(v.decode()))

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)