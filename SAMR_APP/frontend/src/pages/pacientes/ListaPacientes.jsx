import { Icon } from "../../components/ui/Icon";

const MOCK_PACIENTES = [
  { id: 1, nombre: "FERNÁNDEZ DE FLORES, DIONIO", edad: 45, sangre: "O+", alergias: "Ninguna", ultimaVisita: "29 Sep 2026", estado: "Estable" },
  { id: 2, nombre: "BREGUAL SIESTO, RAMIRO", edad: 62, sangre: "A-", alergias: "Penicilina", ultimaVisita: "15 Sep 2026", estado: "En Tratamiento" }
];

export function ListaPacientes() {
  return (
    <div className="card animate-fade-in" style={{ padding: 24 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
        <h2 style={{ margin: 0, fontSize: 20, color: 'var(--c-deep)' }}>Directorio de Pacientes</h2>
        <div style={{ display: 'flex', gap: 10 }}>
          <div style={{ position: 'relative' }}>
            <Icon name="search" size={14} style={{ position: 'absolute', top: 10, left: 10, color: 'var(--muted)' }} />
            <input type="text" placeholder="Buscar paciente..." style={{ padding: '8px 10px 8px 30px', border: '1px solid var(--border)', borderRadius: 6 }} />
          </div>
          <button className="btn btn-primary" style={{ display: 'flex', gap: 6, alignItems: 'center' }}>
            <Icon name="user-plus" size={14} /> Nuevo
          </button>
        </div>
      </div>

      <table className="table">
        <thead>
          <tr>
            <th>Nombre Completo</th>
            <th>Edad</th>
            <th>Sangre</th>
            <th>Alergias</th>
            <th>Última Visita</th>
            <th>Estado</th>
            <th>Acciones</th>
          </tr>
        </thead>
        <tbody>
          {MOCK_PACIENTES.map((p) => (
            <tr key={p.id}>
              <td style={{ fontWeight: 600 }}>{p.nombre}</td>
              <td>{p.edad} años</td>
              <td>{p.sangre}</td>
              <td>{p.alergias}</td>
              <td>{p.ultimaVisita}</td>
              <td>
                <span className={`pill ${p.estado === 'Estable' ? 'pill-ok' : 'pill-warn'}`}>{p.estado}</span>
              </td>
              <td>
                <button className="btn btn-ghost btn-sm" title="Ver Historial"><Icon name="file-text" size={14} /></button>
                <button className="btn btn-ghost btn-sm" title="Iniciar Teleconsulta"><Icon name="video" size={14} /></button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
