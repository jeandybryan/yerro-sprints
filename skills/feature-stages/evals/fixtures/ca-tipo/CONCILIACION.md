# Etapa 03 — tipo de criterio declarado

**Estado:** abierta
**Presupuesto no funcional:**
- Latencia: no aplica (la etapa no expone una ruta con presupuesto de latencia)
- Memoria: no aplica (no hay proceso residente en la etapa)
- Tamaño/artefacto: no aplica (la etapa no entrega un artefacto con tamaño propio)
- Dependencias nuevas: 0
- Rendimiento de operación crítica: no aplica (no hay operación crítica en la etapa)

## Criterios de aceptación

- **CA-01 — [condición de salida]:** estímulo → resultado observable; no falla; evidencia `conductual`.
- **CA-02 — [invariante acumulado]:** el total se conserva; evidencia `estructural`.
- **CA-03:** estímulo → resultado observable; evidencia `estructural`. **Salida de etapa.**
- **CA-04:** el total se conserva; evidencia `ambiental`. **Invariante acumulada.**
- **CA-05:** el camino de salida deja el invariante del contador intacto; evidencia `conductual`.
- **CA-06 — [invariante acumulado | condición de salida]:** estímulo → resultado observable; evidencia `sistema`.
