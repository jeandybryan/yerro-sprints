# Templates

Copy these files. Fill; do not invent a parallel format.

## `README.md` (feature index, placed in `<feature-root>/`)

```markdown
# <Feature> — etapas de implementación

**Spec:** [<SPEC>.md](<SPEC>.md)
**Código:** …

## Ciclo

1. Conciliar → CONCILIACION.md
2. Tareas → TAREAS.md
3. Implementar
4. Auditar → AUDIT.md; si no coincide, TAREAS-delta-NN.md y repetir 3–4

## Ciclo activo

> Bloque opcional del índice; no crea un archivo ni exige estimaciones.

**Objetivo:** resultado observable que se quiere dejar utilizable.
**Etapas comprometidas:** …
**Por qué ahora:** prioridad, dependencia o desbloqueo que determina este ciclo.
**Criterio de éxito:** evidencia mínima …
**Fuera de este ciclo:** …
**Siguiente decisión:** …

### Cierre del ciclo

**Resultado:** …
**Evidencia:** …
**Desviaciones:** …
**Pendiente/bloqueado:** …
**Siguiente decisión:** …

## Estado del corte

| # | Carpeta | Resultado | Depende de | Conciliación | Estado | Trabajo activo | Tareas | Auditoría |
|---|---------|-----------|------------|--------------|--------|----------------|--------|-----------|
| 01 | [01-…](01-…/CONCILIACION.md) | … | — | borrador-corte | borrador | — | — | — |
```

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

## `CONCILIACION.md`

```markdown
# Etapa NN — <nombre>

**Estado:** borrador-corte | abierta | cerrada
**Riesgo:** bajo | medio | alto
**Presupuesto de deltas:** 2
**Spec:** [<SPEC>.md](../<SPEC>.md) §…

## Resultado observable

Una frase que describa qué capacidad queda utilizable al cerrar la etapa.

## Dependencias

- **DEP-01 — <etapa/condición>:** `cerrada | excepción`; si es excepción,
  justificar por qué se permite avanzar y qué evidencia falta.
- `Ninguna` si no hay.

## Entra

- …

## No entra

- …

## Aclaraciones

- **Baseline:** versión/fecha de la conciliación que estas decisiones fijan.
- AAAA-MM-DD — **Decisión:** …
  - Motivo: …
  - Consecuencias: …

## Criterios de aceptación

- **CA-01 — [condición de salida | invariante acumulado]:** precondición/estímulo → resultado
  observable; fallo, límite o promesa negativa relevante; evidencia
  `estructural | conductual | sistema | ambiental`.
  - Si es `ambiental`: entorno/configuración, ventana, umbral y artefacto/log esperado.
- **CA-02:** …

## Riesgos y compatibilidad

- Riesgo o regresión que debe vigilarse; `Ninguno identificado` si no hay.

## Bloqueos

- **B-01:** causa; responsable/desbloqueador; evidencia requerida; próxima
  revisión AAAA-MM-DD.
- `Ninguno` si no hay.

## Preguntas abiertas

- Pregunta (contexto breve). Opciones: (1) … (2) … (3) … Propuesta: (n) — …
- `Ninguna` si no hay; aplazada solo a una etapa **nombrada**.

## Criterio para cerrar conciliación

…
```

Close only when the observable result, dependencies, acceptance criteria,
risks and scope are agreed, and open questions are empty or explicitly
deferred to a later stage **by name**. Each criterion must state whether it
is a **condición de salida** or an **invariante acumulado**, and must name
an evidence level. For complex behaviour, add a few representative examples in
the criterion or Aclaraciones; do not create a separate specification format.

`**Riesgo:**` freezes with the conciliation and does not change silently:

- `bajo`: change is local, reversible and covered by existing tests.
- `medio`: touches shared behaviour, data or contracts, but has a tested
  rollback path.
- `alto`: touches data migration, security/authorization, shared contracts,
  concurrency, delivery/rollout or leaves a test gap. Name the concrete items
  after the level, e.g. `alto — datos, contratos compartidos`.
- The auditor may raise the level in `AUDIT.md`; lowering it reopens the
  conciliation.
- `**Presupuesto de deltas:**` bounds corrective work. Default `2`; higher
  values must be justified in Aclaraciones. Without the field, the default
  applies.

## `TAREAS.md`

Generate **only** when conciliation is `cerrada`. Each item: checkbox,
action, acceptance criterion/source pointer, and verification.

```markdown
# Tareas — etapa NN <nombre>

**Principal:** sí
**Origen:** CONCILIACION.md cerrada <fecha>
**Spec:** …
**Estado:** pendiente | en curso | implementada | auditada

## Listado

- [ ] T1 — … (CA-01; spec §…)
  Impacto: módulos/contratos | datos/migración | config | lifecycle/recovery |
  observabilidad | perfil/hardware | limpieza/rollback (solo lo aplicable).
  Verificar: nivel `estructural | conductual | sistema | ambiental`; procedimiento
  y oráculo observable.

## Trazabilidad

| Criterio | Tareas | Verificación prevista |
|----------|--------|-----------------------|
| CA-01 | T1 | test / inspección / demostración / medición |

## Verificación global

- [ ] Tests y lints relevantes.
- [ ] Documentación/config/migraciones actualizadas si aplica.
- [ ] Sin cambios fuera del alcance aprobado.

### Notas de implementación (no auditadas)

- Paths, comandos o decisiones útiles para el auditor. No constituyen
  evidencia de cumplimiento.

## Fuera de este listado

Items the agent must not do even if convenient (from “No entra”).
```

