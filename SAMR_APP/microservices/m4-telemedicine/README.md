# M4 - Teleconsulta

## Responsabilidad
Canal de video/audio via WebRTC para la consulta medica, panel
paralelo con sugerencias diagnosticas XAI de Med-Gemini, y
emision de receta digital. El medico acepta, modifica o rechaza
cada sugerencia; la decision final se registra en M5.

## Tecnologia
Node.js + Express, WebRTC, adaptador hexagonal Med-Gemini,
PostgreSQL (historial clinico)

## Contrato
Ver /docs/openapi.yaml

## Eventos que publica
- evento_auditoria (cada decision medica registrada)

## Definition of Done
- [x] Cumple el contrato openapi.yaml sin desviaciones (POST
      /teleconsultation, /diagnosis, /prescription)
- [x] Video/audio real por WebRTC: `src/signaling.js` retransmite
      offer/answer/ICE por WebSocket (`/signaling`, JWT validado al conectar)
      entre los dos clientes de una misma consulta; el Gateway proxea el
      upgrade de WebSocket. Solo hay STUN publico, no TURN server.
- [x] Publica evento_auditoria en inicio de consulta, decision del medico y
      emision de receta
- [ ] Pasa las pruebas en /tests (no hay pruebas automatizadas todavia)