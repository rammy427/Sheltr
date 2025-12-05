#!/bin/bash
set -e

# Sheltr Docker Entrypoint Script
# Handles database initialization, seeding, and application startup

echo "Starting Sheltr application..."

DB_PATH="/app/instance/sheltr.sqlite"

if [ ! -f "$DB_PATH" ]; then
    echo "Database not found. Initializing database..."
    flask init-db
    echo "Database initialized."

    echo "Seeding database with test data..."
    python -c "
import sys
sys.path.insert(0, '/app')

from sheltr import create_app
from sheltr.db import get_db
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    db = get_db()

    # Insert test volunteers
    volunteers = [
        ('volunteer1', 'volunteer1@test.com', generate_password_hash('Volunteer1!'), 'Alice Johnson', '5551234567', 'Miami', 'volunteer'),
        ('volunteer2', 'volunteer2@test.com', generate_password_hash('Volunteer2!'), 'Bob Smith', '5552345678', 'Tampa', 'volunteer'),
        ('volunteer3', 'volunteer3@test.com', generate_password_hash('Volunteer3!'), 'Carol Davis', '5553456789', 'Orlando', 'volunteer'),
    ]
    for v in volunteers:
        db.execute('INSERT INTO user (username, email, password, name, phone, city, role) VALUES (?, ?, ?, ?, ?, ?, ?)', v)

    # Insert test managers
    managers = [
        ('manager1', 'manager1@test.com', generate_password_hash('Manager1!'), 'David Wilson', '5554567890', 'Jacksonville', 'manager'),
        ('manager2', 'manager2@test.com', generate_password_hash('Manager2!'), 'Emma Brown', '5555678901', 'Tallahassee', 'manager'),
    ]
    for m in managers:
        db.execute('INSERT INTO user (username, email, password, name, phone, city, role) VALUES (?, ?, ?, ?, ?, ?, ?)', m)

    # Insert test shelters
    shelters = [
        ('Miami Convention Center', 'Miami, FL', 'Large shelter with 500 bed capacity.'),
        ('Tampa Bay Arena', 'Tampa, FL', 'Medium shelter with 300 bed capacity.'),
        ('Orlando Sports Complex', 'Orlando, FL', 'Large shelter with 400 bed capacity.'),
        ('Jacksonville Community Center', 'Jacksonville, FL', 'Small shelter with 150 bed capacity.'),
        ('Tallahassee High School Gym', 'Tallahassee, FL', 'Medium shelter with 200 bed capacity.'),
    ]
    for s in shelters:
        db.execute('INSERT INTO shelters (shelter_name, shelter_location, shelter_description) VALUES (?, ?, ?)', s)

    # Insert test emergencies
    emergencies = [
        ('Hurricane Maria', 1, '2024-09-15', 'https://example.com/hurricane.jpg', 'Category 4 hurricane approaching Florida.'),
        ('Tropical Storm Alex', 0, '2024-06-10', 'https://example.com/storm.jpg', 'Tropical storm that caused flooding. Now resolved.'),
        ('Wildfire Season 2024', 1, '2024-03-01', 'https://example.com/wildfire.jpg', 'Ongoing wildfire threats in rural areas.'),
    ]
    for e in emergencies:
        db.execute('INSERT INTO emergencies (emergency_name, emergency_status, emergency_date, image_url, emergency_description) VALUES (?, ?, ?, ?, ?)', e)

    # Link shelters to emergencies
    links = [
        ('2024-09-15', 1, 1, '2024-09-25'),
        ('2024-09-15', 2, 1, '2024-09-25'),
        ('2024-09-16', 3, 1, '2024-09-25'),
        ('2024-06-10', 4, 2, '2024-06-15'),
        ('2024-03-01', 5, 3, '2024-05-01'),
    ]
    for link in links:
        db.execute('INSERT INTO shelters_of_emergency (starting_date, shelter_id, emergency_id, end_date) VALUES (?, ?, ?, ?)', link)

    # Insert additional tasks
    tasks = [
        ('Set up cots', 'Arrange 100 cots in the main hall.', 'pending'),
        ('Stock water supplies', 'Ensure 50 cases of bottled water.', 'pending'),
        ('Coordinate food delivery', 'Contact restaurants for donations.', 'in_progress'),
        ('Medical station setup', 'Set up first aid station.', 'pending'),
        ('Register evacuees', 'Process incoming evacuees.', 'in_progress'),
        ('Pet care area', 'Establish pet area with supplies.', 'pending'),
        ('Communication center', 'Set up phones and charging stations.', 'finished'),
    ]
    for t in tasks:
        db.execute('INSERT INTO task (task_name, description, status) VALUES (?, ?, ?)', t)

    # Assign tasks to volunteers
    assignments = [(1, 4), (1, 5), (2, 6), (2, 7), (3, 8), (3, 9), (1, 10)]
    for a in assignments:
        db.execute('INSERT INTO user_task (user_id, task_id) VALUES (?, ?)', a)

    db.commit()
    print('Database seeded successfully!')
"
    echo "Test data inserted."
else
    echo "Database already exists at $DB_PATH"
fi

echo "Starting application server..."
exec "$@"
