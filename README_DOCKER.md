# Flask Academic Website - Docker Deployment Guide

## 🚀 What's Been Updated

### 1. **Python Upgrade** 
- Upgraded from Python 2.7 to Python 3.12
- All packages updated to latest versions (as of Jan 2025)
- Flask upgraded from 0.10.1 to 3.1.0

### 2. **Pure CSS Update**
- Updated Pure CSS from v0.6 (2016) to v3.0.0 (latest)
- Downloaded latest minified versions for better performance

### 3. **Docker Containerization**
- Created multi-stage Dockerfile for optimized image size
- Added docker-compose.yml for easy orchestration
- Included health checks and automatic restart
- Volume mounts for database persistence and easy updates

## 📦 Package Updates

| Package | Old Version | New Version |
|---------|-------------|-------------|
| Flask | 0.10.1 | 3.1.0 |
| Werkzeug | 0.11.3 | 3.1.3 |
| Jinja2 | 2.8 | 3.1.4 |
| BeautifulSoup | 3.2.1 | 4.12.3 |
| Pure CSS | 0.6.x | 3.0.0 |
| Gunicorn | N/A | 23.0.0 |

## 🐳 Docker Setup

### Prerequisites
- Docker Desktop installed
- Docker Compose (included with Docker Desktop)

### Quick Start

1. **Build and run the container:**
```bash
# Using the Makefile
make build
make run

# Or using docker compose directly
docker compose build
docker compose up -d web
```

2. **Access the website:**
- Open browser to: http://localhost:5001
- The application runs inside container on port 5000, mapped to host port 5001

### Available Commands

```bash
# Build containers
make build

# Run in development mode
make dev

# Run in production mode with nginx (SSL)
make prod

# View logs
make logs

# Stop containers
make stop

# Access container shell
make shell

# Initialize database
make init-db

# Backup database
make backup-db

# Update citation counts
make update-citations
```

## 📁 Project Structure

```
FlaskApp/
├── Dockerfile              # Container definition
├── docker-compose.yml      # Service orchestration
├── .dockerignore          # Files to exclude from image
├── requirements.txt       # Python dependencies (updated)
├── Makefile              # Convenience commands
├── nginx.conf            # Nginx configuration (for production)
├── main.py              # Flask application (Python 3 compatible)
├── wsgi.py              # WSGI server configuration
├── wcg.py               # Web scraping utilities (updated)
├── db/
│   ├── information_.db  # SQLite database
│   └── schema.sql       # Database schema
├── static/
│   └── pure/           # Pure CSS files (updated to v3.0.0)
└── templates/          # HTML templates
```

## 🔧 Configuration

### Environment Variables (.env)
Create a `.env` file based on `.env.example`:

```bash
FLASK_ENV=development
FLASK_DEBUG=False
FLASK_APP=main.py
DATABASE_PATH=/app/db/information_.db
HOST=0.0.0.0
PORT=5000
```

### Database
- SQLite database is mounted as volume for persistence
- Located at `./db/information_.db`
- Schema updated to match actual database structure

### SSL Certificates
- Place SSL certificates in project root
- Update paths in `docker-compose.yml` if needed
- Nginx configuration included for production HTTPS

## 🚀 Migration Notes

### Code Changes Made:
1. **Python 3 Compatibility:**
   - Updated print statements to print()
   - Fixed import statements (urllib2 → urllib.request)
   - Updated BeautifulSoup usage
   - Added proper error handling

2. **Flask Updates:**
   - Updated deprecated Flask patterns
   - Added proper logging
   - Environment-based configuration

3. **Docker Integration:**
   - Gunicorn as WSGI server
   - Health checks for container monitoring
   - Volume mounts for development

## 🔄 Deployment to Production

### Using Docker on Remote Server:

1. **Copy files to server:**
```bash
rsync -avz --exclude 'venv' --exclude '*.pyc' ./ user@server:/path/to/app/
```

2. **On the server:**
```bash
cd /path/to/app
docker compose build
docker compose --profile production up -d
```

3. **For HTTPS with Nginx:**
- Ensure SSL certificates are in place
- Update `nginx.conf` with your domain
- Run with production profile

### Using Docker Swarm or Kubernetes:
The containerized application is ready for orchestration platforms. The health check endpoint ensures proper monitoring.

## 🛠️ Troubleshooting

### Common Issues:

1. **Port already in use:**
   - Change port mapping in docker-compose.yml
   - Current mapping: 5001:5000 (host:container)

2. **Database not found:**
   - Run `make init-db` to initialize
   - Check volume mount in docker-compose.yml

3. **Container not starting:**
   - Check logs: `docker logs flask-academic-website`
   - Verify all files are present

## 📝 Maintenance

### Updating Dependencies:
1. Update `requirements.txt`
2. Rebuild container: `make build`
3. Restart: `make restart`

### Database Backup:
```bash
make backup-db
# Creates timestamped backup in backups/ directory
```

### Monitoring:
- Health check: `curl http://localhost:5001/`
- Container status: `docker ps`
- Resource usage: `docker stats`

## 🎯 Next Steps

1. Set up CI/CD pipeline for automated deployments
2. Add environment-specific configurations
3. Implement database migrations system
4. Add monitoring and logging aggregation
5. Set up automated backups

## 📧 Support

For issues or questions about the Docker setup, refer to:
- Docker documentation: https://docs.docker.com
- Flask documentation: https://flask.palletsprojects.com
- Project repository: [Your GitHub URL]