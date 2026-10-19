# Fixture — salud estructural

Cada etapa viola una regla distinta de `doctor.py`; el informe debe nombrarla.

- `01-sin-tareas`: etapa `lista` sin `TAREAS.md`.
- `02-sin-audit`: etapa `auditando` sin `AUDIT.md`.
- `03-sin-conciliacion`: carpeta de etapa sin `CONCILIACION.md`.
- `04-delta-malo`: delta con nombre fuera de `NN` y delta sin `Cierra:`.

## Estado del corte

| # | Carpeta | Resultado | Depende de | Conciliación | Estado | Trabajo activo | Tareas | Auditoría |
|---|---------|-----------|------------|--------------|--------|----------------|--------|-----------|
| 01 | [01-sin-tareas](01-sin-tareas/CONCILIACION.md) | implementar | — | cerrada | lista | — | — | — |
| 02 | [02-sin-audit](02-sin-audit/CONCILIACION.md) | auditar | — | cerrada | auditando | — | TAREAS.md | — |
| 03 | [03-sin-conciliacion](03-sin-conciliacion/CONCILIACION.md) | conciliar | — | borrador-corte | borrador | — | — | — |
| 04 | [04-delta-malo](04-delta-malo/CONCILIACION.md) | cerrar delta | — | cerrada | lista | TAREAS-delta-02.md | TAREAS.md | AUDIT.md |
