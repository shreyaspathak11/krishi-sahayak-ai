# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
# This is the crucial step where the large models will be downloaded and cached.
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code into the container at /app
COPY . .

# Command to run your application
# Render will automatically use the correct port, so we use $PORT
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "$PORT"]