# Tareas

**Principal:** sí

## Listado

- [ ] T1 — implementar el parseo (CA-02)
  **Archivos:** `src/parseo.py`, `tests/test_parseo.py`
  Test-first: sí; Test: pytest -q test_parser.py;
  Verificar: nivel `conductual`; ejecutar test focalizado; oráculo observable: exit 0 y assertion verde.
  Ruling: separador `;` — el CA menciona locales europeos — coste: una línea en el parser y su test.
  Ruling: codificar UTF-8 — el fixture de entrada lo ya declara — coste: una constante y un test.
  Ruling: ordenar claves al exportar — el test compara el texto completo — coste: una línea de sorted.
