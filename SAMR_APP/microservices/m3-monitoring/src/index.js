const express = require("express");
const app = express();
app.get("/health", (req, res) => res.json({ status: "ok", modulo: "m3-monitoring" }));
app.listen(3000, () => console.log("m3-monitoring escuchando en puerto 3000"));
