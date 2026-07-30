export interface Consentimiento {
  id: string;
  pacienteId: string;
  estado: "vigente" | "revocado";
  firmaDPO: string;
  fecha: string;
}
