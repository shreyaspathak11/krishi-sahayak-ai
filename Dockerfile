# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

# Set the working directory in the container
WORKDIR /app

# Install system dependencies (minimal set for building wheels)
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy requirements first for better layer caching
COPY requirements.txt .

# Upgrade pip and install Python dependencies
# We use --no-cache-dir to keep the image small
RUN pip install --upgrade pip --no-cache-dir \
    && pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code
COPY . .

# Create necessary directories
RUN mkdir -p data/source_documents

# Create a non-root user for security
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# Expose the port the app runs on
EXPOSE $PORT

# Lightweight health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD python -c "import requests; import os; response = requests.get(f'http://localhost:{os.getenv(\"PORT\", 8000)}/status', timeout=5); exit(0 if response.status_code == 200 else 1)" || exit 1

# Command to run your application
CMD python start.py