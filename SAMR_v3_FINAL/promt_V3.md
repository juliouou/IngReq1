

1. CONTEXTO

Actúa como un equipo de desarrollo experto en Ingeniería de Requisitos, arquitectura
de software médico y diseño de interfaces conversacionales con IA.

Basado en el Documento de Visión SAMR v3.2, el objetivo es construir un prototipo
vertical funcional y completo para el Sistema de Atención Médica Remota (SAMR),
transformado mediante Inteligencia Artificial — específicamente Med-Gemini como
motor clínico — e interfaces conversacionales (chatbot y voicebot).

El sistema SAMR está estructurado en 5 módulos esenciales:

  M1 — Gestión de Usuarios y Acceso
  M2 — Triaje Inteligente y Gestión de Solicitudes (Med-Gemini)
  M3 — Monitoreo Biométrico Predictivo (Med-Gemini)
  M4 — Teleconsulta y Atención Médica (Med-Gemini)
  M5 — Seguridad, Auditoría y Cumplimiento

Los 8 stakeholders clave del sistema son:
  ST01 — Paciente
  ST02 — Personal Médico
  ST03 — Personal Administrativo
  ST04 — Centro de Asistencia / Consorcio Médico
  ST05 — Ministerio de Salud Pública (MSP)
  ST06 — Oficial de Protección de Datos (DPO)
  ST07 — Equipo MLOps / Med-Gemini
  ST08 — Patrocinador (Ing. Armando Cabrera)

2. LÓGICA — FLUJO DE CASOS DE USO

Sigue estrictamente los siguientes flujos de eventos definidos en las
especificaciones de casos de uso del sistema SAMR v3.2:

M1 — GESTIÓN DE USUARIOS Y ACCESO

El Paciente solicita registrarse en el sistema SAMR.
El Sistema solicita al Paciente completar el formulario con sus datos personales
y número de afiliación al IESS.
El Paciente completa el formulario y selecciona su perfil: paciente, médico
o administrativo.
El Sistema envía un código MFA al teléfono del Paciente para verificar su identidad.
El Paciente ingresa el código MFA y el Sistema confirma la autenticación.
El Sistema consulta automáticamente la API del IESS para verificar la cobertura
activa del Paciente.
La API del IESS responde al Sistema con el estado de afiliación del Paciente.
El Sistema presenta al Paciente el formulario de consentimiento bajo la LOPDP,
con supervisión del DPO.
El Paciente acepta el consentimiento explícito y el Sistema lo registra
de forma auditable.
El Sistema activa los servicios domiciliarios y notifica al Paciente que su
registro fue exitoso.


M2 — TRIAJE INTELIGENTE Y GESTIÓN DE SOLICITUDES

El Paciente inicia contacto con el sistema a través del Bot Conversacional
por texto o voz.
El Bot Conversacional saluda al Paciente y le solicita describir sus síntomas
de forma natural.
El Paciente describe sus síntomas al Bot Conversacional.
Med-Gemini analiza la descripción de síntomas del Paciente, aplica razonamiento
clínico y clasifica la solicitud por nivel de prioridad: CRÍTICO, URGENTE,
MODERADO o LEVE.
Med-Gemini genera una explicación comprensible (XAI) del nivel de riesgo asignado.
El Bot Conversacional comunica al Paciente la clasificación y la explicación
en lenguaje simple.
Si el Bot Conversacional no puede resolver la situación, escala automáticamente
al Personal Médico, transfiriendo el contexto completo de la conversación.
El Sistema genera la solicitud de auxilio de forma asíncrona con los datos
del triaje y el historial del Paciente.
Med-Gemini ejecuta el motor de matching evaluando especialidad, disponibilidad,
ubicación y tiempo de respuesta de cada Centro de Asistencia disponible.
El Sistema asigna la solicitud al Centro de Asistencia y al Personal Médico
más idóneo.
El Paciente recibe confirmación y visualiza el estado en el panel dinámico
en tiempo real.


M3 — MONITOREO BIOMÉTRICO PREDICTIVO

