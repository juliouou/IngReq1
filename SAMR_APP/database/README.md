# database/

## Qué hay aquí
- `fixtures/` — datos semilla (copiados desde `backend/fixtures`, tal como estaban).

## Por qué las migraciones NO están aquí

Puede parecer raro que las migraciones de Django (`0001_initial.py`, etc.) sigan
viviendo dentro de `backend/apps/<app>/migrations/` y no en esta carpeta
`database/`. Es una restricción técnica real, no un descuido:

Django espera que cada app tenga su propia carpeta `migrations/` **al lado**
de sus `models.py`, salvo que se reconfigure explícitamente con el setting
`MIGRATION_MODULES` en `config/settings/base.py`. Mover las migraciones aquí
sin hacer ese cambio de configuración rompería `python manage.py migrate`.

**Si en algún momento quieres moverlas de verdad:**
```python
# config/settings/base.py
MIGRATION_MODULES = {
    "usuarios": "database.migrations.usuarios",
    "triaje": "database.migrations.triaje",
    # ... una entrada por cada app
}
```
Es totalmente posible, pero es un cambio aparte que vale la pena hacer con
cuidado (y probarlo) — no lo apliqué de una vez para no arriesgar que
`migrate` deje de funcionar sin que lo hayas visto correr primero.

## Esquema actual (resumen)

| App | Modelos principales |
|---|---|
| `usuarios` | `Usuario` (con roles: admin, médico, paciente) |
| `triaje` | `SolicitudAtencion`, `EvaluacionTriaje` |
| `biometria` | Lecturas de dispositivos IoT (hypertable de TimescaleDB) |
| `teleconsulta` | `Teleconsulta`, `Receta`, `HistorialClinico` |
| `auditoria` | `RegistroAuditoria` (con cadena de hash SHA-256) |
| `portal` | Autenticación / registro con MFA |
