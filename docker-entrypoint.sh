#!/bin/bash

echo "Run migrations..."
python manage.py upgrade

echo "Start server"
