// M3 - Monitoreo Biometrico (SAMR_APP/microservices/m3-monitoring/docs/openapi.yaml)
import { apiFetch } from "../apiClient";

export const enviarLecturaBiometrica = ({ pacienteId, tipo, valor }, token) =>
  apiFetch("/biometrics", { method: "POST", body: { pacienteId, tipo, valor }, token });

export const listarAlertas = (token) => apiFetch("/alerts", { method: "GET", token });

export const generarAlerta = ({ pacienteId, tipo, valor }, token) =>
  apiFetch("/alerts", { method: "POST", body: { pacienteId, tipo, valor }, token });
