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
- [x] Cumple el contrato openapi.yaml sin desviaciones (POST /biometrics,
      GET/POST /alerts)
- [x] Publica alerta_biometrica en dos colas separadas (`alerta_biometrica_m4`
      y `alerta_biometrica_m5`) para que ambos modulos la reciban: BullMQ
      reparte cada job a un solo worker por cola, asi que el fan-out se logra
      duplicando la cola, no compartiendola
- [x] Deteccion de anomalias por umbral (`src/motorAnomalias.js`, mismo
      patron de stub que M2)
- [ ] Tipos de signo vital: el modelo compartido (`shared/models/Alerta.ts`)
      declara `"EKG" | "EEG" | "SpO2"`, pero eso son tipos de examen, no
      lecturas continuas de un wearable. Se implemento con los signos que
      realmente ingiere un smartwatch/banda de presion (`FC`, `SPO2`,
      `TA_SIS`, `TEMP`); falta reconciliar el modelo compartido con esto.
- [ ] Pasa las pruebas en /tests (no hay pruebas automatizadas todavia)
