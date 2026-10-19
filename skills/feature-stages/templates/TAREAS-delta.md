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
