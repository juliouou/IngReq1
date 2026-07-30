const express = require("express");
const app = express();
app.get("/health", (req, res) => res.json({ status: "ok", modulo: "m2-triage" }));
app.listen(3000, () => console.log("m2-triage escuchando en puerto 3000"));
