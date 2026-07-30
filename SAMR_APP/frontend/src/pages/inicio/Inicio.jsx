import { Link } from "react-router-dom";
import { Topbar } from "../../components/layout/Topbar";
import { useAuth } from "../../context/AuthContext";
import { NAV_ITEMS, ROLE_LABELS } from "../../lib/roles";

export function Inicio() {
  const { user } = useAuth();
  const modulos = NAV_ITEMS.filter((item) => !user?.rol || item.roles.includes(user.rol));

  return (
    <>
      <Topbar
        title={`Hola, ${user?.email || "de nuevo"}`}
        subtitle={`Rol: ${ROLE_LABELS[user?.rol] || user?.rol || "sin definir"}`}
      />
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fill, minmax(220px, 1fr))",
          gap: 16,
        }}
      >
        {modulos.map((item) => (
          <Link key={item.to} to={item.to} className="card" style={{ textDecoration: "none" }}>
            <div className="card-title">{item.label}</div>
            <p className="helper" style={{ margin: 0 }}>Ir al modulo de {item.label.toLowerCase()}.</p>
          </Link>
        ))}
      </div>
    </>
  );
}
