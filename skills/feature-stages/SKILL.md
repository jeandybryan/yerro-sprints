---
name: feature-stages
description: >-
  Guides the feature implementation cycle and routes requests through the
  six-stage contract. Use only for routing, unknown state, contract and gate
  questions. Do not conciliate, generate tasks, implement code or audit. Use
  operational skills for those actions.
---

# Feature stages

Use the complete cycle for product work with an agreed specification. Read only the contract and artifacts needed for the current transition; do not
implement without closed conciliation and a valid principal task list. Do not
rewrite the baseline to fit code. This skill writes no feature artifact: it only routes.

## Choose the proportional path

For a small correction, run:

```bash
python3 <skills-root>/feature-stages/scripts/expres.py <repo> [--base REF]
```

The express lane permits one production file and at most 20 production lines,
with no excluded route, new CA or public-interface change. Tests do not count.
If the result is `no cabe`, or the two human confirmations are unavailable,
open a normal stage. Record accepted express changes in `EXPRES.md`.
See [express-lane.md](references/express-lane.md).

## Read the contract before acting

```bash
python3 <skills-root>/feature-stages/scripts/next_step.py <feature-root> [--stage NN-slug] [--json]
python3 <skills-root>/feature-stages/scripts/preflight.py <feature-root> [--fase <skill>] [--json]
python3 <skills-root>/feature-stages/scripts/doctor.py <feature-root>
```

`preflight.py` lists what the phase must read and what it must not, with a
reason for each omission: no silent cut (P11, P14). Without
`**Presupuesto de contexto:**` in the conciliation it only reports; with it,
`--check` fails when the read exceeds the budget.

`next_step.py` is read-only and returns exactly one public state:
`trabajando`, `verificando`, `listo` or `necesita-decision`, plus the next
skill and blockers. `doctor.py` reports structural contradictions. Never guess
the next skill or replace `necesita-decision` with a default.

For audit work, also use:

```bash
python3 <skills-root>/feature-stages/scripts/snapshot.py <repo> --exclude <feature-root> --exclude .yerro/approvals.yml
python3 <skills-root>/feature-stages/scripts/validate_stage.py <stage> --repo <repo>
```

## Gates

A stage is ready to implement only with closed conciliation, stable CA IDs,
closed or justified dependencies, a principal `TAREAS.md`, and bidirectional
traceability. Each criterion has a decision origin; each task has `Test-first:`,
a reproducible `Test:` command that invokes a runner, and a `Sensibilidad:` that
shows the test could fail. See
[decision-traceability.md](references/decision-traceability.md) and
[evidence.md](references/evidence.md).

A stage is done only when every principal CA is `cumple`, required evidence and
checks pass, each `E-NN` row shows a demonstrated `Sensibilidad` (a ledger that
only proves the test passed does not close), the audited snapshot is current,
risk was not lowered, and there is no blocking deviation. Snapshot, risk and delta-budget rules live in
[stage-contract.md](references/stage-contract.md).

## Routing

| Intent | Skill or command |
|---|---|
| New feature or split a spec | `identify-feature-stages` |
| Decisions, scope or questions | `conciliate-stage` |
| Closed conciliation | `generate-stage-tasks` |
| Approved task list | `implement-stage` |
| Implemented or close request | `audit-stage` |
| Unknown state | `next_step.py` |

Preserve the six phases and their boundaries. Domain-specific rules stay out of
this package. Templates are in [templates.md](templates.md); maintenance rules
are in [skill-maintenance.md](references/skill-maintenance.md).

## When in doubt

Do not guess product intent, scope, evidence level, risk, owner or a closed
decision. Reply visibly with **Contexto**, **Pregunta** and **Propuesta** before
asking for a choice. AskQuestion is only the option picker. See
[decision-and-questions.md](references/decision-and-questions.md).
