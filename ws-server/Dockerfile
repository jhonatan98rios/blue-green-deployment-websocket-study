# Use slim Python base image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Install system dependencies (wget for healthcheck, pip, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
 && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the server code
COPY main.py .

# Expose port used by WebSocket server
EXPOSE 8000

# Define default command
CMD ["python3", "-u", "main.py"]
