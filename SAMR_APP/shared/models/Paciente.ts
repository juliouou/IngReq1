export interface Paciente {
  id: string;
  nombre: string;
  fechaNacimiento: string;
  telefono: string;
  direccion: string;
  consentimientoLOPDP: boolean;
  coberturaIESS: boolean;
}
