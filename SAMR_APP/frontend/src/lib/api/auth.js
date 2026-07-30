// M1 - Usuarios y Acceso (SAMR_APP/microservices/m1-users/docs/openapi.yaml)
import { apiFetch } from "../apiClient";

export const registerUsuario = ({ nombre, email, password, rol }) =>
  apiFetch("/auth/register", { method: "POST", body: { nombre, email, password, rol } });

export const login = ({ email, password }) =>
  apiFetch("/auth/login", { method: "POST", body: { email, password } });

export const verifyToken = (token) => apiFetch("/auth/verify", { method: "GET", token });

export const verifyMfa = ({ email, codigo }) =>
  apiFetch("/auth/mfa/verify", { method: "POST", body: { email, codigo } });

export const verifyIess = ({ afiliacionIess }) =>
  apiFetch("/auth/iess/verify", { method: "POST", body: { afiliacionIess } });

export const registerConsent = ({ pacienteId, estado }) =>
  apiFetch("/consent", { method: "POST", body: { pacienteId, estado } });
