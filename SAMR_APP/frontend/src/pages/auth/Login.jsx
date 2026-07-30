import { useRef, useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { AuthLayout } from "./AuthLayout";
import { useAuth } from "../../context/AuthContext";
import { ApiError } from "../../lib/apiClient";
import * as authApi from "../../lib/api/auth";

function OtpInput({ digits, setDigits, disabled }) {
  const refs = useRef([]);
  const onDigitChange = (i, value) => {
    const clean = value.replace(/\D/g, "").slice(-1);
    const next = [...digits];
    next[i] = clean;
    setDigits(next);
    if (clean && i < 5) refs.current[i + 1]?.focus();
  };
  const onKeyDown = (i, e) => {
    if (e.key === "Backspace" && !digits[i] && i > 0) refs.current[i - 1]?.focus();
  };

  return (
    <div className="otp">
      {digits.map((d, i) => (
        <input
          key={i}
          ref={(el) => (refs.current[i] = el)}
          value={d}
          onChange={(e) => onDigitChange(i, e.target.value)}
          onKeyDown={(e) => onKeyDown(i, e)}
          disabled={disabled}
          inputMode="numeric"
          maxLength={1}
          aria-label={`Digito ${i + 1} del codigo`}
        />
      ))}
    </div>
  );
}

export function Login() {
  const { login, verifyMfaAndLogin } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [form, setForm] = useState({ email: "", password: "" });
  const [status, setStatus] = useState("idle");
  const [error, setError] = useState(null);

  const [mfa, setMfa] = useState(null); // { email, codigoDebug } | null
  const [otp, setOtp] = useState(["", "", "", "", "", ""]);
  const [mfaStatus, setMfaStatus] = useState("idle");
  const [mfaError, setMfaError] = useState(null);

  const onChange = (e) => setForm((f) => ({ ...f, [e.target.name]: e.target.value }));

  const goToApp = () => {
    const redirectTo = location.state?.from?.pathname || "/";
    navigate(redirectTo, { replace: true });
  };

  const onSubmit = async (e) => {
    e.preventDefault();
    setStatus("loading");
    setError(null);
    try {
      const result = await login(form.email, form.password);
      if (result.requiereMfa) {
        setMfa({ email: result.email, codigoDebug: result.codigoDebug });
        setStatus("idle");
      } else {
        goToApp();
      }
    } catch (err) {
      setStatus("error");
      setError(err instanceof ApiError ? err.message : "No se pudo iniciar sesion. Intenta de nuevo.");
    }
  };

  const onVerifyMfa = async (e) => {
    e.preventDefault();
    setMfaStatus("loading");
    setMfaError(null);
    try {
      await verifyMfaAndLogin(mfa.email, otp.join(""));
      goToApp();
    } catch (err) {
      setMfaStatus("error");
      setMfaError(err instanceof ApiError ? err.message : "No se pudo verificar el codigo.");
    }
  };

  const reenviarCodigo = async () => {
    setMfaError(null);
    try {
      const result = await authApi.login({ email: form.email, password: form.password });
      if (result?.requiereMfa) setMfa({ email: result.email, codigoDebug: result.codigoDebug });
    } catch (err) {
      setMfaError(err instanceof ApiError ? err.message : "No se pudo reenviar el codigo.");
    }
  };

  if (mfa) {
    return (
      <AuthLayout
        title="Verificacion en dos pasos"
        description="Ingresa el codigo de 6 digitos que enviamos a tu dispositivo para confirmar tu identidad."
      >
        <form onSubmit={onVerifyMfa} noValidate>
          {mfaError && (
            <div className="banner banner-error" role="alert">
              {mfaError}
            </div>
          )}
          <div className="mfa-card">
            <span className="step">Paso 2 - Verificacion en dos pasos</span>
            <p>
              Enviamos un codigo de 6 digitos a la cuenta <b>{mfa.email}</b>.
              {mfa.codigoDebug && (
                <>
                  {" "}
                  No hay un proveedor de SMS conectado todavia; en modo desarrollo el codigo es{" "}
                  <b>{mfa.codigoDebug}</b>.
                </>
              )}
            </p>
            <OtpInput digits={otp} setDigits={setOtp} disabled={mfaStatus === "loading"} />
            <div className="mfa-links">
              <button type="button" onClick={reenviarCodigo}>
                Reenviar codigo
              </button>
              <button type="button" onClick={() => setMfa(null)}>
                Volver
              </button>
            </div>
          </div>
          <button
            className="btn btn-primary btn-block"
            type="submit"
            style={{ marginTop: 18 }}
            disabled={mfaStatus === "loading" || otp.some((d) => !d)}
          >
            {mfaStatus === "loading" ? "Verificando..." : "Verificar identidad"}
          </button>
        </form>
      </AuthLayout>
    );
  }

  return (
    <AuthLayout
      title="Atencion medica remota impulsada por IA clinica"
      description="Triaje inteligente, monitoreo biometrico predictivo y teleconsulta con el respaldo del motor clinico Med-Gemini."
    >
      <form onSubmit={onSubmit} noValidate>
        {location.state?.registered && !error && (
          <div className="banner banner-ok" role="status">
            Cuenta creada. Inicia sesion con tus credenciales.
          </div>
        )}
        {error && (
          <div className="banner banner-error" role="alert">
            {error}
          </div>
        )}

        <div className="field">
          <label htmlFor="email">Correo electronico o usuario</label>
          <input
            id="email"
            name="email"
            type="email"
            required
            autoComplete="username"
            placeholder="nombre@correo.com"
            value={form.email}
            onChange={onChange}
          />
        </div>
        <div className="field">
          <label htmlFor="password">Contrasena</label>
          <input
            id="password"
            name="password"
            type="password"
            required
            autoComplete="current-password"
            placeholder="Tu contrasena"
            value={form.password}
            onChange={onChange}
          />
        </div>

        <div className="auth-row-between">
          <label style={{ display: "flex", gap: 7, alignItems: "center", color: "#527377" }}>
            <input type="checkbox" defaultChecked /> Recordarme
          </label>
          <Link className="auth-link" to="/acceso/recuperar">
            Olvidaste tu contrasena?
          </Link>
        </div>

        <button className="btn btn-primary btn-block" type="submit" disabled={status === "loading"}>
          {status === "loading" ? "Verificando..." : "Continuar"}
        </button>
      </form>
    </AuthLayout>
  );
}
