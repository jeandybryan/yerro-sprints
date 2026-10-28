# Fixture — fila exprés sin la prueba ni la confirmación

El árbol es coherente: `EXPRES.md` es registral y la etapa `01-etapa` está `lista`.
Lo que falta es lo único que convierte el registro en prueba de que se probó: la
fila no declara ni el comando, ni el resultado, ni quién confirmó que no hay CA
nuevo ni cambio de interfaz pública.

Debe fallar: una fila sin `Comando`, `Resultado` y `Confirmado por` escritos no
es un registro, es una intención.

## Estado del corte

| # | Carpeta | Resultado | Depende de | Conciliación | Estado | Trabajo activo | Tareas | Auditoría |
|---|---------|-----------|------------|--------------|--------|----------------|--------|-----------|
| 01 | [01-etapa](01-etapa/CONCILIACION.md) | resultado | — | cerrada | lista | — | TAREAS.md | — |
