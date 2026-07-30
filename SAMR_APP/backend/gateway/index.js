const express = require("express");
const app = express();
app.get("/health", (req, res) => res.json({ status: "ok", modulo: "api-gateway" }));
app.listen(3000, () => console.log("api-gateway escuchando en puerto 3000"));
