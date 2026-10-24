# Tareas

**Principal:** sí

## Listado

- [ ] T1 — implementar salida (CA-01)
  **Archivos:** `src/salida.py`, `tests/test_salida.py`
  **Sujeto a revisión R1:** límite por defecto 50 en `/items` y no 100 — coincide con
  el resto de listados del proyecto — coste: cambiar una constante y un test.
  Test-first: sí; Test: pytest -q test_focal.py;
  Verificar: nivel `conductual`; ejecutar test focalizado; oráculo observable: exit 0 y assertion verde.
