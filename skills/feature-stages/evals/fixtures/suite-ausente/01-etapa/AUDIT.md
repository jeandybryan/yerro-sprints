# Auditoría

## Pasada 1

**Snapshot:** head=0000000000000000000000000000000000000000 tree=1111111111111111111111111111111111111111 dirty=no exclude=ninguno
**Riesgo auditado:** medio
**Trazabilidad:** CA-01 → T1 → test_focal.py → E-01

| Criterio | Afirmaciones auditadas | Tareas | Resultado | Evidencia reproducible | Limitaciones |
|----------|-------------------------|--------|-----------|-------------------------|--------------|
| CA-01 | salida y negativo | T1 | cumple | E-01 | ninguna |

### Ledger de evidencia

| ID | CA | Procedimiento/comando | Sensibilidad | Esperado | Observado/exit | Entorno y timestamp | Artefacto/log | Limitación |
|----|----|------------------------|--------------|----------|----------------|---------------------|---------------|------------|
| E-01 | CA-01 | pytest test_focal.py | revertir → rojo → restaurar; caso límite: entrada vacía → rechazo | verde | verde/0 | local; 2026-09-30 | log | ninguna |

**Veredicto:** coincide
**Veredicto (calidad):** aceptable
