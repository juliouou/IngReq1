import { Link } from "react-router-dom";
import "../../styles/landing.css";
import { Icon } from "../../components/ui/Icon";

export function Landing() {
  return (
    <div className="landing-page">
      {/* Navbar */}
      <nav className="landing-nav">
        <div className="landing-logo">
          <img src="/logo.png" alt="SAMR Logo" style={{ width: '50px', height: '50px', objectFit: 'contain' }} />
        </div>
        <div className="nav-links">
          <a href="#quienes-somos">¿Quiénes Somos?</a>
          <a href="#que-hacemos">¿Qué Hacemos?</a>
          <a href="#contacto">Contacto</a>
        </div>
        <div className="auth-buttons">
          <Link to="/acceso" className="btn btn-ghost">Iniciar Sesión</Link>
          <Link to="/acceso/registro" className="btn btn-primary">Registrarse</Link>
        </div>
      </nav>

      {/* Hero Section */}
      <header className="hero">
        <div className="hero-watermark">
          <img src="/logo.png" alt="" />
        </div>
        <div className="hero-content">
          <h1>El Futuro de la Salud Conectada</h1>
          <p>Experimenta la próxima generación de telemedicina con inteligencia artificial clínica, monitoreo biométrico en tiempo real y triaje instantáneo.</p>
          <div className="hero-actions">
            <Link to="/acceso/registro" className="btn btn-primary btn-large">Comenzar ahora</Link>
            <a href="#que-hacemos" className="btn btn-outline btn-large">Descubre más</a>
          </div>
        </div>
      </header>

      {/* Who We Are */}
      <section id="quienes-somos" className="section bg-soft">
        <div className="container">
          <h2 className="section-title">¿Quiénes Somos?</h2>
          <p className="section-subtitle">
            SAMR (Sistema de Atención Médica Remota) nace con la misión de democratizar el acceso a la atención médica de calidad utilizando el poder de Med-Gemini y dispositivos IoT. 
            Conectamos a pacientes y doctores en milisegundos, eliminando las barreras de la distancia.
          </p>
        </div>
      </section>

      {/* What We Do */}
      <section id="que-hacemos" className="section">
        <div className="container">
          <h2 className="section-title">¿Qué ofrece nuestra plataforma?</h2>
          <div className="features-grid">
            <div className="feature-card">
              <div className="feature-icon"><Icon name="bot" size={32} /></div>
              <h3>Evaluación Médica IA</h3>
              <p>Nuestro asistente inteligente analiza tus síntomas en tiempo real para brindarte un pre-diagnóstico certero antes de ver al médico.</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon"><Icon name="heart" size={32} /></div>
              <h3>Monitoreo IoT</h3>
              <p>Conexión directa con sensores biométricos para alertar automáticamente a los doctores ante cualquier anomalía crítica.</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon"><Icon name="video" size={32} /></div>
              <h3>Teleconsulta HD</h3>
              <p>Videollamadas estables con acceso inmediato a tu historial clínico y signos vitales en pantalla durante la sesión.</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon"><Icon name="shield" size={32} /></div>
              <h3>Máxima Seguridad</h3>
              <p>Auditoría en blockchain y cifrado de grado bancario (MFA) para proteger la privacidad absoluta de tus datos médicos.</p>
            </div>
          </div>
        </div>
      </section>

      {/* Contact Section */}
      <section id="contacto" className="section bg-soft">
        <div className="container">
          <div className="contact-box card">
            <h2 className="section-title">¿Tienes preguntas o comentarios?</h2>
            <p className="section-subtitle" style={{textAlign: 'center', marginBottom: 30}}>
              Nos encantaría escuchar tu opinión para seguir mejorando.
            </p>
            <form className="contact-form" onSubmit={e => { e.preventDefault(); alert('¡Gracias por tus comentarios! Nos pondremos en contacto pronto.'); }}>
              <div className="field">
                <label>Tu Nombre</label>
                <input required placeholder="Ej. Ana Pérez" />
              </div>
              <div className="field">
                <label>Correo Electrónico</label>
                <input type="email" required placeholder="ana@ejemplo.com" />
              </div>
              <div className="field">
                <label>Mensaje</label>
                <textarea rows="4" required placeholder="Escribe tu mensaje o comentario aquí..."></textarea>
              </div>
              <button type="submit" className="btn btn-primary btn-block">Enviar Mensaje</button>
            </form>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="footer">
        <div className="container footer-content">
          <div className="footer-logo">
            <img src="/logo.png" alt="SAMR Logo" style={{ width: '50px', height: '50px', objectFit: 'contain' }} />
          </div>
          <div className="footer-links">
            <a href="#">Privacidad (LOPDP)</a>
            <a href="#">Términos de Servicio</a>
            <a href="#">Soporte Médico</a>
          </div>
        </div>
        <div className="footer-bottom">
          © 2026 SAMR. Todos los derechos reservados. Impulsado por Med-Gemini.
        </div>
      </footer>
    </div>
  );
}
