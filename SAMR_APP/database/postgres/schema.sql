CREATE TABLE usuarios (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  nombre VARCHAR(150) NOT NULL,
  email VARCHAR(150) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  rol VARCHAR(30) NOT NULL,
  mfa_activo BOOLEAN DEFAULT false
);

-- El id de pacientes es el mismo UUID que usuarios.id cuando el usuario
-- tiene rol 'paciente' (perfil clinico 1:1 sobre la cuenta de acceso).
CREATE TABLE pacientes (
  id UUID PRIMARY KEY REFERENCES usuarios(id),
  nombre VARCHAR(150) NOT NULL,
  fecha_nacimiento DATE,
  telefono VARCHAR(20),
  direccion VARCHAR(255),
  consentimiento_lopdp BOOLEAN DEFAULT false,
  cobertura_iess BOOLEAN DEFAULT false
);

CREATE TABLE codigos_mfa (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  usuario_id UUID NOT NULL REFERENCES usuarios(id),
  codigo VARCHAR(6) NOT NULL,
  expira TIMESTAMP NOT NULL,
  usado BOOLEAN DEFAULT false,
  creado TIMESTAMP NOT NULL DEFAULT now()
);

CREATE TABLE centros_asistencia (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  nombre VARCHAR(150) NOT NULL,
  ubicacion VARCHAR(255) NOT NULL,
  disponible BOOLEAN DEFAULT true
);

CREATE TABLE solicitudes_triaje (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  paciente_id UUID NOT NULL REFERENCES pacientes(id),
  tipo VARCHAR(20) NOT NULL,
  estado VARCHAR(20) NOT NULL DEFAULT 'pendiente',
  sintomas TEXT,
  prioridad VARCHAR(20),
  explanation TEXT,
  centro_id UUID REFERENCES centros_asistencia(id),
  medico_id UUID REFERENCES usuarios(id),
  tiempo_estimado VARCHAR(50),
  timestamp TIMESTAMP NOT NULL DEFAULT now()
);

CREATE TABLE alertas_biometricas (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  paciente_id UUID NOT NULL REFERENCES pacientes(id),
  tipo VARCHAR(10) NOT NULL,
  valor DOUBLE PRECISION NOT NULL,
  timestamp TIMESTAMP NOT NULL DEFAULT now()
);

CREATE TABLE consultas (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  paciente_id UUID REFERENCES pacientes(id),
  medico_id UUID REFERENCES usuarios(id),
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

CREATE TABLE auditoria (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  modulo_origen VARCHAR(50) NOT NULL,
  actor VARCHAR(150) NOT NULL,
  accion VARCHAR(255) NOT NULL,
  timestamp TIMESTAMP NOT NULL DEFAULT now(),
  hash VARCHAR(64) NOT NULL
);

CREATE INDEX idx_lecturas_alertas_paciente ON alertas_biometricas (paciente_id);
CREATE INDEX idx_auditoria_timestamp ON auditoria (timestamp);
CREATE INDEX idx_solicitudes_paciente ON solicitudes_triaje (paciente_id);

-- Datos semilla minimos para que M2 pueda hacer matching desde el primer arranque.
INSERT INTO centros_asistencia (nombre, ubicacion, disponible) VALUES
  ('Hospital UTPL Loja', 'Loja, Ecuador', true),
  ('Centro de Salud Norte', 'Loja, Ecuador', true),
  ('Clinica San Agustin', 'Loja, Ecuador', true);
