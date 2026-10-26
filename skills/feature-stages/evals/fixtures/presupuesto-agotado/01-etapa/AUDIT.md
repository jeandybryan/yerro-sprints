# Auditoría — etapa 01

## Pasada 1

| Criterio | Afirmaciones auditadas | Tareas | Resultado | Evidencia reproducible | Limitaciones |
|----------|-------------------------|--------|-----------|-------------------------|--------------|
| CA-01 | negativo | T1 | no cumple | E-01 | el delta 01 no cerró el hueco |

### Ledger de evidencia

| ID | CA | Procedimiento/comando | Esperado | Observado/exit | Entorno y timestamp | Artefacto/log | Limitación |
|----|----|------------------------|----------|----------------|---------------------|---------------|------------|
| E-01 | CA-01 | pytest | rojo | verde/0 | local; 2026-10-19 | log | sigue faltando el caso inverso |

**Veredicto:** no coincide
