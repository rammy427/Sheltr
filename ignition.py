#!/usr/bin/env python3
"""
Ignition - Cross-platform launch script for the Sheltr dev server.
Uses Docker by default. Falls back to local venv if Docker is unavailable.

Usage:
    python ignition.py          # Launch with Docker + hot reload (code changes apply instantly)
    python ignition.py --prod   # Launch with Docker in production mode (static container)
    python ignition.py --local  # Launch with local venv (no Docker)
    python ignition.py --stop   # Stop Docker containers
    python ignition.py --reset  # Reset database and restart

=== TEST CREDENTIALS ===

VOLUNTEERS:
  - Username: volunteer1  |  Password: Volunteer1!  |  Email: volunteer1@test.com
  - Username: volunteer2  |  Password: Volunteer2!  |  Email: volunteer2@test.com
  - Username: volunteer3  |  Password: Volunteer3!  |  Email: volunteer3@test.com

MANAGERS:
  - Username: manager1    |  Password: Manager1!    |  Email: manager1@test.com
  - Username: manager2    |  Password: Manager2!    |  Email: manager2@test.com

========================
"""

import os
import sys
import subprocess
import platform
import time
import webbrowser

PORT = 5001
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
DOCKER_DIR = os.path.join(PROJECT_ROOT, "docker")
VENV_PATH = os.path.join(PROJECT_ROOT, "venv")
DB_INITIALIZED_FLAG = os.path.join(PROJECT_ROOT, ".db_initialized")

IS_WINDOWS = platform.system() == "Windows"

if IS_WINDOWS:
    PYTHON_EXECUTABLE = os.path.join(VENV_PATH, "Scripts", "python.exe")
    PIP_EXECUTABLE = os.path.join(VENV_PATH, "Scripts", "pip.exe")
    FLASK_EXECUTABLE = os.path.join(VENV_PATH, "Scripts", "flask.exe")
else:
    PYTHON_EXECUTABLE = os.path.join(VENV_PATH, "bin", "python")
    PIP_EXECUTABLE = os.path.join(VENV_PATH, "bin", "pip")
    FLASK_EXECUTABLE = os.path.join(VENV_PATH, "bin", "flask")


def check_docker():
    """Check if Docker is available and running."""
    try:
        result = subprocess.run(
            ["docker", "info"],
            capture_output=True,
            text=True
        )
        return result.returncode == 0
    except FileNotFoundError:
        return False


