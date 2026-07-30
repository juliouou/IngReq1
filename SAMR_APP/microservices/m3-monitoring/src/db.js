const { Pool } = require("pg");

// Postgres clinico: alertas_biometricas (relacionadas con pacientes).
const pool = new Pool({
  host: process.env.DB_HOST,
  port: process.env.DB_PORT,
  user: process.env.DB_USER,
  password: process.env.DB_PASSWORD,
  database: process.env.DB_NAME,
});

// TimescaleDB: lecturas_biometricas (hypertable de series de tiempo IoT).
const timescalePool = new Pool({
  host: process.env.TIMESCALE_HOST,
  port: process.env.TIMESCALE_PORT,
  user: process.env.TIMESCALE_USER,
  password: process.env.TIMESCALE_PASSWORD,
  database: process.env.TIMESCALE_NAME,
});

module.exports = { pool, timescalePool };
