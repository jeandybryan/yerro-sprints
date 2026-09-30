---
name: identify-feature-stages
description: >-
  Splits a product specification into an implementation-stage folder tree
  with a README index and per-stage CONCILIACION.md drafts. Use when the
  user wants implementation stages or needs to divide an existing or new
  feature specification into stages. Do not
  write TAREAS.md yet.
---

# Identify feature stages

Read [feature-stages](../feature-stages/SKILL.md) and [templates.md](../feature-stages/templates.md).

## Do

1. Place the specification in the project's agreed feature-artifact directory
   (`<feature-root>/`). Move it only when the project convention requires it,
   then update repository links.
2. Extract product outcomes, constraints and cross-cutting requirements
   before cutting. Ensure each spec requirement is allocated to at least
   one stage or explicitly marked as context/out of scope.
   For every allocation record the dominant risk (data, external process,
   concurrency, security, performance or hardware), the external boundary,
   and the highest evidence level that will eventually be required.
3. Cut **implementable, auditable deliverables** (not one folder per
   heading). Prefer vertical outcomes; use infrastructure stages only
   when later work genuinely depends on them.
4. Declare dependencies and order. Avoid circular dependencies; split or
   merge stages that cannot produce an observable result independently.
5. Write `README.md` index with stage status `borrador`.
6. Write each `NN-slug/CONCILIACION.md` as a **proposal** with Resultado
   observable, Dependencias, Entra, No entra, draft acceptance criteria,
   Riesgos/compatibilidad and Preguntas abiertas. Conciliation status is
   `borrador-corte`.
7. Check coverage: every closed product decision and acceptance case in
   the spec has an owning stage. Record a compact spec/case → stage map in
   the feature index when the source spec is large or cross-cutting.
8. Do **not** create `TAREAS.md`, `AUDIT.md`, or start coding.
9. If a cut, owner stage or split is ambiguous, ask with the
   [feature-stages](../feature-stages/SKILL.md) **Ask when in doubt**
   format; do not silently pick the split.

## Existing staged features

When the user asks to re-split an already staged feature, update only the
index and draft conciliations. Do not discard, rewrite scope/criteria, or move
ownership from a closed conciliation without user agreement and the reopening
protocol in `conciliate-stage`.

## After

Tell the user the cut is a draft. Next skill: `conciliate-stage` starting at `01-…`.
