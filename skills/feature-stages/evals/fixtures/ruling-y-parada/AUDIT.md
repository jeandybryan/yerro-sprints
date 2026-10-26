# Auditoría

## Pasada 1

**Snapshot:** head=0000000000000000000000000000000000000000 tree=1111111111111111111111111111111111111111 dirty=no exclude=ninguno
**Riesgo auditado:** medio
**Trazabilidad:** CA-01 → T1 → test_export.py → E-01

| Criterio | Afirmaciones auditadas | Tareas | Resultado | Evidencia reproducible | Limitaciones |
|----------|-------------------------|--------|-----------|-------------------------|--------------|
| CA-01 | salida y negativo | T1 | cumple | E-01 | ninguna |

### Ledger de evidencia

| ID | CA | Procedimiento/comando | Sensibilidad | Esperado | Observado/exit | Entorno y timestamp | Artefacto/log | Limitación |
|----|----|------------------------|--------------|----------|----------------|---------------------|---------------|------------|
| E-01 | CA-01 | pytest tests/test_export.py | revertir → rojo → restaurar; caso límite: sin solicitudes, solo cabecera | verde | verde/0 | local; 2026-09-30 | log | ninguna |

### Rulings revisados

El nombre de la columna con el total existía solo como ambigüedad: en esta
pasada nadie lo marcó, porque la categoría 3 lo dejó fuera del alcance. Es el
estado inicial del caso conductual, antes de que el agente trabaje sobre él.

**Veredicto:** coincide
