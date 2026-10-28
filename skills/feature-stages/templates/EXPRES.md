## `EXPRES.md` (registro de cambios que no abren etapa)

Optional to create, mandatory to complete once it exists: `next_step.py`
never reads it and it never changes a transition, but `doctor.py` treats an
incomplete row as an error (P8). A row without its command, its result and
its human confirmation records an intention, not a verification.

```markdown
# Registro de cambios exprés

Cambios que no abren etapa. Una línea por cambio, en orden cronológico.
Si un cambio deja de cumplir la frontera, se promueve a etapa y esta línea
se marca `→ NN-slug`.

| # | Fecha | Cambio | Archivos | CA | Frontera | Comando | Resultado | Confirmado por |
|---|-------|--------|----------|----|----------|---------|-----------|----------------|
| E-01 | AAAA-MM-DD | … | `ruta.py` | — | 1 archivo, 8 líneas | `pytest tests/test_ruta.py` | exit 0 · el mensaje conserva el formato | Ana Ruiz · AAAA-MM-DD |
```

La columna **Frontera** es la que evita la regresión: obliga a escribir *por
qué* el cambio cabía. **Comando** y **Resultado** impiden el cambio exprés sin
ninguna comprobación: el resultado nombre el exit (`exit 0`) o el recuento de
la prueba, porque `ok` no distingue «pasó» de «no se ejecutó». **Confirmado
por** es la firma humana de las dos condiciones que `expres.py` no puede leer
del diff; si el trabajo se promueve, el destino va ahí como `→ NN-slug` y
`doctor.py` comprueba que esa etapa exista en el índice.

## La frontera exprés

`scripts/expres.py <repo> [--base REF]` decide si un cambio cabe fuera del
ciclo. Cabe solo si cumple **todo**:

- **1 archivo de producción** y **≤ 20 líneas de producción**. Las pruebas no
  cuentan: un cambio con su test es un buen cambio, no un cambio grande.
- Ninguna ruta excluida: `migrations/`, `schemas/`, `proto/`, `auth/`,
  `security/`, `crypto/`, `secrets/`, `contracts/`, `openapi`, `idl/`,
  manifiestos de dependencias (`package.json`, `pyproject.toml`, `go.mod`,
  `Cargo.toml`, …), extensiones `.sql`, `.proto`, `.avsc`, `.graphql`.

Dos cosas el script no puede leer del diff y quedan a confirmación humana,
declaradas en la fila de `EXPRES.md`:

- **sin criterio de aceptación nuevo**: si aparece un `CA-NN` que no existía,
  es producto nuevo y abre etapa;
- **sin cambio de interfaz pública**: un cambio de firma, formato o contrato
  observable abre etapa, aunque sean tres líneas.

Regla de decisión: si `expres.py` dice `no cabe`, o si alguna de las dos
confirmaciones no se puede afirmar, **abre etapa**. La vía exprés no tiene
override.

### Promoción a etapa

`doctor.py` rechaza (error, no aviso) cuando `EXPRES.md` acumula **3 o más**
cambios sobre el mismo `CA` o el mismo archivo, o cuando un cambio toca un
archivo que declara una tarea de una etapa en `lista`, `implementando` o
`auditando`. En los dos casos el corte estaba mal: se promueve a etapa y la
línea pasa a `→ NN-slug`. Una etapa cerrada no cuenta: sus archivos son
histórico, no trabajo en curso.

