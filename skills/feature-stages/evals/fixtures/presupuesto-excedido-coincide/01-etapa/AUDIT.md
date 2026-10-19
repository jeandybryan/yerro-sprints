# Auditoría — etapa 01

## Pasada 1

| Criterio | Afirmaciones auditadas | Tareas | Resultado | Evidencia reproducible | Limitaciones |
|----------|-------------------------|--------|-----------|-------------------------|--------------|
| CA-01 | negativo | T1 | no cumple | E-01 | el delta 02 no cerró el hueco |

### Ledger de evidencia

| ID | CA | Procedimiento/comando | Esperado | Observado/exit | Entorno y timestamp | Artefacto/log | Limitación |
|----|----|------------------------|----------|----------------|---------------------|---------------|------------|
| E-01 | CA-01 | pytest | rojo | verde/0 | local; 2026-10-19 | log | sigue faltando el caso inverso |

**Veredicto:** no coincide

## Pasada 2

**Snapshot:** head=0000000000000000000000000000000000000000 tree=4444444444444444444444444444444444444444 dirty=no exclude=ninguno
**Riesgo auditado:** medio

| Criterio | Afirmaciones auditadas | Tareas | Resultado | Evidencia reproducible | Limitaciones |
|----------|-------------------------|--------|-----------|-------------------------|--------------|
| CA-01 | salida, negativo y límite | T1 | cumple | E-02 | ninguna |

### Ledger de evidencia

| ID | CA | Procedimiento/comando | Esperado | Observado/exit | Entorno y timestamp | Artefacto/log | Limitación |
|----|----|------------------------|----------|----------------|---------------------|---------------|------------|
| E-02 | CA-01 | pytest | verde | verde/0 | local; 2026-10-19 | log | ninguna |

**Veredicto:** coincide
