# SAMR

Sistema de Atencion Medica Remota distribuido en microservicios, con un API Gateway como punto unico de entrada, persistencia separada por dominio y una capa compartida de modelos de negocio.

## Nota de arquitectura (leer primero)

Este repositorio tuvo dos intentos de backend en paralelo: un backend Django
monolitico (`SAMR_APP/backend/apps/*`, `config/`, `manage.py`) y los
microservicios Node.js descritos en este README (`backend/gateway/` +
`microservices/`). Se prioriza la version de **microservicios Node** porque
es la que esta funcionando de punta a punta (frontend real conectado a
Gateway, M1-M5, Postgres, TimescaleDB y Redis, probado end-to-end). El
codigo Django sigue en el repositorio pero **no se ejecuta ni se mantiene**;
se dejo sin borrar para no perder ese trabajo hasta que el equipo decida
formalmente que hacer con el (portar algo util, o eliminarlo).

## Arquitectura general

```mermaid
flowchart LR
  F[Frontend] --> G[API Gateway]
  G --> M1[M1 Usuarios y Acceso]
  G --> M2[M2 Triaje Inteligente]
  G --> M3[M3 Monitoreo Biometrico]
  G --> M4[M4 Teleconsulta]
  G --> M5[M5 Seguridad y Auditoria]

  M1 --> P[(PostgreSQL clinico)]
  M4 --> P
  M3 --> T[(TimescaleDB IoT)]
  M2 --> R[(Redis / BullMQ)]
  M3 --> R
  M5 --> P
  M5 --> R

  M1 -. JWT .-> G
  M2 -. eventos .-> M5
  M3 -. eventos .-> M4
  M3 -. eventos .-> M5
  M4 -. eventos .-> M5
```

### Capas del sistema

- `frontend/`: cliente web (React + Vite) que consume el Gateway; ver `frontend/README.md`.
- `backend/gateway/`: entrada unica del sistema, responsable de ruteo y validacion del JWT.
- `backend/apps/`, `backend/config/`, `backend/manage.py`: backend Django anterior, **no usado** (ver nota de arquitectura arriba).
- `microservices/`: dominios funcionales separados por responsabilidad (M1-M5).
- `database/`: esquemas de PostgreSQL y TimescaleDB que usan los microservicios.
- `deployment/`: orquestacion local con Docker Compose (Gateway + M1-M5 + Postgres + TimescaleDB + Redis).
- `shared/models/`: contratos de dominio comunes entre modulos (TypeScript, solo como referencia de forma de datos).

Ver `COMO_EJECUTAR.md` para el paso a paso de como levantar todo.

## Componentes y responsabilidad

### API Gateway

Punto de entrada unico. Valida el JWT emitido por M1, enruta peticiones a M1-M5 y aplica autorizacion por rol. Ninguna logica de negocio vive aqui.

### M1 - Usuarios y Acceso

Gestiona registro, login, MFA, verificacion IESS y consentimiento LOPDP. Es el unico modulo que emite JWT.

### M2 - Triaje Inteligente

Recibe solicitudes de triaje, evalua sintomas o alertas IoT, consulta Med-Gemini y realiza matching con centros de asistencia.

### M3 - Monitoreo Biometrico

Ingiere datos IoT, detecta anomalias y distribuye alertas a paciente, medico y centro de asistencia.

### M4 - Teleconsulta

Gestiona video/audio por WebRTC, apoyo diagnostico XAI y emision de receta digital.

### M5 - Seguridad y Auditoria

Consume eventos del resto del sistema, los normaliza, los hashiza con SHA-256 y conserva trazabilidad inmutable.

## Infraestructura local

El `docker-compose.yml` define estos servicios:

- `gateway` en `3000`
- `m1` en `3001`
- `m2` en `3002`
- `m3` en `3003`
- `m4` en `3004`
- `m5` en `3005`
- `postgres` para datos clinicos
- `timescaledb` para telemetria IoT
- `redis` para colas y eventos

## Estado real del repositorio

El flujo de extremo a extremo funciona: autenticacion en M1 (con MFA e IESS),
enrutamiento y autorizacion por rol en el Gateway, triaje con matching en M2,
ingesta y alertas en M3, teleconsulta con WebRTC real y receta en M4, y
consumo de eventos con hash SHA-256 mas exportacion PDF en M5. El frontend
consume todo esto sin simular respuestas.

Lo que todavia falta, para ser honestos sobre el alcance:

