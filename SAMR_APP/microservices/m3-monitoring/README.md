# M3 - Monitoreo Biometrico

## Responsabilidad
Ingesta continua de datos IoT (EKG, EEG, SpO2), deteccion
predictiva de anomalias via Med-Gemini, y distribucion simultanea
de alertas a paciente, medico y centro de asistencia.

## Tecnologia
Node.js + Express, TimescaleDB, BullMQ (Redis), adaptador
hexagonal Med-Gemini

## Contrato
Ver /docs/openapi.yaml

## Eventos que publica
- alerta_biometrica (consumido por m4-telemedicine y m5-audit)

## Definition of Done
- Cumple el contrato openapi.yaml sin desviaciones
- Publica alerta_biometrica segun /shared/contracts/events/schemas.json
- La notificacion llega simultaneamente a paciente, medico y
  centro de asistencia, no en secuencia
- Cumple la metrica RNF asignada: latencia de ingesta/consulta
  IoT <=1s, precision de deteccion >=98%
- Pasa las pruebas en /tests
