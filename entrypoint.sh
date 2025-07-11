#!/bin/bash

# Fix permissions on the mounted /data volume
chown -R appuser:appuser /data

# Run migrations as appuser
su appuser -c "python manage.py migrate"

# Start the application as appuser
exec su appuser -c "$*"