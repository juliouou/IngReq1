"""
Paquete de settings dividido por entorno.

- base.py         : configuracion comun.
- development.py  : entorno local (por defecto).
- production.py   : entorno productivo.

El modulo activo se define con la variable de entorno
DJANGO_SETTINGS_MODULE (manage.py usa config.settings.development).
"""
