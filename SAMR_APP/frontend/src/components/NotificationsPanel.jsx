import { useNotifications } from "./NotificationContext";
import { Icon } from "./ui/Icon";
import { formatDistanceToNow } from 'date-fns';
import { es } from 'date-fns/locale';

export function NotificationsPanel({ onClose }) {
  const { notifications, markAsRead } = useNotifications();

  return (
    <div className="card animate-fade-in" style={{ position: 'absolute', top: 60, right: 20, width: 350, maxHeight: 450, overflowY: 'auto', zIndex: 1000, boxShadow: '0 10px 25px rgba(0,0,0,0.2)', padding: 0 }}>
      <div style={{ padding: '16px 20px', borderBottom: '1px solid var(--border)', display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: '#f8fafc', position: 'sticky', top: 0, zIndex: 2 }}>
        <h3 style={{ margin: 0, fontSize: 16, color: 'var(--c-deep)' }}>Notificaciones</h3>
        <button onClick={onClose} style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--muted)' }}><Icon name="x" size={16} /></button>
      </div>
      
      <div style={{ display: 'flex', flexDirection: 'column' }}>
        {notifications.length === 0 ? (
          <div style={{ padding: 30, textAlign: 'center', color: 'var(--muted)', fontSize: 13 }}>
            <Icon name="bell-off" size={24} style={{ marginBottom: 10, opacity: 0.5 }} />
            <p>No tienes notificaciones</p>
          </div>
        ) : (
          notifications.map(noti => (
            <div 
              key={noti.id} 
              onClick={() => markAsRead(noti.id)}
              style={{ padding: '16px 20px', borderBottom: '1px solid var(--border)', background: noti.read ? 'var(--white)' : '#f0fafc', cursor: 'pointer', display: 'flex', gap: 12, transition: 'background 0.2s' }}
            >
              <div style={{ marginTop: 2 }}>
                <Icon name={noti.type === 'error' ? 'alert-circle' : noti.type === 'success' ? 'check-circle' : 'info'} size={18} color={noti.type === 'error' ? '#ef4444' : noti.type === 'success' ? '#10b981' : '#3b82f6'} />
              </div>
              <div style={{ flex: 1 }}>
                <p style={{ margin: '0 0 4px', fontSize: 13, fontWeight: noti.read ? 600 : 800, color: 'var(--c-deep)' }}>{noti.title}</p>
                <p style={{ margin: '0 0 6px', fontSize: 12, color: 'var(--muted)', lineHeight: 1.4 }}>{noti.message}</p>
                <p style={{ margin: 0, fontSize: 10, color: '#94a3b8' }}>
                  {formatDistanceToNow(new Date(noti.date), { addSuffix: true, locale: es })}
                </p>
              </div>
              {!noti.read && <div style={{ width: 8, height: 8, borderRadius: '50%', background: '#3b82f6', marginTop: 6 }}></div>}
            </div>
          ))
        )}
      </div>
    </div>
  );
}
