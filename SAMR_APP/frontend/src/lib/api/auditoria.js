// M5 - Seguridad y Auditoria (SAMR_APP/microservices/m5-audit/docs/openapi.yaml)
import { apiFetch } from "../apiClient";

export const listarLogs = (token) => apiFetch("/audit/logs", { method: "GET", token });

export const obtenerLog = (id, token) => apiFetch(`/audit/logs/${id}`, { method: "GET", token });

export const exportarAuditoria = (token) =>
  apiFetch("/audit/export", { method: "POST", token });
