**Snapshot:** fixture tree
# Auditoría — etapa 07

## Pasada 1

| Criterio | Afirmaciones auditadas | Tareas | Resultado | Evidencia reproducible | Limitaciones |
|----------|-------------------------|--------|-----------|-------------------------|--------------|
| CA-01 | negativo | T1 | no cumple | E-01 | no se intentó el caso inverso |

### Ledger de evidencia

| ID | CA | Procedimiento/comando | Esperado | Observado/exit | Entorno y timestamp | Artefacto/log | Limitación |
|----|----|------------------------|----------|----------------|---------------------|---------------|------------|
| E-01 | CA-01 | pytest | rojo | verde/0 | local; 2026-10-19 | log | falta el caso negativo |

**Veredicto:** no coincide


**Trazabilidad:** S-01 → CA-01 → T1 → pytest → E-01
