import { useState } from "react";
import { AuthLayout } from "./AuthLayout";

export function RecuperarAcceso() {
  const [email, setEmail] = useState("");
  const [submitted, setSubmitted] = useState(false);

  const onSubmit = (e) => {
    e.preventDefault();
    setSubmitted(true);
  };

  return (
    <AuthLayout
      title="Recupera el acceso a tu cuenta"
      description="Ingresa tu correo y te guiaremos para restablecer tu contrasena."
    >
      <form onSubmit={onSubmit} noValidate>
        {submitted ? (
          <div className="banner banner-warn" role="status">
            M1 - Usuarios y Acceso todavia no define en su contrato (
            <code>docs/openapi.yaml</code>) un endpoint de recuperacion de contrasena. Esta
            pantalla queda lista en el frontend; falta que Backend/Arquitectura agreguen el
            endpoint correspondiente para poder conectarla.
          </div>
        ) : (
          <div className="field">
            <label htmlFor="recover-email">Correo electronico</label>
            <input
              id="recover-email"
              type="email"
              required
              placeholder="nombre@correo.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
          </div>
        )}

        <button className="btn btn-primary btn-block" type="submit" disabled={submitted}>
          Enviar instrucciones
        </button>
      </form>
    </AuthLayout>
  );
}
