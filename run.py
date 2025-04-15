#!/usr/bin/env python
import os
import sys
import django
from django.core.management import execute_from_command_line

def run_server():
    try:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'applovin_reports.settings')
        django.setup()
        port = '8000'
        host = '127.0.0.1'  # Use localhost for better Windows compatibility
        execute_from_command_line(['run.py', 'runserver', f'{host}:{port}', '--noreload'])
    except Exception as e:
        print(f"Error starting server: {e}")
        input("Press Enter to exit...")  # Keep window open on error

if __name__ == '__main__':
    run_server()