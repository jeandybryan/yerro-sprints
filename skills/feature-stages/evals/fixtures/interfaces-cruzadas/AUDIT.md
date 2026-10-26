# Auditoría

## Pasada 1

**Snapshot:** head=0000000000000000000000000000000000000000 tree=1111111111111111111111111111111111111111 dirty=no exclude=ninguno
**Riesgo auditado:** medio
**Trazabilidad:** CA-01 → T1, T2 → test_export.py → E-01

| Criterio | Afirmaciones auditadas | Tareas | Resultado | Evidencia reproducible | Limitaciones |
|----------|-------------------------|--------|-----------|-------------------------|--------------|
| CA-01 | salida y negativo | T1, T2 | cumple | E-01 | el ejemplo de `docs/export.md` declara `export(rows) -> str`, que no es la firma de `T1` |

### Ledger de evidencia

| ID | CA | Procedimiento/comando | Sensibilidad | Esperado | Observado/exit | Entorno y timestamp | Artefacto/log | Limitación |
|----|----|------------------------|--------------|----------|----------------|---------------------|---------------|------------|
| E-01 | CA-01 | pytest tests/test_export.py | revertir → rojo → restaurar; caso límite: sin argumentos se usa `,` | verde | verde/0 | local; 2026-09-30 | log | la documentación no se ejecutó |

**Veredicto:** coincide
