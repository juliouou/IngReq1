CREATE TABLE usuarios (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  nombre VARCHAR(150) NOT NULL,
  email VARCHAR(150) UNIQUE NOT NULL,
  rol VARCHAR(30) NOT NULL,
  mfa_activo BOOLEAN DEFAULT false
);

CREATE TABLE pacientes (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  nombre VARCHAR(150) NOT NULL,
  fecha_nacimiento DATE,
  telefono VARCHAR(20),
  direccion VARCHAR(255),
  consentimiento_lopdp BOOLEAN DEFAULT false,
  cobertura_iess BOOLEAN DEFAULT false
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

CREATE TABLE auditoria (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  modulo_origen VARCHAR(50) NOT NULL,
  actor VARCHAR(150) NOT NULL,
  accion VARCHAR(255) NOT NULL,
  timestamp TIMESTAMP NOT NULL DEFAULT now(),
  hash VARCHAR(64) NOT NULL
);
