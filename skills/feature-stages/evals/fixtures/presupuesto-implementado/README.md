# Fixture — delta implementado sin reauditar

Etapa de riesgo `medio` (presupuesto derivado 1) con un delta ya `implementada`
tras una pasada `no coincide`, pero sin la pasada que lo reaudita. El delta no
gastó el presupuesto todavía: el siguiente paso es `audit-stage`, no detenerse.
El control es `presupuesto-agotado`, donde una pasada posterior reaudita el
delta y la auditoría sigue sin coincidir.

## Estado del corte

| # | Carpeta | Resultado | Depende de | Conciliación | Estado | Trabajo activo | Tareas | Auditoría |
|---|---------|-----------|------------|--------------|--------|----------------|--------|-----------|
| 01 | [01-etapa](01-etapa/CONCILIACION.md) | resultado | — | cerrada | auditando | TAREAS-delta-01.md | TAREAS.md | AUDIT.md |
