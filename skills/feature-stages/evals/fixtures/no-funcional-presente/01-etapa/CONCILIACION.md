# Etapa 01 — suite con evidencia

**Estado:** cerrada
**Presupuesto no funcional:**
- Latencia: p95 ≤ 200 ms en la ruta de salida
- Memoria: ≤ 64 MB por proceso
- Tamaño/artefacto: no aplica (la etapa no entrega artefacto; solo código)
- Dependencias nuevas: 0
- Rendimiento de operación crítica: no aplica (sin operación crítica)

## Aclaraciones

- **S-01 — Decisión de baseline:** se acepta el resultado observable del criterio y su verificación focalizada.
**Riesgo:** medio
**Suites de referencia:** `pytest test_focal.py`

## Criterios de aceptación

- **CA-01 — [condición de salida | invariante acumulado]:** estímulo → resultado observable; no falla; evidencia `conductual`. Origen: S-01
