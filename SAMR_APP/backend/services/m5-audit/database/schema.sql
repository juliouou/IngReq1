CREATE TABLE auditoria (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  modulo_origen VARCHAR(50) NOT NULL,
  actor VARCHAR(150) NOT NULL,
  accion VARCHAR(255) NOT NULL,
  timestamp TIMESTAMP NOT NULL DEFAULT now(),
  hash VARCHAR(64) NOT NULL
);

CREATE INDEX idx_auditoria_timestamp ON auditoria (timestamp);
