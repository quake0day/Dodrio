# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Flask-based personal academic website (Professor Si Chen's profile) with Google Scholar integration for tracking and displaying publications with citation counts. Uses SQLite for storage, Docker for deployment, and Nginx as a reverse proxy in production.

## Commands

### Development

```bash
# Docker (preferred)
make build              # Build Docker containers
make dev                # Run with live output (port 5001)
make run                # Run in background (port 5001)
make stop               # Stop containers
make logs               # View container logs
make shell              # Access container shell

# Native Python
python main.py          # Runs on port 5001
```

### Production

```bash
make prod               # Run with Nginx reverse proxy (ports 80/443)
# Or directly:
docker compose -f docker-compose.prod.yml up -d
```

### Database

```bash
make init-db            # Initialize SQLite database from schema
make backup-db          # Backup database to backups/ directory
# Database file: db/information_.db
# Schema: db/schema.sql
```

### Citation Updates

```bash
make update-citations                   # Update citation counts (in Docker)
python update_citations.py              # Python 3 version (title-based)
python FlaskApp/citation_update.py      # Legacy Python 2 version (cluster-based)
```

### CI/CD

Push to `main` triggers GitHub Actions (`.github/workflows/deploy.yml`) which SSHs to the server and redeploys via Docker Compose. No automated tests in the pipeline.

## Architecture

### Request Flow

```
Client → Nginx (:443 SSL) → Gunicorn (:5000, 4 workers) → Flask app → SQLite
```

### Entry Points

- **`main.py`** (root) — Primary Flask app. Single `/` route queries all publications from SQLite, renders `templates/index.html`. Also serves `/health` endpoint.
- **`FlaskApp/main.py`** — Older copy of the same app (legacy structure).

### Database

Single `entries` table in SQLite (`db/information_.db`). Key columns: `id`, `type`, `title`, `author`, `confname`, `urlpaper`, `urlslides`, `cite` (citation count), `year`, `cluster` (Google Scholar cluster ID), `video`.

Database connections use Flask's `g` object pattern (`before_request`/`teardown_request`). No ORM — raw SQL queries.

### Google Scholar Integration

- **`scholar.py`** (1310 lines) — Google Scholar API wrapper with `ScholarQuery`, `SearchScholarQuery`, `ClusterScholarQuery` classes.
- **`update_citations.py`** — Python 3 citation updater using title-based search.
- **`FlaskApp/citation_update.py`** — Legacy Python 2 updater using cluster IDs, randomly samples 8 publications per run to avoid rate limiting.
- **Cron automation**: `sh FlaskApp/run_update.sh` → logs to `citationUpdate.log`.

### Data Import Scripts

- **`update_db_from_cv.py`** — Parses LaTeX CV file and imports publications into the database.
- **`add_book_chapters.py`** — Adds book chapter entries.
- **`restore_official_urls.py`** / **`restore_pdf_links.py`** — URL restoration utilities.

### Frontend

Jinja2 templates with Pure CSS 3.0.0 framework. No JavaScript build process. Static assets served from `static/` (CSS, images, paper PDFs, presentation slides).

### Docker Setup

- **`Dockerfile`** — Python 3.12-slim base, Gunicorn WSGI server.
- **`docker-compose.yml`** — Development: Flask on port 5001, SQLite volume mount, health checks.
- **`docker-compose.prod.yml`** — Production: adds Nginx with SSL termination, gzip, caching headers, security headers.

## Key Files

| File | Purpose |
|------|---------|
| `main.py` | Flask application entry point |
| `db/information_.db` | SQLite database (note the underscore) |
| `db/schema.sql` | Database schema definition |
| `templates/index.html` | Main page template |
| `requirements.txt` | Python dependencies (Flask 3.1.0, Python 3.12) |
| `nginx.conf` | Production Nginx configuration |
| `.env.example` | Environment variable template |
