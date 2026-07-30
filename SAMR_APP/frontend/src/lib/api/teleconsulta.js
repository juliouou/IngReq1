// M4 - Teleconsulta (SAMR_APP/microservices/m4-telemedicine/docs/openapi.yaml)
import { apiFetch } from "../apiClient";

export const iniciarTeleconsulta = ({ pacienteId, medicoId }, token) =>
  apiFetch("/teleconsultation", { method: "POST", body: { pacienteId, medicoId }, token });

export const registrarDiagnostico = (
  { consultaId, sugerenciaMedGemini, explanation, decisionMedico },
  token
) =>
  apiFetch("/diagnosis", {
    method: "POST",
    body: { consultaId, sugerenciaMedGemini, explanation, decisionMedico },
    token,
  });

export const emitirReceta = ({ consultaId, medicamentos }, token) =>
  apiFetch("/prescription", { method: "POST", body: { consultaId, medicamentos }, token });
