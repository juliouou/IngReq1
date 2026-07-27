# M1 - Usuarios y Acceso

## Responsabilidad
Gestion exclusiva de identidad: registro, login, autenticacion
multifactor (MFA), verificacion de cobertura IESS y registro
auditable del consentimiento LOPDP. Es el unico modulo que emite
tokens JWT; todos los demas modulos consumen ese token via el
API Gateway.

## Tecnologia
Node.js + Express, OAuth 2.0 + JWT, MFA (Authy), PostgreSQL

## Contrato
Ver /docs/openapi.yaml

## Eventos que publica
- evento_auditoria (cada registro, login, cambio de consentimiento)

## Definition of Done
- Cumple el contrato openapi.yaml sin desviaciones
- Publica evento_auditoria segun /shared/contracts/events/schemas.json
- Cumple la metrica RNF asignada: registro completo en <=3 pasos,
  MFA obligatorio en cada login
- El JWT emitido es el unico valido para todo el sistema
- Pasa las pruebas en /tests