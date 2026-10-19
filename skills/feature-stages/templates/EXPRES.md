## `EXPRES.md` (registro de cambios que no abren etapa)

Optional. Create it only when there was at least one express change. It is a
record, not a gate: `next_step.py` never reads it, it never changes a
transition and it never blocks a stage.

```markdown
# Registro de cambios exprés

Cambios que no abren etapa. Una línea por cambio, en orden cronológico.
Si un cambio deja de cumplir la frontera, se promueve a etapa y esta línea
se marca `→ NN-slug`.

| # | Fecha | Cambio | Archivos | CA | Frontera | Verificación |
|---|-------|--------|----------|----|----------|--------------|
| E-01 | AAAA-MM-DD | … | `ruta.py` | — | 1 archivo, 8 líneas | test focalizado; exit 0 |
```

La columna **Frontera** es la que evita la regresión: obliga a escribir *por
qué* el cambio cabía. La columna **Verificación** impide el cambio exprés sin
ninguna comprobación.

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

`doctor.py` avisa (nunca bloquea) cuando `EXPRES.md` acumula **3 o más**
cambios sobre el mismo `CA` o el mismo archivo. Esa acumulación significa que
la etapa estaba mal cortada: se promueve a etapa y la línea pasa a `→ NN-slug`.

