# SAMR_APP

Sistema de Atención Médica Remota — estructura reorganizada.

## Mapa de carpetas

```
SAMR_APP/
├── backend/        Proyecto Django (apps, config, manage.py) — el sistema en sí
├── shared/         Código transversal usado por todas las apps (antes "core/")
├── database/       Fixtures + notas de esquema (las migraciones siguen en backend/apps/*/migrations, ver database/README.md)
├── deployment/     Dockerfile, docker-compose.yml, Makefile, scripts
├── microservices/  Vacía por ahora — plan de separación futura, ver microservices/README.md
└── README.md       Este archivo
```

## Cómo correrlo

```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac/Linux
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

(Se corre desde `backend/`, no desde la raíz — ahí sigue estando `manage.py`.)

## Para Docker / despliegue

Los archivos de `deployment/` (Dockerfile, docker-compose.yml) asumen el
contexto de build en `SAMR_APP/` para poder copiar tanto `backend/` como
`shared/` dentro de la imagen. Si vas a correr `docker build`, hazlo desde
la raíz `SAMR_APP/`, no desde `deployment/`.
