# M2 - Triaje Inteligente

## Responsabilidad
Recepcion de solicitudes (formulario de sintomas o alerta IoT),
triaje clinico via adaptador hexagonal a Med-Gemini, y matching
inteligente con centro de asistencia.

## Tecnologia
Node.js + Express, BullMQ (Redis), adaptador hexagonal Med-Gemini

## Contrato
Ver /docs/openapi.yaml
Ver /shared/contracts/openapi/med-gemini-adapter.yaml (campo
explanation obligatorio en cada respuesta de Med-Gemini)

## Eventos que publica
- solicitud_triaje (consumido por m5-audit)

## Definition of Done
- [x] Cumple el contrato openapi.yaml sin desviaciones (POST /triage,
      POST /matching, GET /triage/{id})
- [x] Publica solicitud_triaje, consumido por m5-audit
- [x] El adaptador a Med-Gemini exige el campo "explanation" en toda
      respuesta, sin excepcion (ver `src/motorTriaje.js`, stub por reglas de
      palabras clave con la misma interfaz que tendria el modelo real)
- [ ] Circuit breaker / modo degradado: no aplica todavia porque el
      adaptador es local (el stub no puede "no responder"); falta disenarlo
      para cuando se conecte un Med-Gemini real
- [ ] Pasa las pruebas en /tests (no hay pruebas automatizadas todavia)