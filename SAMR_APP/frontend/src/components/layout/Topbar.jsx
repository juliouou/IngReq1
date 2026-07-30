import { useAuth } from "../../context/AuthContext";
import { Icon } from "../ui/Icon";

export function Topbar({ title, subtitle }) {
  const { user } = useAuth();
  const initials = (user?.email || "??").slice(0, 2).toUpperCase();

  return (
    <div className="topbar">
      <div>
        <h1>{title}</h1>
        {subtitle && <div className="sub">{subtitle}</div>}
      </div>
      <div className="topbar-right">
        <div className="bell" aria-hidden="true">
          <Icon name="bell" size={15} />
        </div>
        <div className="avatar">{initials}</div>
      </div>
    </div>
  );
}
