import { Icon } from "../../components/ui/Icon";
import "../../styles/recetas.css";

const MOCK_RECETAS = [
  {
    id: "REC-2026-001",
    fecha: "2026-07-28",
    medico: "Dr. Dionio Fernández",
    especialidad: "Medicina General",
    diagnostico: "Infección respiratoria aguda",
    medicamentos: ["Amoxicilina 500mg", "Ibuprofeno 400mg"],
    estado: "Vigente"
  },
  {
    id: "REC-2026-002",
    fecha: "2026-06-15",
    medico: "Dra. Ana López",
    especialidad: "Cardiología",
    diagnostico: "Hipertensión controlada",
    medicamentos: ["Losartán 50mg"],
    estado: "Expirada"
  }
];

export function Recetas() {
  const handleDownload = (id) => {
    // Simular descarga
    console.log(`Descargando receta ${id}`);
    alert(`Descargando PDF de la receta ${id}...`);
  };

  return (
    <div className="recetas-container animate-fade-in">
      <div className="recetas-header">
        <h2>Mis Recetas Médicas</h2>
        <p>Historial de prescripciones emitidas por tus médicos tratantes.</p>
      </div>

      <div className="recetas-grid">
        {MOCK_RECETAS.map((receta) => (
          <div key={receta.id} className="receta-card">
            <div className="receta-card-header">
              <div className="receta-icon">
                <Icon name="file-text" size={24} />
              </div>
              <div className="receta-meta">
                <span className="receta-id">{receta.id}</span>
                <span className={`receta-estado ${receta.estado === 'Vigente' ? 'vigente' : 'expirada'}`}>
                  {receta.estado}
                </span>
              </div>
            </div>
            
            <div className="receta-card-body">
              <div className="receta-detail">
                <Icon name="calendar" size={14} />
                <span>Emitida: {receta.fecha}</span>
              </div>
              <div className="receta-detail">
                <Icon name="user" size={14} />
                <span>{receta.medico} ({receta.especialidad})</span>
              </div>
              <div className="receta-detail">
                <Icon name="activity" size={14} />
                <span>{receta.diagnostico}</span>
              </div>
              
              <div className="receta-medicamentos">
                <strong>Medicamentos prescritos:</strong>
                <ul>
                  {receta.medicamentos.map((med, i) => (
                    <li key={i}>{med}</li>
                  ))}
                </ul>
              </div>
            </div>

            <div className="receta-card-footer">
              <button className="btn btn-outline btn-block" onClick={() => handleDownload(receta.id)}>
                <Icon name="download" size={16} /> Descargar PDF
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
