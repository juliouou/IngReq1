import { NavLink } from "react-router-dom";

const TABS = [
  { to: "/acceso", label: "Iniciar sesión" },
  { to: "/acceso/registro", label: "Registrarme" },
];

export function AuthLayout({ title, description, children }) {
  return (
    <div className="auth-page-split">
      <div className="auth-hero-side">
        <div className="auth-hero-overlay"></div>
        <div className="auth-hero-content">
          <div className="auth-logo-hero">
            <img src="/logo.png" alt="SAMR Logo" style={{ width: '80px', height: '80px', objectFit: 'contain' }} />
          </div>
          <h1>{title}</h1>
          <p>{description}</p>
          
          <div className="auth-badges-hero">
            <span>ISO/IEC/IEEE 29148</span>
            <span>LOPDP compliant</span>
            <span>Integracion IESS</span>
          </div>
        </div>
      </div>

      <div className="auth-form-side">
        <div className="auth-form-container">
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

          <div className="auth-footer-text">
            2026 SAMR - Sistema de Atención Médica Remota
          </div>
        </div>
      </div>
    </div>
  );
}
