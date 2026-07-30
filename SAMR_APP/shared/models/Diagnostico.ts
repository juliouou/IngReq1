export interface Diagnostico {
  id: string;
  consultaId: string;
  sugerenciaMedGemini: string;
  explanation: string;
  decisionMedico: "aceptado" | "modificado" | "rechazado";
}
