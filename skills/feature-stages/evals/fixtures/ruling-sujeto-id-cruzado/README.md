# Fixture — resolución de otro identificador

`T1` marca `R1`; `AUDIT.md` trae una resolución `- aceptado R2`. Hay una
resolución, pero no la del sujeto marcado.

Debe **fallar** (B-26): el cruce es por conjunto de IDs. Contar resoluciones
dejaría pasar este caso, que es el más probable cuando dos marcas se escriben
seguidas.
