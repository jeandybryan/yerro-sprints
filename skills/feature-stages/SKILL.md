---
name: feature-stages
description: >-
  Guides the feature implementation cycle: spec folder, per-stage
  CONCILIACION.md, principal TAREAS.md, implementation, evidence-based
  AUDIT.md, then TAREAS-delta-NN.md until acceptance criteria and code
  match. Use when adding a feature in stages, conciliating, implementing,
  generating tasks, auditing, or when the user mentions etapas,
  conciliación, TAREAS.md, deltas, or AUDIT.md.
---

# Feature stages

Use this cycle for any product feature with an agreed specification.

Do not implement a stage that has no **closed** conciliation and principal
task list. Do not rewrite conciliation to match the code; deltas close
implementation or verification gaps.

## Layout

```text
<feature-root>/
  <SPEC>.md                 # source of truth (what we want)
  README.md                 # stage index + status
  NN-slug/
    CONCILIACION.md         # first
    TAREAS.md               # after conciliation closes
    AUDIT.md                # after implementation; one section per pass
    TAREAS-delta-NN.md      # only if audit finds a gap
```

Templates: [templates.md](templates.md).
Contrato transversal: [stage-contract.md](references/stage-contract.md).
Validador estructural: `python3 <skills-root>/feature-stages/scripts/validate_stage.py <feature-root>/<NN-slug>`.
Regression rubric for changes to this cycle: [EVALUATION.md](EVALUATION.md).

## States

`CONCILIACION.md`: `borrador-corte` → `abierta` → `cerrada`.

Stage (in feature README): `borrador` → `conciliando` → `lista` →
`implementando` → `auditando` → `cerrada`. Use `bloqueada` only with a
written blocker. Keep the conciliation state and active work separate in the
index: `lista` can mean initial principal work or a named pending delta.

`TAREAS.md` is the **principal** list. Deltas do not replace it; they
close gaps against the same acceptance baseline.

## Gates

- **Ready to implement:** conciliation closed; acceptance criteria have
  stable IDs (`CA-01`...); dependencies are `cerrada` or have a named,
  justified exception in the conciliation; `TAREAS.md` traces every
  criterion to a verification method.
- **Done:** every principal criterion is `cumple`; relevant tests/lints pass;
  docs/config/migrations are updated when affected; no unresolved
  `requiere revisión` or `bloqueante` scope deviation; `AUDIT.md` contains
  fresh reproducible evidence.
  `Parcial`, `no cumple` or `no verificado` always means `no coincide`.

## Ciclo activo

El índice puede incluir un objetivo observable, etapas comprometidas, criterio de éxito, fuera de ciclo y siguiente decisión. Es opcional y no crea un archivo por sprint.

### Selección, WIP y bloqueos

Selecciona: etapa nombrada por el usuario; luego comprometida en `Ciclo activo`; luego delta que la desbloquea; luego mayor prioridad documentada; y solo al final la primera elegible. Registra `Por qué ahora`. Mantén como máximo una etapa en `implementando` y una en `auditando` por línea funcional, salvo razón anotada en `Trabajo activo`. Todo bloqueo indica causa, desbloqueador, evidencia requerida y siguiente revisión.

### Cambios y cierre

Un defecto contra el baseline va a delta; un cambio de producto o prioridad actualiza el objetivo o se difiere, reabriendo conciliación si cambia alcance; un incidente urgente registra qué compromiso desplaza. Al cerrar, anota resultado, evidencia, desviaciones, pendientes y siguiente decisión. El aprendizaje solo se registra ante una fricción material o repetible.

### Handoff a revisión

Tras `audit-stage` con `coincide`, se prepara revisión/PR si aplica. `autopilot` queda limitado a conflictos, comentarios y CI; Bugbot/Security Review se usan según riesgo y petición explícita. Ninguno sustituye la auditoría o validación ambiental, y el merge queda bajo decisión del usuario.

## Which skill

| User intent | Skill |
|-------------|--------|
| New feature / split a spec | `identify-feature-stages` |
| Talk through a stage, decisions, out of scope | `conciliate-stage` |
| Conciliation just closed | `generate-stage-tasks` |
| Execute an approved principal/delta list | `implement-stage` |
| “already implemented” / close the stage | `audit-stage` |

## Ask when in doubt

Do not guess product intent, scope, evidence level or a closed decision.
Stop and ask before writing it as agreed.

**Contexto** and **Propuesta** must appear in the visible Spanish reply.
AskQuestion is only the option picker; it does not replace those labels.
A card that shows just the question and buttons is a failed ask.

Visible reply (required before any AskQuestion call):

1. **Contexto:** 1–2 sentences — why it matters and what is blocked.
2. **Pregunta:** one explicit question.
3. **Propuesta:** the option you recommend and one-sentence justification
   (point at the spec when it exists).

If AskQuestion is available, call it after that text: `title` = short
topic; `prompt` = the same three labeled blocks (not the question alone);
≥3 distinct options, recommended first with ` (Recomendado)`; `Other`
remains available. More options when the choice is not a small set.

Enough to decide; no essay. Do not batch unrelated questions unless each
independently blocks the same step.

## Rules

- Stages are **implementable deliverables**, not 1:1 spec headings.
- Each stage has one observable outcome, dependencies, acceptance
  criteria, risks/compatibility notes, and explicit exclusions.
- A criterion is a **condición de salida** or an **invariante acumulado**.
  A condición de salida can be true at that historical point (for example
  “does not yet start a loop”); later approved stages may supersede it. An
  invariante acumulado must remain true and is rechecked by later audits.
- Spec context sections bind to stages; they are not stages by themselves.
- Tasks say **how** to satisfy criteria; they do not replace criteria.
- Evidence has a declared level: **structural** (source/config), **conductual**
  (focused test), **system** (integrated process) or **ambiental** (real
  host/hardware/operation). Verification proves the agreed build; validation
  proves it works in the intended environment. A validation criterion belongs
  to a named field/overnight stage unless explicitly required earlier.
- Audit verifies both compliance (built as specified) and acceptance
  (the outcome works in the intended context).
- Audit decomposes each criterion into atomic assertions and tries to refute
  completion with negative/boundary checks proportional to risk. A passing
  suite, source inspection or task checkbox does not replace the verification
  method agreed in `TAREAS.md`.
- Audit does not repair findings in the same pass. It preserves the failed
  evidence, emits a delta against the unchanged baseline and appends a later
  re-audit.
- If product intent changes after closure, reopen conciliation and update
  the baseline before coding. Deltas are not a mechanism for changing
  requirements.
- A recurring audit limitation is process feedback: add it to the next
  applicable conciliation or feature index, rather than hiding it in a
  one-off audit note.
- Domain-specific skills and project rules stay separate from this workflow.
  They may add constraints to a stage, but never weaken this cycle's gates.
