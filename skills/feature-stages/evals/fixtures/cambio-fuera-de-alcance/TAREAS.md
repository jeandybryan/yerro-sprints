# Tareas — etapa 01

**Principal:** sí

## Listado

- [ ] T1 — implementar salida (CA-01)
  **Archivos:** `src/export.csv`, `tests/test_export_csv.py`
  Test-first: sí; Test: pytest -q tests/test_export_csv.py;
  Sensibilidad: revertir → rojo → restaurar; caso límite: entrada vacía → rechazo;
  Verificar: nivel `conductual`; ejecutar test focalizado; oráculo observable: exit 0 y assertion verde.
