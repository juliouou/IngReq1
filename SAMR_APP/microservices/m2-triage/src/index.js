const express = require("express");
const pool = require("./db");
const { clasificarSintomas } = require("./motorTriaje");
const { solicitudTriajeQueue } = require("./queue");

const app = express();
app.use(express.json());

app.get("/health", (req, res) => res.json({ status: "ok", modulo: "m2-triage" }));

async function asignarCentroYMedico(client) {
  const centro = await client.query(
    "SELECT id, nombre FROM centros_asistencia WHERE disponible = true ORDER BY random() LIMIT 1"
  );
  const medico = await client.query(
    "SELECT id, nombre FROM usuarios WHERE rol = 'medico' ORDER BY random() LIMIT 1"
  );
  return { centro: centro.rows[0] || null, medico: medico.rows[0] || null };
}

// RF: registrar solicitud de triaje (sintomas del chat o alerta IoT),
// clasificar con el adaptador Med-Gemini, hacer matching con un centro y
// publicar el evento solicitud_triaje para M5.
app.post("/triage", async (req, res) => {
  const { pacienteId, tipo, sintomas } = req.body;
  if (!pacienteId || !tipo) return res.status(400).json({ error: "faltan campos obligatorios" });

  const client = await pool.connect();
  try {
    const clasificacion = clasificarSintomas(sintomas, tipo);
    const { centro, medico } = await asignarCentroYMedico(client);

    const result = await client.query(
      `INSERT INTO solicitudes_triaje
         (paciente_id, tipo, estado, sintomas, prioridad, explanation, centro_id, medico_id, tiempo_estimado)
       VALUES ($1, $2, 'en_proceso', $3, $4, $5, $6, $7, $8)
       RETURNING id, timestamp`,
      [
        pacienteId,
        tipo,
        sintomas || null,
        clasificacion.prioridad,
        clasificacion.explanation,
        centro?.id || null,
        medico?.id || null,
        clasificacion.tiempoEstimado,
      ]
    );
    const solicitud = result.rows[0];

    await solicitudTriajeQueue.add("solicitud_triaje", {
      id: solicitud.id,
      pacienteId,
      tipo,
      prioridad: clasificacion.prioridad,
      timestamp: solicitud.timestamp,
    });

    res.status(201).json({
      id: solicitud.id,
      estado: "en_proceso",
      prioridad: clasificacion.prioridad,
      tiempoEstimado: clasificacion.tiempoEstimado,
      explanation: clasificacion.explanation,
      sintomasDetectados: clasificacion.sintomasDetectados,
      centroAsignado: centro?.nombre || null,
      medicoAsignado: medico?.nombre || null,
    });
  } catch (err) {
    res.status(500).json({ error: err.message });
  } finally {
    client.release();
  }
});

// RF: (re)hacer matching de una solicitud existente con un centro/medico
app.post("/matching", async (req, res) => {
  const { triageId } = req.body;
  if (!triageId) return res.status(400).json({ error: "falta triageId" });

  const client = await pool.connect();
  try {
    const { centro, medico } = await asignarCentroYMedico(client);
    const result = await client.query(
      `UPDATE solicitudes_triaje SET centro_id = $1, medico_id = $2 WHERE id = $3
       RETURNING id`,
      [centro?.id || null, medico?.id || null, triageId]
    );
    if (!result.rows[0]) return res.status(404).json({ error: "solicitud no encontrada" });

    res.json({
      id: triageId,
      centroAsignado: centro?.nombre || null,
      medicoAsignado: medico?.nombre || null,
    });
  } catch (err) {
    res.status(500).json({ error: err.message });
  } finally {
    client.release();
  }
});

// RF: consultar estado de un triaje
app.get("/triage/:id", async (req, res) => {
  try {
    const result = await pool.query(
      `SELECT s.id, s.tipo, s.estado, s.sintomas, s.prioridad, s.explanation, s.tiempo_estimado,
              s.timestamp, c.nombre AS centro_nombre, u.nombre AS medico_nombre
       FROM solicitudes_triaje s
       LEFT JOIN centros_asistencia c ON c.id = s.centro_id
       LEFT JOIN usuarios u ON u.id = s.medico_id
       WHERE s.id = $1`,
      [req.params.id]
    );
    const solicitud = result.rows[0];
    if (!solicitud) return res.status(404).json({ error: "solicitud no encontrada" });

    res.json({
      id: solicitud.id,
      tipo: solicitud.tipo,
      estado: solicitud.estado,
      prioridad: solicitud.prioridad,
      tiempoEstimado: solicitud.tiempo_estimado,
      explanation: solicitud.explanation,
      centroAsignado: solicitud.centro_nombre,
      medicoAsignado: solicitud.medico_nombre,
      timestamp: solicitud.timestamp,
    });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

app.listen(3000, () => console.log("m2-triage escuchando en puerto 3000"));
