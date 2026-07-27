# API Gateway

## Responsabilidad
Punto unico de entrada del sistema. Enruta cada peticion del
frontend al microservicio correspondiente (M1-M5) y valida el
token JWT emitido por M1 antes de dejar pasar cualquier peticion.
Ningun microservicio implementa su propia validacion de sesion.

## Estructura
- /routes        -> una ruta por microservicio (m1.js, m2.js, etc.)
- /middlewares    -> validacion JWT, logging, manejo de errores
- /config         -> URLs de los microservicios, variables de entorno

## Definition of Done
- Rechaza toda peticion sin JWT valido
- Enruta correctamente a los 5 microservicios
- TLS 1.3 configurado en el canal de entrada
- Ninguna logica de negocio vive aqui, solo enrutamiento y seguridad
