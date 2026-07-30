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

## Qué cambió técnicamente al reorganizar (no solo mover carpetas)

Mover `core/` a `shared/` como carpeta **hermana** de `backend/` (en vez de
estar adentro) rompía los imports (`from core.xxx import yyy`) en las ~40
archivos que los usaban, porque Python solo agrega automáticamente al
`sys.path` la carpeta donde vive `manage.py` (`backend/`), no su carpeta
padre. Para que siguiera funcionando, hice dos cosas:

1. Reemplacé todos los `from core.` por `from shared.` en todo `backend/`
   (y dentro del propio `shared/`, que también se importaba a sí mismo).
2. Agregué esta línea al inicio de `manage.py`, `config/wsgi.py`,
   `config/asgi.py` y `config/celery.py`:
   ```python
   sys.path.insert(0, str(Path(__file__).resolve().parent.parent[.parent]))
   ```
   Esto le dice a Python "también busca módulos en la carpeta `SAMR_APP/`",
   que es donde vive `shared/` ahora.

Sin este paso, el proyecto habría fallado con `ModuleNotFoundError: No
module named 'shared'` al primer `python manage.py runserver`.

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
