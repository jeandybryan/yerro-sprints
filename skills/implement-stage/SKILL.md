---
name: implement-stage
description: >-
  Implements an approved implementation stage from its principal TAREAS.md or a
  TAREAS-delta-NN.md, verify the requested work, and leave evidence ready
  for a separate audit. Use when the user asks to implement, execute, or
  complete a conciliada/lista stage or its delta. Do not close or audit
  the stage.
---

# Implement stage

Read [feature-stages](../feature-stages/SKILL.md),
[stage-contract.md](../feature-stages/references/stage-contract.md),
[templates.md](../feature-stages/templates.md), the stage `CONCILIACION.md`,
principal `TAREAS.md`, and the requested delta if any.

## Entry gate

Start only when:

- conciliation is `cerrada`;
- principal tasks exist and trace all acceptance criteria;
- dependencies are `cerrada` or have a named justified exception in the
  conciliation;
- the user asked to implement this stage/list;
- when implementing a delta: its `Cierra:` points to a `no coincide` audit pass,
  it names the affected CA/evidence, and the feature index marks it as active work.

Run `python3 <skills-root>/feature-stages/scripts/validate_stage.py <stage>`
before work; structural errors block implementation.

If product intent, scope or acceptance must change to proceed, or a task
is ambiguous, stop and ask
([feature-stages](../feature-stages/SKILL.md) **Ask when in doubt**).
Return to `conciliate-stage` when the answer changes the baseline. Do not
hide the change in code or a delta.

## Do

1. Set stage `implementando` and task state `en curso`.
2. Implement only the requested principal/delta list. Preserve existing
   invariantes acumulados outside its approved scope. Do not reinterpret a
   historical condición de salida as an invariante acumulado after a later
   approved stage superseded it.
3. Mark a task checkbox only after its own **Verificar** step passes.
4. Run proportional tests/lints and update affected docs, configuration
   and migrations named by the list.
5. For data loss, lifecycle, concurrency, external process, security,
   performance or hardware paths, establish test sensitivity before marking
   the task: red/green, a focused injected failure or a justified mutation.
   Prefer real temporary filesystem, database, or process dependencies when cheap;
   mocks prove their boundary only.
6. Record concise implementation notes beside tasks when useful
   (paths/tests), clearly marked as not audited; do not write the audit
   verdict.
7. Run the structural validator again; correct errors in task evidence before
   handoff. When all requested checks pass, set task state `implementada` and
   stage `auditando`. Hand off to `audit-stage`.

## If blocked

Set stage `bloqueada` and write the concrete blocker in the feature
README or task list. Do not mark incomplete work done.

## Do not

- Expand scope with cleanup or “nice to have” work.
- Modify acceptance criteria to match implementation.
- Create `AUDIT.md` or close the stage.
- Generate a delta before an audit identifies a gap.
