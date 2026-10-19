# Decisiones, trazabilidad y test-first

La cadena normativa es:

```text
S-NN → CA-NN → T-NN → implementación → test → E-NN
```

- Cada decisión acordada tiene un ID estable `S-NN`, cita textual cuando sea
  relevante, fecha, motivo y consecuencias. No se recicla un ID.
- Cada `CA-NN` incluye `Origen: S-NN`.
- Cada tarea incluye `Test-first: sí` y `Test: <comando reproducible>` antes de
  marcarla como implementada.
- `AUDIT.md` conserva `**Trazabilidad:**` y enlaza cada CA con sus tareas,
  tests y evidencias `E-NN`.
- Si el test-first no puede ejecutarse, el resultado es `no verificado`; no se
  infiere `cumple`.
