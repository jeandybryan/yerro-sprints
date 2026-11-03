# Fixture — reapertura ya resuelta

La pasada 2 reabrió el alcance y la pasada 3 cierra sobre el árbol resultante.
La pasada 3 menciona la reapertura que resolvió, pero su veredicto es
`coincide`: la marca solo reabre cuando la pasada **no** cierra. Si el router
lee `**Reapertura:**` sin mirar el veredicto, deja la etapa en
`conciliate-stage` con la última pasada en `coincide` y el índice en `cerrada`,
y `doctor.py` la rechaza.

Transición esperada: `declarada-cerrada`, sin bloqueo.

## Estado del corte

| # | Carpeta | Resultado | Depende de | Conciliación | Estado | Trabajo activo | Tareas | Auditoría |
|---|---------|-----------|------------|--------------|--------|----------------|--------|-----------|
| 01 | [01-resuelta](01-resuelta/CONCILIACION.md) | cerrada | — | cerrada | cerrada | — | TAREAS.md | AUDIT.md |
