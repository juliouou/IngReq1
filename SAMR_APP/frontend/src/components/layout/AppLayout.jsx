import { useEffect, useState } from "react";
import { Outlet, useLocation } from "react-router-dom";
import { Sidebar } from "./Sidebar";
import { Icon } from "../ui/Icon";

export function AppLayout() {
  const [menuOpen, setMenuOpen] = useState(false);
  const location = useLocation();

  useEffect(() => setMenuOpen(false), [location.pathname]);

  return (
    <div className="app-shell">
      <button
        type="button"
        className="mobile-menu-btn"
        aria-label={menuOpen ? "Cerrar menu" : "Abrir menu"}
        aria-expanded={menuOpen}
        onClick={() => setMenuOpen((v) => !v)}
      >
        <Icon name={menuOpen ? "x" : "menu"} size={18} />
      </button>
      {menuOpen && (
        <div className="sidebar-backdrop" onClick={() => setMenuOpen(false)} aria-hidden="true" />
      )}
      <Sidebar className={menuOpen ? "mobile-open" : ""} />
      <main className="main-area">
        <Outlet />
      </main>
    </div>
  );
}
