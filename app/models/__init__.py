# Importa todos los modelos aquí para que Flask-Migrate los detecte
# al correr `flask db migrate`.

from app.models.usuario import Usuario, CodigoMFA, ConsentimientoLOPDP  # noqa: F401
from app.models.solicitud import Solicitud  # noqa: F401
from app.models.captura_biometrica import CapturaBiometrica, AlertaPredictivaXAI  # noqa: F401
from app.models.teleconsulta import Teleconsulta, RecetaDigital  # noqa: F401
from app.models.log_auditoria import LogAuditoria  # noqa: F401
