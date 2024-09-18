#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'page_youtube.settings')

    # Utilisez le port fourni par Render ou 8000 par défaut
    port = os.environ.get('PORT', '8000')

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    # Si l'argument de commande est 'runserver', spécifiez l'adresse et le port
    if len(sys.argv) > 1 and sys.argv[1] == 'runserver':
        sys.argv[2:] = ['0.0.0.0:' + port]  # Utiliser 0.0.0.0 et le port donné

    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
