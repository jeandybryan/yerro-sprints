# Auditoría

## Pasada 1

**Snapshot:** head=0000000000000000000000000000000000000000 tree=3333333333333333333333333333333333333333 dirty=no exclude=ninguno
**Riesgo auditado:** bajo

| Criterio | Afirmaciones auditadas | Tareas | Resultado | Evidencia reproducible | Limitaciones |
|----------|-------------------------|--------|-----------|-------------------------|--------------|
| CA-01 | salida y negativo | T1 | cumple | E-01 | ninguna |

### Ledger de evidencia

| ID | CA | Procedimiento/comando | Esperado | Observado/exit | Entorno y timestamp | Artefacto/log | Limitación |
|----|----|------------------------|----------|----------------|---------------------|---------------|------------|
| E-01 | CA-01 | pytest | verde | verde/0 | local; 2026-10-19 | log | ninguna |

**Veredicto:** coincide
