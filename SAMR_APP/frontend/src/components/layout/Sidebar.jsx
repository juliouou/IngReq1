import { NavLink } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";
import { NAV_ITEMS, ROLE_LABELS } from "../../lib/roles";
import { Icon } from "../ui/Icon";

export function Sidebar({ className = "" }) {
  const { user, logout } = useAuth();
  const items = NAV_ITEMS.filter((item) => !user?.rol || item.roles.includes(user.rol));
  const initials = (user?.email || "??").slice(0, 2).toUpperCase();

  return (
    <aside className={`sidebar ${className}`.trim()}>
      <div className="logo">
        <span className="mark">S</span>SAMR
      </div>

      <NavLink to="/" end className={({ isActive }) => `nav-item${isActive ? " active" : ""}`}>
        <span className="ic"><Icon name="home" /></span>Inicio
      </NavLink>
      {items.map((item) => (
        <NavLink
          key={item.to}
          to={item.to}
          className={({ isActive }) => `nav-item${isActive ? " active" : ""}`}
        >
          <span className="ic"><Icon name={item.icon} /></span>
          {item.label}
        </NavLink>
      ))}

      <div className="divider" />

      <div className="patient-card">
        <div className="id">
          <div className="avatar">{initials}</div>
          <div style={{ minWidth: 0 }}>
            <div className="name" title={user?.email}>{user?.email || "Usuario"}</div>
            <div className="role">{ROLE_LABELS[user?.rol] || user?.rol}</div>
          </div>
        </div>
        <button className="logout" type="button" onClick={logout}>
          Salir
        </button>
      </div>
    </aside>
  );
}