El Dispositivo IoT del Paciente (EKG, EEG, oxímetro) envía lecturas biométricas
continuas al Sistema.
El Sistema procesa el flujo de datos en tiempo real con latencia máxima de
1 segundo por muestra.
Med-Gemini analiza las lecturas contra umbrales clínicos e historial biométrico
del Paciente, buscando patrones precursores de eventos críticos.
Med-Gemini detecta un patrón anómalo y genera una alerta proactiva con tipo
de anomalía, nivel de riesgo y explicación clínica.
El Sistema envía la alerta simultáneamente al Paciente, al Personal Médico
y al Centro de Asistencia asignado.
El Bot Conversacional explica al Paciente las razones de la alerta de Med-Gemini
en lenguaje comprensible, sin tecnicismos.
El Bot Conversacional guía al Paciente con los pasos a seguir mientras
llega la ayuda.
El Personal Médico evalúa el caso y decide la acción: teleconsulta o ambulancia.

M4 — TELECONSULTA Y ATENCIÓN MÉDICA

El Personal Médico recibe la notificación del caso con el resumen del triaje
y las sugerencias iniciales de Med-Gemini.
El Sistema abre el canal de teleconsulta de video y audio con latencia ≤ 200ms.
El Personal Médico visualiza el historial clínico completo del Paciente en
la misma pantalla.
Med-Gemini genera sugerencias diagnósticas con explicación XAI visible para
el Personal Médico en tiempo real.
El Personal Médico evalúa, acepta, modifica o rechaza las sugerencias de
Med-Gemini y el Sistema registra la decisión.
El Personal Médico emite la receta digital y el Sistema aplica la firma
electrónica automáticamente.
El Sistema envía la receta firmada al Paciente por app y correo electrónico.
Si el caso es crítico, el Personal Médico activa la derivación de emergencia
presencial y el Sistema notifica al Centro de Asistencia.


M5 — SEGURIDAD, AUDITORÍA Y CUMPLIMIENTO

El Paciente otorga consentimiento explícito bajo la LOPDP supervisado por el DPO.
El Sistema cifra todos los datos con AES-256 en reposo y TLS 1.3 en tránsito.
El Sistema almacena el historial clínico con retención mínima de 5 años.
El Sistema genera logs de auditoría inmutables con hash criptográfico por cada
acción, incluyendo decisiones de Med-Gemini y conversaciones con el bot.
El Equipo MLOps audita la equidad de Med-Gemini verificando ausencia de sesgos.
El MSP inspecciona los logs para certificar el comportamiento del sistema.
El DPO firma digitalmente el informe de auditoría como co-responsable del
cumplimiento de la LOPDP.


3. RESTRICCIONES NO FUNCIONALES


Asegúrate de que el prototipo cumpla con los siguientes atributos de calidad
definidos en el Documento de Visión SAMR v3.2, según las preocupaciones de
cada stakeholder:

RNF-01  SEGURIDAD (ST06 — DPO)
        Autenticación MFA obligatoria en el registro. El prototipo debe
        mostrar el flujo de verificación de identidad y el registro de
        consentimiento LOPDP de forma explícita y auditable.

RNF-03  USABILIDAD (ST01 — Paciente)
        La interfaz del paciente debe ser completable en máximo 3 pasos.
        Tasa de error de usuario ≤ 10%. El flujo del bot debe ser simple,
        claro y accesible para adultos mayores con baja alfabetización digital.

RNF-05  EFICIENCIA (ST03 — Personal Administrativo)
        El procesamiento y asignación de solicitudes debe completarse en
        ≤ 5 segundos. El panel de estados debe refrescarse visualmente
        en ≤ 500ms.

RNF-06  EFICIENCIA — Med-Gemini (ST07 — Equipo MLOps)
        Med-Gemini debe clasificar síntomas y generar la explicación XAI
        en ≤ 2 segundos desde el último mensaje del Paciente.

RNF-08  PRECISIÓN — Med-Gemini (ST02 — Personal Médico)
        La tasa de detección de anomalías biométricas debe alcanzar ≥ 98%
        con falsos positivos ≤ 2%. El prototipo debe mostrar el nivel de
        confianza de Med-Gemini en cada decisión clínica.

RNF-09  RENDIMIENTO (ST02 — Personal Médico)
        La latencia de video y audio en la teleconsulta debe ser ≤ 200ms
        en el 95% de las sesiones.

