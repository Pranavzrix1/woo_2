#!/bin/bash

echo "Setting up AI Product Search project..."

# Create directories
mkdir -p app/{models,services,agents,api}
mkdir -p static
mkdir -p scripts

# Make script executable
chmod +x scripts/setup.sh

echo "Project structure created!"
echo "Run 'docker-compose up --build' to start the application"
