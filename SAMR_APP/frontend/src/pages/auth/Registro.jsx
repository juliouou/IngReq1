import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { AuthLayout } from "./AuthLayout";
import * as authApi from "../../lib/api/auth";
import { ApiError } from "../../lib/apiClient";
import { ROLES, ROLE_LABELS } from "../../lib/roles";

const initialForm = {
  nombre: "",
  email: "",
  password: "",
  confirmPassword: "",
  rol: ROLES.PACIENTE,
  afiliacionIess: "",
  dispositivoIot: "vincular_luego",
  consiente: false,
};

export function Registro() {
  const navigate = useNavigate();
  const [form, setForm] = useState(initialForm);
  const [status, setStatus] = useState("idle");
  const [error, setError] = useState(null);
  const [warnings, setWarnings] = useState([]);

  const onChange = (e) => {
    const { name, type, checked, value } = e.target;
    setForm((f) => ({ ...f, [name]: type === "checkbox" ? checked : value }));
  };

  const onSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setWarnings([]);

    if (form.password !== form.confirmPassword) {
      setError("Las contrasenas no coinciden.");
      return;
    }
    if (!form.consiente) {
      setError("Debes aceptar la Politica de Privacidad (LOPDP) para continuar.");
      return;
    }

    setStatus("loading");
    try {
      const usuario = await authApi.registerUsuario({
        nombre: form.nombre,
        email: form.email,
        password: form.password,
        rol: form.rol,
      });

      const pendientes = [];
      try {
        await authApi.registerConsent({ pacienteId: usuario?.id, estado: "vigente" });
      } catch (err) {
        pendientes.push(`Consentimiento LOPDP: ${err.message}`);
      }
      if (form.afiliacionIess) {
        try {
          await authApi.verifyIess({ pacienteId: usuario?.id, afiliacionIess: form.afiliacionIess });
        } catch (err) {
          pendientes.push(`Verificacion IESS: ${err.message}`);
        }
      }

      if (pendientes.length) {
        setWarnings(pendientes);
      }
      navigate("/acceso", { state: { registered: true } });
    } catch (err) {
      setStatus("error");
      setError(
        err instanceof ApiError ? err.message : "No se pudo completar el registro."
      );
    }
  };

  return (
    <AuthLayout
      title="Crea tu cuenta y vincula tus dispositivos IoT"
      description="Tu numero de afiliacion IESS nos permite validar cobertura e historial clinico de forma automatica."
    >
      <form onSubmit={onSubmit} noValidate>
        {error && (
          <div className="banner banner-error" role="alert">
            {error}
          </div>
        )}
        {warnings.length > 0 && (
          <div className="banner banner-warn" role="status">
            Cuenta creada. Algunos pasos secundarios aun no responden en el backend:{" "}
            {warnings.join(" | ")}
          </div>
        )}

        <div className="field-row">
          <div className="field">
            <label htmlFor="nombre">Nombres completos</label>
            <input
              id="nombre"
              name="nombre"
              required
              placeholder="Maria Fernanda Ochoa"
              value={form.nombre}
              onChange={onChange}
            />
          </div>
          <div className="field">
            <label htmlFor="rol">Rol</label>
            <select id="rol" name="rol" value={form.rol} onChange={onChange}>
              {Object.values(ROLES).map((rol) => (
                <option key={rol} value={rol}>
                  {ROLE_LABELS[rol]}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div className="field-row">
          <div className="field">
            <label htmlFor="reg-email">Correo electronico</label>
            <input
              id="reg-email"
              name="email"
              type="email"
              required
              placeholder="nombre@correo.com"
              value={form.email}
              onChange={onChange}
            />
          </div>
          <div className="field">
            <label htmlFor="afiliacionIess">N. de afiliacion IESS (opcional)</label>
            <input
              id="afiliacionIess"
              name="afiliacionIess"
              placeholder="0102030405"
              value={form.afiliacionIess}
              onChange={onChange}
            />
          </div>
        </div>

        <div className="field-row">
          <div className="field">
            <label htmlFor="reg-password">Contrasena</label>
            <input
              id="reg-password"
              name="password"
              type="password"
              required
              minLength={8}
              placeholder="Minimo 8 caracteres"
              value={form.password}
              onChange={onChange}
            />
          </div>
          <div className="field">
            <label htmlFor="confirmPassword">Confirmar contrasena</label>
            <input
              id="confirmPassword"
              name="confirmPassword"
              type="password"
              required
              placeholder="Repite tu contrasena"
              value={form.confirmPassword}
              onChange={onChange}
            />
          </div>
        </div>

        <div className="iot-box">
          <div className="t">Vincular dispositivo IoT (opcional)</div>
          <select name="dispositivoIot" value={form.dispositivoIot} onChange={onChange}>
            <option value="smartwatch">Smartwatch - monitoreo cardiaco</option>
            <option value="banda_presion">Banda de presion arterial</option>
            <option value="vincular_luego">Vincular mas tarde</option>
          </select>
          <div className="helper">
            El emparejamiento real de dispositivos lo hace M3 (Monitoreo) una vez tengas
            sesion iniciada; aqui solo guardamos tu preferencia inicial.
          </div>
        </div>

        <div className="consent-row">
          <input
            type="checkbox"
            name="consiente"
            checked={form.consiente}
            onChange={onChange}
            required
          />
          <span>
            Acepto la <b>Politica de Privacidad (LOPDP)</b> y los terminos de uso del sistema
            SAMR.
          </span>
        </div>

        <button className="btn btn-primary btn-block" type="submit" disabled={status === "loading"}>
          {status === "loading" ? "Creando cuenta..." : "Crear cuenta"}
        </button>
      </form>
    </AuthLayout>
  );
}
