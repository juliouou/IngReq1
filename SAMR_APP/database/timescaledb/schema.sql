CREATE TABLE lecturas_biometricas (
  tiempo TIMESTAMPTZ NOT NULL DEFAULT now(),
  paciente_id UUID NOT NULL,
  tipo VARCHAR(10) NOT NULL,
  valor DOUBLE PRECISION NOT NULL
);

SELECT create_hypertable('lecturas_biometricas', 'tiempo');
