# Fixture — diff fuera del alcance declarado

`T1` declara `src/export.csv` y `tests/test_export_csv.py`. El repo de prueba
toca además `src/utilidades.py`, que ninguna tarea menciona: es un refactor
"de paso", y B-27 lo trata como **alcance nuevo** aunque sea reversible.

Debe **fallar** `diff_scope.py` con exit 1 y nombrar la ruta no declarada.

No lleva `AUDIT.md`: prueba el cruce diff ↔ `**Archivos:**`, no el cierre. El
repo que la ejercita lo construye `test_diff_scope.py`, porque el resultado
depende del diff real de git y no se puede escribir en un archivo estático.
