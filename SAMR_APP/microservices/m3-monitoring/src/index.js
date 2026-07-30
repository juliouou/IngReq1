const express = require("express");
const { pool, timescalePool } = require("./db");
const { detectarAnomalia } = require("./motorAnomalias");
const { alertaBiometricaM4Queue, alertaBiometricaM5Queue } = require("./queue");

const app = express();
app.use(express.json());

app.get("/health", (req, res) => res.json({ status: "ok", modulo: "m3-monitoring" }));

async function publicarAlerta(alerta) {
  const payload = {
    id: alerta.id,
    pacienteId: alerta.paciente_id,
    tipo: alerta.tipo,
    valor: alerta.valor,
    timestamp: alerta.timestamp,
  };
  await Promise.all([
    alertaBiometricaM4Queue.add("alerta_biometrica", payload),
    alertaBiometricaM5Queue.add("alerta_biometrica", payload),
  ]);
}

// RF: ingesta de datos biometricos (IoT). Guarda la serie de tiempo en
// TimescaleDB y, si el valor esta fuera de rango, genera una alerta y
// publica el evento alerta_biometrica.
app.post("/biometrics", async (req, res) => {
  const { pacienteId, tipo, valor } = req.body;
  if (!pacienteId || !tipo || valor === undefined) {
    return res.status(400).json({ error: "faltan campos obligatorios" });
  }
  try {
    await timescalePool.query(
      "INSERT INTO lecturas_biometricas (paciente_id, tipo, valor) VALUES ($1, $2, $3)",
      [pacienteId, tipo, valor]
    );

    const anomalia = detectarAnomalia(tipo, valor);
    let alertaCreada = null;
    if (anomalia) {
      const result = await pool.query(
        "INSERT INTO alertas_biometricas (paciente_id, tipo, valor) VALUES ($1, $2, $3) RETURNING id, paciente_id, tipo, valor, timestamp",
        [pacienteId, tipo, valor]
      );
      alertaCreada = result.rows[0];
      await publicarAlerta(alertaCreada);
    }

    res.status(201).json({ recibido: true, anomalia });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// RF: listar alertas activas
app.get("/alerts", async (req, res) => {
  try {
    const result = await pool.query(
      "SELECT id, paciente_id, tipo, valor, timestamp FROM alertas_biometricas ORDER BY timestamp DESC LIMIT 50"
    );
    res.json(
      result.rows.map((a) => ({
        id: a.id,
        pacienteId: a.paciente_id,
        tipo: a.tipo,
        valor: a.valor,
        timestamp: a.timestamp,
      }))
    );
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// RF: generar alerta biometrica manualmente (ej. boton de emergencia)
app.post("/alerts", async (req, res) => {
  const { pacienteId, tipo, valor } = req.body;
  if (!pacienteId || !tipo || valor === undefined) {
    return res.status(400).json({ error: "faltan campos obligatorios" });
  }
  try {
    const result = await pool.query(
      "INSERT INTO alertas_biometricas (paciente_id, tipo, valor) VALUES ($1, $2, $3) RETURNING id, paciente_id, tipo, valor, timestamp",
      [pacienteId, tipo, valor]
    );
    const alerta = result.rows[0];
    await publicarAlerta(alerta);
    res.status(201).json({
      id: alerta.id,
      pacienteId: alerta.paciente_id,
      tipo: alerta.tipo,
      valor: alerta.valor,
      timestamp: alerta.timestamp,
    });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

app.listen(3000, () => console.log("m3-monitoring escuchando en puerto 3000"));
