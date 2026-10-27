---
name: implement-stage
description: >-
  Implements an approved implementation stage from its principal TAREAS.md or a
  TAREAS-delta-NN.md, verify the requested work, and leave evidence ready
  for a separate audit. Use when the user asks to implement or execute an
  approved stage or delta. Do not change the baseline, close or audit the stage.
---

# Implement stage

Read [feature-stages](../feature-stages/SKILL.md) and [stage-contract.md](../feature-stages/references/stage-contract.md), then the stage `CONCILIACION.md`,
principal `TAREAS.md`, and the requested delta if any. Load the delta template only when writing that delta.

Write code, tests and operational status. Do not change the baseline, acceptance criteria or `AUDIT.md`.

## Entry gate

Start only when:

- conciliation is `cerrada`;
- principal tasks exist and trace all acceptance criteria;
- dependencies are `cerrada` or have a named justified exception in the
  conciliation;
- the user asked to implement this stage/list;
- when implementing a delta: its `Cierra:` points to a `no coincide` audit pass,
  it names the affected CA/evidence, and the feature index marks it as active work;
- writing or implementing another delta stays within `**Presupuesto de deltas:**`,
  which is derived from the risk (`bajo → 2`, `medio → 1`, `alto → 1`) unless the
  conciliation wrote `**Motivo del presupuesto:**`.

Confirma con
`python3 <skills-root>/feature-stages/scripts/next_step.py <feature-root> --stage <NN-slug>`
que el estado es `trabajando` y la skill siguiente es `implement-stage`. Si
devuelve `necesita-decision`, no implementes: presenta el bloqueo y su
resolución.

Run `python3 <skills-root>/feature-stages/scripts/validate_stage.py <stage>`
before work; structural errors block implementation.

If product intent, scope or acceptance must change to proceed, stop and reopen
`conciliate-stage` ([feature-stages](../feature-stages/SKILL.md) **Ask when in
doubt** applies to the baseline). For an ambiguity *inside* the approved plan,
see **Rulings** below: decide and record, do not stop. Do not hide a scope
change in code or a delta.

## Rulings — decide and record

A running plan does not wait on the human for detail. Classify the decision by
what it changes, not by how doubtful it feels:

| Category | What it is | What you do |
| --- | --- | --- |
| 1. Implementation detail | The user receives the same thing | Decide and record `Ruling:` with its cost |
| 2. Observable, reversible effect | Visible but trivial to undo, scope unchanged | Decide, record and mark `**Sujeto a revisión R1:**` |
| 3. Intent, scope or criterion | Changes what was asked or accepted | **Stop and reopen `conciliate-stage`** |

The format is closed and all three parts are required:

```text
Ruling: <what I decided> — <why> — <what it costs if I am wrong>
```

A ruling without a cost hides the decision instead of exposing it, and the
validator rejects it. Write the cost concretely: how much code, what reverts, or
what cannot be recovered. If the third part would be "the deleted records do
not come back", that is not a ruling — it is one of the stops below.

Record the ruling next to the task that produced it in `TAREAS.md`. There is no
separate register: the task list is the register. Number each category 2 mark
(`R1`, `R2`…): the audit resolves it by that ID, and an ID that points nowhere
is a broken close.

In a stage with more than one task, each task declares `Interfaces:` with
`Consume:` (the exact signature it receives from an earlier task, or
`ninguna`) and `Produce:` (names and types later tasks take for granted).
Without it the next task invents names.

Beyond the categories, these always stop, without a ruling:

1. an irreversible or destructive operation;
2. anything touching credentials, permissions or cryptography;
3. an effect outside the worktree (merge, push, publish);
4. a new external dependency (library, service or model): its CVEs and
   licence are inherited, so it is decided with the human, not slipped in;
5. a plan so broken that every path is guessing;
6. category 3 — a change of intent, scope or acceptance criterion.

A "drive-by" refactor is category 3 even when it is reversible: it changes what
gets reviewed. It goes to the next task or to conciliation.

Read the stage through `preflight.py` before opening files: `python3 <skills-root>/feature-stages/scripts/preflight.py <feature-root> --fase implement-stage`. It lists what to read and, for everything it skips, the reason. A silent cut is a defect (P14).

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

Set stage `bloqueada` and write the concrete blocker in `## Bloqueos` of
`CONCILIACION.md`: cause, unblocker, required evidence and next review. That
section is operational, not baseline: leave `Entra`, `No entra`, the decisions
and the criteria untouched. `next_step.py` and `doctor.py` read the cause from
there, so a block written anywhere else is reported as "sin causa escrita" and
the stage looks blocked for no reason. Do not mark incomplete work done.

## Do not

- Write `.yerro/approvals.yml` or any approval mark. The approval is the
  person's file; if you write it, it stops proving anything.
- Expand scope with cleanup or “nice to have” work.
- Modify acceptance criteria to match implementation.
- Create `AUDIT.md` or close the stage.
- Generate a delta before an audit identifies a gap.
