CREATE TABLE alertas_biometricas (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  paciente_id UUID NOT NULL, -- UUID provisto por m1-users
  tipo VARCHAR(10) NOT NULL,
  valor DOUBLE PRECISION NOT NULL,
  timestamp TIMESTAMP NOT NULL DEFAULT now()
);

CREATE INDEX idx_lecturas_alertas_paciente ON alertas_biometricas (paciente_id);
