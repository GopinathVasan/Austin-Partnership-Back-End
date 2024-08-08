#!/bin/bash

# Navigate to the project directory
cd /var/www/myproject

# Pull the latest code from the repository
git pull origin main

# Activate the virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run migrations (if using Django or similar framework)
# python manage.py migrate

# Collect static files (if using Django)
# python manage.py collectstatic --noinput

# Restart the application (e.g., Gunicorn)
sudo systemctl restart myproject
