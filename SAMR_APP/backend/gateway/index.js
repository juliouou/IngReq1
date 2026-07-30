const express = require("express");
const { createProxyMiddleware } = require("http-proxy-middleware");
const services = require("./config/services");
const { requireAuth, requireRole } = require("./middlewares/auth");

const app = express();

// CORS: unico punto de entrada del sistema, asi que el CORS del sistema
// completo vive aqui (no en cada microservicio).
app.use((req, res, next) => {
  res.header("Access-Control-Allow-Origin", "*");
  res.header("Access-Control-Allow-Headers", "Content-Type, Authorization");
  res.header("Access-Control-Allow-Methods", "GET,POST,PUT,DELETE,OPTIONS");
  if (req.method === "OPTIONS") return res.sendStatus(204);
  next();
});

app.use((req, res, next) => {
  console.log(`[gateway] ${req.method} ${req.url}`);
  next();
});

app.get("/health", (req, res) => res.json({ status: "ok", modulo: "api-gateway" }));

function proxyTo(target) {
  return createProxyMiddleware({ target, changeOrigin: true });
}

// M1 - Usuarios y Acceso. Publico: es quien emite el JWT que todo lo demas
// necesita, y /consent + /auth/iess/verify se llaman durante el registro,
// antes de que exista una sesion.
app.use(
  ["/auth/register", "/auth/login", "/auth/mfa/verify", "/auth/iess/verify", "/auth/verify", "/consent"],
  proxyTo(services.m1)
);

// M2 - Triaje Inteligente
app.use(["/triage", "/matching"], requireAuth, proxyTo(services.m2));

// M3 - Monitoreo Biometrico
app.use(["/biometrics", "/alerts"], requireAuth, proxyTo(services.m3));

// M4 - Teleconsulta. /signaling es el upgrade a WebSocket para WebRTC: el
// JWT se valida una sola vez al abrir la conexion (ver signaling.js en M4),
// no en cada mensaje, porque el handshake de upgrade no pasa por este
// middleware de Express.
const m4Proxy = createProxyMiddleware({ target: services.m4, changeOrigin: true, ws: true });
app.use("/teleconsultation", requireAuth, m4Proxy);
app.use(["/diagnosis", "/prescription"], requireAuth, requireRole("medico"), m4Proxy);
app.use("/signaling", m4Proxy);

// M5 - Seguridad y Auditoria: solo roles con responsabilidad de supervision
app.use("/audit", requireAuth, requireRole("administrativo", "msp", "dpo"), proxyTo(services.m5));

app.use((req, res) => res.status(404).json({ error: "ruta no reconocida por el gateway" }));

const server = app.listen(3000, () => console.log("api-gateway escuchando en puerto 3000"));

server.on("upgrade", (req, socket, head) => {
  if (req.url.startsWith("/signaling")) m4Proxy.upgrade(req, socket, head);
});
