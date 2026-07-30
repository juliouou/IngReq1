const express = require("express");
const app = express();
app.get("/health", (req, res) => res.json({ status: "ok", modulo: "m5-audit" }));
app.listen(3000, () => console.log("m5-audit escuchando en puerto 3000"));
