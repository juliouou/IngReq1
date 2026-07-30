import { useEffect, useRef, useState } from "react";
import { Topbar } from "../../components/layout/Topbar";
import { useAuth } from "../../context/AuthContext";
import * as teleApi from "../../lib/api/teleconsulta";
import { ROLES } from "../../lib/roles";
import { Icon } from "../../components/ui/Icon";
import { useWebRtcCall } from "../../lib/useWebRtcCall";

function RemoteVideo({ stream }) {
  const ref = useRef(null);
  useEffect(() => {
    if (ref.current) ref.current.srcObject = stream || null;
  }, [stream]);
  if (!stream) return null;
  return <video ref={ref} autoPlay playsInline className="remote-video" />;
}

const CONNECTION_LABELS = {
  idle: "Sin iniciar",
  signaling: "Conectando senalizacion...",
  connecting: "Estableciendo video...",
  connected: "Conexion estable",
  disconnected: "Conexion perdida",
  failed: "No se pudo conectar (sin TURN server, puede fallar en redes con NAT restrictivo)",
};

export function Teleconsulta() {
  const { user, token } = useAuth();
  const esMedico = user?.rol === ROLES.MEDICO;
  const videoRef = useRef(null);
  const streamRef = useRef(null);

  const [form, setForm] = useState({
    pacienteId: esMedico ? "" : user?.id || "",
    medicoId: esMedico ? user?.id || "" : "",
  });
  const [sesion, setSesion] = useState(null);
  const [sesionStatus, setSesionStatus] = useState({ status: "idle", error: null });
  const [micOn, setMicOn] = useState(true);
  const [camOn, setCamOn] = useState(true);
  const [localStream, setLocalStream] = useState(null);

  const { remoteStream, connectionState } = useWebRtcCall({
    roomId: sesion?.id,
    token,
    localStream,
    isCaller: esMedico,
    enabled: Boolean(sesion?.id && localStream),
  });

  const [diagnostico, setDiagnostico] = useState({
    sugerenciaMedGemini: "",
    explanation: "",
    decisionMedico: "aceptado",
  });
  const [diagStatus, setDiagStatus] = useState({ status: "idle", error: null });

  const [medicamentos, setMedicamentos] = useState([""]);
  const [rxStatus, setRxStatus] = useState({ status: "idle", error: null });

  useEffect(() => {
    return () => {
      streamRef.current?.getTracks().forEach((t) => t.stop());
    };
  }, []);

  const iniciarSesion = async (e) => {
    e.preventDefault();
    setSesionStatus({ status: "loading", error: null });
    try {
      const data = await teleApi.iniciarTeleconsulta(
        { pacienteId: form.pacienteId, medicoId: form.medicoId },
        token
      );
      setSesion(data || { id: null, pacienteId: form.pacienteId, medicoId: form.medicoId });
      setSesionStatus({ status: "success", error: null });
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
        streamRef.current = stream;
        if (videoRef.current) videoRef.current.srcObject = stream;
        setLocalStream(stream);
      } catch {
        setLocalStream(null);
      }
    } catch (err) {
      setSesionStatus({ status: "error", error: err });
    }
  };

  const toggleMic = () => {
    streamRef.current?.getAudioTracks().forEach((t) => (t.enabled = !micOn));
    setMicOn((v) => !v);
  };
  const toggleCam = () => {
    streamRef.current?.getVideoTracks().forEach((t) => (t.enabled = !camOn));
    setCamOn((v) => !v);
  };
  const finalizarLlamada = () => {
    streamRef.current?.getTracks().forEach((t) => t.stop());
    streamRef.current = null;
    setLocalStream(null);
    setSesion(null);
    setSesionStatus({ status: "idle", error: null });
  };

  const enviarDiagnostico = async (e) => {
    e.preventDefault();
    setDiagStatus({ status: "loading", error: null });
    try {
      await teleApi.registrarDiagnostico(
        {
          consultaId: sesion?.id,
          sugerenciaMedGemini: diagnostico.sugerenciaMedGemini,
          explanation: diagnostico.explanation,
          decisionMedico: diagnostico.decisionMedico,
        },
        token
      );
      setDiagStatus({ status: "success", error: null });
    } catch (err) {
      setDiagStatus({ status: "error", error: err });
    }
  };

  const enviarReceta = async (e) => {
    e.preventDefault();
    setRxStatus({ status: "loading", error: null });
    try {
      await teleApi.emitirReceta(
        { consultaId: sesion?.id, medicamentos: medicamentos.filter(Boolean) },
        token
      );
      setRxStatus({ status: "success", error: null });
    } catch (err) {
      setRxStatus({ status: "error", error: err });
    }
  };

  if (!sesion) {
    return (
      <>
        <Topbar title="Teleconsulta" subtitle="Inicia sesion contra POST /teleconsultation (M4)" />
        <div className="card" style={{ maxWidth: 460 }}>
          <div className="card-title">Iniciar teleconsulta</div>
          {sesionStatus.status === "error" && (
            <div className="banner banner-error">{sesionStatus.error.message}</div>
          )}
          <form onSubmit={iniciarSesion}>
            <div className="field">
              <label htmlFor="pacienteId">ID de paciente</label>
              <input
                id="pacienteId"
                required
                disabled={!esMedico}
                value={form.pacienteId}
                onChange={(e) => setForm((f) => ({ ...f, pacienteId: e.target.value }))}
              />
            </div>
            <div className="field">
              <label htmlFor="medicoId">ID de medico</label>
              <input
                id="medicoId"
                required
                disabled={esMedico}
                value={form.medicoId}
                onChange={(e) => setForm((f) => ({ ...f, medicoId: e.target.value }))}
              />
            </div>
            <button className="btn btn-primary btn-block" type="submit" disabled={sesionStatus.status === "loading"}>
              {sesionStatus.status === "loading" ? "Conectando..." : "Iniciar teleconsulta"}
            </button>
          </form>
          <p className="helper" style={{ marginTop: 14 }}>
            Comparte el mismo ID de consulta con la otra parte (medico/paciente) para probar la
            videollamada real entre dos pestanas o dispositivos distintos.
          </p>
        </div>
      </>
    );
  }

  return (
    <>
      <Topbar
        title="Teleconsulta en curso"
        subtitle={`Consulta ${sesion.id || "(pendiente de M4)"} - ${CONNECTION_LABELS[connectionState] || connectionState}`}
      />

      <div className="tele-grid">
        <div className="video-card">
          <div className="video-main">
            {remoteStream ? (
              <RemoteVideo stream={remoteStream} />
            ) : (
              <>
                <div className="doc-avatar">{esMedico ? "PA" : "MD"}</div>
                <div className="video-label">
                  {CONNECTION_LABELS[connectionState] || "Esperando a la otra parte..."}
                </div>
              </>
            )}
            <div className="vitals-overlay">
              <div>
                <div className="v">--</div>
                <div className="l">BPM</div>
              </div>
              <div>
                <div className="v">--</div>
                <div className="l">SpO2</div>
              </div>
            </div>
            <div className="pip">
              {localStream ? <video ref={videoRef} autoPlay muted playsInline /> : "Tu camara"}
            </div>
          </div>
          <div className="video-controls">
            <button className={`vctrl${micOn ? " on" : ""}`} type="button" onClick={toggleMic} aria-label="Microfono">
              <Icon name={micOn ? "mic" : "mic-off"} size={17} />
            </button>
            <button className={`vctrl${camOn ? " on" : ""}`} type="button" onClick={toggleCam} aria-label="Camara">
              <Icon name="camera" size={17} />
            </button>
            <button className="vctrl end" type="button" onClick={finalizarLlamada} aria-label="Finalizar">
              <Icon name="x" size={19} />
            </button>
          </div>
        </div>

        <div className="side-col">
          <div className="card">
            <div className="card-title">Diagnostico asistido por Med-Gemini</div>
            {!esMedico ? (
              <p className="helper">Solo el medico a cargo puede registrar el diagnostico.</p>
            ) : (
              <form onSubmit={enviarDiagnostico}>
                {diagStatus.status === "error" && (
                  <div className="banner banner-error">{diagStatus.error.message}</div>
                )}
                {diagStatus.status === "success" && (
                  <div className="banner banner-ok">Diagnostico registrado en POST /diagnosis.</div>
                )}
                <div className="field">
                  <label htmlFor="sugerencia">Sugerencia de Med-Gemini</label>
                  <input
                    id="sugerencia"
                    placeholder="Ej. Cefalea tensional"
                    value={diagnostico.sugerenciaMedGemini}
                    onChange={(e) =>
                      setDiagnostico((d) => ({ ...d, sugerenciaMedGemini: e.target.value }))
                    }
                  />
                </div>
                <div className="field">
                  <label htmlFor="explanation">Explicacion (XAI, obligatoria)</label>
                  <textarea
                    id="explanation"
                    required
                    rows={3}
                    value={diagnostico.explanation}
                    onChange={(e) => setDiagnostico((d) => ({ ...d, explanation: e.target.value }))}
                  />
                </div>
                <div className="field">
                  <label htmlFor="decision">Decision del medico</label>
                  <select
                    id="decision"
                    value={diagnostico.decisionMedico}
                    onChange={(e) =>
                      setDiagnostico((d) => ({ ...d, decisionMedico: e.target.value }))
                    }
                  >
                    <option value="aceptado">Aceptado</option>
                    <option value="modificado">Modificado</option>
                    <option value="rechazado">Rechazado</option>
                  </select>
                </div>
                <button className="btn btn-ghost btn-block" type="submit" disabled={diagStatus.status === "loading"}>
                  {diagStatus.status === "loading" ? "Guardando..." : "Registrar diagnostico"}
                </button>
              </form>
            )}
          </div>

          <div className="card">
            <div className="card-title">Receta digital</div>
            {rxStatus.status === "error" && (
              <div className="banner banner-error">{rxStatus.error.message}</div>
            )}
            {rxStatus.status === "success" && (
              <div className="banner banner-ok">Receta enviada via POST /prescription.</div>
            )}
            {esMedico ? (
              <form onSubmit={enviarReceta}>
                {medicamentos.map((med, i) => (
                  <div className="field" key={i}>
                    <label htmlFor={`med-${i}`}>Medicamento {i + 1}</label>
                    <input
                      id={`med-${i}`}
                      placeholder="Ej. Paracetamol 500 mg - 1 tab c/8h"
                      value={med}
                      onChange={(e) =>
                        setMedicamentos((list) =>
                          list.map((m, idx) => (idx === i ? e.target.value : m))
                        )
                      }
                    />
                  </div>
                ))}
                <button
                  type="button"
                  className="btn btn-outline btn-sm"
                  style={{ marginBottom: 14 }}
                  onClick={() => setMedicamentos((list) => [...list, ""])}
                >
                  + Agregar medicamento
                </button>
                <div className="sign-status">
                  <span className="pill pill-warn">Pendiente de firma</span>
                  <button className="btn btn-primary" type="submit" disabled={rxStatus.status === "loading"}>
                    {rxStatus.status === "loading" ? "Firmando..." : "Firmar y enviar receta"}
                  </button>
                </div>
              </form>
            ) : (
              <p className="helper">
                Tu medico emitira la receta al finalizar la consulta; aparecera aqui una vez
                que M4 confirme <code>POST /prescription</code>.
              </p>
            )}
          </div>
        </div>
      </div>
    </>
  );
}
