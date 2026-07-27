# M5 - Seguridad y Auditoria

## Responsabilidad
Bus de auditoria transversal: consume los eventos de auditoria
de todos los demas modulos, los hashea con SHA-256 y los
almacena de forma inmutable. Ningun modulo controla su propio
rastro; M5 es el unico custodio.

## Tecnologia
Node.js + Express, PostgreSQL + pgcrypto, BullMQ (Redis) como
consumidor

## Contrato
Ver /docs/openapi.yaml

## Eventos que consume
- solicitud_triaje (de m2-triage)
- alerta_biometrica (de m3-monitoring)
- evento_auditoria (de m1-users y m4-telemedicine)

## Definition of Done
- Cumple el contrato openapi.yaml sin desviaciones
- Consume todos los eventos definidos en
  /shared/contracts/events/schemas.json sin perder ninguno
- Cada log se almacena con hash SHA-256 y es inmutable
  (sin metodo de edicion/borrado expuesto)
- Cumple la metrica RNF asignada: cumplimiento LOPDP, logs
  auditables exportables para el MSP
- Pasa las pruebas en /tests