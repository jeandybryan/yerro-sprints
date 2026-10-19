# Auditoría — etapa 05

## Pasada 1

| Criterio | Afirmaciones auditadas | Tareas | Resultado | Evidencia reproducible | Limitaciones |
|----------|-------------------------|--------|-----------|-------------------------|--------------|
| CA-01 | salida | T1 | parcial | E-01 | falta el caso negativo |

### Ledger de evidencia

| ID | CA | Procedimiento/comando | Esperado | Observado/exit | Entorno y timestamp | Artefacto/log | Limitación |
|----|----|------------------------|----------|----------------|---------------------|---------------|------------|
| E-01 | CA-01 | pytest | verde | verde/0 | local; 2026-10-19 | log | cubre solo el camino feliz |

**Veredicto:** no coincide
