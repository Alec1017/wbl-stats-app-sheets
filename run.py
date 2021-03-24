#!/usr/bin/python3

import os

from app import create_app
from config import Production, Development


# Create the application instance
if os.environ.get('FLASK_ENV') == 'production':
    app = create_app(Production)
elif os.environ.get('FLASK_ENV') == 'development':
    app = create_app(Development)
else:
    error_message = 'No application instance mode provided. Please try one of (--prod, --dev)'

    raise Exception(error_message)