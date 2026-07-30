CREATE TABLE usuarios (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  nombre VARCHAR(150) NOT NULL,
  email VARCHAR(150) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  rol VARCHAR(30) NOT NULL,
  mfa_activo BOOLEAN DEFAULT false
);

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