## `AUDIT.md`

```markdown
# Auditoría — etapa NN

## Pasada 1 — <fecha>

**Contra:** TAREAS.md (principal)
**Snapshot:** head=… tree=… dirty=… exclude=…
**Riesgo auditado:** bajo | medio | alto
**Baseline:** conciliación cerrada <fecha>; origen de tareas <fecha>; entorno <entorno/configuración relevante>

| Criterio | Afirmaciones auditadas | Tareas | Resultado | Evidencia reproducible | Limitaciones |
|----------|-------------------------|--------|-----------|-------------------------|--------------|
| CA-01 | comportamiento, error, negativo, límite | T1 | cumple / parcial / no cumple / no verificado | E-01, E-02 | … |

### Ledger de evidencia

| ID | CA | Procedimiento/comando | Esperado | Observado/exit | Entorno y timestamp | Artefacto/log | Limitación |
|----|----|------------------------|----------|----------------|---------------------|---------------|------------|
| E-01 | CA-01 | … | … | … | entorno/configuración; AAAA-MM-DDTHH:MM | path/URL | … |

**Veredicto:** coincide | no coincide

### Verificación global

- Tests/lints relevantes ejecutados en esta pasada.
- Métodos `Verificar:` de TAREAS cubiertos.
- Trazabilidad inversa de cambios a CA/tarea revisada.

### Desviaciones de alcance

- Ninguna; o `informativa | requiere revisión | bloqueante`, cambio y su
  impacto/evidencia.

### Huecos (si no coincide)

Write `TAREAS-delta-01.md` with only the implementation or verification
gaps needed to satisfy the current criteria. If evidence is externally
blocked, record the blocker and required evidence instead of approving by
inference. A changed product requirement reopens conciliation; it is not a
delta. Do not delete principal rows or failed prior passes.
```

`**Snapshot:**` is the exact value emitted by
`python3 <skills-root>/feature-stages/scripts/snapshot.py <repo> --exclude <feature-root>`.
It freezes the code the pass audited: same `head`, `tree` and `dirty` mean the
same candidate. If the tree changes after the pass, the verdict is stale and
the stage must be audited again; never reuse it to close. The feature root is
excluded so writing this file does not invalidate its own evidence, and
`exclude=` travels inside the value so verification recomputes the same tree.

`**Riesgo auditado:**` must be greater than or equal to the risk frozen in
`CONCILIACION.md`. Raising it is a finding; lowering it requires reopening the
conciliation.

Scoring is strict:

- `cumple`: all atomic assertions and the prescribed verification method
  have sufficient evidence.
- `parcial`: only a subset or weaker substitute is proven.
- `no cumple`: evidence contradicts the criterion or behaviour is absent.
- `no verificado`: evidence could not be obtained; never infer `cumple`.

`coincide` requires every principal criterion to be `cumple`, every
applicable task verification method evidenced, global checks passing and no
unresolved blocking deviation. Any other criterion result means
`no coincide`.

Evidence level is not a quality ranking by itself. It must meet the level
named by the criterion/task: structural proves shape; conductual proves the
asserted branch; system proves process integration; ambiental proves the
declared host/hardware/operation.

Para evidencia ambiental, el ledger identifica host, perfil, ventana y umbral
acordados, además del artefacto que permite reproducir la observación.

## `TAREAS-delta-NN.md`

Un delta conserva la forma de `TAREAS.md`, pero además enlaza de forma explícita
la brecha auditada. No reemplaza la lista principal.

```markdown
# Delta NN — etapa NN <nombre>

**Principal:** no
**Cierra:** AUDIT.md pasada N; CA-01; E-03
**Hueco:** comportamiento o evidencia que no cumplió el baseline.
**Estado:** pendiente | en curso | implementada

## Listado

- [ ] D01-T1 — acción mínima para cerrar el hueco (CA-01)
  Verificar: nivel `…`; procedimiento; oráculo observable.

## Fuera de este delta

- Trabajo no necesario para cerrar el hueco auditado.
```

Use IDs `D01-T1`, `D01-T2`... After implementing the delta, add **Pasada N+1**
to `AUDIT.md`, still scored against the principal criteria.

The number of deltas is bounded by `**Presupuesto de deltas:**` (default two).
If the audit after the last allowed delta still says `no coincide`, stop and
ask: reopen the conciliation, accept the residual risk with a named owner, or
leave the stage blocked. Do not write another delta to avoid the decision.

## Change after closure

If intent/scope/acceptance changes:

1. Set conciliation back to `abierta`; append a dated clarification with
   reason and consequences.
2. Update acceptance criteria while preserving IDs when semantics did not
   change; add new IDs otherwise. Never reuse an ID for another meaning.
3. Close again with user agreement.
4. Update `TAREAS.md` and its `Origen` date before implementation resumes.
5. Record in `AUDIT.md` which baseline/date was audited.

Deltas are only for code gaps against an unchanged baseline.