RNF-11  DISPONIBILIDAD (ST04 — Centro de Asistencia)
        El sistema debe garantizar disponibilidad ≥ 99.5%. El prototipo
        debe mostrar indicadores de estado del servicio en tiempo real.

RNF-15  EXPLICABILIDAD XAI (ST05 — MSP / ST02 — Médico)
        El 100% de las decisiones de Med-Gemini deben incluir una
        explicación comprensible. Cada sugerencia diagnóstica, clasificación
        de triaje y alerta biométrica debe mostrar el razonamiento clínico
        de Med-Gemini de forma visible en la interfaz.

RNF-16  EQUIDAD (ST07 — MLOps / ST06 — DPO)
        Med-Gemini no debe presentar sesgos discriminatorios verificables.
        El prototipo debe mostrar que las decisiones son independientes de
        la edad, género o condición socioeconómica del Paciente.


4. DATOS DE PRUEBA REALES

Utiliza los siguientes datos reales del contexto ecuatoriano para que la
validación del prototipo sea significativa:

PACIENTE:
  Nombre         : Carlos Mendoza
  Edad           : 68 años
  Cédula         : 1103456789
  Afiliación IESS: AF-2023-00451
  Condición      : Hipertensión crónica, seguimiento domiciliario
  Dispositivos   : EKG conectado activo, oxímetro
  Ubicación      : Loja, Ecuador
  Señal          : Internet doméstico estándar

PERSONAL MÉDICO:
  Nombre         : Dra. Fernanda Rodríguez
  Especialidad   : Cardiología
  Centro asignado: Centro de Asistencia Loja Norte
  Turno          : Activo — mañana

CENTROS DEL CONSORCIO:
  Centro Loja Norte    — 35% carga — cardiólogo disponible — 2.1 km
  Clínica Sur UTPL     — 78% carga — médico general        — 3.4 km
  Hospital General Loja— 52% carga — internista disponible — 3.8 km
  Centro Catamayo      — 20% carga — médico general        — 22 km

ALERTA ACTIVA (para M3):
  Tipo           : Arritmia cardíaca precursora
  Señal EKG      : Variabilidad R-R > 35ms, segmento ST elevado 1.8mm
  Confianza      : Med-Gemini 94%
  Nivel de riesgo: CRÍTICO
  Anticipación   : 8 a 12 minutos antes del evento estimado

AUDITOR MSP (para M5):
  Nombre         : Dr. Marco Villareal
  Cargo          : Director de Habilitación — MSP Zona 7
  Período        : Mayo 2026
  Registros      : 1.842 logs auditables disponibles



5. ESPECIFICACIONES TÉCNICAS POR ROL — HERRAMIENTAS Y STACK INTEGRADO


El stack tecnológico del equipo es coherente y todos los roles se integran
entre sí. El frontend consume las APIs del backend, el backend persiste en
la base de datos diseñada por el DBA, la seguridad aplica sobre todas las
capas, el arquitecto define la estructura que todos siguen, y el UX/UI
garantiza que la interfaz refleje fielmente los requisitos.

Stack general del equipo:
  Frontend   : React + Tailwind CSS (PWA responsive web y móvil)
  Backend    : Node.js + Express (API REST asíncrona)
  Base datos : PostgreSQL (relacional) + TimescaleDB (series temporales IoT)
  IA         : Med-Gemini API (Google) — integrada como servicio desacoplado
  Seguridad  : JWT + OAuth 2.0 + MFA (Authy) + cifrado AES-256 / TLS 1.3
  Auditoría  : Logs inmutables con SHA-256 almacenados en PostgreSQL
  Despliegue : Docker + Google Cloud Platform (GCP)
  Diseño     : Figma + Storybook


ARQUITECTO DE SOFTWARE — Leydi Robalino

Herramientas: Docker · Google Cloud Platform (GCP) · draw.io · C4 Model

El Arquitecto define la estructura modular que todos los demás roles siguen.
Diseña la separación de los 5 módulos (M1–M5) como microservicios independientes
desplegados en contenedores Docker sobre GCP, garantizando que cada módulo
pueda escalar, fallar y actualizarse de forma independiente (RNF-11, RNF-17).

