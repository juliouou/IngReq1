import { useState, useRef, useEffect } from "react";
import { Icon } from "./Icon";
import { useAuth } from "../../context/AuthContext";
import * as triajeApi from "../../lib/api/triaje";
import "../../styles/chat-widget.css";

const initialMessages = [
  {
    from: "bot",
    text: "¡Hola! Soy tu asistente médico inteligente. ¿Estás bien? ¿Necesitas ayuda o sientes algún síntoma?",
  },
];

export function ChatWidget() {
  const { user, token } = useAuth();
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
    setMessages((m) => [...m, { from: "user", text }]);
    setSending(true);
    
    try {
      const data = await triajeApi.crearTriaje({ pacienteId: user?.id, tipo: "sintomas", sintomas: text }, token);
      setMessages((m) => [...m, { from: "bot", text: data?.explanation || "Solicitud registrada. Un especialista revisará tu caso en breve." }]);
    } catch (err) {
      setMessages((m) => [...m, { from: "bot", text: "Lo siento, tuve un problema al procesar eso. Por favor, intenta de nuevo." }]);
    } finally {
      setSending(false);
    }
  };

  return (
    <>
      {isOpen && (
        <div className="chat-widget-window animate-fade-in">
          <div className="chat-widget-header">
            <div className="header-info">
              <div className="bot-avatar"><Icon name="bot" size={18} /></div>
              <div>
                <h4>Asistente SAMR</h4>
                <span>En línea</span>
              </div>
            </div>
            <button className="close-btn" onClick={() => setIsOpen(false)}><Icon name="x" size={16} /></button>
          </div>
          
          <div className="chat-widget-body" ref={bodyRef}>
            {messages.map((m, i) => (
              <div key={i} className={`msg ${m.from}`}>{m.text}</div>
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
      >
        <Icon name={isOpen ? "chevron-down" : "message-circle"} size={24} />
      </button>
    </>
  );
}
