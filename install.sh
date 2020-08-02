#!/usr/bin/env bash

echo "Creating virtual environment..."
virtualenv venv

echo "Installing dependencies..."
pipenv install