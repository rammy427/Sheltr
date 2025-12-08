# Sheltr

A disaster relief coordination platform built with Flask for managing volunteers, tasks, emergencies, and shelters.

## Overview

Sheltr helps coordinate disaster relief efforts by connecting volunteers with tasks, tracking emergencies, and managing shelter information. The platform supports two user roles:

- **Volunteers** - View and manage assigned tasks, track progress
- **Managers** - Oversee operations, assign tasks, manage emergencies

## Features

| Feature | Status | Description |
|---------|--------|-------------|
| User Authentication | Complete | Registration, login, JWT-based sessions |
| Task Management | Complete | View, filter, and update task status |
| Profile Management | Complete | Edit profile, change password |
| Emergency Tracking | Complete | View active emergencies and details |
| Donations | Placeholder | UI present, backend pending |
| Disasters | Placeholder | UI present, backend pending |

## Quick Start

### Using the Launcher (Recommended)

```bash
python ignition.py
```

This cross-platform script handles everything: Docker setup, database initialization, and opens your browser automatically.

### Using Docker Directly

```bash
cd docker
docker compose up -d          # Production (port 5000)
docker compose --profile dev up sheltr-dev  # Development (port 5001)
```

### Manual Setup

```bash
python -m venv .venv
source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements.txt
flask --app sheltr init-db
flask --app sheltr run --debug
```

## Test Credentials

| Role | Username | Password | Email |
|------|----------|----------|-------|
| Volunteer | volunteer1 | Volunteer1! | volunteer1@test.com |
| Volunteer | volunteer2 | Volunteer2! | volunteer2@test.com |
| Manager | manager1 | Manager1! | manager1@test.com |

## Project Structure

```
sheltr/
├── __init__.py          # Flask app factory
├── db.py                # Database connection
├── schema.sql           # SQLite schema
├── auth.py              # Authentication routes
├── jwt_utils.py         # JWT token utilities
├── tasks.py             # Task management
├── profile.py           # User profile routes
├── emergency.py         # Emergency routes
├── models/              # Data models
│   ├── user.py          # User model (base)
│   ├── volunteer.py     # Volunteer model
│   ├── manager.py       # Manager model
│   ├── task.py          # Task model
│   └── emergency.py     # Emergency model
├── templates/           # Jinja2 templates
└── static/              # CSS and assets
```

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Flask 3.1, Python 3.12 |
| Database | SQLite 3 |
| Frontend | Bootstrap 5, Jinja2 |
| Auth | JWT (PyJWT), Werkzeug |
| Server | Gunicorn (production) |
| Container | Docker, Docker Compose |
| Testing | pytest, pytest-cov |

## Testing

The project includes a comprehensive test suite with **309 tests** achieving **100% code coverage**.

```bash
# Run all tests
pytest tests/

# Run with coverage report
pytest tests/ --cov=sheltr --cov-report=term-missing

# Run specific test file
pytest tests/test_auth.py -v

# Run tests matching a pattern
pytest tests/ -k "password" -v

# Run tests in Docker (no local setup required)
cd docker && docker compose --profile test run --rm sheltr-test
```

### Test Coverage

| Module | Coverage |
|--------|----------|
| All Modules | 100% |

See [Development Guide](docs/DEVELOPMENT.md) for detailed testing documentation.

## Documentation

- [API Reference](docs/API.md) - Route endpoints and responses
- [Data Models](docs/MODELS.md) - Database schema and model classes
- [Development Guide](docs/DEVELOPMENT.md) - Setup, testing, contributing
- [Docker Setup](docker/README.md) - Container configuration

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Client (Browser)                     │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     Flask Application                       │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────────────┐ │
│  │  Auth   │  │  Tasks  │  │ Profile │  │   Emergency     │ │
│  │Blueprint│  │Blueprint│  │Blueprint│  │   Blueprint     │ │
│  └────┬────┘  └────┬────┘  └────┬────┘  └───────┬─────────┘ │
│       └────────────┴───────────┴────────────────┘           │
│                              │                              │
│                              ▼                              │
│  ┌─────────────────────────────────────────────────────────┐│
│  │                    Model Layer                          ││
│  │   User  │  Volunteer  │  Manager  │  Task  │  Emergency ││
│  └─────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    SQLite Database                          │
│   user │ task │ user_task │ emergencies │ shelters          │
└─────────────────────────────────────────────────────────────┘
```

## Security

- Passwords hashed with PBKDF2 (Werkzeug)
- JWT tokens in HttpOnly cookies
- SQL parameter binding (injection prevention)
- Strong password requirements enforced
- Non-root Docker container user

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SECRET_KEY` | `dev` | Flask secret key (change in production!) |
| `FLASK_ENV` | `production` | Set to `development` for debug mode |
| `FLASK_DEBUG` | `0` | Set to `1` for Flask debugger |

## License

MIT License - See [LICENSE](LICENSE) for details.
