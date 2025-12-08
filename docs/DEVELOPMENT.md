# Development Guide

## Prerequisites

- Python 3.12+
- Docker & Docker Compose (recommended)
- Git

## Setup Options

### Option 1: Docker (Recommended)

The easiest way to get started:

```bash
# Clone and enter directory
cd Sheltr

# Use the launcher script
python ignition.py

# Or use Docker directly
cd docker
docker compose --profile dev up sheltr-dev
```

The development server runs at `http://localhost:5001` with hot reload enabled.

### Option 2: Local Python Environment

```bash
# Create virtual environment
python -m venv .venv

# Activate (macOS/Linux)
source .venv/bin/activate

# Activate (Windows)
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Initialize database
flask --app sheltr init-db

# Run development server
flask --app sheltr run --debug --port 5001
```

---

## Project Layout

```
Sheltr/
├── sheltr/                 # Application package
│   ├── __init__.py         # App factory (create_app)
│   ├── db.py               # Database utilities
│   ├── schema.sql          # Database schema
│   ├── auth.py             # Auth blueprint
│   ├── jwt_utils.py        # JWT utilities
│   ├── tasks.py            # Tasks blueprint
│   ├── profile.py          # Profile blueprint
│   ├── emergency.py        # Emergency blueprint
│   ├── donations.py        # Donations blueprint
│   ├── disasters.py        # Disasters blueprint
│   ├── models/             # Data models
│   ├── templates/          # Jinja2 templates
│   └── static/             # CSS, JS, images
├── docker/                 # Docker configuration
├── docs/                   # Documentation
├── instance/               # Instance folder (database)
├── ignition.py             # Development launcher
└── requirements.txt        # Python dependencies
```

---

## Development Workflow

### Running the Server

```bash
# With hot reload (recommended for development)
flask --app sheltr run --debug --port 5001

# Production mode (Gunicorn)
gunicorn -w 2 -b 0.0.0.0:5000 'sheltr:create_app()'
```

### Database Operations

```bash
# Initialize/reset database
flask --app sheltr init-db

# Access SQLite directly
sqlite3 instance/sheltr.sqlite

# Common queries
.tables                          # List tables
.schema user                     # Show table schema
SELECT * FROM user;              # View all users
```

### Adding Test Data

The database is seeded with test data on initialization. To add more:

```python
# In Python/Flask shell
flask --app sheltr shell

>>> from sheltr.db import get_db
>>> db = get_db()
>>> db.execute("""
...     INSERT INTO user (username, email, password, name, role)
...     VALUES (?, ?, ?, ?, ?)
... """, ('testuser', 'test@example.com', 'hashed_pw', 'Test', 'volunteer'))
>>> db.commit()
```

---

## Adding New Features

### Creating a New Blueprint

1. Create the blueprint file:

```python
# sheltr/new_feature.py
from flask import Blueprint, render_template, g
from sheltr.auth import login_required

bp = Blueprint('new_feature', __name__, url_prefix='/new-feature')

@bp.route('/')
@login_required
def index():
    return render_template('new_feature/index.html')
```

2. Register in app factory (`sheltr/__init__.py`):

```python
from . import new_feature
app.register_blueprint(new_feature.bp)
```

3. Create template (`sheltr/templates/new_feature/index.html`):

```html
{% extends 'base.html' %}
{% block content %}
<h1>New Feature</h1>
{% endblock %}
```

### Creating a New Model

1. Create the model file:

```python
# sheltr/models/new_model.py
from sheltr.db import get_db

class NewModel:
    def __init__(self, id, name):
        self.id = id
        self.name = name

    @classmethod
    def get_by_id(cls, model_id):
        db = get_db()
        row = db.execute(
            "SELECT * FROM new_table WHERE id = ?",
            (model_id,)
        ).fetchone()
        if row:
            return cls(row['id'], row['name'])
        return None

    @classmethod
    def create(cls, name):
        db = get_db()
        cursor = db.execute(
            "INSERT INTO new_table (name) VALUES (?)",
            (name,)
        )
        db.commit()
        return cls(cursor.lastrowid, name)
```

2. Add table to schema (`sheltr/schema.sql`):

```sql
CREATE TABLE new_table (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

3. Export from models (`sheltr/models/__init__.py`):

```python
from .new_model import NewModel
```

### Adding a Protected Route

Use the provided decorators:

```python
from sheltr.auth import login_required, manager_required

@bp.route('/user-only')
@login_required
def user_route():
    # g.user is available here
    return f"Hello, {g.user.name}"

@bp.route('/manager-only')
@manager_required
def manager_route():
    # Only managers can access
    return "Manager dashboard"
