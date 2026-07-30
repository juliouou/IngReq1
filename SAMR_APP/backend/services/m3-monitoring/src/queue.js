const { Queue } = require("bullmq");

const connection = {
  host: process.env.REDIS_HOST || "redis",
  port: Number(process.env.REDIS_PORT || 6379),
};

// El evento alerta_biometrica lo consumen dos modulos distintos (M4 y M5).
// BullMQ reparte cada job a un solo worker por cola, asi que para lograr el
// fan-out del diagrama de arquitectura se publica en dos colas separadas
// en vez de una compartida.
const alertaBiometricaM4Queue = new Queue("alerta_biometrica_m4", { connection });
const alertaBiometricaM5Queue = new Queue("alerta_biometrica_m5", { connection });

module.exports = { alertaBiometricaM4Queue, alertaBiometricaM5Queue };
