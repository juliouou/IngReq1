"""Middleware personalizado del proyecto SAMR."""
import logging
import uuid

logger = logging.getLogger("samr")


class RequestIDMiddleware:
    """Asigna un identificador unico a cada peticion y lo expone en la respuesta."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.request_id = uuid.uuid4().hex
        response = self.get_response(request)
        response["X-Request-ID"] = request.request_id
        return response


class AuditoriaMiddleware:
    """
    Registra automaticamente las peticiones que modifican datos.

    El registro se realiza de forma tolerante a fallos: cualquier problema
    (por ejemplo, que las tablas aun no existan durante las migraciones) se
    ignora sin interrumpir la peticion.
    """

    METODOS_AUDITABLES = {"POST", "PUT", "PATCH", "DELETE"}

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        try:
            self._registrar(request, response)
        except Exception:  # noqa: BLE001
            logger.debug("No se pudo registrar la auditoria", exc_info=True)
        return response

    def _registrar(self, request, response):
        if request.method not in self.METODOS_AUDITABLES:
            return

        usuario = getattr(request, "user", None)
        if usuario is None or not usuario.is_authenticated:
            return

        # Import diferido para evitar dependencias circulares en el arranque.
        from apps.auditoria.models import RegistroAuditoria

        RegistroAuditoria.objects.create(
            usuario=usuario,
            accion=request.method,
            ruta=request.path[:255],
            codigo_estado=response.status_code,
            request_id=getattr(request, "request_id", ""),
            ip=self._obtener_ip(request),
        )

    @staticmethod
    def _obtener_ip(request):
        reenviada = request.META.get("HTTP_X_FORWARDED_FOR")
        if reenviada:
            return reenviada.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR", "")
