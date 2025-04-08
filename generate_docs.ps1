# PowerShell script to generate documentation using Docker

# Build a temporary image based on the Flask Dockerfile with pdoc installed
docker build -t flask-pdoc -f docker/flask/Dockerfile .

# Run the container with the current directory mounted
$current_dir = (Get-Location).Path
docker run --rm -v "${current_dir}:/app" flask-pdoc bash -c "pip install pdoc && PYTHONPATH=/app python -m pdoc -o /app/docs src.flask_app.routes.auth"

Write-Host "Documentation generated in the docs directory"
