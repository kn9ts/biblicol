#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bootstrap.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)


# NOTES:
# manage.py is a script that helps with management of the site.
# With it we will be able to start a web server on our computer without
# installing anything else, amongst other things.
