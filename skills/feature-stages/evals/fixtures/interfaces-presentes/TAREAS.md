# Tareas

**Principal:** sí

## Listado

- [ ] T1 — implementar salida (CA-01)
  Interfaces:
    Consume: ninguna
    Produce: `export(items) -> str`
  Test-first: sí; Test: pytest -q test_focal.py;
  Verificar: nivel `conductual`; ejecutar test focalizado; oráculo observable: exit 0 y assertion verde.

- [ ] T2 — documentar salida (CA-01)
  Interfaces:
    Consume: `export(items) -> str` de T1
    Produce: ejemplo de uso en el README
  Test-first: sí; Test: pytest -q test_focal.py;
  Verificar: nivel `estructural`; revisar el README; oráculo observable: el ejemplo usa la firma de T1.