```

---

## Code Style

### Python

- Follow PEP 8
- Use type hints where practical
- Docstrings for public functions

```python
def get_user_by_id(user_id: int) -> User | None:
    """Retrieve a user by their ID.

    Args:
        user_id: The user's primary key

    Returns:
        User object if found, None otherwise
    """
    ...
```

### Templates

- Extend `base.html` for consistent layout
- Use Bootstrap 5 classes
- Keep logic minimal in templates

```html
{% extends 'base.html' %}
{% block title %}Page Title{% endblock %}
{% block content %}
<div class="container">
    <!-- Content here -->
</div>
{% endblock %}
```

### CSS

- Custom styles go in `sheltr/static/style.css`
- Use CSS variables for colors:

```css
:root {
    --color-teal: #18BEBC;
    --color-persimmon: #EF6C57;
    --color-jungle: #3A5045;
    --color-sand: #F2E5B1;
    --color-charcoal: #404040;
}
```

---

## Testing

### Test Suite Overview

The project includes a comprehensive test suite with **309 tests** achieving **100% code coverage**.

```
tests/
├── conftest.py                    # Shared fixtures and test helpers
├── test_auth.py                   # Authentication blueprint (40 tests)
├── test_db.py                     # Database operations (23 tests)
├── test_disasters.py              # Disasters blueprint (3 tests)
├── test_donations.py              # Donations blueprint (3 tests)
├── test_emergency_routes.py       # Emergency routes (18 tests)
├── test_factory.py                # App factory (10 tests)
├── test_jwt_utils.py              # JWT utilities (29 tests)
├── test_profile.py                # Profile blueprint (25 tests)
├── test_tasks.py                  # Tasks blueprint (17 tests)
└── test_models/
    ├── test_user.py               # User model (59 tests)
    ├── test_volunteer.py          # Volunteer model (11 tests)
    ├── test_manager.py            # Manager model (10 tests)
    ├── test_task.py               # Task model (22 tests)
    └── test_emergency.py          # Emergency model (29 tests)
```

### Running Tests

#### Local Environment

```bash
# Install test dependencies (already included in requirements.txt)
pip install pytest pytest-cov

# Run all tests
pytest tests/

# Run with verbose output
pytest tests/ -v

# Run with coverage report
pytest tests/ --cov=sheltr --cov-report=term-missing

# Run specific test file
pytest tests/test_auth.py -v

# Run tests matching a pattern
pytest tests/ -k "password" -v

# Run only model tests
pytest tests/test_models/ -v

# Stop on first failure
pytest tests/ -x
```

#### Docker Environment

Run tests inside a Docker container (no local Python setup required):

```bash
cd docker
docker compose --profile test run --rm sheltr-test
```

This runs the full test suite with coverage reporting inside an isolated container.

### Test Categories

#### Unit Tests
Test individual functions and model methods in isolation:
- Model validation (password, email, phone, name, city)
- CRUD operations (create, read, update, delete)
- Password hashing and verification
- JWT token generation and validation

#### Integration Tests
Test complete request/response cycles:
- Authentication flow (register, login, logout)
- Profile management (view, edit, password change)
- Task management (view, filter, status update)
- Authorization decorators (`@login_required`, `@manager_required`)

#### Database Tests
Test schema and data integrity:
- Table creation and constraints
- Foreign key relationships
- Timestamp handling
- CLI commands (`flask init-db`)

### Coverage Report

| Module | Coverage | Description |
|--------|----------|-------------|
| `__init__.py` | 100% | App factory |
| `auth.py` | 100% | Authentication routes |
| `db.py` | 100% | Database connection management |
| `disasters.py` | 100% | Disasters routes |
| `donations.py` | 100% | Donations routes |
| `emergency.py` | 100% | Emergency routes |
| `jwt_utils.py` | 100% | JWT utilities |
| `profile.py` | 100% | Profile routes |
| `tasks.py` | 100% | Task routes |
| `models/emergency.py` | 100% | Emergency model |
| `models/manager.py` | 100% | Manager model |
| `models/task.py` | 100% | Task model |
| `models/user.py` | 100% | User model |
| `models/volunteer.py` | 100% | Volunteer model |
| **Overall** | **100%** | |

### Writing New Tests

#### Test File Structure

```python
"""
Tests for [feature].
"""

import pytest
from sheltr.models import User


class TestFeatureName:
    """Tests for feature group."""

    def test_specific_behavior(self, app_context, db):
        """Test that specific behavior works correctly."""
        # Arrange
        # ... setup code ...

        # Act
        result = some_function()

        # Assert
        assert result == expected_value

    def test_edge_case(self, app_context):
        """Test edge case handling."""
        # ...
