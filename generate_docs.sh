#!/bin/bash
# Script to generate documentation using Docker

# Build a temporary image based on the Flask Dockerfile with pdoc installed
docker build -t flask-pdoc -f docker/flask/Dockerfile .

# Run the container with the current directory mounted
docker run --rm -v "$(pwd):/app" flask-pdoc bash -c "pip install pdoc && python -m pdoc --html --force --output-dir /app/docs src.flask_app.routes.auth"

echo "Documentation generated in the docs directory"