Integración con el equipo:
  - Define los contratos de API (OpenAPI/Swagger) que el Backend implementa
    y el Frontend consume, garantizando que Med-Gemini opere como servicio
    desacoplado con versionado explícito.
  - Establece la arquitectura de datos que el DBA implementa: repositorio
    relacional (PostgreSQL) para historial clínico y logs, y TimescaleDB
    para los flujos IoT del M3.
  - Define las políticas de cifrado y autenticación que el Especialista en
    Seguridad aplica en todas las capas.
  - Garantiza que el frontend (React PWA) se comunique con el backend a través
    de endpoints REST documentados, con tiempos de respuesta que cumplan los
    RNF definidos en el Documento de Visión v3.2.


DESARROLLADOR BACKEND — Antonela Parra

Herramientas: Node.js · Express · Med-Gemini API · BullMQ · Socket.io · Swagger

El Backend implementa los contratos de API definidos por el Arquitecto y
expone los endpoints que el Frontend consume. Es responsable de integrar
Med-Gemini como servicio externo y gestionar toda la lógica de negocio.

Integración con el equipo:
  - Implementa el procesamiento asíncrono de solicitudes con BullMQ (colas
    de mensajes), garantizando ≤ 5 segundos de respuesta (RNF-05).
  - Integra la Med-Gemini API de Google para el triaje (M2), la detección
    predictiva (M3) y el soporte diagnóstico (M4), enviando el contexto
    clínico del Paciente y recibiendo la clasificación con XAI.
  - Expone endpoints WebSocket con Socket.io para que el Frontend actualice
    el panel de estados en tiempo real (≤ 500ms, RNF-04).
  - Simula las APIs del IESS y MSP con mocks realistas bajo el estándar
    HL7/FHIR que el Arquitecto especificó.
  - Genera los logs de auditoría inmutables con hash SHA-256 que el DBA
    almacena en PostgreSQL y que el Especialista en Seguridad protege.


DESARROLLADOR FRONTEND — Paula López

Herramientas: React · Tailwind CSS · Socket.io (cliente) · Figma (handoff) · Vite

El Frontend consume los endpoints REST y WebSocket del Backend y renderiza
la interfaz definida por el Diseñador UX/UI en Figma. Es una PWA responsive
que funciona en web y móvil con el mismo código base.

Integración con el equipo:
  - Consume los endpoints REST del Backend (Node.js/Express) para todos
    los módulos M1–M5, manejando estados de carga, error y éxito.
  - Se suscribe a los WebSocket de Socket.io para actualizar el panel de
    estados del M2 y las alertas biométricas del M3 en tiempo real.
  - Implementa los componentes definidos en Storybook por el UX/UI: chat
    del bot (M2), semáforo de riesgo (M3), panel médico integrado (M4) y
    tabla de auditoría (M5).
  - Aplica el cifrado en tránsito (TLS 1.3) en todas las llamadas al Backend,
    coordinado con el Especialista en Seguridad.
  - Muestra la versión activa de Med-Gemini y el nivel de confianza de cada
    decisión, recibidos del Backend, cumpliendo RNF-15 (XAI visible).


ESPECIALISTA EN SEGURIDAD — Alisson Condoy

Herramientas: JWT · OAuth 2.0 · Authy (MFA) · AES-256 · TLS 1.3 · OWASP ZAP

El Especialista en Seguridad aplica las políticas de protección en todas
las capas del stack definido por el Arquitecto: desde el Frontend hasta
la base de datos, pasando por las APIs del Backend y la integración con
Med-Gemini.

Integración con el equipo:
  - Configura OAuth 2.0 y JWT en el Backend (Node.js) para autenticar todas
    las peticiones del Frontend, con tokens de expiración configurable (RNF-01).
  - Integra Authy como proveedor MFA en el flujo de registro del M1, coordinado
    con el Frontend para mostrar el paso de verificación (RNF-01).
  - Define las políticas de cifrado AES-256 en reposo que el DBA aplica en
    PostgreSQL para el historial clínico y los logs de auditoría (RF-16).
  - Garantiza TLS 1.3 en tránsito en todas las comunicaciones: Frontend ↔
    Backend, Backend ↔ Med-Gemini API y Backend ↔ APIs IESS/MSP (RF-16).
  - Ejecuta análisis de vulnerabilidades con OWASP ZAP sobre los endpoints
    del Backend antes de cada despliegue en GCP.
