#!/usr/bin/env bash

echo "Creating virtual environment..."
pipenv shell

sleep 2

echo "Installing dependencies..."
pipenv install