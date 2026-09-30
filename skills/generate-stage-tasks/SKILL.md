---
name: generate-stage-tasks
description: >-
  Generates TAREAS.md (principal task list) after an implementation stage
  conciliation is cerrada, traced to CONCILIACION.md and the spec. Use when the user
  asks for the task file, listado principal, or says conciliation is done.
  Do not invent tasks outside Entra. Do not implement unless the user
  also asks to implement.
---

# Generate stage tasks

Read [feature-stages](../feature-stages/SKILL.md),
[stage-contract.md](../feature-stages/references/stage-contract.md) and
[templates.md](../feature-stages/templates.md). Refuse if `CONCILIACION.md`
is not `cerrada`. Run `validate_stage.py <stage>` before and after writing;
pre-existing legacy warnings may be recorded, but structural errors block the list.

## Do

1. Confirm estado `cerrada`, acceptance criteria with stable IDs,
   dependencies `cerrada` or a named justified exception in the
   conciliation, and empty/deferred questions.
2. Write `NN-slug/TAREAS.md` only. Each task:
   - stable id (`T1`, `T2`, …)
   - one implementable action
   - pointer to one or more `CA-NN` and spec/conciliation source
   - compact applicable impact: modules/contracts, data/migration, config,
     lifecycle/recovery, observability, profile/hardware, cleanup/rollback
   - **Verificar:** evidence level plus procedure and observable oracle
3. Add a compact traceability section. Every acceptance criterion maps
   to at least one task and verification; every task maps back to a
   criterion. Remove untraceable “nice to have” work.
4. Add global verification: relevant tests/lints, affected docs/config/
   migrations, and no unapproved scope changes.
5. Copy **Fuera de este listado** from conciliation **No entra**.
6. Update feature README: Tareas = `TAREAS.md`, stage = `lista`.
7. Run `python3 <skills-root>/feature-stages/scripts/validate_stage.py <stage>`;
   correct all errors before handing off.
8. Do not create delta files here.
9. If a task would invent work outside Entra, pick an unverified method,
   or collapse two criteria, stop and ask
   ([feature-stages](../feature-stages/SKILL.md) **Ask when in doubt**).
   Do not invent the list item.

## Regeneration after reopening

If a closed conciliation was reopened and closed again, update the existing
principal `TAREAS.md`; do not create a parallel principal list. Preserve a
task ID when its purpose and criterion are unchanged; retire or add IDs when
semantics change. Update `Origen`, record the baseline change in the task
file, and set the stage `lista` with `Trabajo activo: principal actualizado`.

## Quality

- Tasks are what code/tests/docs in **this** stage must do, not overnight of a later stage.
- No “nice to have” from other stages.
- Keep tasks small enough to verify independently, but do not split
  mechanically into one task per file.
- Prefer module names already established by the specification when they exist
  (for example, `<module>/<subsystem>/…`).

## After

Stop. Implement only if the user asks. Closing the stage later is `audit-stage`.
