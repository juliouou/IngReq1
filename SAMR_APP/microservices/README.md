# microservices/

## Estado actual: esta carpeta está vacía a propósito

Hoy SAMR **no es una arquitectura de microservicios real**: es un solo
proyecto Django (`backend/`) con varias apps (`usuarios`, `triaje`,
`biometria`, `teleconsulta`, `auditoria`, `portal`) que comparten una única
base de datos y un único proceso. Eso no es un defecto — para el tamaño
actual del proyecto, un monolito modular es más simple de mantener, migrar
y depurar que microservicios reales.

Esta carpeta existe como el lugar donde, **cuando llegue el momento**, se
irían moviendo las apps que tenga sentido separar en servicios
independientes y desplegables por su cuenta.

## Candidatas a separar primero, y por qué

| App | ¿Por qué sería la primera en separarse? |
|---|---|
| `biometria` | Ya es la más distinta al resto: usa Celery, Channels (WebSockets) y una hypertable de TimescaleDB para las lecturas de dispositivos IoT. Tiene un patrón de carga (muchas escrituras pequeñas y constantes) muy diferente al resto del sistema, que es más transaccional. |
| `teleconsulta` | También usa WebSockets (videollamada/chat) y podría escalar de forma independiente en momentos de mucha demanda (ej. horas pico de consultas). |
| `triaje` | Depende de un motor de IA (`shared/motor_ia_llm.py`) que en el futuro podría necesitar su propio ciclo de despliegue (ej. cambiar de modelo sin tocar el resto del sistema). |

`usuarios`, `auditoria` y `portal` conviene dejarlas en el backend
principal por ahora: son transversales (todas las demás apps las necesitan)
y separarlas primero generaría más llamadas entre servicios sin un
beneficio claro todavía.

## Qué implica separar una app de verdad (para cuando se haga)

No es solo mover la carpeta aquí. Cada microservicio real necesitaría:
1. Su propio `settings.py`, `manage.py` y base de datos (o esquema aparte).
2. Una forma de comunicarse con el resto (API REST interna, o colas de
   mensajes — Celery/RabbitMQ ya están en el proyecto y ayudarían aquí).
3. Autenticación compartida (ej. JWT validado por cada servicio, sin
   depender de que `usuarios` esté siempre disponible).
4. Su propio Dockerfile y entrada en `deployment/docker-compose.yml`.

Por ahora, el valor de esta carpeta es dejar documentado el plan, no
fingir una separación que técnicamente no existe todavía.
