## `AUDIT.md`

```markdown
# Auditoría — etapa NN

## Pasada 1 — <fecha>

**Contra:** TAREAS.md (principal)
**Snapshot:** head=… tree=… dirty=… exclude=…
**Riesgo auditado:** bajo | medio | alto
**Trazabilidad:** S-01 → CA-01 → T1 → <test> → E-01
**Baseline:** conciliación cerrada <fecha>; origen de tareas <fecha>; entorno <entorno/configuración relevante>

| Criterio | Afirmaciones auditadas | Tareas | Resultado | Evidencia reproducible | Limitaciones |
|----------|-------------------------|--------|-----------|-------------------------|--------------|
| CA-01 | comportamiento, error, negativo, límite | T1 | cumple / parcial / no cumple / no verificado | E-01, E-02 | … |

### Ledger de evidencia

| ID | CA | Procedimiento/comando | Sensibilidad | Esperado | Observado/exit | Entorno y timestamp | Artefacto/log | Limitación |
|----|----|------------------------|--------------|----------|----------------|---------------------|---------------|------------|
| E-01 | CA-01 | `evidence.py run -- <comando>` | revertir → rojo → restaurar | … | … firma=… | entorno/configuración; AAAA-MM-DDTHH:MM | path/URL | … |

**Deltas:** D1, D2 | `ninguno`
**Cruza riesgo:** no | sí — <qué criterio se bajó y por qué>
**Motivo del presupuesto:** <obligatorio si `Cruza riesgo: sí` o si los deltas superan el presupuesto vigente>

### Rulings revisados

Cada `**Sujeto a revisión R-NN:**` de `TAREAS.md` se resuelve aquí con su mismo
identificador, leyendo los artefactos y el diff, nunca la conversación de
implementación (B-32). Una marca sin resolución, o una resolución que apunta a
otro ID, impide el cierre (B-26).

- aceptado R1 — <qué se decidió>: <por qué es correcto con el CA y el diff>
- hallazgo R2 — <qué se decidió>: <qué contradice el baseline o la evidencia>

**Veredicto:** coincide | no coincide

### Verificación global

- Tests/lints relevantes ejecutados en esta pasada.
- Métodos `Verificar:` de TAREAS cubiertos.
- Trazabilidad inversa de cambios a S/CA/tarea revisada.
- Cada `Test-first:` existía y fallaba o demostraba el hueco antes de la implementación; la auditoría registra la mutación o la razón por la que no aplica.

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
`python3 <skills-root>/feature-stages/scripts/snapshot.py <repo> --exclude <feature-root> --exclude .yerro/approvals.yml`.
Both exclusions are required: the validator always excludes the approval file,
so a snapshot without it never matches even when the tree is identical. The
value freezes the code the pass audited: same `head`, `tree` and `dirty` mean
the same candidate. If the tree changes after the pass, the verdict is stale and
the stage must be audited again; never reuse it to close. The feature root is
excluded so writing this file does not invalidate its own evidence, and
`exclude=` travels inside the value so verification recomputes the same tree.

## Trazabilidad y test-first

- Cada decisión acordada tiene un ID estable `S-NN`, cita verbal exacta cuando la haya, fecha, motivo y consecuencias. No se recicla un ID para otra decisión.
- Cada `CA-NN` incluye `Origen: S-NN`; un criterio sin decisión origen no puede cerrar en modo estricto.
- Cada tarea incluye `Test-first: sí` y `Test: <comando>`. El comando debe expresar el oráculo y existir antes de marcar la tarea como implementada.
- `AUDIT.md` conserva `**Trazabilidad:** S-NN → CA-NN → T-NN → test → E-NN` y no acepta evidencia sin procedimiento reproducible.
- Si el test-first no puede ejecutarse, la tarea es `no verificado`; no se infiere `cumple`.

`**Riesgo auditado:**` must be greater than or equal to the risk frozen in
`CONCILIACION.md`. Raising it is a finding; lowering it requires reopening the
conciliation.

Scoring is strict:

- `cumple`: all atomic assertions and the prescribed verification method
  have sufficient evidence.

`Sensibilidad` proves the test could fail: `revertir → rojo → restaurar`,
`mutante: <qué> → rojo`, or a functional regression against `HEAD`. A cell
that says `no demostrada` is `no verificado`, never `cumple`. The result after
the arrow is the observation: `→ verde` (the mutant survived) and `→ rojo
esperado` (a prediction) are not sensitivity, and one surviving mutant is
enough to invalidate an `alto` stage. See
[evidence.md](../references/evidence.md).

The ledger also carries the **background the risk level demands**: above `bajo`,
a demonstrated limit or negative case; at `alto`, a `mutante:` (or injected
failure) with a red result per critical CA. Write the result you observed:
`→ verde` (the mutant survived) and `→ rojo esperado` (a prediction) are not
sensitivity. A `coincide` that lowers the
strictest criterion writes `**Cruza riesgo:** sí — …` and
`**Motivo del presupuesto:** …`, or it does not close. No `**Aprobado por:**`
line exists: the human approval lives in `.yerro/approvals.yml`.
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

