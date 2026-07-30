import { createContext, useContext, useState, useCallback } from "react";
import { Icon } from "./ui/Icon";

const NotificationContext = createContext();

export function NotificationProvider({ children }) {
  const [notifications, setNotifications] = useState([
    { id: 1, type: "info", title: "Bienvenido", message: "Gracias por usar SAMR", date: new Date().toISOString(), read: false }
  ]);
  const [popup, setPopup] = useState(null);

  const addNotification = useCallback((noti) => {
    const newNoti = { id: Date.now(), date: new Date().toISOString(), read: false, ...noti };
    setNotifications(prev => [newNoti, ...prev]);
    
    if (noti.critical) {
      setPopup(newNoti);
    }
  }, []);

  const markAsRead = useCallback((id) => {
    setNotifications(prev => prev.map(n => n.id === id ? { ...n, read: true } : n));
  }, []);

  const clearPopup = () => setPopup(null);

  return (
    <NotificationContext.Provider value={{ notifications, addNotification, markAsRead }}>
      {children}
      
      {/* Global Critical Popup */}
      {popup && (
        <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.6)', backdropFilter: 'blur(4px)', zIndex: 9999, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <div className="card animate-fade-in" style={{ width: '90%', maxWidth: 400, padding: 24, textAlign: 'center', border: popup.type === 'error' ? '2px solid #ef4444' : 'none' }}>
            <div style={{ background: popup.type === 'error' ? '#fef2f2' : '#f0fafc', width: 60, height: 60, borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 20px' }}>
              <Icon name={popup.type === 'error' ? 'alert-triangle' : 'bell'} size={30} color={popup.type === 'error' ? '#ef4444' : '#20b2aa'} />
            </div>
            <h2 style={{ margin: '0 0 10px', fontSize: 20, color: 'var(--c-deep)' }}>{popup.title}</h2>
            <p style={{ color: 'var(--muted)', fontSize: 14, marginBottom: 24 }}>{popup.message}</p>
            <button className="btn btn-primary btn-block" onClick={clearPopup} style={{ background: popup.type === 'error' ? '#ef4444' : '' }}>
              Entendido
            </button>
          </div>
        </div>
      )}
    </NotificationContext.Provider>
  );
}

export const useNotifications = () => useContext(NotificationContext);
