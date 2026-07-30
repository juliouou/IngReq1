export interface Alerta {
  id: string;
  pacienteId: string;
  tipo: "EKG" | "EEG" | "SpO2";
  valor: number;
  timestamp: string;
}
