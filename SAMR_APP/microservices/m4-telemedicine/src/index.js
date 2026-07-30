const http = require("http");
const express = require("express");
const pool = require("./db");
const { eventoAuditoriaQueue, iniciarConsumidorAlertas } = require("./queue");
const { iniciarSignaling } = require("./signaling");

const app = express();
app.use(express.json());

app.get("/health", (req, res) => res.json({ status: "ok", modulo: "m4-telemedicine" }));

function actorDe(req) {
  return req.headers["x-user-email"] || "desconocido";
}

async function publicarEventoAuditoria(req, accion) {
  await eventoAuditoriaQueue.add("evento_auditoria", {
    moduloOrigen: "m4-telemedicine",
    actor: actorDe(req),
    accion,
    timestamp: new Date().toISOString(),
  });
}

// RF: iniciar teleconsulta
app.post("/teleconsultation", async (req, res) => {
  const { pacienteId, medicoId } = req.body;
  if (!pacienteId || !medicoId) return res.status(400).json({ error: "faltan campos obligatorios" });
  try {
    const result = await pool.query(
      "INSERT INTO consultas (paciente_id, medico_id, fecha, estado) VALUES ($1, $2, now(), 'en_curso') RETURNING id, estado, fecha",
      [pacienteId, medicoId]
    );
    const consulta = result.rows[0];
    await publicarEventoAuditoria(req, `inicio teleconsulta ${consulta.id}`);
    res.status(201).json({ id: consulta.id, pacienteId, medicoId, estado: consulta.estado });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// RF: registrar decision del medico (con XAI de Med-Gemini). El campo
// explanation es obligatorio, sin excepcion (igual que en M2).
app.post("/diagnosis", async (req, res) => {
  const { consultaId, sugerenciaMedGemini, explanation, decisionMedico } = req.body;
  if (!consultaId || !explanation || !decisionMedico) {
    return res.status(400).json({ error: "faltan campos obligatorios (explanation es obligatorio)" });
  }
  try {
    const result = await pool.query(
      `INSERT INTO diagnosticos (consulta_id, sugerencia_medgemini, explanation, decision_medico)
       VALUES ($1, $2, $3, $4) RETURNING id`,
      [consultaId, sugerenciaMedGemini || null, explanation, decisionMedico]
    );
    await publicarEventoAuditoria(
      req,
      `medico ${decisionMedico} la sugerencia de diagnostico para consulta ${consultaId}`
    );
    res.status(201).json({ id: result.rows[0].id, consultaId, decisionMedico });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// RF: emitir receta digital
app.post("/prescription", async (req, res) => {
  const { consultaId, medicamentos } = req.body;
  if (!consultaId || !Array.isArray(medicamentos) || medicamentos.length === 0) {
    return res.status(400).json({ error: "faltan campos obligatorios" });
  }
  try {
    const result = await pool.query(
      `INSERT INTO recetas (consulta_id, medicamentos) VALUES ($1, $2)
       RETURNING id, fecha_emision`,
      [consultaId, JSON.stringify(medicamentos)]
    );
    await pool.query("UPDATE consultas SET estado = 'finalizada' WHERE id = $1", [consultaId]);
    await publicarEventoAuditoria(req, `receta digital emitida para consulta ${consultaId}`);
    res.status(201).json({
      id: result.rows[0].id,
      consultaId,
      medicamentos,
      fechaEmision: result.rows[0].fecha_emision,
    });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

const server = http.createServer(app);
iniciarSignaling(server);
iniciarConsumidorAlertas();

server.listen(3000, () => console.log("m4-telemedicine escuchando en puerto 3000"));
