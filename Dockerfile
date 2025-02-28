# Use official Python base image
FROM python:3.9-slim

# Install system dependencies, including TA-Lib
RUN apt-get update && apt-get install -y \
    libta-lib0 libta-lib-dev \
    && rm -rf /var/lib/apt/lists/*

# Set up your working directory
WORKDIR /app

# Copy your project files into the container
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port for the Flask app
EXPOSE 5000

# Set the command to run the app
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:5000"]
