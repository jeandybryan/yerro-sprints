---
name: audit-stage
description: >-
  Audits an implementation stage against its closed acceptance criteria and
  principal TAREAS.md using reproducible evidence; write AUDIT.md and,
  for implementation or verification gaps, TAREAS-delta-NN.md. Use when
  implementation is said to be complete, the user asks to close a stage,
  or requests an audit. Iterate until criteria, tasks, evidence and code
  match. Never rewrite CONCILIACION.md to fit code.
---

# Audit stage

Read [feature-stages](../feature-stages/SKILL.md),
[stage-contract.md](../feature-stages/references/stage-contract.md) and
[templates.md](../feature-stages/templates.md). Need closed
`CONCILIACION.md` and principal `TAREAS.md`. Score every pass against the
same acceptance baseline, including after deltas.

## Audit posture

The audit tries to **disprove** completion, not confirm the implementation
story. Task checkboxes, code presence, passing tests and developer notes are
inputs, not conclusions. Absence of contrary evidence is not proof.

Keep role independence:

- Do not implement or repair findings during the audit pass.
- Do not rewrite acceptance criteria, tasks or expected results to fit code.
- Re-run required checks; do not inherit the implementer's green result.
- Preserve the result against the audited snapshot, then create a delta and
  re-audit the corrected snapshot in a later pass.

## Procedure

1. Read the feature spec, closed `CONCILIACION.md`, principal `TAREAS.md`,
   existing deltas, prior audit and the feature index.
   A normal close audit requires stage `auditando` and the active principal
   list/delta marked `implementada`. An explicit user request may audit an
   `implementando` or `bloqueada` stage as an intermediate pass, but cannot
   change it to `cerrada`.
2. Run `python3 <skills-root>/feature-stages/scripts/validate_stage.py <stage>`.
   Structural errors block a `coincide` verdict; legacy warnings must be recorded
   as a limitation or normalized in the next baseline. Record the baseline: conciliation close date, task origin, current commit
   when available, relevant working-tree state and audit environment. Set the
   stage `auditando`.
3. Expand every `CA-NN` into its **atomic assertions**, including negative
   promises such as “does not spawn”, error behaviour, boundaries and
   compatibility constraints. Map each assertion to its task and prescribed
   verification method.
4. Check traceability in both directions:
   `CA → task → implementation → test/assertion → execution evidence`, and
   every relevant implementation change back to an approved CA/task.
5. Choose depth by risk. At minimum inspect all assertions; for high-risk
   paths (data loss, lifecycle, concurrency, external processes, security,
   recovery, performance or hardware) add a relevant negative, boundary or
   fault-injection attempt independent from the implementation evidence.
   Use mutation testing selectively only where an existing focused suite can
   expose weak assertions; record the mutant or why it is not useful, and
   never require a global mutation score.
6. Inspect code, tests, env examples, migrations, docs and runtime evidence
   as applicable. Execute the verification method named in `TAREAS.md`.
   Inspection cannot silently replace a required test, demonstration,
   measurement, restart or overnight run.
7. Record fresh reproducible evidence in the `E-NN` ledger: exact command or procedure, expected
   and observed result, exit status, relevant environment/config/fixture,
   timestamp and artifact/log path when one exists. A path or source reading
   proves structure or intent only; it does not prove runtime behaviour.
8. Score every CA using the rules below. Also audit global verification,
   task-level verification methods and deviations outside scope.
9. Write one immutable pass section in `AUDIT.md`, link every CA to its `E-NN` rows, then run the validator again before a `coincide` verdict. Do not erase failed or
   superseded passes; append the re-audit.
   If a prior `AUDIT.md` uses a legacy format, retain it as historical
   evidence but use the current template for the new pass. Do not inherit a
   legacy `coincide` verdict without rechecking its atomic assertions.

## Scoring rules

Use exactly these results:

- **`cumple`**: every atomic assertion is supported by sufficient direct
  evidence, the prescribed verification method ran successfully, and no
  material contradictory evidence remains.
