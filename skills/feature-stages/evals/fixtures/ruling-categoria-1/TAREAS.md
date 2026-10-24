# Tareas

**Principal:** sí

## Listado

- [ ] T1 — implementar salida (CA-01)
  **Archivos:** `src/salida.py`, `tests/test_salida.py`
  Ruling: separador `;` en el CSV — el CA menciona locales europeos — coste: una
  línea en el exportador y el test de formato.
  Test-first: sí; Test: pytest -q test_focal.py;
  Verificar: nivel `conductual`; ejecutar test focalizado; oráculo observable: exit 0 y assertion verde.
