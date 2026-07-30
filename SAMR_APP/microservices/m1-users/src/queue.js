const { Queue } = require("bullmq");

const connection = {
  host: process.env.REDIS_HOST || "redis",
  port: Number(process.env.REDIS_PORT || 6379),
};

const eventoAuditoriaQueue = new Queue("evento_auditoria", { connection });

module.exports = { eventoAuditoriaQueue };
