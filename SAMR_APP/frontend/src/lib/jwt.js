// Decodifica el payload de un JWT solo para uso en UI (rol, email, id).
// La validacion real de la firma la hace el backend en cada peticion.
export function decodeJwtPayload(token) {
  try {
    const [, payload] = token.split(".");
    const json = atob(payload.replace(/-/g, "+").replace(/_/g, "/"));
    return JSON.parse(json);
  } catch {
    return null;
  }
}
