# Decisiones, trazabilidad y test-first

La cadena normativa es:

```text
S-NN → CA-NN → T-NN → implementación → test → E-NN
```

- Cada decisión acordada tiene un ID estable `S-NN`, cita textual cuando sea
  relevante, fecha, motivo y consecuencias. No se recicla un ID.
- Cada `CA-NN` incluye `Origen: S-NN`.
- Cada tarea incluye `Test-first: sí`, `Test: <comando reproducible>` y
  `Sensibilidad: <cómo se vio fallar>` antes de marcarla como implementada.
- `AUDIT.md` conserva `**Trazabilidad:**` y enlaza cada CA con sus tareas,
  tests y evidencias `E-NN`.
- Si el test-first no puede ejecutarse, el resultado es `no verificado`; no se
  infiere `cumple`.

## Sensibilidad

`Test: <comando>` demuestra que algo pasa. `Sensibilidad:` demuestra que el test
pudo fallar, y es la parte que hace que `cumple` signifique algo:

```text
revertir → rojo → restaurar | mutante: <qué> → rojo | regresión HEAD
```

El validador rechaza un `Test:` decorativo (`true`, `echo`, `sleep`, `:`) y
exige la columna `Sensibilidad` en el ledger de una pasada `coincide`. Si la
sensibilidad no se pudo demostrar, el criterio es `no verificado`. Detalle en
[evidence.md](evidence.md).
