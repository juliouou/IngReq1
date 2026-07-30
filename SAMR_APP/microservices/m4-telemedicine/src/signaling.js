const { WebSocketServer } = require("ws");
const jwt = require("jsonwebtoken");
const { URL } = require("url");

const JWT_SECRET = process.env.JWT_SECRET;

// Servidor de senalizacion WebRTC (RF-13). No transporta audio/video (eso
// va peer-a-peer entre los navegadores); solo retransmite offer/answer/ICE
// candidates entre los dos clientes que comparten el mismo consultaId.
function iniciarSignaling(server) {
  const wss = new WebSocketServer({ server, path: "/signaling" });
  const salas = new Map(); // consultaId -> Set<ws>

  wss.on("connection", (ws, req) => {
    const url = new URL(req.url, "http://localhost");
    const consultaId = url.searchParams.get("room");
    const token = url.searchParams.get("token");

    if (!consultaId || !token) {
      ws.close(4000, "faltan parametros room/token");
      return;
    }
    try {
      jwt.verify(token, JWT_SECRET);
    } catch {
      ws.close(4001, "token invalido");
      return;
    }

    if (!salas.has(consultaId)) salas.set(consultaId, new Set());
    const sala = salas.get(consultaId);
    sala.add(ws);

    ws.on("message", (data) => {
      for (const peer of sala) {
        if (peer !== ws && peer.readyState === peer.OPEN) peer.send(data.toString());
      }
    });

    ws.on("close", () => {
      sala.delete(ws);
      if (sala.size === 0) salas.delete(consultaId);
    });
  });

  return wss;
}

module.exports = { iniciarSignaling };
