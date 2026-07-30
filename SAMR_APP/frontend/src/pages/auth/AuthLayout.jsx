import { NavLink } from "react-router-dom";

const TABS = [
  { to: "/acceso", label: "Iniciar sesion" },
  { to: "/acceso/registro", label: "Registrarme" },
];

export function AuthLayout({ title, description, children }) {
  return (
    <div className="auth-page">
      <div className="auth-device">
        <div className="auth-shell">
          <div className="auth-brand">
            <div>
              <div className="logo">
                <span className="mark">S</span>SAMR
              </div>
              <h1>{title}</h1>
              <p>{description}</p>
              <div className="auth-badges">
                <span>ISO/IEC/IEEE 29148</span>
                <span>LOPDP compliant</span>
                <span>Integracion IESS</span>
              </div>
            </div>
            <div className="foot">2026 SAMR - Sistema de Atencion Medica Remota</div>
          </div>

          <div className="auth-form-side">
            <div className="auth-tabs">
              {TABS.map((tab) => (
                <NavLink
                  key={tab.to}
                  to={tab.to}
                  end
                  className={({ isActive }) => `auth-tab${isActive ? " on" : ""}`}
                >
                  {tab.label}
                </NavLink>
              ))}
            </div>
            {children}
          </div>
        </div>
      </div>
    </div>
  );
}
