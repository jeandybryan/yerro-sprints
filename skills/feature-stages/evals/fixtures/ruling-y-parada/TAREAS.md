# Tareas — etapa 03 exportar solicitudes cerradas

**Principal:** sí

## Listado

- [ ] T1 — exportar las solicitudes cerradas (CA-01; Origen: S-01)
  **Archivos:** `src/export.py`, `tests/test_export.py`
  Interfaces:
    Consume: ninguna
    Produce: `export(rows) -> str`
  Test-first: sí; Test: pytest -q tests/test_export.py;
  Sensibilidad: revertir → rojo → restaurar;
  Verificar: nivel `conductual`; ejecutar el test de export; oráculo
  observable: con dos filas el archivo trae dos; sin filas, solo la cabecera.

## Trazabilidad

| Criterio | Tareas | Verificación prevista |
|----------|--------|-----------------------|
| CA-01 | T1 | tests/test_export.py |
