# API Gateway

## Responsabilidad
Punto unico de entrada del sistema. Enruta cada peticion del
frontend al microservicio correspondiente (M1-M5) y valida el
token JWT emitido por M1 antes de dejar pasar cualquier peticion.
Ningun microservicio implementa su propia validacion de sesion.

## Estructura
- `index.js`         -> registro de rutas por microservicio (proxy con http-proxy-middleware)
- `middlewares/auth.js` -> requireAuth (JWT) y requireRole (autorizacion por rol)
- `config/services.js`  -> URLs de los microservicios (variables de entorno)

## Definition of Done
- [x] Rechaza toda peticion sin JWT valido (401)
- [x] Rechaza peticiones de un rol no autorizado en rutas sensibles (403):
      `/audit/*` solo administrativo/msp/dpo, `/diagnosis` y `/prescription`
      solo medico
- [x] Enruta correctamente a los 5 microservicios, incluyendo el upgrade de
      WebSocket para la senalizacion WebRTC de M4 (`/signaling`)
- [ ] TLS 1.3 en el canal de entrada: fuera de alcance para desarrollo
      local; en un despliegue real lo terminaria un proxy/load balancer
- [x] Ninguna logica de negocio vive aqui, solo enrutamiento y seguridad
