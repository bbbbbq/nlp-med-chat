#!/bin/bash
# This script builds and runs the Rust backend server

# Navigate to the directory containing minio docker-compose.yml and start the container

# Kill any existing process listening on port 3000
if lsof -i :3000 -t >/dev/null; then
    echo "Killing process on port 3000..."
    lsof -i :3000 | awk 'NR!=1 {print $2}' | xargs kill -9
fi

echo "Starting MinIO container..."
sudo docker-compose -f ../minio/docker-compose.yml up -d

# Navigate to the directory containing docker-compose.yml and start the database
echo "Starting MySQL container..."
sudo docker-compose -f ../mysql/docker-compose.yml up -d

# Wait for services to initialize
echo "Waiting for services to be ready..."
sleep 3

echo "Setting up Python environment and starting Flask server..."

# Install Python dependencies
pip install -r requirements.txt

# Kill any process that is using port 3000
if sudo lsof -t -i:3000; then
    sudo kill -9 $(sudo lsof -t -i:3000)
    echo "Killed process on port 3000"
fi

# Run the Flask application
python3 app.py
