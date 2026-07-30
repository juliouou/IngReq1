const { Queue } = require("bullmq");

// Cada microservicio copia este helper (no hay build context compartido
// entre contenedores: cada Dockerfile solo empaqueta su propia carpeta).
const connection = {
  host: process.env.REDIS_HOST || "redis",
  port: Number(process.env.REDIS_PORT || 6379),
};

const solicitudTriajeQueue = new Queue("solicitud_triaje", { connection });

module.exports = { solicitudTriajeQueue };
