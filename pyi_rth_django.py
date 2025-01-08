# pyi_rth_django.py
import django
import os
import sys

def pre_find_module_path():
    try:
        django.setup()
    except Exception as e:
        print(f"Error initializing Django: {e}", file=sys.stderr)
        raise

pre_find_module_path()
