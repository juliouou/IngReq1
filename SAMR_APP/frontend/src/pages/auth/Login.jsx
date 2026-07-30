import { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { AuthLayout } from "./AuthLayout";
import { useAuth } from "../../context/AuthContext";
import { ApiError } from "../../lib/apiClient";

export function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [form, setForm] = useState({ email: "", password: "" });
  const [status, setStatus] = useState("idle");
  const [error, setError] = useState(null);

  const onChange = (e) => setForm((f) => ({ ...f, [e.target.name]: e.target.value }));

  const onSubmit = async (e) => {
    e.preventDefault();
    setStatus("loading");
    setError(null);
    try {
      await login(form.email, form.password);
      const redirectTo = location.state?.from?.pathname || "/";
      navigate(redirectTo, { replace: true });
    } catch (err) {
      setStatus("error");
      setError(
        err instanceof ApiError
          ? err.message
          : "No se pudo iniciar sesion. Intenta de nuevo."
      );
    }
  };

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

        <p className="helper" style={{ marginTop: 16 }}>
          Este formulario llama a <code>POST /auth/login</code> en el API Gateway. Si el
          Gateway o M1 aun no estan corriendo localmente, veras el error de conexion arriba
          en vez de un acceso simulado.
        </p>
      </form>
    </AuthLayout>
  );
}
