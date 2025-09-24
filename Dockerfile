# Use Python 3.12 slim image for smaller size
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies for building Python packages
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libxml2-dev \
    libxslt-dev \
    libssl-dev \
    libffi-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create database directory and initialize database
RUN mkdir -p /app/db && \
    if [ -f /app/db/schema.sql ]; then \
        apt-get update && apt-get install -y sqlite3 && \
        sqlite3 /app/db/information_.db < /app/db/schema.sql && \
        apt-get remove -y sqlite3 && apt-get autoremove -y && \
        rm -rf /var/lib/apt/lists/*; \
    fi

# Set environment variables
ENV FLASK_APP=main.py
ENV PYTHONUNBUFFERED=1

# Expose port 5000 for Flask
EXPOSE 5000

# Run the application with gunicorn for production
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--threads", "2", "main:app"]