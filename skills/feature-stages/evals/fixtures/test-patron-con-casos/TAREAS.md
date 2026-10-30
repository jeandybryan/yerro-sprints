# Tareas

**Principal:** sí

## Listado

- [ ] T1 — implementar salida (CA-01)
  **Archivos:** `src/salida.py`, `tests/salida.test.mjs`
  Interfaces:
    Consume: ninguna
    Produce: `export(items) -> str`
  Test-first: sí; Test: node --test --test-name-pattern "salida conserva el orden" tests/salida.test.mjs;
  Verificar: nivel `conductual`; ejecutar el caso de la salida; oráculo observable: exit 0 y el caso nombre el origen.

- [ ] T2 — documentar salida (CA-01)
  **Archivos:** `docs/salida.md`
  Interfaces:
    Consume: `export(items) -> str` (T1)
    Produce: `docs/salida.md` con el ejemplo de uso
  Test-first: sí; Test: node --test --test-name-pattern "salida" tests/salida.test.mjs;
  Verificar: nivel `estructural`; revisar el README; oráculo observable: el ejemplo usa la firma de T1.