- **`parcial`**: some assertions are proven but at least one is not, or the
  evidence/method covers only a weaker substitute (for example in-process
  call instead of process restart, scheduled retry without executing it, or
  mocked branch when the criterion requires integration behaviour).
- **`no cumple`**: reproducible evidence contradicts an assertion, required
  behaviour is absent, or forbidden behaviour occurs.
- **`no verificado`**: sufficient evidence could not be obtained or executed;
  do not infer success from source, intent, a stub, another test or lack of
  observed failures.

Statements such as “not executed”, “not tested”, “inspection only”, “the stub
does not cover”, “not reproduced” or “deferred” are material limitations when
they refer to an atomic assertion or prescribed method. Such a row cannot be
`cumple`. If the omitted activity is genuinely outside the CA and its agreed
method, explain that non-material distinction explicitly.

Passing a broad suite does not override a missing assertion. Code coverage is
only a gap-finding signal, not proof that outcomes were asserted.

## Verdict and next state

- **`coincide`** only when every principal CA is `cumple`, every applicable
  task verification method is evidenced, global checks pass, and there is no
  unresolved blocking scope deviation.
- Any `parcial`, `no cumple` or `no verificado` means **`no coincide`**.
- For an implementation or verification gap against the unchanged baseline,
  write the next `TAREAS-delta-NN.md` with only the work needed to close it.
  Its header must identify the failed audit pass, CA and evidence/hueco; set
  `Trabajo activo` to that delta and stage to `lista`. Do not implement unless asked.
- If required external/runtime evidence is temporarily unavailable and no
  code or test change can produce it, set the stage `bloqueada`, record the
  concrete blocker and required evidence; never close provisionally.
- If product intent or acceptance changed, first confirm with the user that
  this is a product change rather than an implementation/verification gap
  ([feature-stages](../feature-stages/SKILL.md) **Ask when in doubt**).
  Only then do not create a delta: set conciliation `abierta`, stage
  `conciliando`, and return to `conciliate-stage`.
- On `coincide`, mark principal task verification complete, set task state
  `auditada`, and stage `cerrada`.

## Evidence strength

Use the strongest method required by the criterion:

1. Runtime demonstration/measurement in the intended environment.
2. Integration or process-level test with observable outcomes.
3. Focused automated test exercising the required branch and assertions.
4. Static analysis or source/config inspection for structural claims.

A lower level is not automatically invalid: it is sufficient when the
criterion and `TAREAS.md` explicitly call for it. Stubs and mocks prove the
contract at their boundary, not the real dependency, process or hardware.

For overnight/hardware criteria, require the named logs/metrics, host/profile,
time window and thresholds. For negative promises, use an observable check
(spy, process list, filesystem state, diff scope or equivalent), not only a
text search when runtime side effects are possible.

## Scope deviations

Classify each deviation:

- **informativa**: no CA, risk or runtime behaviour is affected;
- **requiere revisión**: impact is uncertain or evidence is incomplete;
- **bloqueante**: contradicts scope, creates an unaccepted risk or invalidates
  the audited snapshot.

`requiere revisión` must be resolved or reclassified with evidence.
`bloqueante` prevents `coincide`.

## Do not

- Edit `CONCILIACION.md` so the code “already satisfied” the stage.
- Audit against the delta only (deltas exist to satisfy the principal list).
- Treat extra unrequested code as completing a missing task.
- Treat an out-of-scope change as harmless without recording its impact.
- Mark a CA `cumple` while its Notes admit a material untested assertion.
- Substitute source inspection for an agreed runtime/test method without
  scoring the criterion below `cumple`.
- Use test counts, coverage percentages or file presence as sufficient proof.
- Fix code/tests and then judge the repaired state in the same audit pass.
- Skip evidence for overnight stages: require logs/metrics the spec named.

## After a delta is implemented

New audit pass vs **TAREAS.md**, not vs the delta file alone. Repeat until coincide.