- No hay pruebas automatizadas en los directorios `tests/` de cada modulo.
- No hay TURN server para WebRTC: en redes con NAT restrictivo la
  videollamada puede no conectar (solo hay STUN publico).
- No hay TLS configurado en el canal de entrada del Gateway (asumido fuera
  de alcance para desarrollo local; en despliegue real lo terminaria un
  proxy/load balancer).
- `JWT_SECRET` y las credenciales de base de datos siguen en
  `docker-compose.yml` en texto plano, no en un `.env` ignorado por git.
- M2 no tiene circuit breaker ni modo degradado si Med-Gemini (o su stub)
  no responde.
- `shared/contracts/` (eventos BullMQ y adaptador Med-Gemini) no se formalizo
  como archivos; los payloads de los eventos quedaron documentados como
  comentarios en el codigo de cada productor/consumidor.
- Las migraciones de base de datos son un solo `schema.sql`, no archivos
  numerados por migracion; no hay script de backup.

## Roles y responsables

La asignacion de trabajo queda definida con los nombres del documento de vision. El orden sugerido respeta dependencias reales del sistema: primero base de datos y arquitectura, luego seguridad y backend, despues frontend y cierre de pruebas/documentacion.

| Integrante | Rol | Primero que debe hacer | Entrega exacta que debe completar |

| --- | --- | --- | --- |
| Julio Maldonado | Administrador de Base de Datos | Definir la base persistente del sistema para que todo lo demas pueda funcionar sobre una estructura estable. | Terminar los esquemas de PostgreSQL y TimescaleDB, crear migraciones, llaves foraneas, indices y restricciones, dejar datos semilla, y validar que M1, M3, M4 y M5 puedan leer y escribir sin romper el modelo de datos. 

|
| Leydi Robalino | Arquitecto de Software | Cerrar la arquitectura objetivo y asegurar que cada modulo tenga una responsabilidad unica. | Completar la arquitectura logica y fisica, definir flujos entre Gateway, M1-M5, fijar contratos entre modulos, definir dependencias, eventos y limites de cada servicio, y dejar documentada la trazabilidad del sistema. 

|
| Alisson Condoy | Especialista en Seguridad | Asegurar autenticacion, autorizacion, auditoria y controles de entrada antes de abrir el sistema. | Terminar la estrategia de seguridad del Gateway y M1, definir validacion JWT, MFA, manejo de sesiones, politica de secretos, trazabilidad de eventos y requisitos LOPDP para que el sistema no exponga datos sensibles.

 |
| Antonela Parra | Desarrollador Backend | Implementar la logica de negocio y los endpoints de los microservicios. | Completar Gateway, M1, M2, M3, M4 y M5 en la capa backend: rutas, validaciones, integracion con base de datos, colas, eventos, adaptadores externos y cumplimiento de los contratos OpenAPI de cada modulo. 

|
| Paula López | Desarrollador Frontend | Construir la experiencia de usuario que consuma los servicios ya definidos por backend. | Completar el frontend conectado al Gateway, crear pantallas de registro, login, triaje, monitoreo, teleconsulta y auditoria, manejar estados, formularios y consumo de API, y dejar el flujo navegable de punta a punta. 

|
| David León | Diseñador UX/UI | Definir la experiencia, jerarquia visual y claridad operativa del sistema antes de cerrar la interfaz. | Entregar prototipos, flujos de navegacion, sistema visual, componentes reutilizables, estados de error/exito, version responsive y guia visual para que frontend implemente una interfaz coherente y util. |

## Que debe hacer cada integrante exactamente

### Julio Maldonado - Administrador de Base de Datos

Debe empezar por la base de datos, porque el resto del sistema depende de eso. Su orden recomendado es:

- 1. Revisar los modelos de dominio y decidir la estructura final de tablas.
- 2. Crear o terminar los esquemas de PostgreSQL y TimescaleDB.
- 3. Definir migraciones y relaciones entre usuarios, pacientes, consultas, solicitudes, alertas y auditoria.
- 4. Crear restricciones, llaves foraneas e indices.
- 5. Preparar datos semilla y validar que los servicios conecten correctamente.
- 6. Dejar la persistencia lista para que M1, M3, M4 y M5 puedan leer y escribir.

### Leydi Robalino - Arquitecto de Software

Debe cerrar la arquitectura para que no existan ambiguedades entre modulos. Su orden recomendado es:

