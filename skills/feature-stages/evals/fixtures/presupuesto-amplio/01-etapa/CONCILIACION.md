# Etapa 01 — presupuesto ampliado

**Estado:** cerrada
**Suites de referencia:** `pytest`
**Riesgo:** medio
**Presupuesto de deltas:** 3
**Motivo del presupuesto:** la etapa corrige dos defectos ya auditados en el mismo módulo; se acota a tres para no reabrir conciliación por el segundo.
**Presupuesto no funcional:**
- Latencia: no aplica (la etapa no expone una ruta con presupuesto de latencia)
- Memoria: no aplica (no hay proceso residente en la etapa)
- Tamaño/artefacto: no aplica (la etapa no entrega un artefacto con tamaño propio)
- Dependencias nuevas: 0
- Rendimiento de operación crítica: no aplica (no hay operación crítica en la etapa)

## Criterios de aceptación

- **CA-01 — [condición de salida]:** estímulo → resultado; límite; evidencia `conductual`.

## Preguntas abiertas

- `Ninguna`
