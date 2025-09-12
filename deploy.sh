#!/bin/bash

# Server deployment script for Flask Academic Website
# This script sets up the initial deployment on a Debian server

set -e

echo "=== Flask Academic Website Deployment Script ==="

# Check if running as root
if [ "$EUID" -eq 0 ]; then 
   echo "Please do not run this script as root for security reasons"
   exit 1
fi

# Update system packages
echo "Updating system packages..."
sudo apt-get update
sudo apt-get upgrade -y

# Install Docker if not present
if ! command -v docker &> /dev/null; then
    echo "Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    rm get-docker.sh
    echo "Docker installed. Please log out and log back in for group changes to take effect."
fi

# Install Docker Compose if not present
if ! command -v docker-compose &> /dev/null; then
    echo "Installing Docker Compose..."
    sudo apt-get install -y docker-compose
fi

# Install Git if not present
if ! command -v git &> /dev/null; then
    echo "Installing Git..."
    sudo apt-get install -y git
fi

# Install nginx if not present (for reverse proxy)
if ! command -v nginx &> /dev/null; then
    echo "Installing Nginx..."
    sudo apt-get install -y nginx
fi

# Create application directory
APP_DIR="$HOME/flask-app"
echo "Setting up application in $APP_DIR..."
mkdir -p $APP_DIR
cd $APP_DIR

# Clone or update repository
if [ -d ".git" ]; then
    echo "Updating existing repository..."
    git pull origin main || git pull origin master
else
    echo "Cloning repository..."
    git clone https://github.com/quake0day/Dodrio.git .
fi

# Create necessary directories
mkdir -p db
mkdir -p logs

# Set up environment variables
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cat > .env << EOL
# Flask Configuration
FLASK_ENV=production
SECRET_KEY=$(openssl rand -hex 32)

# Database
DATABASE_PATH=/app/db/information.db

# Server Configuration
GUNICORN_WORKERS=4
GUNICORN_THREADS=2
EOL
fi

# Build and start Docker containers
echo "Building and starting Docker containers..."
docker compose -f docker-compose.prod.yml down || true
docker compose -f docker-compose.prod.yml build --no-cache
docker compose -f docker-compose.prod.yml up -d

# Set up Nginx reverse proxy
echo "Configuring Nginx..."
sudo tee /etc/nginx/sites-available/flask-app << EOL
server {
    listen 80;
    server_name _;  # Replace with your domain name

    client_max_body_size 10M;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    location /static {
        alias $APP_DIR/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
EOL

# Enable site
sudo ln -sf /etc/nginx/sites-available/flask-app /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t && sudo systemctl reload nginx

# Set up automatic Docker container restart
echo "Setting up auto-restart..."
sudo tee /etc/systemd/system/flask-app.service << EOL
[Unit]
Description=Flask Academic Website
Requires=docker.service
After=docker.service

[Service]
Type=simple
WorkingDirectory=$APP_DIR
ExecStart=/usr/bin/docker-compose -f docker-compose.prod.yml up
ExecStop=/usr/bin/docker-compose -f docker-compose.prod.yml down
Restart=always
User=$USER

[Install]
WantedBy=multi-user.target
EOL

sudo systemctl daemon-reload
sudo systemctl enable flask-app

# Set up firewall
echo "Configuring firewall..."
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
echo "y" | sudo ufw enable

echo "=== Deployment Complete ==="
echo ""
echo "Next steps:"
echo "1. Update the Nginx configuration with your domain name"
echo "2. Set up SSL with Let's Encrypt: sudo certbot --nginx"
echo "3. Configure GitHub secrets for automatic deployment:"
echo "   - SERVER_HOST: Your server IP or domain"
echo "   - SERVER_USER: $USER"
echo "   - SERVER_PORT: 22"
echo "   - SERVER_SSH_KEY: Your private SSH key"
echo ""
echo "Your website should now be accessible at http://$(hostname -I | cut -d' ' -f1)"