import { useState, useRef, useEffect } from "react";
import { Icon } from "./Icon";
import { useAuth } from "../../context/AuthContext";
import { useNotifications } from "../NotificationContext";
import * as triajeApi from "../../lib/api/triaje";
import "../../styles/chat-widget.css";

const initialMessages = [
  {
    from: "bot",
    text: "¡Hola, soy Chati uwu! Tu asistente médico de confianza. ¿Cómo estás hoy? ¿Te puedo ayudar con algún síntoma?",
  },
];

export function ChatWidget() {
  const { user, token } = useAuth();
  const { addNotification } = useNotifications();
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState(initialMessages);
  const [draft, setDraft] = useState("");
  const [sending, setSending] = useState(false);
  const bodyRef = useRef(null);

  useEffect(() => {
    if (isOpen && bodyRef.current) {
      bodyRef.current.scrollTo({ top: bodyRef.current.scrollHeight, behavior: "smooth" });
    }
  }, [messages, isOpen]);

  const onSubmitChat = async (e) => {
    e.preventDefault();
    const text = draft.trim();
    if (!text || sending) return;
    
    setDraft("");
    
    // Add user message to state
    const newMessages = [...messages, { from: "user", text }];
    setMessages(newMessages);
    setSending(true);
    
    try {
      // Build Ollama chat history format
      const ollamaMessages = newMessages.map(m => ({
        role: m.from === 'bot' ? 'assistant' : 'user',
        content: m.text
      }));

      // Prepend System Prompt
      ollamaMessages.unshift({
        role: 'system',
        content: "Eres Chati, la asistente médica virtual del sistema SAMR. Tu tono debe ser natural, cálido, profesional y respetuoso, inspirando confianza en los pacientes. Muestra empatía ante sus síntomas, pero mantén la formalidad médica. Tu objetivo principal es ayudar a los pacientes a sentirse cómodos, preguntar por sus síntomas con claridad, y darles recomendaciones muy generales. CRÍTICO: Si determinas que el paciente requiere una consulta médica presencial o virtual (porque el caso no se puede resolver solo con recomendaciones), DEBES incluir exactamente la frase 'Te recomiendo agendar una cita.' en tu respuesta. No des diagnósticos médicos definitivos, siempre aclara que eres una inteligencia artificial de soporte. Responde siempre en español, de forma clara, conversacional y profesional."
      });

      const response = await fetch('http://localhost:11434/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          model: 'llama3', // Modelo por defecto, el usuario debe tenerlo instalado
          messages: ollamaMessages,
          stream: false // Para simplicidad, esperamos la respuesta completa
        })
      });

      if (!response.ok) {
        throw new Error("Ollama network error");
      }

      const data = await response.json();
      const botReply = data.message?.content || "No pude generar una respuesta uwu";
      
      const requiresPainScale = botReply.toLowerCase().includes("escala") || botReply.toLowerCase().includes("1 al 10") || botReply.toLowerCase().includes("1 a 10");
      const requiresAppointment = botReply.toLowerCase().includes("agendar una cita");
      
      setMessages((m) => [...m, { from: "bot", text: botReply, requiresPainScale, requiresAppointment }]);
    } catch (err) {
      console.error("Error connecting to Ollama:", err);
      setMessages((m) => [...m, { from: "bot", text: "Ay no... no me puedo conectar a mi cerebro local pipipi. Asegúrate de tener Ollama corriendo en el puerto 11434 con el modelo 'llama3' :(" }]);
    } finally {
      setSending(false);
    }
  };

  const handlePainScaleClick = async (level) => {
    const text = `Mi nivel de dolor es ${level}/10.`;
    setMessages((m) => [...m, { from: "user", text }]);
    setSending(true);

    // Trigger Doctor Alert immediately
    addNotification({
      title: "¡Alerta Médica Inmediata!",
      message: `El paciente ${user?.nombre || user?.email} reporta un nivel de dolor crítico (${level}/10).`,
      type: "error",
      critical: true
    });

    try {
      const data = await triajeApi.crearTriaje({ pacienteId: user?.id, tipo: "sintomas", sintomas: `Dolor nivel ${level}/10 reportado vía Chatbot.` }, token);
      setMessages((m) => [...m, { from: "bot", text: "He enviado una alerta inmediata de prioridad alta a tu doctor asignado. Un especialista revisará tu caso en los próximos minutos." }]);
    } catch (e) {
      setMessages((m) => [...m, { from: "bot", text: "He intentado enviar la alerta, pero hubo un error de conexión. Por favor, acércate a emergencias." }]);
    } finally {
      setSending(false);
    }
  };

  const handleScheduleClick = () => {
    setMessages((m) => [...m, { from: "user", text: "Quiero agendar una cita médica ahora." }]);
    setSending(true);

    // Simulate API call for scheduling
    setTimeout(() => {
      addNotification({
        title: "Cita Agendada",
        message: "Tu cita presencial ha sido confirmada para mañana a las 10:00 AM.",
        type: "success",
        critical: false
      });
      setMessages((m) => [...m, { from: "bot", text: "¡Listo! He agendado tu cita presencial para mañana a las 10:00 AM con tu médico especialista. También he notificado a la clínica. ¿Hay algo más en lo que te pueda ayudar?" }]);
      setSending(false);
    }, 1500);
  };

  const getPainColor = (level) => {
    if (level <= 3) return "#10b981"; // Green
    if (level <= 6) return "#f59e0b"; // Yellow/Orange
    if (level <= 8) return "#f97316"; // Orange
    return "#ef4444"; // Red
  };

  return (
    <>
      {isOpen && (
        <div className="chat-widget-window animate-fade-in">
          <div className="chat-widget-header">
            <div className="header-info">
              <div className="bot-avatar" style={{ overflow: 'hidden' }}>
                <img src="/chati-avatar.png" alt="Chati" style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
              </div>
              <div>
                <h4>Chati :3</h4>
                <span>En línea</span>
              </div>
            </div>
            <button className="close-btn" onClick={() => setIsOpen(false)}><Icon name="x" size={16} /></button>
          </div>
          
          <div className="chat-widget-body" ref={bodyRef}>
            {messages.map((m, i) => (
              <div key={i} style={{ display: 'flex', flexDirection: 'column' }}>
                <div className={`msg ${m.from}`}>{m.text}</div>
                {m.requiresPainScale && m.from === "bot" && (
                  <div className="pain-scale-container animate-fade-in">
                    {[1,2,3,4,5,6,7,8,9,10].map(num => (
                      <button 
                        key={num} 
                        className="pain-scale-btn" 
                        style={{ backgroundColor: getPainColor(num) }}
                        onClick={() => handlePainScaleClick(num)}
                        disabled={sending}
                      >
                        {num}
                      </button>
                    ))}
                  </div>
                )}
                {m.requiresAppointment && m.from === "bot" && (
                  <div style={{ marginTop: 10, textAlign: 'center' }} className="animate-fade-in">
                    <button 
                      className="btn btn-primary" 
                      style={{ fontSize: 13, padding: '8px 16px', borderRadius: 20, width: '100%' }}
                      onClick={handleScheduleClick}
                      disabled={sending}
                    >
                      <Icon name="calendar" size={14} style={{ marginRight: 6 }} />
                      Agendar Cita Inmediata
                    </button>
                  </div>
                )}
              </div>
            ))}
            {sending && (
              <div className="typing" aria-label="El asistente esta escribiendo">
                <span /><span /><span />
              </div>
            )}
          </div>
          
          <form className="chat-widget-input" onSubmit={onSubmitChat}>
            <input 
              type="text" 
              placeholder="Escribe tu mensaje..." 
              value={draft} 
              onChange={(e) => setDraft(e.target.value)} 
              disabled={sending} 
            />
            <button type="submit" disabled={sending || !draft.trim()}>
              <Icon name="send" size={15} />
            </button>
          </form>
        </div>
      )}
      
      <button 
        className={`chat-widget-trigger ${isOpen ? 'open' : ''}`}
        onClick={() => setIsOpen(!isOpen)}
        aria-label="Abrir chat de asistencia"
        style={{ padding: 0, overflow: 'hidden' }}
      >
        {isOpen ? (
          <Icon name="chevron-down" size={24} />
        ) : (
          <img src="/chati-avatar.png" alt="Chati" style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
        )}
      </button>
    </>
  );
}
