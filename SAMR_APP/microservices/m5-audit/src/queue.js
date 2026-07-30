const { Worker } = require("bullmq");
const crypto = require("crypto");
const pool = require("./db");

const connection = {
  host: process.env.REDIS_HOST || "redis",
  port: Number(process.env.REDIS_PORT || 6379),
};

function hashDe(payload) {
  return crypto.createHash("sha256").update(JSON.stringify(payload)).digest("hex");
}

async function actorParaPaciente(pacienteId) {
  const result = await pool.query("SELECT email FROM usuarios WHERE id = $1", [pacienteId]);
  return result.rows[0]?.email || pacienteId;
}

// Consume un evento y lo deja en `auditoria` de forma inmutable: no hay
// endpoint de edicion ni borrado en este servicio (RNF de trazabilidad).
async function registrarEvento(moduloOrigen, actor, accion, payload) {
  await pool.query(
    "INSERT INTO auditoria (modulo_origen, actor, accion, hash) VALUES ($1, $2, $3, $4)",
    [moduloOrigen, actor, accion, hashDe(payload)]
  );
}

function iniciarConsumidores() {
  const workers = [
    new Worker(
      "solicitud_triaje",
      async (job) => {
        const actor = await actorParaPaciente(job.data.pacienteId);
        await registrarEvento(
          "m2-triage",
          actor,
          `creo solicitud de triaje (${job.data.tipo}), prioridad ${job.data.prioridad}`,
          job.data
        );
      },
      { connection }
    ),
    new Worker(
      "alerta_biometrica_m5",
      async (job) => {
        const actor = await actorParaPaciente(job.data.pacienteId);
        await registrarEvento(
          "m3-monitoring",
          actor,
          `alerta biometrica ${job.data.tipo} = ${job.data.valor}`,
          job.data
        );
      },
      { connection }
    ),
    new Worker(
      "evento_auditoria",
      async (job) => {
        await registrarEvento(job.data.moduloOrigen, job.data.actor, job.data.accion, job.data);
      },
      { connection }
    ),
  ];

  workers.forEach((w) => w.on("failed", (job, err) => console.error(`[m5] job fallido:`, err)));
  return workers;
}

module.exports = { iniciarConsumidores };