```

#### Using Fixtures

The test suite provides several fixtures in `conftest.py`:

```python
# Application and client
def test_with_app(app):
    """Access Flask app instance."""
    assert app.config['TESTING'] is True

def test_with_client(client):
    """Make HTTP requests."""
    response = client.get('/auth/login')
    assert response.status_code == 200

# Database access
def test_with_db(app_context, db):
    """Direct database access within app context."""
    db.execute("INSERT INTO task ...")
    db.commit()

# Pre-created users
def test_with_user(created_user):
    """Use pre-created test user."""
    assert created_user.username == 'testuser'

def test_with_manager(created_manager):
    """Use pre-created test manager."""
    assert created_manager.is_manager() is True

# Authenticated clients
def test_authenticated(authenticated_client):
    """Client logged in as volunteer."""
    response = authenticated_client.get('/profile/')
    assert response.status_code == 200

def test_manager_auth(authenticated_manager_client):
    """Client logged in as manager."""
    response = authenticated_manager_client.get('/profile/')
    assert response.status_code == 200

# Sample data
def test_with_task(sample_task):
    """Use pre-created task dict."""
    assert sample_task['task_name'] == 'Test Task'

def test_with_emergency(sample_emergency):
    """Use pre-created emergency dict."""
    assert sample_emergency['emergency_name'] == 'Test Emergency'

# Auth helper
def test_with_auth_helper(auth):
    """Use authentication helper."""
    auth.login(username='testuser', password='TestPass123!')
    auth.logout()
    auth.register(username='newuser', ...)
```

#### Testing Models

```python
class TestUserValidation:
    """Test User model validation."""

    def test_valid_password(self):
        valid, error = User.validate_password('TestPass123!')
        assert valid is True
        assert error is None

    def test_invalid_password_too_short(self):
        valid, error = User.validate_password('Short1!')
        assert valid is False
        assert 'at least 8 characters' in error
```

#### Testing Routes

```python
class TestLoginRoute:
    """Test login endpoint."""

    def test_login_success(self, client, created_user):
        response = client.post('/auth/login', data={
            'username': 'testuser',
            'password': 'TestPass123!'
        }, follow_redirects=True)
        assert response.status_code == 200

    def test_login_wrong_password(self, client, created_user):
        response = client.post('/auth/login', data={
            'username': 'testuser',
            'password': 'WrongPassword!'
        }, follow_redirects=True)
        assert b'Incorrect' in response.data
```

#### Testing JSON APIs

```python
def test_update_task_status(self, authenticated_client, sample_task):
    response = authenticated_client.post('/tasks/update_status',
        data=json.dumps({
            'id': sample_task['task_id'],
            'status': 'in_progress'
        }),
        content_type='application/json'
    )
    data = response.get_json()
    assert data['success'] is True
```

### Manual Testing

Test credentials are pre-configured:

| Username | Password | Role |
|----------|----------|------|
| volunteer1 | Volunteer1! | volunteer |
| volunteer2 | Volunteer2! | volunteer |
| manager1 | Manager1! | manager |

### Continuous Integration

For CI/CD pipelines, use:

```yaml
# Example GitHub Actions workflow
- name: Run tests
  run: |
    pip install -r requirements.txt
    pytest tests/ --cov=sheltr --cov-report=xml

- name: Upload coverage
  uses: codecov/codecov-action@v3
```

---

## Common Tasks

### Reset Database

```bash
# Docker
docker compose down -v
docker compose up -d

# Local
rm instance/sheltr.sqlite
flask --app sheltr init-db
```

### View Logs

```bash
# Docker
docker compose logs -f sheltr-dev

# Local
# Logs appear in terminal
```

### Access Container Shell

```bash
docker compose exec sheltr-dev /bin/bash
```

### Check Application Health

```bash
curl http://localhost:5001/
# Should redirect to login or show dashboard
```

---

## Troubleshooting

### "No such table" Error

Database not initialized:
```bash
flask --app sheltr init-db
```

### Port Already in Use

```bash
# Find process using port
lsof -i :5001

# Kill it
kill -9 <PID>

# Or use different port
flask --app sheltr run --port 5002
```

### Docker Build Issues

```bash
# Clean rebuild
docker compose build --no-cache
docker compose up -d
```

### Import Errors

Ensure virtual environment is activated:
```bash
source .venv/bin/activate
which python  # Should show .venv path
```

---

## Contributing

1. Create a feature branch: `git checkout -b feature/my-feature`
2. Make changes with clear commits
3. Test thoroughly
4. Submit pull request

### Commit Message Format

```
type: Short description

Longer explanation if needed.

Types: feat, fix, docs, style, refactor, test, chore
```

Examples:
```
feat: Add password reset functionality
fix: Correct task status validation
docs: Update API documentation
```
