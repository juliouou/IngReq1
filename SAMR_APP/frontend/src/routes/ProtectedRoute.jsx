import { Navigate, useLocation } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export function ProtectedRoute({ children, roles }) {
  const { isAuthenticated, user } = useAuth();
  const location = useLocation();

  if (!isAuthenticated) {
    return <Navigate to="/acceso" replace state={{ from: location }} />;
  }
  if (roles && !roles.includes(user?.rol)) {
    return <Navigate to="/" replace />;
  }
  return children;
}
