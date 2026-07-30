CREATE TABLE centros_asistencia (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  nombre VARCHAR(150) NOT NULL,
  ubicacion VARCHAR(255) NOT NULL,
  disponible BOOLEAN DEFAULT true
);

CREATE TABLE solicitudes_triaje (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  paciente_id UUID NOT NULL, -- UUID provisto por m1-users
  tipo VARCHAR(20) NOT NULL,
  estado VARCHAR(20) NOT NULL DEFAULT 'pendiente',
  sintomas TEXT,
  prioridad VARCHAR(20),
  explanation TEXT,
  centro_id UUID REFERENCES centros_asistencia(id),
  medico_id UUID, -- UUID provisto por m1-users
  tiempo_estimado VARCHAR(50),
  timestamp TIMESTAMP NOT NULL DEFAULT now()
);

CREATE INDEX idx_solicitudes_paciente ON solicitudes_triaje (paciente_id);

INSERT INTO centros_asistencia (nombre, ubicacion, disponible) VALUES
  ('Hospital UTPL Loja', 'Loja, Ecuador', true),
  ('Centro de Salud Norte', 'Loja, Ecuador', true),
  ('Clinica San Agustin', 'Loja, Ecuador', true);