ADMINISTRADOR DE BASE DE DATOS — Julio Maldonado

Herramientas: PostgreSQL · TimescaleDB · pgcrypto · DBeaver · Liquibase

El DBA diseña e implementa el modelo de datos que el Backend persiste y
consulta. Define dos repositorios especializados según la naturaleza de
los datos, siguiendo la arquitectura definida por el Arquitecto.

Integración con el equipo:
  - PostgreSQL para el historial clínico estructurado (M4), los registros
    de solicitudes (M2), los consentimientos LOPDP (M5) y los logs de
    auditoría inmutables con hash SHA-256 generados por el Backend (RF-19).
  - TimescaleDB (extensión de PostgreSQL) para los flujos de datos biométricos
    continuos del M3 (EKG, EEG, oxímetro), optimizado para series temporales
    con latencia ≤ 1 segundo (RNF-07).
  - pgcrypto para cifrado AES-256 en reposo de los datos sensibles del Paciente,
    coordinado con las políticas del Especialista en Seguridad (RF-16).
  - Liquibase para el control de versiones del esquema de base de datos,
    garantizando que los cambios del Backend no rompan la estructura existente.
  - Retención mínima de 5 años con particionamiento por fecha para los logs
    de auditoría y el historial clínico (RNF-14).


DISEÑADOR UX/UI — David León

Herramientas: Figma · Storybook · React (componentes) · Tailwind CSS · Lighthouse

El Diseñador UX/UI define la experiencia visual del sistema y entrega
los componentes documentados en Storybook que el Frontend implementa.
Es el puente entre los requisitos del Documento de Visión y la interfaz
que ven los stakeholders.

Integración con el equipo:
  - Diseña en Figma los wireframes y mockups de alta fidelidad para la vista
    del Paciente (ST01) y el Panel Médico (ST02), que el Frontend implementa
    en React + Tailwind CSS siguiendo el handoff de diseño.
  - Documenta en Storybook todos los componentes reutilizables del sistema:
    componente de chat del bot (M2), semáforo de riesgo biométrico (M3),
    XAI card de Med-Gemini (M4) y tabla de logs de auditoría (M5).
  - Define la accesibilidad de la interfaz bajo WCAG 2.1 AA, coordinando
    con el Frontend los tamaños de fuente, contraste y navegación por teclado
    para adultos mayores (ST01, RNF-03).
  - Valida el cumplimiento de RNF-03 usando Lighthouse (Google) para medir
    rendimiento, accesibilidad y PWA score de la interfaz implementada.
  - El flujo del bot (M2) debe completarse en máximo 3 pasos con botones
    grandes y opciones predefinidas, pensado para pacientes con baja
    alfabetización digital (ST01).


6. RESULTADO ESPERADO


Un prototipo web y móvil (PWA) de una sola página con navegación lateral
que incluya los siguientes módulos funcionales e interconectados:

  1. Dashboard general con métricas clave del sistema en tiempo real.
  2. M1 — Flujo de registro con MFA, validación IESS simulada y consentimiento LOPDP.
  3. M2 — Bot conversacional con triaje de Med-Gemini, clasificación de riesgo
          con XAI, matching inteligente y panel de estados.
  4. M3 — Monitoreo IoT con señales biométricas en tiempo real, alerta predictiva
          de Med-Gemini con explicación XAI y guía del bot al paciente.
  5. M4 — Teleconsulta médica con historial integrado, sugerencias de Med-Gemini
          con XAI, emisión de receta digital y derivación de emergencia.
  6. M5 — Módulo de auditoría MSP con logs inmutables, hash criptográfico,
          verificación de consentimientos LOPDP y exportación de informes.
  7. Vista móvil diferenciada para el Paciente (ST01) y el Médico (ST02).

El prototipo debe ser completamente interactivo, usar los datos reales del
contexto ecuatoriano definidos en la sección 4, mostrar explícitamente los
RNF cumplidos y demostrar la trazabilidad completa con el Documento de Visión
SAMR v3.2. Todas las decisiones de Med-Gemini deben incluir su explicación
XAI visible en la interfaz.

================================================================================
FIN DEL PROMPT — SAMR v3.2 | Equipo LLdE | UTPL | Mayo 2026
================================================================================
