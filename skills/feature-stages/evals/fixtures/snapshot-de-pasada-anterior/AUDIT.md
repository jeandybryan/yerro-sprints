# Auditoría

## Pasada 1

**Snapshot:** head=0000000000000000000000000000000000000000 tree=5555555555555555555555555555555555555555 dirty=no exclude=ninguno
**Riesgo auditado:** medio

| Criterio | Afirmaciones auditadas | Tareas | Resultado | Evidencia reproducible | Limitaciones |
|----------|-------------------------|--------|-----------|-------------------------|--------------|
| CA-01 | negativo | T1 | no cumple | E-01 | falta el caso inverso |

### Ledger de evidencia

| ID | CA | Procedimiento/comando | Esperado | Observado/exit | Entorno y timestamp | Artefacto/log | Limitación |
|----|----|------------------------|----------|----------------|---------------------|---------------|------------|
| E-01 | CA-01 | pytest | rojo | verde/0 | local; 2026-10-19 | log | falta el caso inverso |

**Veredicto:** no coincide

## Pasada 2

**Riesgo auditado:** medio

| Criterio | Afirmaciones auditadas | Tareas | Resultado | Evidencia reproducible | Limitaciones |
|----------|-------------------------|--------|-----------|-------------------------|--------------|
| CA-01 | salida y negativo | T1 | cumple | E-02 | ninguna |

### Ledger de evidencia

| ID | CA | Procedimiento/comando | Esperado | Observado/exit | Entorno y timestamp | Artefacto/log | Limitación |
|----|----|------------------------|----------|----------------|---------------------|---------------|------------|
| E-02 | CA-01 | pytest | verde | verde/0 | local; 2026-10-19 | log | ninguna |

**Veredicto:** coincide
**Veredicto (calidad):** aceptable
