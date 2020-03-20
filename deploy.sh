#!/usr/bin/env bash

echo "Opening virtual environment..."
source ./venv/bin/activate

echo "Deploying production instance..."
gunicorn run:app -b localhost:5000 &

echo "Deployed!"