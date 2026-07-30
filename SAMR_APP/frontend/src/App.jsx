import { Navigate, Route, Routes } from "react-router-dom";
import { AppLayout } from "./components/layout/AppLayout";
import { ProtectedRoute } from "./routes/ProtectedRoute";
import { Login } from "./pages/auth/Login";
import { Registro } from "./pages/auth/Registro";
import { RecuperarAcceso } from "./pages/auth/RecuperarAcceso";
import { Inicio } from "./pages/inicio/Inicio";
import { Triaje } from "./pages/triaje/Triaje";
import { Monitoreo } from "./pages/monitoreo/Monitoreo";
import { Teleconsulta } from "./pages/teleconsulta/Teleconsulta";
import { Auditoria } from "./pages/auditoria/Auditoria";
import { ROLES } from "./lib/roles";

export default function App() {
  return (
    <Routes>
      <Route path="/acceso" element={<Login />} />
      <Route path="/acceso/registro" element={<Registro />} />
      <Route path="/acceso/recuperar" element={<RecuperarAcceso />} />

      <Route
        element={
          <ProtectedRoute>
            <AppLayout />
          </ProtectedRoute>
        }
      >
        <Route path="/" element={<Inicio />} />
        <Route path="/triaje" element={<Triaje />} />
        <Route path="/monitoreo" element={<Monitoreo />} />
        <Route path="/teleconsulta" element={<Teleconsulta />} />
        <Route
          path="/auditoria"
          element={
            <ProtectedRoute roles={[ROLES.ADMINISTRATIVO, ROLES.MSP, ROLES.DPO]}>
              <Auditoria />
            </ProtectedRoute>
          }
        />
      </Route>

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
