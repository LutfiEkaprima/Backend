# Use the official Python image from the Docker Hub
FROM python:3.12.6-slim

# Set the working directory
WORKDIR /app

# Install system-level dependencies required for TensorFlow
RUN apt-get update && apt-get install -y \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements.txt and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire application into the container
COPY . .

# Copy the trained model file into the container
COPY path/to/your/model.h5 /app/model.h5

# Expose port 8080 to the outside world
EXPOSE 8080

# Set environment variable for Flask
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

# Run the Flask application with Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:app"]

