import { useState } from "react";
import { useAuth } from "../../context/AuthContext";
import { Icon } from "../../components/ui/Icon";
import { LineChart, Line, ResponsiveContainer, ReferenceLine } from "recharts";

const mainChartData = [
  { time: "0", real: 68 }, { time: "1", real: 72 }, { time: "2", real: 70 },
  { time: "3", real: 85 }, { time: "4", real: 82 }, { time: "5", real: 90 },
  { time: "6", real: 88 }, { time: "7", real: 105 }, { time: "8", real: 100 },
  { time: "9", real: 115 }, { time: "10", real: 108 }, { time: "11", real: 116 },
  { time: "12", real: 112 }
];

const sparkDataFC = [{v: 60}, {v: 65}, {v: 80}, {v: 75}, {v: 95}, {v: 90}, {v: 112}];
const sparkDataSPO2 = [{v: 98}, {v: 97}, {v: 97}, {v: 98}, {v: 97}, {v: 96}, {v: 96}];
const sparkDataTA = [{v: 120}, {v: 121}, {v: 122}, {v: 120}, {v: 125}, {v: 128}, {v: 128}];
const sparkDataTEMP = [{v: 36.5}, {v: 36.6}, {v: 36.6}, {v: 36.8}, {v: 37.0}, {v: 37.1}, {v: 37.1}];

const VITALS = [
  { tipo: "FC", label: "Frecuencia cardíaca", unidad: "bpm", valor: "112", status: "Atención", color: "#d97706", sparkData: sparkDataFC, icon: "heart", pillClass: "pill-atencion" },
  { tipo: "SPO2", label: "Saturación SpO2", unidad: "%", valor: "96", status: "Normal", color: "#059669", sparkData: sparkDataSPO2, iconText: "O₂", pillClass: "pill-normal" },
  { tipo: "TA", label: "Presión arterial", unidad: "mmHg", valor: "128/84", status: "Normal", color: "#059669", sparkData: sparkDataTA, icon: "activity", pillClass: "pill-normal" },
  { tipo: "TEMP", label: "Temperatura corporal", unidad: "°C", valor: "37.1", status: "Normal", color: "#0284c7", sparkData: sparkDataTEMP, icon: "thermometer", pillClass: "pill-normal" }
];

