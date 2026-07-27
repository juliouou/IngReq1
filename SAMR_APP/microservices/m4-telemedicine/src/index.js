const express = require("express");
const app = express();
app.get("/health", (req, res) => res.json({ status: "ok", modulo: "m4-telemedicine" }));
app.listen(3000, () => console.log("m4-telemedicine escuchando en puerto 3000"));
