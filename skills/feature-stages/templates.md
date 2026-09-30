# Templates

Copy these files. Fill; do not invent a parallel format.

## `README.md` (feature index, placed in `<feature-root>/`)

```markdown
# <Feature> — etapas de implementación

**Spec:** [<SPEC>.md](<SPEC>.md)
**Código:** …

## Ciclo

1. Conciliar → CONCILIACION.md
2. Tareas → TAREAS.md
3. Implementar
4. Auditar → AUDIT.md; si no coincide, TAREAS-delta-NN.md y repetir 3–4

## Ciclo activo

> Bloque opcional del índice; no crea un archivo ni exige estimaciones.

**Objetivo:** resultado observable que se quiere dejar utilizable.
**Etapas comprometidas:** …
**Por qué ahora:** prioridad, dependencia o desbloqueo que determina este ciclo.
**Criterio de éxito:** evidencia mínima …
**Fuera de este ciclo:** …
**Siguiente decisión:** …

### Cierre del ciclo

**Resultado:** …
**Evidencia:** …
**Desviaciones:** …
**Pendiente/bloqueado:** …
**Siguiente decisión:** …

## Estado del corte

| # | Carpeta | Resultado | Depende de | Conciliación | Estado | Trabajo activo | Tareas | Auditoría |
|---|---------|-----------|------------|--------------|--------|----------------|--------|-----------|
| 01 | [01-…](01-…/CONCILIACION.md) | … | — | borrador-corte | borrador | — | — | — |
```

## `CONCILIACION.md`

```markdown
# Etapa NN — <nombre>

**Estado:** borrador-corte | abierta | cerrada
**Spec:** [<SPEC>.md](../<SPEC>.md) §…

## Resultado observable

Una frase que describa qué capacidad queda utilizable al cerrar la etapa.

## Dependencias

- **DEP-01 — <etapa/condición>:** `cerrada | excepción`; si es excepción,
  justificar por qué se permite avanzar y qué evidencia falta.
- `Ninguna` si no hay.

## Entra

- …

## No entra

- …

## Aclaraciones

- **Baseline:** versión/fecha de la conciliación que estas decisiones fijan.
- AAAA-MM-DD — **Decisión:** …
  - Motivo: …
  - Consecuencias: …

## Criterios de aceptación

- **CA-01 — [condición de salida | invariante acumulado]:** precondición/estímulo → resultado
  observable; fallo, límite o promesa negativa relevante; evidencia
  `estructural | conductual | sistema | ambiental`.
  - Si es `ambiental`: entorno/configuración, ventana, umbral y artefacto/log esperado.
- **CA-02:** …

## Riesgos y compatibilidad

- Riesgo o regresión que debe vigilarse; `Ninguno identificado` si no hay.

## Bloqueos

- **B-01:** causa; responsable/desbloqueador; evidencia requerida; próxima
  revisión AAAA-MM-DD.
- `Ninguno` si no hay.

## Preguntas abiertas

- Pregunta (contexto breve). Opciones: (1) … (2) … (3) … Propuesta: (n) — …
- `Ninguna` si no hay; aplazada solo a una etapa **nombrada**.

## Criterio para cerrar conciliación

…
```

Close only when the observable result, dependencies, acceptance criteria,
risks and scope are agreed, and open questions are empty or explicitly
deferred to a later stage **by name**. Each criterion must state whether it
is a **condición de salida** or an **invariante acumulado**, and must name
an evidence level. For complex behaviour, add a few representative examples in
the criterion or Aclaraciones; do not create a separate specification format.

## `TAREAS.md`

Generate **only** when conciliation is `cerrada`. Each item: checkbox,
action, acceptance criterion/source pointer, and verification.

```markdown
# Tareas — etapa NN <nombre>

**Principal:** sí
**Origen:** CONCILIACION.md cerrada <fecha>
**Spec:** …
**Estado:** pendiente | en curso | implementada | auditada

## Listado

- [ ] T1 — … (CA-01; spec §…)
  Impacto: módulos/contratos | datos/migración | config | lifecycle/recovery |
  observabilidad | perfil/hardware | limpieza/rollback (solo lo aplicable).
  Verificar: nivel `estructural | conductual | sistema | ambiental`; procedimiento
  y oráculo observable.

## Trazabilidad

| Criterio | Tareas | Verificación prevista |
|----------|--------|-----------------------|
| CA-01 | T1 | test / inspección / demostración / medición |

## Verificación global

- [ ] Tests y lints relevantes.
- [ ] Documentación/config/migraciones actualizadas si aplica.
- [ ] Sin cambios fuera del alcance aprobado.

### Notas de implementación (no auditadas)

- Paths, comandos o decisiones útiles para el auditor. No constituyen
  evidencia de cumplimiento.

## Fuera de este listado

Items the agent must not do even if convenient (from “No entra”).
```

## `AUDIT.md`

```markdown
# Auditoría — etapa NN

## Pasada 1 — <fecha>

**Contra:** TAREAS.md (principal)
**Baseline:** conciliación cerrada <fecha>; origen de tareas <fecha>;
commit/working tree <identificador>; entorno <entorno/configuración relevante>

| Criterio | Afirmaciones auditadas | Tareas | Resultado | Evidencia reproducible | Limitaciones |
|----------|-------------------------|--------|-----------|-------------------------|--------------|
| CA-01 | comportamiento, error, negativo, límite | T1 | cumple / parcial / no cumple / no verificado | E-01, E-02 | … |

### Ledger de evidencia

| ID | CA | Procedimiento/comando | Esperado | Observado/exit | Entorno y timestamp | Artefacto/log | Limitación |
|----|----|------------------------|----------|----------------|---------------------|---------------|------------|
| E-01 | CA-01 | … | … | … | entorno/configuración; AAAA-MM-DDTHH:MM | path/URL | … |

**Veredicto:** coincide | no coincide

### Verificación global

- Tests/lints relevantes ejecutados en esta pasada.
- Métodos `Verificar:` de TAREAS cubiertos.
- Trazabilidad inversa de cambios a CA/tarea revisada.

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

Scoring is strict:

- `cumple`: all atomic assertions and the prescribed verification method
  have sufficient evidence.
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
