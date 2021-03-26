#!/usr/bin/env bash

echo "Killing deployed instance..."
pkill -f gunicorn

echo "instance killed"