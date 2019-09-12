#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

def main():
    message = "Please make sure it's installed and available on your PATH, or check if your virtualenv is active."
    try:
        from dotenv import load_dotenv
    except ImportError as ex:
        raise ImportError("Couldn't import python-dotenv. " + message) from ex
    try:
        from django.core.management import execute_from_command_line
    except ImportError as ex:
        raise ImportError("Couldn't import Django. " + message) from ex
    # Execute Django with the specified environment variables
    load_dotenv()
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'application.settings')
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()
