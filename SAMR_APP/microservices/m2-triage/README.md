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
- Cumple el contrato openapi.yaml sin desviaciones
- Publica solicitud_triaje segun /shared/contracts/events/schemas.json
- El adaptador a Med-Gemini exige el campo "explanation" en toda
  respuesta, sin excepcion
- Incluye circuit breaker: si Med-Gemini no responde, el modulo
  sigue operativo en modo degradado (sin sugerencia de IA)
- Cumple la metrica RNF asignada: panel de estados <=500ms,
  clasificacion XAI <=2s
- Pasa las pruebas en /tests