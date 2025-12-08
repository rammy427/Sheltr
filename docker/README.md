# Sheltr Docker Setup

This folder contains all Docker configuration files for running Sheltr.

## Quick Start

### Production Mode
```bash
cd docker
docker compose up -d
```
The app will be available at `http://localhost:5000`

### Development Mode (with hot reload)
```bash
cd docker
docker compose --profile dev up sheltr-dev
```
The dev server will be available at `http://localhost:5001`

### Running Tests
```bash
cd docker
docker compose --profile test run --rm sheltr-test
```
This runs the full test suite with coverage report inside a Docker container.

## Files Overview

| File | Purpose |
|------|---------|
| `Dockerfile` | Multi-stage build for the Flask application |
| `docker-compose.yml` | Container orchestration with production & dev services |
| `entrypoint.sh` | Handles database initialization on first run |
| `.dockerignore` | Excludes unnecessary files from the Docker build |

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SECRET_KEY` | `change-me-in-production` | Flask secret key for sessions/JWT |
| `FLASK_ENV` | `production` | Set to `development` for debug mode |
| `FLASK_DEBUG` | `0` | Set to `1` to enable Flask debugger |

### Setting a Secure Secret Key

For production, generate a secure secret key:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Then set it:
```bash
export SECRET_KEY="your-generated-key"
docker compose up -d
```

Or create a `.env` file in the `docker/` folder:
```
SECRET_KEY=your-generated-key
```

## Data Persistence

The SQLite database is stored in a Docker volume (`sheltr-data`). Data persists across container restarts.

### Backup Database
```bash
docker cp sheltr-app:/app/instance/sheltr.sqlite ./backup.sqlite
```

### Restore Database
```bash
docker cp ./backup.sqlite sheltr-app:/app/instance/sheltr.sqlite
docker compose restart
```

## Building & Running Manually

### Build the Image
```bash
docker build -t sheltr -f docker/Dockerfile .
```

### Run the Container
```bash
docker run -d \
  --name sheltr \
  -p 5000:5000 \
  -e SECRET_KEY=your-secret-key \
  -v sheltr-data:/app/instance \
  sheltr
```

## Troubleshooting

### Check Logs
```bash
docker compose logs -f sheltr
```

### Access Container Shell
```bash
docker compose exec sheltr /bin/bash
```

### Reset Database
```bash
docker compose down -v
docker compose up -d
```

### Health Check
```bash
docker compose ps
curl http://localhost:5000/
```
