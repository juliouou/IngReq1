// Roles definidos en SAMR_APP/shared/models/Usuario.ts
export const ROLES = {
  PACIENTE: "paciente",
  MEDICO: "medico",
  ADMINISTRATIVO: "administrativo",
  MSP: "msp",
  DPO: "dpo",
};

export const ROLE_LABELS = {
  [ROLES.PACIENTE]: "Paciente",
  [ROLES.MEDICO]: "Medico",
  [ROLES.ADMINISTRATIVO]: "Administrativo",
  [ROLES.MSP]: "MSP",
  [ROLES.DPO]: "DPO",
};

// Que modulos ve cada rol en la navegacion (RF: navegacion por rol y permisos visibles)
export const NAV_ITEMS = [
  {
    to: "/triaje",
    label: "Evaluación Médica",
    icon: "chat",
    roles: [ROLES.PACIENTE, ROLES.MEDICO, ROLES.ADMINISTRATIVO],
  },
  {
    to: "/monitoreo",
    label: "Monitoreo",
    icon: "heart",
    roles: [ROLES.PACIENTE, ROLES.MEDICO, ROLES.ADMINISTRATIVO],
  },
  {
    to: "/teleconsulta",
    label: "Teleconsulta",
    icon: "video",
    roles: [ROLES.PACIENTE, ROLES.MEDICO],
  },
  {
    to: "/auditoria",
    label: "Auditoria",
    icon: "shield",
    roles: [ROLES.ADMINISTRATIVO, ROLES.MSP, ROLES.DPO],
  },
];
