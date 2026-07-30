// M2 - Triaje Inteligente (SAMR_APP/microservices/m2-triage/docs/openapi.yaml)
import { apiFetch } from "../apiClient";

export const crearTriaje = ({ pacienteId, tipo, sintomas }, token) =>
  apiFetch("/triage", { method: "POST", body: { pacienteId, tipo, sintomas }, token });

export const solicitarMatching = ({ triageId }, token) =>
  apiFetch("/matching", { method: "POST", body: { triageId }, token });

export const consultarTriaje = (id, token) => apiFetch(`/triage/${id}`, { method: "GET", token });
