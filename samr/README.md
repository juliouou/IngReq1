# SAMR - Sistema de Atencion Medica Remota

Backend desarrollado con Django 4.2 + Django REST Framework, autenticacion JWT,
base de datos SQLite y arquitectura por capas.

## Arquitectura

El proyecto separa responsabilidades en capas:

- models: definicion de tablas y relaciones.
- repositories: acceso a datos (Repository Pattern).
- services: logica de negocio (Service Layer).
- dtos: objetos de transferencia de datos.
- serializers: validacion y (de)serializacion DRF.
- views: controladores HTTP (ViewSets / APIViews).
- urls: enrutamiento por app.
- permissions: autorizacion por roles.
- validators: validaciones reutilizables.

Modulos transversales en la carpeta core:
excepciones personalizadas, paginacion, middleware, respuestas
estandarizadas, utilidades y permisos base.

## Aplicaciones

- usuarios: usuario personalizado, perfiles de medico y paciente, roles.
- triaje: solicitudes de atencion y evaluacion de triaje.
- biometria: dispositivos IoT, lecturas biometricas y alertas.
- teleconsulta: teleconsultas, recetas, detalles e historial clinico.
- auditoria: registro automatico de acciones sobre el sistema.

## Requisitos

- Python 3.11+
- pip

## Instalacion y ejecucion

    cd samr
    python -m venv venv
    # Windows: venv\Scripts\activate
    # Linux/Mac: source venv/bin/activate
    pip install -r requirements.txt
    python manage.py makemigrations
    python manage.py migrate
    python manage.py createsuperuser
    python manage.py seed
    python manage.py runserver

## Datos de prueba

El comando de seed genera datos relacionados y consistentes
(sin datos quemados en los modelos):

    python manage.py seed

Genera: administrador, medicos, pacientes, solicitudes de atencion,
evaluaciones de triaje, teleconsultas, recetas, dispositivos IoT,
lecturas biometricas, alertas e historial clinico.

## Documentacion de la API

- Esquema OpenAPI: /api/schema/
- Swagger UI: /api/docs/
- Redoc: /api/redoc/

## Autenticacion (JWT)

    POST /api/auth/login/      -> obtiene access y refresh
    POST /api/auth/refresh/    -> renueva el access token
    POST /api/auth/verify/     -> verifica un token

Enviar en cada peticion protegida el encabezado:

    Authorization: Bearer <access_token>

## Docker

    docker-compose up --build

## Roles

- ADMIN: acceso total.
- MEDICO: gestiona teleconsultas, recetas e historial de sus pacientes.
- PACIENTE: consulta su informacion, crea solicitudes de atencion.

## Licencia

Uso academico - UTPL.
