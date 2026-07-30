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
- [x] Cumple el contrato openapi.yaml sin desviaciones (GET /audit/logs,
      GET /audit/logs/{id}, POST /audit/export)
- [x] Consume solicitud_triaje, alerta_biometrica_m5 y evento_auditoria
      (este ultimo agregado por m1-users y m4-telemedicine); el payload de
      cada evento queda documentado como comentario en su productor, no en
      un `shared/contracts/events/schemas.json` formal (no se creo ese
      archivo)
- [x] Cada log se almacena con hash SHA-256 y es inmutable (no hay
      endpoint de edicion/borrado)
- [x] Exportacion a PDF real (`pdfkit`) con firma de texto del DPO
- [ ] pgcrypto: no se aplico cifrado a nivel de columna todavia
- [ ] Pasa las pruebas en /tests (no hay pruebas automatizadas todavia)