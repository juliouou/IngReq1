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
- [x] Cumple el contrato openapi.yaml sin desviaciones (register, login,
      mfa/verify, iess/verify, consent)
- [x] Publica evento_auditoria en registro, login y cambio de consentimiento
- [ ] MFA obligatorio en cada login: hoy es opcional por usuario
      (`usuarios.mfa_activo`), no forzado globalmente. No hay proveedor real
      de SMS/correo; el codigo se ve en la respuesta en modo desarrollo.
- [x] El JWT emitido es el unico valido para todo el sistema
- [ ] Pasa las pruebas en /tests (no hay pruebas automatizadas todavia)