- 1. Confirmar el mapa completo de servicios: Gateway, M1, M2, M3, M4 y M5.
- 2. Definir las responsabilidades exactas de cada modulo.
- 3. Alinear los contratos OpenAPI con el flujo de negocio real.
- 4. Definir eventos entre servicios y que modulo produce o consume cada uno.
- 5. Validar dependencias de infraestructura: PostgreSQL, TimescaleDB y Redis.
- 6. Documentar el flujo extremo a extremo desde autenticacion hasta auditoria.

### Alisson Condoy - Especialista en Seguridad

Debe asegurar que el sistema no se abra sin control de acceso ni trazabilidad. Su orden recomendado es:

- 1. Definir como se valida el JWT emitido por M1.
- 2. Revisar el flujo de autenticacion y MFA.
- 3. Establecer manejo seguro de secretos y variables de entorno.
- 4. Definir reglas de acceso por rol y por modulo.
- 5. Asegurar la trazabilidad de eventos para auditoria.
- 6. Proponer controles LOPDP y criterios de inmutabilidad en M5.

### Antonela Parra - Desarrollador Backend

Debe construir la logica funcional de los servicios. Su orden recomendado es:

- 1. Completar el API Gateway para enrutar a M1-M5.
- 2. Terminar M1 con registro, login, MFA, IESS y consentimiento.
- 3. Implementar M2 con triaje, matching y cola de procesamiento.
- 4. Implementar M3 con ingesta IoT, alertas y persistencia en TimescaleDB.
- 5. Implementar M4 con teleconsulta, decisiones medicas y receta digital.
- 6. Implementar M5 con consumo de eventos, hash SHA-256 y exportacion de auditoria.
- 7. Conectar todo con las pruebas de contrato y validacion de flujos.

### Paula López - Desarrollador Frontend

Debe convertir la arquitectura en una interfaz usable para los roles operativos. Su orden recomendado es:

- 1. Construir login, registro y recuperacion de acceso.
- 2. Implementar navegacion por rol y permisos visibles.
- 3. Crear pantallas para triaje, monitoreo, teleconsulta y auditoria.
- 4. Conectar formularios y vistas con los endpoints reales del backend.
- 5. Manejar estados de carga, error, vacio y exito.
- 6. Validar que la experiencia sea responsive y consistente con el diseno.

### David León - Diseñador UX/UI

Debe dejar lista la experiencia antes de que el frontend se cierre. Su orden recomendado es:

- 1. Definir flujos de usuario para paciente, medico, administrativo, MSP y DPO.
- 2. Diseñar wireframes y prototipos de las pantallas clave.
- 3. Definir jerarquia visual, colores, tipografia y componentes.
- 4. Establecer estados de formularios, alertas, tablas y paneles.
- 5. Entregar guia visual para implementacion en frontend.
- 6. Validar accesibilidad y comportamiento responsive.

## Que falta por modulo

### Gateway

- TLS en el canal de entrada.
- Mover `JWT_SECRET` y credenciales a `.env` (hoy en `docker-compose.yml`).
- Middleware de logging estructurado (hoy es un `console.log` por peticion).

### M1

- Pruebas automatizadas.
- Proveedor real de SMS/correo para MFA (hoy el codigo se ve en la respuesta
  en modo desarrollo, no hay envio real).
- Integracion HL7/FHIR real con el IESS (hoy es una validacion de formato).

### M2

- Circuit breaker y modo degradado si Med-Gemini no responde.
- Adaptador a un modelo Med-Gemini real (hoy es un motor de reglas por
  palabras clave, con la misma interfaz que tendria la integracion real).
- Pruebas automatizadas.

### M3

- Integracion con un modelo predictivo real (hoy la deteccion de anomalias
  es por umbral fijo, mismo patron que M2).
- Pruebas automatizadas.

### M4

- TURN server para WebRTC en redes con NAT restrictivo (hoy solo hay STUN).
- Persistencia de historial clinico en formato FHIR.
- Pruebas automatizadas.

### M5

- Pruebas automatizadas.
- `shared/contracts/events/schemas.json` formal (hoy los payloads de cada
  evento estan documentados como comentarios en el productor/consumidor).

## Siguiente paso recomendado

Completar primero los contratos de cada microservicio junto con sus pruebas, y despues implementar el flujo de extremo a extremo: autenticar en M1, enrutar desde Gateway, generar triaje en M2, registrar alerta en M3, atender en M4 y consolidar trazabilidad en M5.
