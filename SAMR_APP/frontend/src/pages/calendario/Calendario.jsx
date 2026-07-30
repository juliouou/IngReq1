import { useState } from "react";
import { Icon } from "../../components/ui/Icon";
import "../../styles/calendario.css";

const MOCK_CITAS = [
  { id: 1, hora: "09:30", dura: 15, paciente: "FERNÁNDEZ DE FLORES, DIONIO", descripcion: "Control general", profesional: "DR. ANA CLETO" },
  { id: 2, hora: "14:00", dura: 15, paciente: "BREGUAL SIESTO, RAMIRO", descripcion: "ECOGRAFÍA TRANSVERSAL", profesional: "DR. ANEO PARIOLO" }
];

export function Calendario() {
  const [fecha, setFecha] = useState("2026-09-29");

  return (
    <div className="card calendario-card animate-fade-in">
      <div className="calendario-header">
        <div className="cal-left">
          <div className="cal-date-picker">
            <span style={{ fontSize: 10, color: 'var(--muted)', display: 'block' }}>IR AL DÍA -></span>
            <input type="date" value={fecha} onChange={(e) => setFecha(e.target.value)} />
          </div>
          <button className="btn btn-primary" style={{ display: 'flex', gap: 5, alignItems: 'center' }}>
            <Icon name="plus-circle" size={14} /> Paciente
          </button>
          <button className="btn btn-outline" style={{ display: 'flex', gap: 5, alignItems: 'center', borderColor: '#20b2aa', color: '#20b2aa' }}>
            <Icon name="plus-circle" size={14} /> Cita
          </button>
        </div>

        <div className="cal-center">
          <button className="nav-arrow"><Icon name="chevron-left" size={16} /></button>
          <h2 className="current-date">martes 29 septiembre 2026</h2>
          <button className="nav-arrow"><Icon name="chevron-right" size={16} /></button>
        </div>

        <div className="cal-right">
          <button className="btn btn-ghost" style={{ border: '1px solid var(--border)' }}>
            IR A HOY <Icon name="calendar" size={14} style={{ marginLeft: 6 }} />
          </button>
          <button className="btn btn-warning" style={{ background: '#f97316', color: '#fff', border: 'none' }}>
            <Icon name="briefcase" size={14} /> Consultar Citas
          </button>
        </div>
      </div>

      <div className="calendario-filters">
        <select><option>VER Citas Por SALA</option></select>
        <select><option>VER Citas por PROFESIONAL</option></select>
        
        <div className="view-toggles">
          <button className="active"><Icon name="align-justify" size={14} /> Diaria</button>
          <button><Icon name="clock" size={14} /> Horaria</button>
          <button><Icon name="columns" size={14} /> Semanal</button>
          <button><Icon name="grid" size={14} /> Mensual</button>
        </div>
      </div>

      <table className="table cal-table">
        <thead>
          <tr>
            <th>Hora</th>
            <th>Dura</th>
            <th>Sala</th>
            <th>Paciente</th>
            <th>Descripción</th>
            <th>Profesional</th>
          </tr>
        </thead>
        <tbody>
          {MOCK_CITAS.map((cita) => (
            <tr key={cita.id}>
              <td><strong>{cita.hora}</strong></td>
              <td>{cita.dura}</td>
              <td></td>
              <td>{cita.paciente}</td>
              <td><Icon name="edit-2" size={12} style={{marginRight: 6, color: 'var(--muted)'}} /> {cita.descripcion}</td>
              <td>{cita.profesional}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