def check_docker_compose():
    """Check if docker compose is available."""
    # Try 'docker compose' (v2) first
    try:
        result = subprocess.run(
            ["docker", "compose", "version"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            return "docker compose"
    except FileNotFoundError:
        pass

    # Try 'docker-compose' (v1)
    try:
        result = subprocess.run(
            ["docker-compose", "version"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            return "docker-compose"
    except FileNotFoundError:
        pass

    return None


def docker_stop():
    """Stop Docker containers."""
    compose_cmd = check_docker_compose()
    if not compose_cmd:
        print("Docker Compose not found.")
        return

    print("Stopping Sheltr containers...")
    cmd = compose_cmd.split() + [
        "-f", os.path.join(DOCKER_DIR, "docker-compose.yml"),
        "--profile", "dev",
        "down"
    ]
    subprocess.run(cmd, cwd=PROJECT_ROOT)
    print("Containers stopped.")


def docker_reset():
    """Reset database and restart containers."""
    compose_cmd = check_docker_compose()
    if not compose_cmd:
        print("Docker Compose not found.")
        return

    print("Resetting Sheltr (removing volumes and rebuilding)...")
    cmd = compose_cmd.split() + [
        "-f", os.path.join(DOCKER_DIR, "docker-compose.yml"),
        "--profile", "dev",
        "down", "-v"
    ]
    subprocess.run(cmd, cwd=PROJECT_ROOT)
    print("Volumes removed. Restarting...")
    docker_start()


def image_exists():
    """Check if the Docker image already exists."""
    try:
        result = subprocess.run(
            ["docker", "images", "-q", "sheltr-app"],
            capture_output=True,
            text=True
        )
        return bool(result.stdout.strip())
    except Exception:
        return False


def container_running():
    """Check if any Sheltr container is already running."""
    try:
        # Check for both prod and dev containers
        for container in ["Sheltr", "Sheltr-dev"]:
            result = subprocess.run(
                ["docker", "ps", "-q", "-f", f"name={container}"],
                capture_output=True,
                text=True
            )
            if result.stdout.strip():
                return True
        return False
    except Exception:
        return False


def docker_start(prod_mode=False):
    """Start with Docker. Default is dev mode with hot reload."""
    compose_cmd = check_docker_compose()
    if not compose_cmd:
        print("ERROR: Docker Compose not found.")
        print("Please install Docker Desktop or use --local flag.")
        sys.exit(1)

    # Check if already running
    if container_running():
        print("Sheltr is already running!")
        print(f"Visit http://localhost:{PORT}")
        print("\nCommands:")
        print(f"  python ignition.py --stop   # Stop the server")
        print(f"  python ignition.py --reset  # Reset database")
        print(f"  python ignition.py --logs   # View logs")
        return

    # Only build if image doesn't exist
    needs_build = not image_exists()

    if prod_mode:
        mode_name = "production"
        service = "sheltr"
    else:
        mode_name = "development (hot reload)"
        service = "sheltr-dev"

    if needs_build:
        print(f"First run - building Docker image ({mode_name})...")
        print("This may take a moment...\n")
    else:
        print(f"Starting Sheltr in {mode_name} mode...\n")

    # Build only if needed, use appropriate service
    cmd = compose_cmd.split() + [
        "-f", os.path.join(DOCKER_DIR, "docker-compose.yml"),
        "--profile", "dev" if not prod_mode else "default",
        "up", "-d", service
    ]
    if needs_build:
        cmd.insert(-2, "--build")

    result = subprocess.run(cmd, cwd=PROJECT_ROOT)

    if result.returncode != 0:
        print("\nERROR: Failed to start Docker containers.")
        print("Try running with --local flag instead.")
        sys.exit(1)

    # Wait for container to be healthy
    print("\nWaiting for application to start...")
    time.sleep(3)

    # Open browser automatically
    open_browser()

    # Show container status
    cmd = compose_cmd.split() + ["-f", os.path.join(DOCKER_DIR, "docker-compose.yml"), "ps"]
    subprocess.run(cmd, cwd=PROJECT_ROOT)

    print("\n" + "=" * 50)
    print(f"  Sheltr is running at: http://localhost:{PORT}")
    print("=" * 50)
    print("\nCommands:")
    print(f"  python ignition.py --stop   # Stop the server")
    print(f"  python ignition.py --reset  # Reset database")
    print(f"  python ignition.py --logs   # View logs")
    print()

    # Follow logs
    print("Showing logs (Ctrl+C to exit, server keeps running):\n")
    try:
        cmd = compose_cmd.split() + ["-f", os.path.join(DOCKER_DIR, "docker-compose.yml"), "logs", "-f"]
        subprocess.run(cmd, cwd=PROJECT_ROOT)
    except KeyboardInterrupt:
        print("\n\nServer is still running in the background.")
        print(f"Visit http://localhost:{PORT}")
        print("Run 'python ignition.py --stop' to stop.")


def docker_logs():
    """Show Docker logs."""
    compose_cmd = check_docker_compose()
    if not compose_cmd:
        print("Docker Compose not found.")
        return

    cmd = compose_cmd.split() + ["-f", os.path.join(DOCKER_DIR, "docker-compose.yml"), "logs", "-f"]
    try:
        subprocess.run(cmd, cwd=PROJECT_ROOT)
    except KeyboardInterrupt:
        pass


def open_browser():
    """Open the browser to the app URL."""
    url = f"http://localhost:{PORT}"
    print(f"Opening browser to {url}...")
    webbrowser.open(url)


# ============================================================
# Local (non-Docker) functions below
# ============================================================

def run_command(command, env=None):
    """Run a command and return success status."""
    try:
        subprocess.run(command, check=True, env=env)
        return True
    except subprocess.CalledProcessError:
        return False


def create_venv():
    """Create virtual environment if it doesn't exist."""
    if not os.path.exists(VENV_PATH):
        print("Virtual environment not found. Creating one...")
        subprocess.run([sys.executable, "-m", "venv", VENV_PATH], check=True)
        print(f"Virtual environment created at {VENV_PATH}")
    else:
        print("Virtual environment found.")


def install_dependencies():
    """Install/upgrade dependencies."""
    print("Checking dependencies...")

    if IS_WINDOWS:
        subprocess.run([PYTHON_EXECUTABLE, "-m", "pip", "install", "--quiet", "--upgrade", "pip"], check=True)
        subprocess.run([PYTHON_EXECUTABLE, "-m", "pip", "install", "--quiet", "flask", "bootstrap-flask", "PyJWT", "werkzeug"], check=True)
    else:
        subprocess.run([PIP_EXECUTABLE, "install", "--quiet", "--upgrade", "pip"], check=True)
        subprocess.run([PIP_EXECUTABLE, "install", "--quiet", "flask", "bootstrap-flask", "PyJWT", "werkzeug"], check=True)

    print("Dependencies installed.")


def initialize_database():
    """Initialize database if not already done."""
    if not os.path.exists(DB_INITIALIZED_FLAG):
        print("Initializing database...")
        env = os.environ.copy()
        env["FLASK_APP"] = "sheltr"
        subprocess.run([FLASK_EXECUTABLE, "init-db"], check=True, env=env, cwd=PROJECT_ROOT)

        print("Seeding database with test data...")
        subprocess.run([PYTHON_EXECUTABLE, "-c", get_seed_script()], env=env, cwd=PROJECT_ROOT, check=True)
        print("Test data inserted.")

        with open(DB_INITIALIZED_FLAG, "w") as f:
            f.write("")
        print("Database initialized.")
    else:
        print("Database already initialized.")


def get_seed_script():
    """Return Python script to seed database with test data."""
    return '''
import sys
sys.path.insert(0, ".")

from sheltr import create_app
from sheltr.db import get_db
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    db = get_db()

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
        ("Hurricane Maria", 1, "2024-09-15", "https://example.com/hurricane.jpg", "Category 4 hurricane approaching the Florida coast. Mandatory evacuations in coastal areas."),
        ("Tropical Storm Alex", 0, "2024-06-10", "https://example.com/storm.jpg", "Tropical storm that caused flooding in northern Florida. Now resolved."),
        ("Wildfire Season 2024", 1, "2024-03-01", "https://example.com/wildfire.jpg", "Ongoing wildfire threats in rural areas. Multiple shelters activated."),
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
'''


def kill_process_on_port():
    """Attempt to kill any process using the target port."""
    print(f"Checking for processes on port {PORT}...")
    try:
        if IS_WINDOWS:
            result = subprocess.run(
                ["netstat", "-ano", "-p", "TCP"],
                capture_output=True,
                text=True
            )
            for line in result.stdout.splitlines():
                if f":{PORT}" in line and "LISTENING" in line:
                    parts = line.split()
                    pid = parts[-1]
                    print(f"Stopping process {pid} on port {PORT}...")
                    subprocess.run(["taskkill", "/F", "/PID", pid], capture_output=True)
        else:
            result = subprocess.run(
                ["lsof", "-ti", f"tcp:{PORT}"],
                capture_output=True,
                text=True
            )
            if result.stdout.strip():
                pids = result.stdout.strip().split("\n")
                for pid in pids:
                    print(f"Stopping process {pid} on port {PORT}...")
                    subprocess.run(["kill", pid], capture_output=True)
    except Exception:
        pass
    print(f"Port {PORT} is ready.")


def start_server():
    """Start the Flask development server."""
    print(f"Starting Sheltr on port {PORT}...")
    print("Press Ctrl+C to stop the server.\n")
    env = os.environ.copy()
    env["FLASK_APP"] = "sheltr"

    # Open browser after a short delay (in background)
    import threading
    def delayed_open():
        time.sleep(2)
        open_browser()
    threading.Thread(target=delayed_open, daemon=True).start()

    try:
        subprocess.run([FLASK_EXECUTABLE, "run", "--port", str(PORT)], env=env, cwd=PROJECT_ROOT)
    except KeyboardInterrupt:
        print("\nServer stopped.")


def local_start():
    """Run without Docker (original behavior)."""
    create_venv()
    install_dependencies()
    initialize_database()
    kill_process_on_port()
    start_server()


def main():
    print("=" * 50)
    print("  SHELTR - Cross-Platform Ignition Script")
    print(f"  OS: {platform.system()}")
    print("=" * 50)
    print()

    # Parse arguments
    args = sys.argv[1:]

    if "--help" in args or "-h" in args:
        print(__doc__)
        sys.exit(0)

    if "--stop" in args:
        docker_stop()
        sys.exit(0)

    if "--reset" in args:
        docker_reset()
        sys.exit(0)

    if "--logs" in args:
        docker_logs()
        sys.exit(0)

    if "--local" in args:
        print("Running in LOCAL mode (no Docker)\n")
        local_start()
        sys.exit(0)

    prod_mode = "--prod" in args

    # Default: try Docker first
    if check_docker():
        if prod_mode:
            print("Docker detected. Using production mode (static container).")
        else:
            print("Docker detected. Using dev mode (hot reload enabled).")
        print("(Use --local flag to run without Docker)\n")
        docker_start(prod_mode=prod_mode)
    else:
        print("Docker not available. Falling back to local mode.\n")
        local_start()


if __name__ == "__main__":
    main()
