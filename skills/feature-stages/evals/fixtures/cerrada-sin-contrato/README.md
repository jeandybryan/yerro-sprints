# Fixture — cerrada sin contrato

Árbol de feature con una etapa que se declara cerrada y cuya auditoría dice
`coincide`, pero a la que le falta `**Snapshot:**` en la pasada. El router no
mira ese campo: por eso la etapa aparece como terminada mientras el contrato de
artefactos la rechaza. Existe para pinchar esa diferencia con un caso.

## Estado del corte

| # | Carpeta | Resultado | Depende de | Conciliación | Estado | Trabajo activo | Tareas | Auditoría |
|---|---------|-----------|------------|--------------|--------|----------------|--------|-----------|
| 01 | [01-cerrada](01-cerrada/CONCILIACION.md) | cerrada | — | cerrada | cerrada | — | TAREAS.md | AUDIT.md |
