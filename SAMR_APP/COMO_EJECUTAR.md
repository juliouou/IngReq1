# Como ejecutar SAMR (rama feature/frontend)

Esta rama trae un sistema completo y funcional de punta a punta: backend en
microservicios Node.js + Gateway, y el frontend en React que los consume.
Nada de lo que ves aqui es simulado: cada pantalla llama al backend real.

> **Nota sobre arquitectura:** mientras se construia esto, `main` cambio de
> arquitectura y volvio a un backend Django monolitico (`SAMR_APP/backend/`
> con `apps/*`), abandonando los microservicios Node. Esta rama sigue el
> diseno original de microservicios (Gateway + M1-M5) documentado en
> `SAMR_APP/README.md` y no se fusiono con ese cambio para no mezclar dos
> backends incompatibles. Habria que decidir en equipo cual arquitectura es
> la definitiva antes de mergear esto a `main`.

## Requisitos

- Docker Desktop (para Postgres, TimescaleDB, Redis y los 6 servicios Node)
- Node.js 18+ (para correr el frontend en modo desarrollo)

## 1. Levantar el backend

```bash
cd SAMR_APP/deployment
docker compose up -d --build
```

Esto levanta:

| Servicio | Puerto | Que es |
| --- | --- | --- |
| gateway | 3000 | API Gateway (unico punto de entrada real) |
| m1 | 3001 | Usuarios y Acceso |
| m2 | 3002 | Triaje Inteligente |
| m3 | 3003 | Monitoreo Biometrico |
| m4 | 3004 | Teleconsulta (incluye senalizacion WebRTC) |
| m5 | 3005 | Seguridad y Auditoria |
| postgres | 5434 | Datos clinicos |
| timescaledb | 5433 | Series de tiempo IoT |
| redis | 6379 | Colas de eventos (BullMQ) |

La primera vez (o si borraste los volumenes con `docker compose down -v`)
hay que aplicar el esquema a mano, porque no esta automatizado como script
de init de Postgres:

```bash
docker exec -i <contenedor-postgres> psql -U postgres -d samr_clinico < ../database/postgres/schema.sql
docker exec -i <contenedor-timescaledb> psql -U postgres -d samr_iot < ../database/timescaledb/schema.sql
```

(el nombre del contenedor suele ser `deployment-postgres-1` y
`deployment-timescaledb-1`; confirmalo con `docker compose ps`).

Verificar que arrancio bien:

```bash
curl http://localhost:3000/health
```

## 2. Levantar el frontend

```bash
cd SAMR_APP/frontend
npm install
cp .env.example .env
npm run dev
```

Abrir `http://localhost:5173`.

## 3. Crear cuentas de prueba

No hay usuarios precargados (no hay seed script todavia). Regístrate desde
`/acceso/registro`, o crea las 5 por curl:

```bash
curl -X POST http://localhost:3000/auth/register -H "Content-Type: application/json" \
  -d '{"nombre":"Tu Nombre","email":"tu@correo.com","password":"Demo12345","rol":"paciente"}'
```

`rol` acepta: `paciente`, `medico`, `administrativo`, `msp`, `dpo`.

## 4. Apagar todo

```bash
cd SAMR_APP/deployment
docker compose down       # conserva los datos
docker compose down -v    # borra tambien los datos (hay que re-aplicar el esquema despues)
```

## Cosas a tener en cuenta

- **MFA**: esta apagado por defecto (`usuarios.mfa_activo = false`). Para
  probarlo en una cuenta: `UPDATE usuarios SET mfa_activo = true WHERE
  email = '...';` directo en Postgres. No hay proveedor de SMS/correo
  conectado: en modo desarrollo el codigo de un solo uso viene incluido en
  la respuesta de `/auth/login` y se muestra en la propia pantalla de MFA.
- **Videollamada (Teleconsulta)**: es WebRTC real (no un mock). Para ver
  dos videos conectados hacen falta dos sesiones (dos pestañas/dispositivos)
  entrando a la *misma* consulta. Solo hay un STUN publico configurado, sin
  TURN server, asi que en redes con NAT restrictivo puede no conectar.
- **Auditoria**: solo la ven los roles `administrativo`, `msp` y `dpo` (el
  Gateway lo exige con 403, no es solo un candado del frontend).
- **Triaje/Monitoreo/Teleconsulta** usan un motor de reglas por palabras
  clave / umbrales fijos como stand-in de Med-Gemini (documentado en
  `src/motorTriaje.js` y `src/motorAnomalias.js`), no hay modelo de IA real
  conectado.
