# Sistema de Atención Médica Remota (SAMR v3.2)

![SAMR](https://img.shields.io/badge/Status-Development-blue) ![Microservices](https://img.shields.io/badge/Architecture-Microservices-brightgreen) ![Node.js](https://img.shields.io/badge/Backend-Node.js-green) ![React](https://img.shields.io/badge/Frontend-React%20Vite-cyan)

El Sistema de Atención Médica Remota (SAMR) es una plataforma integral diseñada bajo los más estrictos estándares de Ingeniería de Software (IngReq1), orientada a ofrecer servicios de telemedicina, triaje inteligente con IA (Med-Gemini local), monitoreo de pacientes IoT y cumplimiento riguroso de la Ley Orgánica de Protección de Datos Personales (LOPDP) de Ecuador.

---

## 🏗️ Arquitectura del Sistema

El sistema fue diseñado desde cero para ser altamente escalable y tolerante a fallos, abandonando los monolitos tradicionales y adoptando **Tres Patrones Arquitectónicos Clave**:

1.  **Arquitectura de Microservicios:** Múltiples servicios pequeños y especializados que pueden escalar de forma independiente.
2.  **Arquitectura Orientada a Eventos (Event-Driven):** Los servicios no se bloquean esperando respuestas; se comunican de forma asíncrona usando **Redis / BullMQ**.
3.  **Arquitectura Hexagonal (Puertos y Adaptadores):** Integración limpia con sistemas externos (como la IA local de Ollama) sin acoplar la lógica de negocio central.

---

## 📁 Estructura de Directorios (Dónde está todo)

El repositorio se organiza para lograr una separación absoluta de responsabilidades:

```text
SAMR_APP/
├── frontend/               # Interfaz de usuario (React + Vite)
│   ├── src/pages/          # Módulos: Triaje, Teleconsulta, Monitoreo, etc.
│   └── src/components/     # Componentes visuales y Widget Global de IA (Chati)
│
├── backend/                # El cerebro del sistema
│   ├── api-gateway/        # (Puerto 3000) Orquestador único. Valida JWT y enruta el tráfico.
│   ├── services/           # Los 5 Microservicios independientes en Node.js (m1 a m5)
│   └── database/           # Patrón Database-per-Service (Esquemas SQL aislados)
│
├── shared/                 # Contratos (OpenAPI) y Modelos TypeScript compartidos
└── deployment/             # Orquestación con Docker Compose
```

---

## 🧠 Desglose de Microservicios (Por qué está todo)

El equipo dividió el negocio en 5 dominios independientes (Ubicados en `backend/services/`):

*   **M1 - Users & Auth (`m1-users`)**: Responsable de la seguridad, autenticación (bcrypt), generación de tokens JWT y validación biométrica MFA. Emite eventos cuando se registran pacientes.
*   **M2 - Inteligencia de Triaje (`m2-triage`)**: Motor de reglas médicas. Se conecta a la IA local (Med-Gemini / Llama 3) para procesar los síntomas ingresados por el usuario y calcular el nivel de riesgo y urgencia.
*   **M3 - Monitoreo IoT (`m3-monitoring`)**: Diseñado para integrarse con **TimescaleDB** y manejar la ingesta masiva de telemetría de dispositivos (EKG, SpO2). Si detecta anomalías, dispara alertas por Redis.
*   **M4 - Telemedicina (`m4-telemedicine`)**: Maneja la señalización (Signaling) vía WebSockets/WebRTC para videollamadas médicas y gestiona la emisión de recetas digitales.
*   **M5 - Auditoría y Legal (`m5-audit`)**: **Requisito crítico (LOPDP)**. Un servicio aislado que solo se dedica a escuchar (consumir) eventos de los demás servicios vía Redis y registrarlos con un Hash (SHA-256) inmutable para garantizar la trazabilidad legal de los datos médicos.

---

## 🔐 Decisiones de Diseño y Requisitos (IngReq1)

1.  **Privacidad In-House (IA Local):** Para cumplir con la confidencialidad de la salud del paciente, no se envían datos a OpenAI/ChatGPT. El widget "Chati" se conecta a un LLM local desplegado vía Ollama en la infraestructura del hospital.
2.  **Database-per-Service:** En lugar de una base de datos monolítica propensa a cuellos de botella, cada microservicio gestiona su propio esquema de PostgreSQL/TimescaleDB. No existen Claves Foráneas físicas entre dominios, garantizando bajo acoplamiento.
3.  **Seguridad Zero-Trust:** El frontend no tiene acceso a los microservicios. Todas las peticiones deben pasar por el `api-gateway`, el cual exige un JWT firmado y valida el rol del usuario (Role-Based Access Control).

---

## 🚀 Cómo ejecutar el proyecto (Entorno Local)

1.  Asegúrate de tener **Docker** y **Node.js** instalados.
2.  Enciende el backend con Docker Compose (levanta Gateway, M1-M5, Postgres, Redis, TimescaleDB):
    ```bash
    cd deployment
    docker-compose up -d --build
    ```
3.  Enciende la Inteligencia Artificial (en una terminal separada):
    ```bash
    ollama run llama3
    ```
4.  Inicia el Frontend:
    ```bash
    cd frontend
    npm install
    npm run dev
    ```

El portal estará disponible en `http://localhost:5173` y el API Gateway en `http://localhost:3000`.