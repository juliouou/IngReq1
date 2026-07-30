import { useRef, useState } from "react";
import { Topbar } from "../../components/layout/Topbar";
import { useAuth } from "../../context/AuthContext";
import * as triajeApi from "../../lib/api/triaje";
import { EmptyState, ErrorState } from "../../components/ui/StateBlock";
import { Icon } from "../../components/ui/Icon";

const initialMessages = [
  {
    from: "bot",
    text: "Hola, soy el asistente de triaje SAMR. Cuentame, cual es tu sintoma principal?",
  },
];

export function Triaje() {
  const { user, token } = useAuth();
  const [messages, setMessages] = useState(initialMessages);
  const [draft, setDraft] = useState("");
  const [sending, setSending] = useState(false);
  const [resultado, setResultado] = useState(null);
  const [errorResumen, setErrorResumen] = useState(null);
  const [emergencia, setEmergencia] = useState({ status: "idle", error: null });
  const bodyRef = useRef(null);

  const enviarSolicitud = async (payload, mensajeUsuario) => {
    setMessages((m) => [...m, { from: "user", text: mensajeUsuario }]);
    setSending(true);
    setErrorResumen(null);
    try {
      const data = await triajeApi.crearTriaje(payload, token);
      setResultado(data);
      setMessages((m) => [
        ...m,
        {
          from: "bot",
          text:
            data?.explanation ||
            data?.mensaje ||
            "Solicitud registrada. Un especialista revisara tu caso en breve.",
        },
      ]);
    } catch (err) {
      setErrorResumen(err);
      setMessages((m) => [
        ...m,
        {
          from: "bot",
          text:
            "No pude clasificar tu solicitud ahora mismo (" +
            err.message +
            "). Tu mensaje quedo registrado localmente; intenta de nuevo en unos minutos.",
        },
      ]);
    } finally {
      setSending(false);
      queueMicrotask(() => {
        bodyRef.current?.scrollTo({ top: bodyRef.current.scrollHeight, behavior: "smooth" });
      });
    }
  };

  const onSubmit = (e) => {
    e.preventDefault();
    const text = draft.trim();
    if (!text || sending) return;
    setDraft("");
    enviarSolicitud(
      { pacienteId: user?.id, tipo: "sintomas", sintomas: text },
      text
    );
  };

  const enviarAlertaEmergencia = async () => {
    setEmergencia({ status: "loading", error: null });
    try {
      await triajeApi.crearTriaje(
        { pacienteId: user?.id, tipo: "alerta_iot", sintomas: "Alerta de emergencia desde dispositivo IoT" },
        token
      );
      setEmergencia({ status: "success", error: null });
    } catch (err) {
      setEmergencia({ status: "error", error: err });
    }
  };

  return (
    <>
      <Topbar title="Asistente de triaje" subtitle="Solicitud guiada por bot conversacional - Med-Gemini" />

      <div className="triage-grid">
        <div className="chat-panel">
          <div className="chat-head">
            <div className="bot-avatar">
              <Icon name="bot" size={18} />
            </div>
            <div>
              <div className="n">Bot de Triaje SAMR</div>
              <div className="s">Conectado a POST /triage (M2)</div>
            </div>
          </div>
          <div className="chat-body" ref={bodyRef}>
            {messages.map((m, i) => (
              <div key={i} className={`msg ${m.from}`}>
                {m.text}
              </div>
            ))}
            {sending && (
              <div className="typing" aria-label="El asistente esta escribiendo">
                <span />
                <span />
                <span />
              </div>
            )}
          </div>
          <form className="chat-input" onSubmit={onSubmit}>
            <input
              type="text"
              placeholder="Describe tus sintomas..."
              value={draft}
              onChange={(e) => setDraft(e.target.value)}
              disabled={sending}
              aria-label="Escribe tu sintoma"
            />
            <button
              className="icon-btn"
              type="submit"
              disabled={sending || !draft.trim()}
              aria-label="Enviar mensaje"
            >
              <Icon name="send" size={15} />
            </button>
          </form>
        </div>

        <div className="side-col">
          <div className="card">
            <div className="card-title">Resumen de tu solicitud</div>
            {resultado ? (
              <>
                <div className="urgency-box">
                  <div>
                    <div className="lbl">Prioridad sugerida por Med-Gemini</div>
                    <div className="val">{resultado.prioridad || "Pendiente"}</div>
                  </div>
                  <span className="pill pill-danger">
                    {resultado.tiempoEstimado || "Por confirmar"}
                  </span>
                </div>
                {Array.isArray(resultado.sintomasDetectados) && (
                  <div className="tag-row">
                    {resultado.sintomasDetectados.map((s) => (
                      <span className="tag" key={s}>
                        {s}
                      </span>
                    ))}
                  </div>
                )}
                {resultado.explanation && (
                  <div className="xai-box">
                    <div className="h">Por que esta prioridad? (XAI)</div>
                    <ul>
                      <li>{resultado.explanation}</li>
                    </ul>
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
              <ErrorState
                title="M2 - Triaje aun no respondio"
                detail={errorResumen.message}
              />
            ) : (
              <EmptyState
                title="Aun no hay una solicitud de triaje"
                detail="Escribe tus sintomas en el chat para generar una."
              />
            )}
          </div>

          <div className="emergency-card">
            <div className="h">Alerta de emergencia IoT</div>
            <p>
              Si tu situacion empeora, envia una alerta inmediata generada desde un
              dispositivo IoT vinculado (solicitud tipo <code>alerta_iot</code>).
            </p>
            {emergencia.status === "success" && (
              <div className="banner banner-ok">Alerta enviada y registrada.</div>
            )}
            {emergencia.status === "error" && (
              <div className="banner banner-error">{emergencia.error.message}</div>
            )}
            <button
              className="btn btn-danger btn-block"
              type="button"
              onClick={enviarAlertaEmergencia}
              disabled={emergencia.status === "loading"}
            >
              {emergencia.status === "loading" ? "Enviando..." : "Enviar alerta de emergencia"}
            </button>
          </div>
        </div>
      </div>
    </>
  );
}
