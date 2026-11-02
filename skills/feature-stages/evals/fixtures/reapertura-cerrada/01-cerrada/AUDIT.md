## Pasada 1 — 2026-10-30

**Snapshot:** head=aaaa111 tree=bbbb222 dirty=no exclude=features/01-reabierta
**Riesgo auditado:** medio
**Trazabilidad:** S-01 → CA-01 → T1 → pytest → E-01

### Resultado por criterio

| CA | Afirmación | Tareas | Resultado | Evidencia | Limitación |
|----|------------|--------|-----------|-----------|------------|
| CA-01 | salida y negativo | T1 | cumple | E-01 | ninguna |

### Ledger de evidencia

| ID | CA | Procedimiento/comando | Esperado | Observado/exit | Entorno y timestamp | Artefacto/log | Limitación |
|----|----|-----------------------|----------|----------------|---------------------|---------------|------------|
| E-01 | CA-01 | pytest | verde | verde/0 | local; 2026-10-30 | log | cubre solo el camino feliz |

**Veredicto:** coincide
**Veredicto (calidad):** aceptable

## Pasada 2 — 2026-11-02

**Reapertura:** otra etapa sustituyó el prompt de esta etapa después del árbol
que auditó la pasada 1; la conformidad de la pasada 1 no cubre el árbol actual,
así que se reabre la conciliación para declarar el alcance nuevo (S-02). No es
un fallo de implementación y no se abre delta.
**Trazabilidad:** S-02 → CA-01 → T1 → pytest → E-01

**Veredicto:** no coincide
