import { useState } from "react";
import { Topbar } from "../../components/layout/Topbar";
import { useAuth } from "../../context/AuthContext";
import * as monitoreoApi from "../../lib/api/monitoreo";
import { useApiQuery } from "../../lib/useApi";
import { EmptyState, ErrorState, LoadingState } from "../../components/ui/StateBlock";
import { Icon } from "../../components/ui/Icon";

const VITAL_TYPES = [
  { tipo: "FC", label: "Frecuencia cardiaca", unidad: "bpm", icon: "heart", rango: [58, 118] },
  { tipo: "SPO2", label: "Saturacion SpO2", unidad: "%", iconText: "O2", rango: [90, 99] },
  { tipo: "TA_SIS", label: "Presion sistolica", unidad: "mmHg", icon: "activity", rango: [100, 138] },
  { tipo: "TEMP", label: "Temperatura corporal", unidad: "C", icon: "thermometer", rango: [36.1, 38.2] },
];

function randomInRange([min, max]) {
  const val = min + Math.random() * (max - min);
  return Number.isInteger(min) && Number.isInteger(max) ? Math.round(val) : Math.round(val * 10) / 10;
}

export function Monitoreo() {
  const { user, token } = useAuth();
  const [lecturas, setLecturas] = useState({});
  const [envioStatus, setEnvioStatus] = useState({ status: "idle", error: null });

  const alertasQuery = useApiQuery(() => monitoreoApi.listarAlertas(token), [token]);

  const simularRonda = async () => {
    setEnvioStatus({ status: "loading", error: null });
    const nuevas = {};
    try {
      for (const vital of VITAL_TYPES) {
        const valor = randomInRange(vital.rango);
        // eslint-disable-next-line no-await-in-loop
        await monitoreoApi.enviarLecturaBiometrica(
          { pacienteId: user?.id, tipo: vital.tipo, valor },
          token
        );
        nuevas[vital.tipo] = { valor, timestamp: new Date().toISOString() };
      }
      setLecturas((prev) => ({ ...prev, ...nuevas }));
      setEnvioStatus({ status: "success", error: null });
    } catch (err) {
      setLecturas((prev) => ({ ...prev, ...nuevas }));
      setEnvioStatus({ status: "error", error: err });
    }
  };

  return (
    <>
      <Topbar title="Monitoreo biometrico" subtitle="Simulador IoT (POST /biometrics) y alertas activas (M3)" />

      <div className="card" style={{ marginBottom: 20 }}>
        <div
          className="card-title"
          style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}
        >
          <span>Simulador de dispositivo IoT</span>
          <button className="btn btn-primary btn-sm" onClick={simularRonda} disabled={envioStatus.status === "loading"}>
            {envioStatus.status === "loading" ? "Enviando..." : "Generar lectura ahora"}
          </button>
        </div>
        <p className="helper" style={{ marginTop: -6, marginBottom: 14 }}>
          M3 aun no expone un endpoint de lectura en vivo, solo ingesta (<code>POST /biometrics</code>).
          Este boton genera valores plausibles y los envia de verdad al Gateway; las tarjetas
          abajo muestran lo ultimo que se envio, no un GET del backend.
        </p>
        {envioStatus.status === "error" && (
          <div className="banner banner-error">{envioStatus.error.message}</div>
        )}

        <div className="vitals-grid" style={{ marginBottom: 0 }}>
          {VITAL_TYPES.map((vital) => {
            const lectura = lecturas[vital.tipo];
            return (
              <div className="card vital-card" key={vital.tipo}>
                <div className="top-row">
                  <div className="ic">
                    {vital.icon ? <Icon name={vital.icon} size={14} /> : vital.iconText}
                  </div>
                  <span className={`pill ${lectura ? "pill-ok" : "pill-info"}`}>
                    {lectura ? "Enviado" : "Sin datos"}
                  </span>
                </div>
                <div className="num">
                  {lectura ? lectura.valor : "--"}{" "}
                  <span style={{ fontSize: 12, color: "#7096A6", fontWeight: 600 }}>
                    {vital.unidad}
                  </span>
                </div>
                <div className="lbl">{vital.label}</div>
              </div>
            );
          })}
        </div>
      </div>

      <div className="card">
        <div
          className="card-title"
          style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}
        >
          <span>Alertas activas</span>
          <button className="btn btn-outline btn-sm" onClick={alertasQuery.refetch}>
            Actualizar
          </button>
        </div>

        {alertasQuery.status === "loading" && <LoadingState text="Consultando GET /alerts..." />}
        {alertasQuery.status === "error" && (
          <ErrorState
            title="M3 - Monitoreo aun no respondio"
            detail={alertasQuery.error.message}
            onRetry={alertasQuery.refetch}
          />
        )}
        {alertasQuery.status === "success" &&
          (Array.isArray(alertasQuery.data) && alertasQuery.data.length > 0 ? (
            <div className="timeline">
              {alertasQuery.data.map((alerta) => (
                <div className="tl-item" key={alerta.id}>
                  <span className="tl-time">
                    {alerta.timestamp ? new Date(alerta.timestamp).toLocaleTimeString() : "--"}
                  </span>
                  <span className="tl-dot" style={{ background: "#C98A1E" }} />
                  <span className="tl-text">
                    <b>{alerta.tipo}</b> - valor {alerta.valor}
                  </span>
                </div>
              ))}
            </div>
          ) : (
            <EmptyState title="No hay alertas activas" detail="M3 respondio una lista vacia." />
          ))}
      </div>
    </>
  );
}
