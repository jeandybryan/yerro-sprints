# Scoring y evidencia

Resultados permitidos:

- `cumple`: todas las afirmaciones y verificaciones tienen evidencia suficiente;
- `parcial`: solo se demuestra una parte o un sustituto más débil;
- `no cumple`: la evidencia contradice o falta el comportamiento;
- `no verificado`: no se obtuvo evidencia suficiente.

Cualquier `parcial`, `no cumple` o `no verificado` implica `no coincide`.

El ledger `E-NN` conserva procedimiento/comando exacto, esperado, observado,
exit, entorno/timestamp, artefacto/log y limitación. Una ruta, lectura de
código, checkbox o suite amplia no demuestra comportamiento por sí sola.

Fuerza de evidencia, de mayor a menor:

1. demostración o medición en el entorno previsto;
2. prueba de integración o de proceso;
3. prueba automatizada focalizada;
4. inspección estática para afirmaciones estructurales.

Las desviaciones se clasifican como `informativa`, `requiere revisión` o
`bloqueante`. Una desviación bloqueante impide `coincide`.
