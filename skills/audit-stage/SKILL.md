---
name: audit-stage
description: >-
  Audits an implementation stage against closed acceptance criteria and the
  principal TAREAS.md using reproducible evidence. Use when implementation is
  said to be complete, the user asks to close a stage, or requests an audit.
  Do not implement repairs or rewrite CONCILIACION.md to fit code.
---

# Audit stage

Read [feature-stages](../feature-stages/SKILL.md) and [stage-contract.md](../feature-stages/references/stage-contract.md). Read the audit references and template only as needed. Need closed
`CONCILIACION.md` and principal `TAREAS.md`. Audit the same acceptance baseline
again after every delta.

Detailed rules:

- [Audit procedure](references/audit-procedure.md)
- [Scoring and evidence](references/scoring-and-evidence.md)
- [Deltas and closure](references/deltas-and-closure.md)

## Entry gate

Confirm the state before editing:

```bash
python3 <skills-root>/feature-stages/scripts/next_step.py <feature-root> --stage <NN-slug>
```

A normal close audit requires `verificando`, stage `auditando`, and the active
principal list or delta marked `implementada`. `necesita-decision` blocks. An
explicit user request may produce an intermediate audit for an implementing or
blocked stage, but cannot close it.

## Audit procedure

1. Read spec, closed conciliation, principal tasks, deltas, previous audits and
   the feature index.
2. Capture a fresh snapshot, record `**Riesgo auditado:**`, and run the
   structural validator:

   ```bash
   python3 <skills-root>/feature-stages/scripts/snapshot.py <repo> --exclude <feature-root>
   python3 <skills-root>/feature-stages/scripts/validate_stage.py <stage>
   ```

3. Expand every CA into atomic assertions and verify
   `S-NN → CA-NN → T-NN → implementation → test → E-NN`.
4. Re-run every declared `Test:` and `Verificar:` method independently. Add
   negative, boundary or fault-injection checks proportional to risk.
5. Write one immutable audit pass with fresh reproducible evidence. Append; do
   not erase failed or superseded passes.
6. Run the validator again before writing `**Veredicto:** coincide`.

Do not implement or repair findings in the same audit pass. A product-intent,
scope or acceptance change reopens conciliation; it is not a delta.

## Verdict

- `coincide` only when every principal CA is `cumple`, task methods and global
  checks have evidence, traceability is complete and no blocking deviation
  remains.
- Any `parcial`, `no cumple` or `no verificado` means `no coincide`.
- A gap against the unchanged baseline may produce the next delta only within
  the frozen budget. After implementation, audit against `TAREAS.md` again
  with a fresh snapshot.

The audit never lowers risk, reuses an obsolete snapshot or changes the
conciliated baseline to make code pass.
