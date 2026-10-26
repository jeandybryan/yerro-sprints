# Tareas — etapa 04 exportar con separador configurable

**Principal:** sí

## Listado

- [ ] T1 — exportar con separador (CA-01; Origen: S-01)
  **Archivos:** `src/export.py`, `tests/test_export.py`
  Interfaces:
    Consume: ninguna
    Produce: `export(rows, sep=",") -> str`
  Test-first: sí; Test: pytest -q tests/test_export.py;
  Sensibilidad: revertir → rojo → restaurar;
  Verificar: nivel `conductual`; ejecutar el test de export; oráculo
  observable: con `sep=";"` el archivo separa por punto y coma; sin argumento,
  por coma.

- [ ] T2 — documentar el export (CA-01; Origen: S-01)
  **Archivos:** `docs/export.md`
  Interfaces:
    Consume: `export(rows) -> str` de T1
    Produce: ejemplo de uso en `docs/export.md`
  Test-first: sí; Test: pytest -q tests/test_export.py;
  Sensibilidad: revertir → rojo → restaurar;
  Verificar: nivel `estructural`; revisar el ejemplo; oráculo observable: el
  ejemplo se puede copiar y ejecutar tal cual.

## Trazabilidad

| Criterio | Tareas | Verificación prevista |
|----------|--------|-----------------------|
| CA-01 | T1, T2 | tests/test_export.py, docs/export.md |
