# Etapa 01 — plantilla copiada

**Estado:** cerrada
**Riesgo:** medio
**Suites de referencia:** `pytest -q`, `npm run lint`
**Runners:** pytest | npm run lint (lint contra el árbol de trabajo)
**Presupuesto de deltas:** 1
**Presupuesto no funcional:**
- Latencia: no aplica (la etapa no expone una ruta con presupuesto de latencia)
- Memoria: no aplica (no hay proceso residente en la etapa)
- Tamaño/artefacto: no aplica (la etapa no entrega un artefacto con tamaño propio)
- Dependencias nuevas: 0
- Rendimiento de operación crítica: no aplica (no hay operación crítica en la etapa)
**Spec:** [SPEC.md](../SPEC.md) §1

## Resultado observable

La etapa entrega la salida que el criterio describe.

## Dependencias

- `Ninguna`

## Entra

- La salida focalizada.

## No entra

- Nada más.

## Aclaraciones

- **Baseline:** 2026-11-16.
- **S-01 — Decisión:** se acepta el resultado observable del criterio.
  - Cita: «…»
  - Motivo: …
  - Consecuencias: …
  - Fecha: 2026-11-16

## Criterios de aceptación

- **CA-01 — [condición de salida]:** precondición/estímulo → resultado observable; fallo, límite o promesa negativa relevante; evidencia `conductual`. `Origen: S-01`.

## Riesgos y compatibilidad

- `Ninguno identificado`

## Bloqueos

- `Ninguno`

## Preguntas abiertas

- `Ninguna`
