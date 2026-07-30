import { Icon } from "../../components/ui/Icon";

export function MapaHospitales() {
  return (
    <div className="card animate-fade-in" style={{ padding: 24, height: 'calc(100vh - 120px)', display: 'flex', flexDirection: 'column' }}>
      <div style={{ marginBottom: 20 }}>
        <h2 style={{ margin: 0, fontSize: 20, color: 'var(--c-deep)', display: 'flex', alignItems: 'center', gap: 10 }}>
          <Icon name="map-pin" size={20} color="#ef4444" /> Clínicas y Hospitales Cercanos
        </h2>
        <p style={{ color: 'var(--muted)', fontSize: 13, marginTop: 4 }}>
          Encuentra centros médicos disponibles para emergencias o atención presencial.
        </p>
      </div>

      <div style={{ flex: 1, borderRadius: 12, overflow: 'hidden', border: '1px solid var(--border)' }}>
        <iframe 
          title="Mapa de Hospitales"
          width="100%" 
          height="100%" 
          style={{ border: 0 }} 
          loading="lazy" 
          allowFullScreen 
          referrerPolicy="no-referrer-when-downgrade" 
          src="https://www.google.com/maps/embed?pb=!1m16!1m12!1m3!1d113911.4552438781!2d-79.9678484!3d-2.1961601!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!2m1!1shospitales%20clinicas!5e0!3m2!1ses!2sec!4v1715000000000!5m2!1ses!2sec"
        ></iframe>
      </div>
    </div>
  );
}
