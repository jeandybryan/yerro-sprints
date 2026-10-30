# Fixture — estado de tareas que el contrato no conoce

`TAREAS.md` declara `**Estado:** completada` con `T4` sin marcar. Un valor
fuera del vocabulario cerrado no se interpreta como "quizá pendiente": el
router no sabe leerlo, cae en el `else` final y antes lo rutaba a `audit-stage`
con trabajo por hacer, con `exit 0`, y nada lo advertía.

Debe **bloquear** con `TAREAS_ESTADO_DESCONOCIDO` y decir cuáles son los
valores válidos. El bloqueo es `in band`: nombra el archivo y el valor.

## Estado del corte

| # | Carpeta | Resultado | Depende de | Conciliación | Estado | Trabajo activo | Tareas | Auditoría |
|---|---------|-----------|------------|--------------|--------|----------------|--------|-----------|
| 01 | [01-etapa](01-etapa/CONCILIACION.md) | implementar | — | cerrada | implementando | — | TAREAS.md | — |
