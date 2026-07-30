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
          placeholder={i >= 3 && !d ? "•" : ""}
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

  const [mfa, setMfa] = useState(null); 
  const [otp, setOtp] = useState(["", "", "", "", "", ""]);
  const [mfaStatus, setMfaStatus] = useState("idle");
  const [mfaError, setMfaError] = useState(null);

  const onChange = (e) => setForm((f) => ({ ...f, [e.target.name]: e.target.value }));

  const goToApp = () => {
    const redirectTo = location.state?.from?.pathname || "/dashboard";
    navigate(redirectTo, { replace: true });
  };

  const onSubmit = async (e) => {
    e.preventDefault();
    
    if (mfa) {
      onVerifyMfa();
      return;
    }

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

  const onVerifyMfa = async () => {
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

  return (
    <AuthLayout
      title="Atencion medica remota impulsada por IA clinica"
      description="Triaje inteligente, monitoreo biometrico predictivo y teleconsulta con el respaldo del motor clinico Med-Gemini."
    >
      <form onSubmit={onSubmit} noValidate>
        {location.state?.registered && !error && !mfaError && (
          <div className="banner banner-ok" role="status">
            Cuenta creada. Inicia sesion con tus credenciales.
          </div>
        )}
        {error && !mfa && (
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
            disabled={!!mfa || status === "loading"}
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
            disabled={!!mfa || status === "loading"}
          />
        </div>

        {!mfa && (
          <div className="auth-row-between">
            <label style={{ display: "flex", gap: 7, alignItems: "center", color: "#527377" }}>
              <input type="checkbox" defaultChecked /> Recordarme
            </label>
            <Link className="auth-link" to="/acceso/recuperar">
              Olvidaste tu contrasena?
            </Link>
          </div>
        )}

        {!mfa && (
          <button className="btn btn-primary btn-block" type="submit" disabled={status === "loading"}>
            {status === "loading" ? "Verificando..." : "Continuar"}
          </button>
        )}
        
        {mfa && (
          <button className="btn btn-primary btn-block" type="button" disabled style={{ opacity: 1 }}>
            Continuar
          </button>
        )}

        {mfa && (
          <>
            {mfaError && (
              <div className="banner banner-error" role="alert" style={{ marginTop: 20, marginBottom: 0 }}>
                {mfaError}
              </div>
            )}
            <div className="mfa-card" style={{ marginTop: 20 }}>
              <span className="step">Paso 2 - Verificacion en dos pasos</span>
              <p>
                Enviamos un codigo de 6 digitos a tu dispositivo móvil terminado en <b>••34</b>.
                {mfa.codigoDebug && (
                  <span style={{ display: 'block', marginTop: 4, color: '#059669' }}>
                    (Debug: <b>{mfa.codigoDebug}</b>)
                  </span>
                )}
              </p>
              <OtpInput digits={otp} setDigits={setOtp} disabled={mfaStatus === "loading"} />
              <div className="mfa-links">
                <button type="button" onClick={reenviarCodigo} disabled={mfaStatus === "loading"}>
                  Reenviar codigo en 00:28
                </button>
                <button type="button" onClick={onVerifyMfa} disabled={mfaStatus === "loading" || otp.some((d) => !d)}>
                  {mfaStatus === "loading" ? "Verificando..." : "Verificar identidad →"}
                </button>
              </div>
            </div>

            <div className="consent-row">
              <input type="checkbox" id="consent" defaultChecked />
              <label htmlFor="consent">
                Acepto la <b>Política de Privacidad (LOPDP)</b> y autorizo el tratamiento de mis datos clinicos para fines de atencion medica.
              </label>
            </div>
          </>
        )}
      </form>
      
      {!mfa && (
        <div style={{ marginTop: 30, borderTop: '1px solid var(--border)', paddingTop: 20 }}>
          <p style={{ fontSize: 11, color: 'var(--muted)', marginBottom: 10, textAlign: 'center', fontWeight: 600 }}>ACCESO RÁPIDO (DEBUG)</p>
          <div style={{ display: 'flex', gap: 10, justifyContent: 'center' }}>
            <button className="btn btn-outline btn-sm" onClick={() => setForm({ email: 'admin@samr.com', password: 'password123' })} type="button" style={{ flex: 1 }}>
              Admin
            </button>
            <button className="btn btn-outline btn-sm" onClick={() => setForm({ email: 'medico1@hospital.com', password: 'password123' })} type="button" style={{ flex: 1 }}>
              Médico
            </button>
            <button className="btn btn-outline btn-sm" onClick={() => setForm({ email: 'empleado2@empresa.com', password: 'password123' })} type="button" style={{ flex: 1 }}>
              Paciente
            </button>
          </div>
        </div>
      )}
    </AuthLayout>
  );
}

