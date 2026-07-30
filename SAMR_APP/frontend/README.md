# SAMR - Frontend

Cliente web del Sistema de Atencion Medica Remota. Construido con React + Vite,
consume el API Gateway (`backend/gateway/`) que enruta a los microservicios
M1-M5. No incluye backend propio ni datos simulados presentados como reales:
cada pantalla llama al endpoint documentado en el `docs/openapi.yaml` del
microservicio correspondiente y expone el resultado real (carga, error, vacio
o exito).

## Requisitos

- Node.js 18+
- El API Gateway corriendo en `http://localhost:3000` (ver
  `SAMR_APP/deployment/docker-compose.yml`) para que las pantallas puedan
  recibir datos reales.

## Instalacion y ejecucion

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
      context/         -> sesion (token JWT + usuario decodificado)
      components/layout -> sidebar, topbar, shell de la app
      routes/          -> rutas protegidas por sesion y por rol
      pages/auth       -> login, registro, recuperacion de acceso
      pages/triaje     -> M2
      pages/monitoreo  -> M3
      pages/teleconsulta -> M4
      pages/auditoria  -> M5 (solo administrativo, msp, dpo)

## Modulos cubiertos (ver SAMR_APP/README.md)

| Modulo | Pantalla | Endpoints que consume |
| --- | --- | --- |
| M1 - Usuarios y Acceso | `/acceso`, `/acceso/registro`, `/acceso/recuperar` | `POST /auth/register`, `POST /auth/login`, `POST /consent`, `POST /auth/iess/verify` |
| M2 - Triaje Inteligente | `/triaje` | `POST /triage` |
| M3 - Monitoreo Biometrico | `/monitoreo` | `POST /biometrics`, `GET /alerts`, `POST /alerts` |
| M4 - Teleconsulta | `/teleconsulta` | `POST /teleconsultation`, `POST /diagnosis`, `POST /prescription` |
| M5 - Seguridad y Auditoria | `/auditoria` | `GET /audit/logs`, `GET /audit/logs/{id}`, `POST /audit/export` |

Navegacion e items visibles en el sidebar cambian segun el rol del usuario
autenticado (`paciente`, `medico`, `administrativo`, `msp`, `dpo`), definido en
`src/lib/roles.js` a partir de `shared/models/Usuario.ts`.

## Decisiones y limitaciones conocidas

El backend hoy es un esqueleto (ver "Estado real del repositorio" en
`SAMR_APP/README.md`): el Gateway solo expone `/health` y todavia no enruta a
M1-M5, M1 solo implementa `register`/`login`/`verify`, y M2-M5 solo exponen
`/health`. Por eso, con el Gateway apagado o sin rutas conectadas, cada
pantalla va a mostrar su estado de error real (banner rojo, "no se pudo
contactar al Gateway"), no una version simulada de exito. Esto es intencional:
en cuanto Backend/Seguridad conecten cada endpoint, el frontend ya deberia
consumirlo sin cambios.

Puntos abiertos que dependen de otros roles del equipo:

- **Recuperacion de acceso**: la pantalla existe (`/acceso/recuperar`) pero
  `M1/docs/openapi.yaml` no define un endpoint de reset de contrasena; falta
  que Arquitectura/Backend lo agreguen al contrato.
- **MFA (`POST /auth/mfa/verify`)**: el cliente ya esta implementado en
  `lib/api/auth.js`, pero no hay una pantalla dedicada porque M1 aun no
  devuelve una senal de "requiere MFA" al hacer login.
- **Vinculacion real de dispositivos IoT**: el formulario de registro guarda
  la preferencia localmente; el emparejamiento real le corresponde a M3.
- **Monitoreo en vivo**: M3 solo expone ingesta (`POST /biometrics`) y
  alertas (`GET/POST /alerts`), no un endpoint para leer signos vitales en
  tiempo real. La pantalla incluye un simulador que envia lecturas reales via
  `POST /biometrics` y las muestra como "ultimo envio", nunca como si vinieran
  de un GET del backend.
- **Almacenamiento del JWT**: se mantiene solo en memoria (se pierde al
  recargar la pagina) hasta que Seguridad defina la practica recomendada de
  persistencia en cliente.
- **Video WebRTC real**: M4 aun no implementa senalizacion; la pantalla de
  teleconsulta muestra la vista previa de camara/microfono local real via
  `getUserMedia`, pero no hay conexion peer a peer todavia.
