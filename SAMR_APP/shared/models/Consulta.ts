export interface Consulta {
  id: string;
  pacienteId: string;
  medicoId: string;
  fecha: string;
  estado: "programada" | "en_curso" | "finalizada";
}
