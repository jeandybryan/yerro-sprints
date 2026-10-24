# Fixture — sujeto a revisión sin identificador

`T1` marca un cambio observable con `**Sujeto a revisión:**`, sin `R1`, y el
`AUDIT.md` lo resuelve. El contenido está bien; falta el identificador.

Debe **fallar** (B-26): sin ID, la marca y su resolución no se pueden cruzar, y
el validador solo podría contar líneas — que es exactamente el agujero que dos
`- aceptado` tapaban.
