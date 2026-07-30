const GATEWAY_URL = import.meta.env.VITE_GATEWAY_URL || "http://localhost:3000";

export class ApiError extends Error {
  constructor(message, { status = null, offline = false, cause } = {}) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.offline = offline;
    this.cause = cause;
  }
}

/**
 * Llama al API Gateway. No simula respuestas: si el backend no esta
 * disponible o el endpoint aun no existe, se propaga un ApiError para
 * que la pantalla lo muestre como estado de error, no como exito falso.
 */
export async function apiFetch(path, { method = "GET", body, token, signal } = {}) {
  const headers = { "Content-Type": "application/json" };
  if (token) headers.Authorization = `Bearer ${token}`;

  let response;
  try {
    response = await fetch(`${GATEWAY_URL}${path}`, {
      method,
      headers,
      body: body !== undefined ? JSON.stringify(body) : undefined,
      signal,
    });
  } catch (cause) {
    throw new ApiError(
      "No se pudo contactar al API Gateway. Verifica que el backend este corriendo en " +
        GATEWAY_URL,
      { offline: true, cause }
    );
  }

  const isJson = response.headers.get("content-type")?.includes("application/json");
  const data = isJson ? await response.json().catch(() => null) : null;

  if (!response.ok) {
    throw new ApiError(data?.error || `Error ${response.status} al llamar ${path}`, {
      status: response.status,
    });
  }

  return data;
}

export { GATEWAY_URL };
