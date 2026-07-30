export interface Usuario {
  id: string;
  nombre: string;
  email: string;
  rol: "paciente" | "medico" | "administrativo" | "msp" | "dpo";
  mfaActivo: boolean;
}
