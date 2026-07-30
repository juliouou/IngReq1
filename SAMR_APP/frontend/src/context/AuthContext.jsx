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

  const completeLogin = useCallback((jwtToken) => {
    const payload = decodeJwtPayload(jwtToken);
    setToken(jwtToken);
    setUser(payload);
    return payload;
  }, []);

  // Paso 1: credenciales. Si el usuario tiene MFA activo, M1 no devuelve
  // token todavia sino { requiereMfa: true }; la sesion se completa en
  // verifyMfaAndLogin.
  const login = useCallback(
    async (email, password) => {
      const data = await authApi.login({ email, password });
      if (data?.requiereMfa) return { requiereMfa: true, email: data.email, codigoDebug: data.codigoDebug };
      if (!data?.token) throw new Error("El backend no devolvio un token valido.");
      return { requiereMfa: false, payload: completeLogin(data.token) };
    },
    [completeLogin]
  );

  // Paso 2 (solo si login() pidio MFA): codigo de un solo uso.
  const verifyMfaAndLogin = useCallback(
    async (email, codigo) => {
      const data = await authApi.verifyMfa({ email, codigo });
      if (!data?.token) throw new Error("El backend no devolvio un token valido.");
      return completeLogin(data.token);
    },
    [completeLogin]
  );

  const logout = useCallback(() => {
    setToken(null);
    setUser(null);
  }, []);

  const value = useMemo(
    () => ({ token, user, isAuthenticated: Boolean(token), login, verifyMfaAndLogin, logout }),
    [token, user, login, verifyMfaAndLogin, logout]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth debe usarse dentro de AuthProvider");
  return ctx;
}
