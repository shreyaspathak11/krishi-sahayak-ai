# Use an official Python runtime as a parent image
FROM python:3.11-alpine

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

# Set the working directory in the container
WORKDIR /app

# Install minimal system dependencies (only curl for health check)
RUN apk add --no-cache curl

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

# Expose the port the app runs on
EXPOSE $PORT

# Command to run your application
CMD ["python", "start.py"]