export function Monitoreo() {
  const { user } = useAuth();
  const [toast, setToast] = useState(null);

  const showToast = (message, icon = "info") => {
    setToast({ message, icon });
    setTimeout(() => setToast(null), 3000);
  };

  return (
    <>
      
      {/* Alert Banner */}
      <div className="alert-banner animate-fade-in">
        <div className="alert-banner-left">
          <div className="ic"><Icon name="alert-triangle" size={18} /></div>
          <div className="txt">
            <div className="t1">Alerta predictiva Med-Gemini — posible taquicardia</div>
            <div className="t2">Detectada hoy a las 14:32 - Patrón anómalo en frecuencia cardíaca sostenida</div>
          </div>
        </div>
        <div className="alert-actions">
          <button className="btn" onClick={() => showToast("Cargando detalles de la alerta...", "activity")}>Ver detalle</button>
          <button className="btn btn-primary-alert" onClick={() => showToast("Notificación enviada al médico de turno.", "check")}>Notificar médico</button>
        </div>
      </div>

      {/* Vitals Grid */}
      <div className="vitals-grid">
        {VITALS.map((vital, i) => (
          <div className={`card vital-card animate-fade-in delay-${i % 2 === 0 ? '1' : '2'}`} key={vital.tipo}>
            <div className="top-row">
              <div className="ic">
                {vital.icon ? <Icon name={vital.icon} size={15} /> : <span style={{fontWeight: 700}}>{vital.iconText}</span>}
              </div>
              <span className={`pill ${vital.pillClass}`}>
                {vital.status === "Atención" && <span className="live-dot" style={{width: 6, height: 6, marginRight: 4}}></span>}
                {vital.status}
              </span>
            </div>
            <div className="num">
              {vital.valor}{" "}
              <span style={{ fontSize: 13, color: "#8fa9ad", fontWeight: 600 }}>
                {vital.unidad}
              </span>
            </div>
            <div className="lbl">{vital.label}</div>
            <div className="vital-sparkline">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={vital.sparkData}>
                  <Line type="monotone" dataKey="v" stroke={vital.color} strokeWidth={2} dot={false} isAnimationActive={true} animationDuration={1500} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
        ))}
      </div>

      {/* Main Grid: Chart and Sidebar */}
      <div className="biometric-grid">
        
        {/* Left: Main Chart */}
        <div className="card chart-card animate-fade-in delay-1">
          <div className="chart-header">
            <div className="chart-title">
              <span className="live-dot"></span>
              Frecuencia cardíaca · últimas 24 h
            </div>
            <div className="chart-legend">
              <div className="chart-legend-item">
                <div className="chart-dot" style={{ background: "#0284c7" }} /> Real
              </div>
              <div className="chart-legend-item">
                <div className="chart-dot" style={{ background: "#f59e0b" }} /> Umbral alerta
              </div>
            </div>
          </div>
          <div style={{ flex: 1, minHeight: 250, marginTop: 10 }}>
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={mainChartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <ReferenceLine y={100} stroke="#f59e0b" strokeDasharray="5 5" strokeWidth={1.5} />
                <Line type="monotone" dataKey="real" stroke="#0284c7" strokeWidth={2.5} dot={{ r: 0 }} activeDot={{ r: 6, fill: "#f59e0b", stroke: "#fff", strokeWidth: 2 }} isAnimationActive={true} animationDuration={2000} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Right Sidebar: Devices and Timeline */}
        <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
          
          <div className="card animate-fade-in delay-2">
            <div className="card-title" style={{ fontSize: 14, marginBottom: 4 }}>
              <Icon name="radio" size={14} style={{ marginRight: 6, verticalAlign: "-2px" }} /> Dispositivos IoT vinculados
            </div>
            <div className="device-row">
              <div className="dic"><Icon name="watch" size={16} /></div>
              <div>
                <div className="dn">Smartwatch SAMR X2</div>
                <div className="ds">• Conectado</div>
              </div>
              <div className="batt" style={{ color: "#059669" }}>
                <Icon name="battery" size={13} style={{ marginRight: 4, verticalAlign: "-2px" }} /> 82%
              </div>
            </div>
            <div className="device-row">
              <div className="dic"><Icon name="activity" size={16} style={{ color: "#be123c" }} /></div>
              <div>
                <div className="dn">Banda de presión</div>
                <div className="ds">• Conectado</div>
              </div>
              <div className="batt" style={{ color: "#059669" }}>
                <Icon name="battery" size={13} style={{ marginRight: 4, verticalAlign: "-2px" }} /> 65%
              </div>
            </div>
          </div>

          <div className="card animate-fade-in delay-2">
            <div className="card-title" style={{ fontSize: 14, marginBottom: 8 }}>
              <Icon name="clock" size={14} style={{ marginRight: 6, verticalAlign: "-2px" }} /> Línea de tiempo
            </div>
            <div className="timeline">
              <div className="tl-item">
                <div className="tl-time">14:32</div>
                <div className="tl-dot" style={{ background: "#d97706" }} />
                <div className="tl-text">
                  <b>Alerta predictiva</b> — taquicardia sostenida
                </div>
              </div>
              <div className="tl-item">
                <div className="tl-time">13:10</div>
                <div className="tl-dot" style={{ background: "#059669" }} />
                <div className="tl-text">Lectura SpO₂ dentro de rango normal</div>
              </div>
              <div className="tl-item">
                <div className="tl-time">11:45</div>
                <div className="tl-dot" style={{ background: "#0ea5e9" }} />
                <div className="tl-text">Sincronización de smartwatch completada</div>
              </div>
              <div className="tl-item">
                <div className="tl-time">09:00</div>
                <div className="tl-dot" style={{ background: "#0ea5e9" }} />
                <div className="tl-text">Inicio de monitoreo diario</div>
              </div>
            </div>
          </div>

        </div>
      </div>
      
      {toast && (
        <div className="toast-container">
          <div className="toast">
            <Icon name={toast.icon} size={16} />
            {toast.message}
          </div>
        </div>
      )}
    </>
  );
}

