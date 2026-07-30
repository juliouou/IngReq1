import { createContext, useCallback, useContext, useMemo, useState } from "react";
import * as authApi from "../lib/api/auth";
import { decodeJwtPayload } from "../lib/jwt";

const AuthContext = createContext(null);

// El token se mantiene solo en memoria (no localStorage/sessionStorage):
// decision provisional hasta que Seguridad defina la practica recomendada
// de almacenamiento en cliente (ver GUIA_EQUIPO.2, seccion Paula - Frontend).
export function AuthProvider({ children }) {
  const [token, setToken] = useState(null);
  const [user, setUser] = useState(null);

  const login = useCallback(async (email, password) => {
    const data = await authApi.login({ email, password });
    if (!data?.token) {
      throw new Error("El backend no devolvio un token valido.");
    }
    const payload = decodeJwtPayload(data.token);
    setToken(data.token);
    setUser(payload);
    return payload;
  }, []);

  const logout = useCallback(() => {
    setToken(null);
    setUser(null);
  }, []);

  const value = useMemo(
    () => ({ token, user, isAuthenticated: Boolean(token), login, logout }),
    [token, user, login, logout]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth debe usarse dentro de AuthProvider");
  return ctx;
}
