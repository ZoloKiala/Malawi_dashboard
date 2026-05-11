"""Django entry point for the WASA Malawi baseline dashboard.

Run locally with:
    python manage.py runserver 127.0.0.1:8051
"""
from __future__ import annotations

import os
import sys

from django.core.management import execute_from_command_line
from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wasa_site.settings")

application = get_wsgi_application()
server = application


if __name__ == "__main__":
    execute_from_command_line([sys.argv[0], "runserver", "127.0.0.1:8051"])
