#!/usr/bin/python3

from app import create_app
from config import Production, Test

# Create the application instance
app = create_app(Test)