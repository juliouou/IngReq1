const express = require("express");
const PDFDocument = require("pdfkit");
const pool = require("./db");
const { iniciarConsumidores } = require("./queue");

const app = express();
app.use(express.json());

app.get("/health", (req, res) => res.json({ status: "ok", modulo: "m5-audit" }));

// RF: listar logs de auditoria (inmutables, con hash SHA-256)
app.get("/audit/logs", async (req, res) => {
  try {
    const result = await pool.query(
      "SELECT id, modulo_origen, actor, accion, timestamp, hash FROM auditoria ORDER BY timestamp DESC LIMIT 200"
    );
    res.json(result.rows);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// RF: consultar un log especifico
app.get("/audit/logs/:id", async (req, res) => {
  try {
    const result = await pool.query("SELECT * FROM auditoria WHERE id = $1", [req.params.id]);
    if (!result.rows[0]) return res.status(404).json({ error: "log no encontrado" });
    res.json(result.rows[0]);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// RF: exportar reporte de auditoria en PDF. La firma del DPO queda como
// campo de texto (no hay integracion real de firma digital todavia).
app.post("/audit/export", async (req, res) => {
  try {
    const result = await pool.query(
      "SELECT modulo_origen, actor, accion, timestamp, hash FROM auditoria ORDER BY timestamp DESC LIMIT 500"
    );

    res.setHeader("Content-Type", "application/pdf");
    res.setHeader("Content-Disposition", "attachment; filename=auditoria-samr.pdf");

    const doc = new PDFDocument({ margin: 40 });
    doc.pipe(res);

    doc.fontSize(16).text("SAMR - Reporte de auditoria", { align: "center" });
    doc.moveDown();
    doc
      .fontSize(9)
      .fillColor("gray")
      .text(`Generado: ${new Date().toISOString()} - Firmado por: ${req.headers["x-user-email"] || "DPO"}`);
    doc.moveDown();

    result.rows.forEach((log, i) => {
      doc
        .fillColor("black")
        .fontSize(10)
        .text(
          `${i + 1}. [${log.modulo_origen}] ${log.actor} - ${log.accion} (${new Date(
            log.timestamp
          ).toLocaleString()})`
        );
      doc.fontSize(8).fillColor("gray").text(`hash: ${log.hash}`);
      doc.moveDown(0.5);
    });

    doc.end();
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

iniciarConsumidores();

app.listen(3000, () => console.log("m5-audit escuchando en puerto 3000"));
