# Etapa 01 — suite con evidencia

**Estado:** cerrada
**Presupuesto no funcional:**
- Latencia: no aplica (la etapa no expone una ruta con presupuesto de latencia)
- Memoria: no aplica (no hay proceso residente en la etapa)
- Tamaño/artefacto: no aplica (la etapa no entrega un artefacto con tamaño propio)
- Dependencias nuevas: 0
- Rendimiento de operación crítica: no aplica (no hay operación crítica en la etapa)

## Aclaraciones

- **S-01 — Decisión de baseline:** se acepta el resultado observable del criterio y su verificación focalizada.
**Riesgo:** medio
**Suites de referencia:** `pytest test_focal.py`

## Criterios de aceptación

- **CA-01 — [condición de salida | invariante acumulado]:** estímulo → resultado observable; no falla; evidencia `conductual`. Origen: S-01
