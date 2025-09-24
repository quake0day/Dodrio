# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Flask-based personal academic website (Professor Si Chen's profile) with Google Scholar integration for tracking and displaying publications with citation counts. The system uses SQLite for data storage and includes automated citation updating functionality.

## Commands

### Running the Application

- **Development server**: `python FlaskApp/main.py` or `python FlaskApp/wsgi.py` (runs on port 443 with SSL)
- **Virtual environment activation**: `source FlaskApp/venv/bin/activate` (Python 2.7 environment)

### Citation Update

- **Manual update**: `python FlaskApp/citation_update.py`
- **Automated update via cron**: `sh FlaskApp/run_update.sh` (logs to citationUpdate.log)

### Database Management

- **Database location**: `FlaskApp/db/information.db`
- **Schema**: See `FlaskApp/schema.sql` for table structure (entries table with publication data)

## Architecture

### Core Components

1. **Main Flask Application** (`FlaskApp/main.py`)
   - SQLite database integration using g.db connection pattern
   - Single route serving index page with publication entries
   - Database queries executed directly in route handlers

2. **Google Scholar Integration** (`FlaskApp/scholar.py`, `FlaskApp/citation_update.py`)
   - `scholar.py`: Core Google Scholar API wrapper with query classes
   - `citation_update.py`: Updates citation counts for publications
   - Uses cluster IDs for efficient citation tracking
   - Implements rate limiting with random sampling to avoid being blocked

3. **Database Structure**
   - Single `entries` table containing publication information
   - Fields: id, type, title, author, confname, urlpaper, urlslides, urlcite, cite (citation count), place, year, text, cluster (Google Scholar cluster ID)

4. **Web Scraping Components**
   - `scrape_author.py`: Author information extraction
   - `scrape_publication.py`: Publication data extraction
   - Uses BeautifulSoup for HTML parsing (see `db/updater/requirements.txt`)

### Key Implementation Details

- **SSL Configuration**: Application configured to run with SSL certificates (see `wsgi.py`)
- **Citation Update Strategy**: Random sampling of 8 publications per run to avoid rate limiting
- **Database Connection Pattern**: Uses Flask's g object for per-request database connections
- **Template System**: Uses Jinja2 templates with PureCSS framework for styling

## Dependencies

Primary dependencies include:
- Flask (web framework)
- sqlite3 (database)
- BeautifulSoup4 (HTML parsing for web scraping)
- selenium (automated browser interaction for scraping)
- werkzeug (WSGI utilities)

Note: System appears to use Python 2.7 in the virtual environment, though Python 3.10.9 is available system-wide.

## Security Considerations

- SSL certificates present in directory (*.crt, *.key files)
- LDAP integration code exists in `db/updater/main.py` but appears to be a separate component
- Direct SQL query construction in citation_update.py - be cautious with SQL injection risks when modifying