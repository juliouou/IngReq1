# SAMR — Guía de implementación

## Cómo correr el proyecto

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
python run.py
```

Abre `http://localhost:5000/registro` para probar el flujo de M1
(registro + MFA) de punta a punta. También hay `/health` y
`/api/m5/logs` para ver la auditoría en vivo.

## Estado actual por módulo

| Módulo | Estado | RF |
|---|---|---|
| M1 - Registro/MFA | **Funcional** (FormularioRegistro + Sesion completos) | RF-01, RF-02, RF-03 |
| M2 - Triaje | Esqueleto con TODOs | RF-04 a RF-08 |
| M3 - Monitoreo | Esqueleto con TODOs | RF-09 a RF-12 |
| M4 - Teleconsulta | Esqueleto con TODOs | RF-13 a RF-16 |
| M5 - Auditoría | **Funcional** (lectura de logs) | RF-17 a RF-20 |

Los nombres de clases y métodos en `app/modules/*/services.py` siguen
**exactamente** los nombres usados en los diagramas de secuencia
corregidos (`new/SAMR_Diagramas_Secuencia_v2/`). Si cambian el diagrama,
cambien el código, y viceversa — así no se pierde la trazabilidad.

## Flujo de ramas por rol

```
main                     ← versión estable, solo se llega vía Pull Request
└── develop              ← integración de todos los módulos (esta rama)
    ├── feature/database      → Julio: modelos, esquemas (app/models/)
    ├── feature/backend       → Antonella: lógica de negocio (app/modules/*/services.py)
    ├── feature/frontend      → Paula: pantallas (app/templates/, app/static/)
    ├── feature/ux-ui         → David: estilos, wireframes, experiencia
    ├── feature/security      → Alisson: auth, cifrado, validaciones
    └── feature/architecture  → Lady: estructura general, diagramas técnicos
```

**Flujo de trabajo día a día:**

```bash
git checkout develop
git pull
git checkout -b feature/tu-rol      # solo la primera vez
# ... trabajas, haces commits normales ...
git push -u origin feature/tu-rol
```

Cuando algo esté listo: abrir un **Pull Request** de `feature/tu-rol` →
`develop` en GitHub, para que alguien más del equipo lo revise antes de
mezclarlo. `develop` se mezcla a `main` solo cuando un módulo completo
esté probado.

**Regla simple para no chocar entre ramas:** cada rol edita
principalmente su carpeta (`app/models/` es de Julio, `app/modules/*/services.py`
es de Antonella, etc.). Si necesitas tocar el archivo de otra persona,
avisa en el grupo antes de hacer el PR.
