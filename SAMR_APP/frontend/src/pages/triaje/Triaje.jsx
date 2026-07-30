import { useRef, useState } from "react";
import { useAuth } from "../../context/AuthContext";
import * as triajeApi from "../../lib/api/triaje";
import { EmptyState, ErrorState } from "../../components/ui/StateBlock";
import { Icon } from "../../components/ui/Icon";

const initialMessages = [
  {
    from: "bot",
    text: "Hola, soy el asistente de triaje SAMR. Cuéntame, ¿cuál es tu síntoma principal?",
  },
];

export function Triaje() {
  const { user, token } = useAuth();
  const [metodo, setMetodo] = useState(null); // 'formulario', 'chat', 'emergencia'
  
  // Shared state
  const [sending, setSending] = useState(false);
  const [resultado, setResultado] = useState(null);
  const [errorResumen, setErrorResumen] = useState(null);

  // Form state
  const [formSintoma, setFormSintoma] = useState("");
  const [formDias, setFormDias] = useState("");
  const [formDolor, setFormDolor] = useState("5");

  const enviarSolicitud = async (payload, callback) => {
    setSending(true);
    setErrorResumen(null);
    try {
      const data = await triajeApi.crearTriaje(payload, token);
      setResultado(data);
      if (callback) callback(null, data);
    } catch (err) {
      setErrorResumen(err);
      if (callback) callback(err, null);
    } finally {
      setSending(false);
    }
  };



  const onSubmitForm = (e) => {
    e.preventDefault();
    if (!formSintoma || sending) return;
    const textoCompuesto = `Síntoma: ${formSintoma}. Duración: ${formDias} días. Nivel de dolor: ${formDolor}/10.`;
    enviarSolicitud({ pacienteId: user?.id, tipo: "sintomas", sintomas: textoCompuesto });
  };

  const enviarAlertaEmergencia = () => {
    enviarSolicitud({ pacienteId: user?.id, tipo: "alerta_iot", sintomas: "Alerta de emergencia desde dispositivo IoT" });
  };

  const resetMethod = () => {
    setMetodo(null);
    setResultado(null);
    setErrorResumen(null);
    setFormSintoma("");
  };

  // -------------------------------------------------------------
  // VISTA: SELECTOR INICIAL
  // -------------------------------------------------------------
  if (!metodo) {
    return (
      <>
                <div className="selector-container animate-fade-in">
          <div className="selector-title">¿Cómo deseas ingresar tu solicitud?</div>
          <div className="selector-grid">
            <div className="selector-card" onClick={() => setMetodo('formulario')}>
              <div className="selector-icon">
                <Icon name="file-text" size={28} />
              </div>
              <div className="selector-name">Formulario Clásico</div>
              <div className="selector-desc">Llena un formulario rápido con tus síntomas, duración y nivel de dolor.</div>
            </div>

            <div className="selector-card danger" onClick={() => { setMetodo('emergencia'); enviarAlertaEmergencia(); }}>
              <div className="selector-icon">
                <Icon name="alert-triangle" size={28} />
              </div>
              <div className="selector-name">Emergencia IoT</div>
              <div className="selector-desc">Envía una alerta inmediata prioritaria extrayendo datos de tu dispositivo IoT.</div>
            </div>
          </div>
        </div>
      </>
    );
  }

  // -------------------------------------------------------------
  // VISTAS INTERNAS (Form / Chat / Emergencia)
  // -------------------------------------------------------------
  return (
    <>
            
      <div style={{ marginBottom: 20 }}>
        <button className="btn btn-ghost btn-sm animate-fade-in" onClick={resetMethod}>
          <Icon name="x" size={14} /> Volver a los métodos
        </button>
      </div>

      <div className="triage-grid animate-fade-in delay-1">


        {metodo === 'formulario' && (
          <div className="card">
            <div className="card-title">Ingresa tus datos médicos</div>
            <form onSubmit={onSubmitForm}>
              <div className="field-row">
                <div className="field">
                  <label>Nombre Completo</label>
                  <input readOnly value={user?.nombre || "Paciente Demo"} disabled style={{ background: "#f0f4f5" }} />
                </div>
                <div className="field">
                  <label>Correo Electrónico</label>
                  <input readOnly value={user?.email || "paciente@demo.com"} disabled style={{ background: "#f0f4f5" }} />
                </div>
              </div>
              <div className="field">
                <label>Síntoma principal</label>
                <textarea required rows="2" placeholder="Ej. Dolor de cabeza intenso y fiebre desde ayer en la noche..." value={formSintoma} onChange={e => setFormSintoma(e.target.value)} disabled={sending || resultado} />
              </div>
              <div className="field-row">
                <div className="field">
                  <label>¿Hace cuántos días?</label>
                  <input type="number" min="0" required placeholder="Ej. 2" value={formDias} onChange={e => setFormDias(e.target.value)} disabled={sending || resultado} />
                </div>
                <div className="field">
                  <label>Nivel de dolor (1-10)</label>
                  <select value={formDolor} onChange={e => setFormDolor(e.target.value)} disabled={sending || resultado}>
                    {[...Array(10)].map((_, i) => <option key={i+1} value={i+1}>{i+1}</option>)}
                  </select>
                </div>
              </div>
              {!resultado && (
                <button className="btn btn-primary btn-block" type="submit" disabled={sending}>
                  {sending ? "Enviando solicitud..." : "Generar Solicitud de Triaje"}
                </button>
              )}
            </form>
          </div>
        )}

        {metodo === 'emergencia' && (
          <div className="emergency-card">
            <div className="h"><Icon name="alert-triangle" size={18} /> Alerta IoT en curso</div>
            <p>Se están recopilando los signos vitales de tus dispositivos vinculados para adjuntarlos a la solicitud prioritaria.</p>
            {sending && <div className="banner banner-warn">Obteniendo métricas y enviando alerta al servidor...</div>}
            {resultado && <div className="banner banner-ok">La alerta crítica ha sido enviada exitosamente.</div>}
            {errorResumen && <div className="banner banner-error">{errorResumen.message}</div>}
          </div>
        )}

        {/* Lado Derecho: Resumen (Siempre visible en todas las vistas) */}
        <div className="side-col">
          <div className="card">
            <div className="card-title">Resumen de tu solicitud</div>
            {sending && !resultado && !errorResumen ? (
              <EmptyState title="Procesando..." detail="Med-Gemini está evaluando la solicitud..." />
            ) : resultado ? (
              <>
                <div className="urgency-box">
                  <div>
                    <div className="lbl">Prioridad sugerida por IA</div>
                    <div className="val">{resultado.prioridad || "Pendiente"}</div>
                  </div>
                  <span className="pill pill-danger">{resultado.tiempoEstimado || "Por confirmar"}</span>
                </div>
                {Array.isArray(resultado.sintomasDetectados) && (
                  <div className="tag-row">
                    {resultado.sintomasDetectados.map((s) => <span className="tag" key={s}>{s}</span>)}
                  </div>
                )}
                {resultado.explanation && (
                  <div className="xai-box">
                    <div className="h">¿Por qué esta prioridad? (XAI)</div>
                    <ul><li>{resultado.explanation}</li></ul>
                  </div>
                )}
                <div className="assign-row">
                  <span>Centro asignado</span>
                  <span>{resultado.centroAsignado || "Por asignar"}</span>
                </div>
                <div className="assign-row">
                  <span>Especialista</span>
                  <span>{resultado.medicoAsignado || "Por asignar"}</span>
                </div>
              </>
            ) : errorResumen ? (
              <ErrorState title="Fallo al procesar" detail={errorResumen.message} />
            ) : (
              <EmptyState title="Sin enviar" detail="Completa la solicitud a la izquierda para obtener un resumen." />
            )}
          </div>
        </div>
      </div>
    </>
  );
}
