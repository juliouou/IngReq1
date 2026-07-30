import { Link } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";
import { ROLE_LABELS } from "../../lib/roles";
import { Icon } from "../../components/ui/Icon";
import "../../styles/inicio.css";

export function Inicio() {
  const { user } = useAuth();
  const userName = user?.email || "Usuario";

  return (
    <>
      
      <div className="welcome-banner animate-fade-in">
        <h1>Hola, {userName.split('@')[0]}</h1>
        <p>Tus signos vitales están dentro de los rangos normales hoy. Tienes una consulta programada para esta tarde.</p>
        <Link to="/teleconsulta" className="welcome-btn">
          <Icon name="video" size={16} /> Entrar a sala de espera
        </Link>
      </div>

      <div className="dashboard-grid">
        <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
          <div className="card animate-fade-in delay-1">
            <div className="card-title">
              <span className="live-dot"></span>
              Resumen Biométrico (Última hora)
            </div>
            <div className="vitals-grid" style={{ marginBottom: 0, marginTop: 16 }}>
              <div className="card vital-card" style={{ boxShadow: 'none', border: '1px solid #eef6f7' }}>
                <div className="top-row">
                  <div className="ic"><Icon name="heart" size={15} /></div>
                  <span className="pill pill-normal">Normal</span>
                </div>
                <div className="num">72 <span style={{ fontSize: 13, color: "#8fa9ad", fontWeight: 600 }}>bpm</span></div>
                <div className="lbl">Frecuencia cardíaca</div>
              </div>
              <div className="card vital-card" style={{ boxShadow: 'none', border: '1px solid #eef6f7' }}>
                <div className="top-row">
                  <div className="ic"><span style={{fontWeight: 700}}>O₂</span></div>
                  <span className="pill pill-normal">Normal</span>
                </div>
                <div className="num">98 <span style={{ fontSize: 13, color: "#8fa9ad", fontWeight: 600 }}>%</span></div>
                <div className="lbl">Saturación SpO2</div>
              </div>
            </div>
            <div style={{ marginTop: 16 }}>
              <Link to="/monitoreo" className="btn btn-outline" style={{ width: '100%', justifyContent: 'center' }}>Ver historial completo</Link>
            </div>
          </div>
          
          <div className="card animate-fade-in delay-2">
            <div className="card-title">Última Evaluación Médica</div>
            <div className="timeline" style={{ marginTop: 16 }}>
              <div className="tl-item">
                <div className="tl-time">Ayer</div>
                <div className="tl-dot" style={{ background: "#059669" }} />
                <div className="tl-text">
                  <b>Evaluación completada</b> — Nivel de riesgo Bajo. Se recomendó reposo.
                </div>
              </div>
            </div>
            <div style={{ marginTop: 16 }}>
              <Link to="/triaje" className="btn btn-primary" style={{ width: '100%', justifyContent: 'center' }}>Realizar nueva evaluación</Link>
            </div>
          </div>
        </div>

        <div className="card animate-fade-in delay-1">
          <div className="card-title">Accesos Rápidos</div>
          <div className="action-list">
            <Link to="/triaje" className="action-item">
              <div className="action-icon" style={{ background: '#0284c7' }}>
                <Icon name="clipboard" size={20} />
              </div>
              <div className="action-text">
                <h4>Evaluación Médica</h4>
                <p>Ingresar síntomas a la evaluación clínica</p>
              </div>
            </Link>
            <Link to="/monitoreo" className="action-item">
              <div className="action-icon" style={{ background: '#059669' }}>
                <Icon name="activity" size={20} />
              </div>
              <div className="action-text">
                <h4>Signos Vitales</h4>
                <p>Ver monitoreo en vivo</p>
              </div>
            </Link>
            <Link to="/teleconsulta" className="action-item">
              <div className="action-icon" style={{ background: '#7c3aed' }}>
                <Icon name="video" size={20} />
              </div>
              <div className="action-text">
                <h4>Teleconsulta</h4>
                <p>Conectar con un especialista</p>
              </div>
            </Link>
          </div>
        </div>
      </div>
    </>
  );
}
