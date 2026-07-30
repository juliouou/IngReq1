CREATE TABLE consultas (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  paciente_id UUID NOT NULL, -- UUID provisto por m1-users
  medico_id UUID NOT NULL,   -- UUID provisto por m1-users
  fecha TIMESTAMP NOT NULL,
  estado VARCHAR(30) NOT NULL
);

CREATE TABLE diagnosticos (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  consulta_id UUID REFERENCES consultas(id),
  sugerencia_medgemini TEXT,
  explanation TEXT NOT NULL,
  decision_medico VARCHAR(30) NOT NULL
);

CREATE TABLE recetas (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  consulta_id UUID REFERENCES consultas(id),
  medicamentos JSONB NOT NULL,
  fecha_emision TIMESTAMP NOT NULL DEFAULT now()
);
