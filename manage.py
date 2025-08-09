#!/usr/bin/env python
import os
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

def main():
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError("Django no está instalado o el entorno virtual no está activo.") from exc
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()