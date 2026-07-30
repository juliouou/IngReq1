const express = require("express");
const bcrypt = require("bcryptjs");
const jwt = require("jsonwebtoken");
const pool = require("./db");

const app = express();
app.use(express.json());

// TEMPORAL: habilita CORS para que un frontend en otro origen (ej. Vite en
// :5173) pueda llamar a este servicio mientras el Gateway no enruta todavia.
// El Gateway va a necesitar lo mismo cuando conecte sus rutas a M1-M5.
app.use((req, res, next) => {
  res.header("Access-Control-Allow-Origin", "*");
  res.header("Access-Control-Allow-Headers", "Content-Type, Authorization");
  res.header("Access-Control-Allow-Methods", "GET,POST,PUT,DELETE,OPTIONS");
  if (req.method === "OPTIONS") return res.sendStatus(204);
  next();
});

const JWT_SECRET = process.env.JWT_SECRET;

app.get("/health", (req, res) => {
  res.json({ status: "ok", modulo: "m1-users" });
});

// RF: registro de usuario
app.post("/auth/register", async (req, res) => {
  const { nombre, email, password, rol } = req.body;
  if (!nombre || !email || !password || !rol) {
    return res.status(400).json({ error: "faltan campos obligatorios" });
  }
  try {
    const hash = await bcrypt.hash(password, 10);
    const result = await pool.query(
      "INSERT INTO usuarios (nombre, email, rol, password_hash) VALUES ($1, $2, $3, $4) RETURNING id, nombre, email, rol",
      [nombre, email, rol, hash]
    );
    res.status(201).json(result.rows[0]);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// RF: login, unico emisor de JWT del sistema
app.post("/auth/login", async (req, res) => {
  const { email, password } = req.body;
  try {
    const result = await pool.query("SELECT * FROM usuarios WHERE email = $1", [email]);
    const usuario = result.rows[0];
    if (!usuario) return res.status(401).json({ error: "credenciales invalidas" });

    const valido = await bcrypt.compare(password, usuario.password_hash);
    if (!valido) return res.status(401).json({ error: "credenciales invalidas" });

    const token = jwt.sign(
      { id: usuario.id, rol: usuario.rol, email: usuario.email },
      JWT_SECRET,
      { expiresIn: "8h" }
    );
    res.json({ token });
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
