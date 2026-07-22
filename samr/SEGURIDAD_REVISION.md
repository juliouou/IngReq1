# Revisión de Seguridad - Módulos Nuevos

Se procedió a revisar las validaciones de seguridad de los flujos recientemente introducidos en la rama `feature/backend` antes de su potencial integración final.

## 1. Escalamiento de Triaje a Humano
**Archivo:** `apps/triaje/web_views.py` (Vista: `escalar_a_humano`)
**Revisión:** Verificamos que sólo el paciente dueño de la solicitud tenga la capacidad de escalarla.
**Resultado:** ✅ **Bien implementado**.
La consulta se hace utilizando `get_object_or_404(SolicitudAtencion, id=solicitud_id, paciente=request.user)`. Esto impone una validación estricta a nivel de base de datos; si un médico, administrador u otro paciente intenta realizar la acción, el ORM levantará un error 404 porque el objeto no coincide con su identificador de usuario.

## 2. Rechazo de Teleconsulta por el Médico Asignado
**Archivo:** `apps/teleconsulta/web_views.py` (Vista: `detalle_teleconsulta`, acción POST `rechazar`)
**Revisión:** Confirmar que únicamente el médico asignado pueda disparar la acción de rechazo de la teleconsulta.
**Resultado:** ✅ **Bien implementado**.
La lógica evalúa explícitamente `es_medico_de_esta_consulta = request.user.id == tc.medico_id` y lo exige como condicional: `if request.method == "POST" and es_medico_de_esta_consulta:`. Esto imposibilita a otros médicos ejecutar el rechazo.

## 3. Registro de Lecturas Biométricas (Simulador IoT)
**Archivo:** `apps/biometria/web_views.py` (Vista: `registrar_lectura`)
**Revisión:** Asegurar que el registro de una lectura impacte exclusiva y obligatoriamente sobre el dispositivo del paciente logueado, sin poder suplantar la identidad de un tercero.
**Resultado:** ✅ **Bien implementado**.
La consulta al dispositivo activo está fuertemente atada al usuario actual: `DispositivoIoT.objects.filter(paciente=request.user, activo=True).first()`. La lectura siempre ingresará al sistema a nombre de un dispositivo del cual el `request.user` es indudablemente el propietario.

## 4. Validación de Motivo en Rechazo de Teleconsulta
**Archivo:** `apps/teleconsulta/services.py` (Método: `rechazar_y_reasignar`)
**Revisión:** Confirmar que el motivo proporcionado por el médico tenga una longitud mínima razonable (al menos 10 caracteres) para evitar justificaciones vacías o evasivas (ej. "a", ".", "no").
**Resultado:** ❌ **Requiere corrección**.
Actualmente la condición estipula únicamente: `if not motivo or not str(motivo).strip():`. Solo protege frente a strings vacíos o compuestos exclusivamente por espacios.

### Corrección recomendada para el merge a `develop`:
Modificar la aserción dentro de `TeleconsultaService.rechazar_y_reasignar()`:

```python
# Reemplazar esto:
if not motivo or not str(motivo).strip():
    raise ReglaNegocioError("El motivo de rechazo no puede estar vacío.")

# Por esto:
motivo_limpio = str(motivo).strip() if motivo else ""
if len(motivo_limpio) < 10:
    raise ReglaNegocioError("Debe proveer un motivo de rechazo válido de al menos 10 caracteres.")
```
