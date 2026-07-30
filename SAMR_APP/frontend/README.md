# SAMR - Frontend

Cliente web del Sistema de Atencion Medica Remota. Construido con React + Vite,
consume el API Gateway (`backend/gateway/`) que enruta a los microservicios
M1-M5. No incluye datos simulados presentados como reales: cada pantalla llama
al endpoint documentado en el `docs/openapi.yaml` del microservicio
correspondiente y expone el resultado real (carga, error, vacio o exito).

## Requisitos

- Node.js 18+
- El stack completo corriendo via Docker Compose (ver
  `SAMR_APP/deployment/docker-compose.yml`): Gateway, M1-M5, Postgres,
  TimescaleDB y Redis.

## Instalacion y ejecucion

    # 1. Backend completo
    cd SAMR_APP/deployment
    docker compose up -d --build
    docker exec -i <contenedor-postgres> psql -U postgres -d samr_clinico < ../database/postgres/schema.sql
    docker exec -i <contenedor-timescaledb> psql -U postgres -d samr_iot < ../database/timescaledb/schema.sql

    # 2. Frontend
    cd SAMR_APP/frontend
    npm install
    cp .env.example .env
    npm run dev

La app queda disponible en `http://localhost:5173`.

## Variables de entorno

- `VITE_GATEWAY_URL`: URL base del API Gateway. Por defecto
  `http://localhost:3000`.

## Estructura

    src/
      lib/api/        -> un archivo por microservicio (auth, triaje, monitoreo,
                          teleconsulta, auditoria), 1:1 con cada docs/openapi.yaml
      lib/apiClient.js -> fetch wrapper compartido, no fabrica respuestas
      lib/useApi.js    -> hooks de loading/error/success reutilizados en cada pantalla
      lib/useWebRtcCall.js -> videollamada real contra la senalizacion de M4
      context/         -> sesion (token JWT + usuario decodificado)
      components/layout -> sidebar, topbar, shell de la app (con nav movil)
      components/ui/Icon.jsx -> set propio de iconos SVG (sin emojis)
      routes/          -> rutas protegidas por sesion y por rol
      pages/auth       -> login (con paso de MFA), registro, recuperacion de acceso
      pages/triaje     -> M2
      pages/monitoreo  -> M3
      pages/teleconsulta -> M4
      pages/auditoria  -> M5 (solo administrativo, msp, dpo)

## Modulos cubiertos (ver SAMR_APP/README.md)

| Modulo | Pantalla | Endpoints que consume |
| --- | --- | --- |
| M1 - Usuarios y Acceso | `/acceso`, `/acceso/registro`, `/acceso/recuperar` | `POST /auth/register`, `POST /auth/login`, `POST /auth/mfa/verify`, `POST /auth/iess/verify`, `POST /consent` |
| M2 - Triaje Inteligente | `/triaje` | `POST /triage` |
| M3 - Monitoreo Biometrico | `/monitoreo` | `POST /biometrics`, `GET /alerts`, `POST /alerts` |
| M4 - Teleconsulta | `/teleconsulta` | `POST /teleconsultation`, `POST /diagnosis`, `POST /prescription`, WebSocket `/signaling` |
| M5 - Seguridad y Auditoria | `/auditoria` | `GET /audit/logs`, `GET /audit/logs/{id}`, `POST /audit/export` |

Navegacion e items visibles en el sidebar cambian segun el rol del usuario
autenticado (`paciente`, `medico`, `administrativo`, `msp`, `dpo`), definido en
`src/lib/roles.js` a partir de `shared/models/Usuario.ts`. El Gateway tambien
aplica autorizacion por rol (`/audit/*` y `/diagnosis`+`/prescription`), no es
solo cosmetica del frontend.

## Decisiones y limitaciones conocidas

- **Recuperacion de acceso**: la pantalla existe (`/acceso/recuperar`) pero
  M1 no define un endpoint de reset de contrasena en su contrato; muestra un
  aviso explicito en vez de fingir que envio instrucciones.
- **Vinculacion de dispositivos IoT en el registro**: el formulario guarda la
  preferencia localmente; el emparejamiento real es un dispositivo llamando a
  `POST /biometrics` directamente (lo que hace el simulador de Monitoreo).
- **Monitoreo en vivo**: M3 no tiene un endpoint de lectura en tiempo real,
  solo ingesta (`POST /biometrics`) y alertas. La pantalla incluye un
  simulador que envia lecturas reales y las muestra como "ultimo envio", no
  como si vinieran de un GET del backend.
- **Almacenamiento del JWT**: se mantiene solo en memoria (se pierde al
  recargar la pagina); decision provisional hasta que Seguridad defina la
  practica recomendada de persistencia en cliente.
- **MFA en modo desarrollo**: no hay proveedor real de SMS/correo conectado
  en M1, asi que el codigo de un solo uso se muestra en la propia pantalla
  (`codigoDebug`) para poder probar el flujo. En produccion eso se retira.
- **Video WebRTC real, sin TURN server**: la senalizacion (`/signaling`) y la
  conexion peer-a-peer son reales (`getUserMedia` + `RTCPeerConnection`),
  pero solo hay un STUN publico configurado; en redes con NAT restrictivo la
  llamada puede no conectar.
