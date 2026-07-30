import { NavLink } from "react-router-dom";
import { useState } from "react";
import { useAuth } from "../../context/AuthContext";
import { Icon } from "../ui/Icon";
import { ROLES } from "../../lib/roles";
import { useNotifications } from "../NotificationContext";
import { NotificationsPanel } from "../NotificationsPanel";

export function Topbar() {
  const { user, logout } = useAuth();
  const initials = (user?.email || "??").slice(0, 2).toUpperCase();
  const esMedico = user?.rol === ROLES.MEDICO;
  const esAdmin = [ROLES.ADMINISTRATIVO, ROLES.MSP, ROLES.DPO].includes(user?.rol);

  const getLinks = () => {
    if (esAdmin) {
      return [
        { to: "/dashboard", label: "Panel", icon: "home" },
        { to: "/triaje", label: "Evaluación Médica", icon: "clipboard" },
        { to: "/monitoreo", label: "Monitoreo", icon: "activity" },
        { to: "/auditoria", label: "Auditoría", icon: "shield" }
      ];
    } else if (esMedico) {
      return [
        { to: "/dashboard", label: "Panel", icon: "home" },
        { to: "/pacientes", label: "Pacientes", icon: "users" },
        { to: "/calendario", label: "Citas Calendario", icon: "calendar" },
        { to: "/triaje", label: "Evaluación Médica", icon: "clipboard" },
        { to: "/teleconsulta", label: "Teleconsulta", icon: "video" },
        { to: "/monitoreo", label: "Monitoreo", icon: "activity" }
      ];
    } else {
      return [
        { to: "/dashboard", label: "Panel", icon: "home" },
        { to: "/triaje", label: "Evaluación Médica", icon: "clipboard" },
        { to: "/teleconsulta", label: "Teleconsulta", icon: "video" },
        { to: "/monitoreo", label: "Monitoreo", icon: "activity" },
        { to: "/hospitales", label: "Clínicas Cercanas", icon: "map-pin" },
        { to: "/recetas", label: "Mis Recetas", icon: "file-text" }
      ];
    }
  };

  const links = getLinks();
  const { notifications, addNotification } = useNotifications();
  const [showNotis, setShowNotis] = useState(false);

  const unreadCount = notifications.filter(n => !n.read).length;

  const triggerTestAlert = () => {
    addNotification({
      title: esMedico ? "¡ALERTA CRÍTICA: Anomalía Cardíaca!" : "¡Nueva receta médica emitida!",
      message: esMedico ? "El paciente Carlos Ruiz registra una caída drástica en saturación de oxígeno (SpO2: 88%)" : "El Dr. Flores ha emitido una nueva receta para su tratamiento.",
      type: "error",
      critical: true
    });
  };

  return (
    <div className="topbar-main">
      <div className="topbar-main-inner container">
        <div className="topbar-brand">
          <NavLink to="/dashboard" style={{ display: 'flex', alignItems: 'center' }}>
            <img src="/logo.png" alt="SAMR Logo" className="topbar-logo-img" />
          </NavLink>
        </div>
        
        <nav className="topbar-nav">
          {links.map((link) => (
            <NavLink
              key={link.to}
              to={link.to}
              className={({ isActive }) => `topbar-tab${isActive ? " active" : ""}`}
            >
              <Icon name={link.icon} size={16} />
              <span>{link.label}</span>
            </NavLink>
          ))}
        </nav>

        <div className="topbar-right" style={{ position: 'relative' }}>
          <button className="btn btn-ghost btn-sm" onClick={triggerTestAlert} style={{ color: '#ef4444', border: '1px solid #ef4444' }} title="Simular Alerta Crítica (Demo)">
            <Icon name="alert-triangle" size={14} /> 
          </button>
          
          <button className="btn btn-ghost" onClick={() => setShowNotis(!showNotis)} style={{ position: 'relative', color: 'var(--white)', padding: '6px 10px' }}>
            <Icon name="bell" size={18} />
            {unreadCount > 0 && (
              <span style={{ position: 'absolute', top: 2, right: 4, background: '#ef4444', color: '#fff', fontSize: 10, fontWeight: 'bold', width: 16, height: 16, borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                {unreadCount}
              </span>
            )}
          </button>

          {showNotis && <NotificationsPanel onClose={() => setShowNotis(false)} />}

          <div className="topbar-user" style={{ borderLeft: '1px solid rgba(255,255,255,0.2)', paddingLeft: 16, marginLeft: 8 }}>
            <Icon name="user" size={14} />
            <span>{user?.email}</span>
          </div>
          <button className="topbar-logout" onClick={logout} title="Salir">
            <Icon name="log-out" size={16} />
            <span>Salir</span>
          </button>
        </div>
      </div>
    </div>
  );
}
