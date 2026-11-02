# Fixture — reapertura de la conciliación desde la auditoría

Una pasada registra `coincide` sobre un árbol y, más tarde, un cambio de
alcance llega **después** de ese árbol: otra etapa sustituyó el contrato del
prompt que esta etapa declaraba. La etapa reabre su conciliación para declarar
el alcance nuevo, y la reapertura se registra en una pasada nueva que declara
`**Reapertura:** <motivo>` y `**Veredicto:** no coincide`, porque la conformidad
que registró la pasada 1 pertenecía a otro árbol.

Transición esperada: `trabajando` → `conciliate-stage`, sin bloqueo y **sin**
abrir delta. La reapertura no es un fallo de implementación: escribir un delta
sería corregir contra un criterio que ya se movió, y el presupuesto de deltas
del corte (0 escritos) no se consume.

## Casos negativos que esta positiva no puede tapar

- `presupuesto-excedido-reabierto`: mismo `AUDIT.md` sin `**Reapertura:**`; con
  el presupuesto agotado, sigue bloqueando `PRESUPUESTO_DE_DELTAS_AGOTADO`. Una
  pasada con veredicto `no coincide` no absuelve el presupuesto por sí sola.
- `reapertura-cerrada`: la pasada reabre y el índice sigue en `cerrada`;
  `doctor.py` lo rechaza en vez de leer la pasada 1 y dar el cierre por bueno.

## Estado del corte

| # | Carpeta | Resultado | Depende de | Conciliación | Estado | Trabajo activo | Tareas | Auditoría |
|---|---------|-----------|------------|--------------|--------|----------------|--------|-----------|
| 01 | [01-reabierta](01-reabierta/CONCILIACION.md) | re-conciliar el alcance | — | abierta | conciliando | — | TAREAS.md | AUDIT.md |
