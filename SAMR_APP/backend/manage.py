#!/usr/bin/env python
"""Utilidad de linea de comandos de Django para el proyecto SAMR."""
import os
import sys
from pathlib import Path

# shared/ vive junto a backend/ (no adentro), como en la estructura de
# carpetas de SAMR_APP. Sin esta linea, "from shared.xxx import yyy" no se
# encontraria: Python solo agrega al sys.path la carpeta de manage.py
# (backend/), no la carpeta padre (SAMR_APP/) donde esta shared/.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "No se pudo importar Django. Verifica que este instalado y que "
            "el entorno virtual este activo."
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
