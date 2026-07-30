export interface Solicitud {
  id: string;
  pacienteId: string;
  tipo: "sintomas" | "alerta_iot";
  estado: "pendiente" | "en_proceso" | "resuelta";
  timestamp: string;
}
