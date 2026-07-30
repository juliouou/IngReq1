const { Queue, Worker } = require("bullmq");

const connection = {
  host: process.env.REDIS_HOST || "redis",
  port: Number(process.env.REDIS_PORT || 6379),
};

const eventoAuditoriaQueue = new Queue("evento_auditoria", { connection });

// M3 -. eventos .-> M4: el contexto clinico reciente se deja en el log del
// contenedor. No hay pantalla que hoy consuma esto desde M4; el objetivo es
// que el medico vea la alerta durante la consulta si el frontend llega a
// pedirlo mas adelante.
function iniciarConsumidorAlertas() {
  return new Worker(
    "alerta_biometrica_m4",
    async (job) => {
      console.log(
        `[m4] alerta biometrica recibida para contexto clinico: paciente=${job.data.pacienteId} tipo=${job.data.tipo} valor=${job.data.valor}`
      );
    },
    { connection }
  );
}

module.exports = { eventoAuditoriaQueue, iniciarConsumidorAlertas };
