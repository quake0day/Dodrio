# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Flask-based personal academic website that displays publication data fetched from Google Scholar. The application uses SQLite for data storage and includes web scraping capabilities for updating citation counts.

## Architecture

### Core Application Structure
- **main.py**: Primary Flask application entry point with route definitions and database connection management
- **wsgi.py**: WSGI server configuration for HTTPS deployment using SSL certificates
- **manager.py**: Flask-Script based management interface for running commands and shell access

### Data Processing Components
- **scholar.py**: Google Scholar API interface for querying academic publications
- **citation_update.py**: Automated citation count updater that queries Google Scholar and updates the SQLite database
- **profile.py**: Google Scholar profile data extraction for faculty publications
- **wcg.py**: Web scraping utilities for extracting badge and ranking information

### Database
- **Database Location**: `db/information_.db` (SQLite)
- **Schema**: Publications stored in `entries` table with fields for title, author, conference, citations, URLs, and metadata
- **Schema File**: `db/schema.sql` defines the database structure

## Development Commands

### Running the Application
```bash
# Development server
python main.py

# Production server with SSL
python wsgi.py

# Management shell
python manager.py shell
```

### Database Operations
```bash
# Initialize/recreate database schema
sqlite3 db/information_.db < db/schema.sql

# Update citation counts (runs on random sample of papers)
python citation_update.py
```

### Virtual Environment
The project includes a Python 2.7 virtual environment in the `venv/` directory. Activate it before running:
```bash
source venv/bin/activate
```

## Key Technical Details

- **Python Version**: Python 2.7 (legacy codebase)
- **Framework**: Flask with SQLite database
- **SSL Configuration**: Uses certificate files (`*.crt`, `*.key`) for HTTPS deployment
- **Static Assets**: Pure CSS framework for styling (`static/pure/`)
- **Templates**: Jinja2 templates in `templates/` directory
- **Google Analytics**: Integrated tracking in the main template

## Important Paths

- **Database**: `/var/www/FlaskApp/FlaskApp/db/information.db` (production) or `./db/information_.db` (development)
- **SSL Certificates**: `4fa581949f17aaa.crt`, `darlingtree.key`
- **Templates**: `templates/index.html` - main page, `templates/404.html` - error page

## Notes for Development

- The application fetches publication data from the SQLite database and displays it on the homepage
- Citation updates are performed by `citation_update.py` which uses the Google Scholar API
- The codebase contains both active code and some legacy/duplicate files (e.g., multiple certificate files, duplicate app directories)
- Error handling includes custom 404 pages and exception handlers