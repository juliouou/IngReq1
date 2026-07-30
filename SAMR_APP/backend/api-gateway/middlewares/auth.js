const jwt = require("jsonwebtoken");

const JWT_SECRET = process.env.JWT_SECRET;

// RF: rechaza (401) cualquier peticion sin JWT valido antes de enrutar a M1-M5.
function requireAuth(req, res, next) {
  const authHeader = req.headers.authorization;
  if (!authHeader) return res.status(401).json({ error: "token no enviado" });

  const token = authHeader.split(" ")[1];
  try {
    const payload = jwt.verify(token, JWT_SECRET);
    req.usuario = payload;
    // El Gateway ya valido la firma; los microservicios confian en estas
    // cabeceras en vez de reverificar el JWT (el Gateway es el unico punto
    // de entrada).
    req.headers["x-user-id"] = payload.id;
    req.headers["x-user-rol"] = payload.rol;
    req.headers["x-user-email"] = payload.email;
    next();
  } catch (err) {
    res.status(401).json({ error: "token invalido o expirado" });
  }
}

// RF: reglas de acceso por rol y por modulo (usar despues de requireAuth).
function requireRole(...rolesPermitidos) {
  return (req, res, next) => {
    if (!rolesPermitidos.includes(req.usuario?.rol)) {
      return res.status(403).json({ error: "rol no autorizado para este recurso" });
    }
    next();
  };
}

module.exports = { requireAuth, requireRole };
