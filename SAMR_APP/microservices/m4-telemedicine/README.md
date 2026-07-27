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
- Cumple el contrato openapi.yaml sin desviaciones
- Med-Gemini nunca esta en el path critico del stream de video
- Publica evento_auditoria por cada decision del medico
- Cumple la metrica RNF asignada: latencia de video <=200ms,
  XAI <=2s, ambos de forma simultanea
- Pasa las pruebas en /tests