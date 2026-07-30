const express = require("express");
const bcrypt = require("bcryptjs");
const jwt = require("jsonwebtoken");
const pool = require("./db");
const { eventoAuditoriaQueue } = require("./queue");

const app = express();
app.use(express.json());

async function publicarEventoAuditoria(actor, accion) {
  await eventoAuditoriaQueue.add("evento_auditoria", {
    moduloOrigen: "m1-users",
    actor,
    accion,
    timestamp: new Date().toISOString(),
  });
}

const JWT_SECRET = process.env.JWT_SECRET;
const MFA_TTL_MINUTES = 5;
// No hay proveedor real de SMS/correo conectado todavia. En modo no
// productivo devolvemos el codigo en la respuesta para poder probar el
// flujo completo; en produccion eso se elimina y el codigo solo se envia
// por el canal externo.
const DEV_MODE = process.env.NODE_ENV !== "production";

function generarCodigoMfa() {
  return String(Math.floor(100000 + Math.random() * 900000));
}

function firmarToken(usuario) {
  return jwt.sign({ id: usuario.id, rol: usuario.rol, email: usuario.email }, JWT_SECRET, {
    expiresIn: "8h",
  });
}

app.get("/health", (req, res) => {
  res.json({ status: "ok", modulo: "m1-users" });
});

// RF: registro de usuario. Si el rol es "paciente" tambien crea su perfil
// clinico en `pacientes`, con el mismo id que `usuarios` (relacion 1:1).
app.post("/auth/register", async (req, res) => {
  const { nombre, email, password, rol } = req.body;
  if (!nombre || !email || !password || !rol) {
    return res.status(400).json({ error: "faltan campos obligatorios" });
  }
  const client = await pool.connect();
  try {
    await client.query("BEGIN");
    const hash = await bcrypt.hash(password, 10);
    const result = await client.query(
      "INSERT INTO usuarios (nombre, email, rol, password_hash) VALUES ($1, $2, $3, $4) RETURNING id, nombre, email, rol",
      [nombre, email, rol, hash]
    );
    const usuario = result.rows[0];

    if (rol === "paciente") {
      await client.query("INSERT INTO pacientes (id, nombre) VALUES ($1, $2)", [
        usuario.id,
        nombre,
      ]);
    }

    await client.query("COMMIT");
    await publicarEventoAuditoria(email, `registro de nuevo usuario (rol ${rol})`);
    res.status(201).json(usuario);
  } catch (err) {
    await client.query("ROLLBACK");
    res.status(500).json({ error: err.message });
  } finally {
    client.release();
  }
});

// RF: login, unico emisor de JWT del sistema. Si el usuario tiene MFA
// activo, no emite el token todavia: genera un codigo y pide el segundo
// factor via POST /auth/mfa/verify.
app.post("/auth/login", async (req, res) => {
  const { email, password } = req.body;
  try {
    const result = await pool.query("SELECT * FROM usuarios WHERE email = $1", [email]);
    const usuario = result.rows[0];
    if (!usuario) return res.status(401).json({ error: "credenciales invalidas" });

    const valido = await bcrypt.compare(password, usuario.password_hash);
    if (!valido) return res.status(401).json({ error: "credenciales invalidas" });

    if (usuario.mfa_activo) {
      const codigo = generarCodigoMfa();
      const expira = new Date(Date.now() + MFA_TTL_MINUTES * 60 * 1000);
      await pool.query(
        "INSERT INTO codigos_mfa (usuario_id, codigo, expira) VALUES ($1, $2, $3)",
        [usuario.id, codigo, expira]
      );
      return res.json({
        requiereMfa: true,
        email: usuario.email,
        ...(DEV_MODE ? { codigoDebug: codigo } : {}),
      });
    }

    await publicarEventoAuditoria(usuario.email, "inicio de sesion");
    res.json({ token: firmarToken(usuario) });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// RF: verificacion de segundo factor (MFA)
app.post("/auth/mfa/verify", async (req, res) => {
  const { email, codigo } = req.body;
  if (!email || !codigo) return res.status(400).json({ error: "faltan campos obligatorios" });
  try {
    const usuarioResult = await pool.query("SELECT * FROM usuarios WHERE email = $1", [email]);
    const usuario = usuarioResult.rows[0];
    if (!usuario) return res.status(401).json({ error: "credenciales invalidas" });

    const codigoResult = await pool.query(
      `SELECT * FROM codigos_mfa
       WHERE usuario_id = $1 AND codigo = $2 AND usado = false AND expira > now()
       ORDER BY creado DESC LIMIT 1`,
      [usuario.id, codigo]
    );
    const registro = codigoResult.rows[0];
    if (!registro) return res.status(401).json({ error: "codigo invalido o expirado" });

    await pool.query("UPDATE codigos_mfa SET usado = true WHERE id = $1", [registro.id]);
    await publicarEventoAuditoria(usuario.email, "inicio de sesion (con MFA)");
    res.json({ token: firmarToken(usuario) });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// RF: verificacion de cobertura IESS (mock HL7/FHIR: valida formato de
// afiliacion, no hay integracion real con el IESS todavia).
app.post("/auth/iess/verify", async (req, res) => {
  const { pacienteId, afiliacionIess } = req.body;
  if (!pacienteId || !afiliacionIess) {
    return res.status(400).json({ error: "faltan campos obligatorios" });
  }
  const elegible = /^\d{10}$/.test(String(afiliacionIess).trim());
  try {
    if (elegible) {
      await pool.query("UPDATE pacientes SET cobertura_iess = true WHERE id = $1", [pacienteId]);
    }
    res.json({
      elegible,
      mensaje: elegible
        ? "Cobertura IESS verificada."
        : "Numero de afiliacion invalido: se esperan 10 digitos. Cobertura pendiente.",
    });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// RF: registrar consentimiento LOPDP
app.post("/consent", async (req, res) => {
  const { pacienteId, estado } = req.body;
  if (!pacienteId || !estado) return res.status(400).json({ error: "faltan campos obligatorios" });
  try {
    await pool.query("UPDATE pacientes SET consentimiento_lopdp = $1 WHERE id = $2", [
      estado === "vigente",
      pacienteId,
    ]);
    await publicarEventoAuditoria(pacienteId, `actualizo consentimiento LOPDP a "${estado}"`);
    res.json({ pacienteId, estado });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// Endpoint de ejemplo para que el Gateway/otros modulos verifiquen el JWT
app.get("/auth/verify", (req, res) => {
  const authHeader = req.headers.authorization;
  if (!authHeader) return res.status(401).json({ error: "token no enviado" });
  const token = authHeader.split(" ")[1];
  try {
    const decoded = jwt.verify(token, JWT_SECRET);
    res.json({ valido: true, payload: decoded });
  } catch (err) {
    res.status(401).json({ valido: false, error: "token invalido" });
  }
});

app.listen(3000, () => console.log("m1-users escuchando en puerto 3000"));
