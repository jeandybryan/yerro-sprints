## `CONCILIACION.md`

```markdown
# Etapa NN — <nombre>

**Estado:** borrador-corte | abierta | cerrada
**Riesgo:** bajo | medio | alto
**Presupuesto de deltas:** 2
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
- **S-01 — Decisión:** …
  - Cita: «…»
  - Motivo: …
  - Consecuencias: …
  - Fecha: AAAA-MM-DD

## Criterios de aceptación

- **CA-01 — [condición de salida | invariante acumulado]:** precondición/estímulo → resultado
  observable; fallo, límite o promesa negativa relevante; evidencia
  `estructural | conductual | sistema | ambiental`. `Origen: S-01`.
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

`**Riesgo:**` freezes with the conciliation and does not change silently:

- `bajo`: change is local, reversible and covered by existing tests.
- `medio`: touches shared behaviour, data or contracts, but has a tested
  rollback path.
- `alto`: touches data migration, security/authorization, shared contracts,
  concurrency, delivery/rollout or leaves a test gap. Name the concrete items
  after the level, e.g. `alto — datos, contratos compartidos`.
- The auditor may raise the level in `AUDIT.md`; lowering it reopens the
  conciliation.
- `**Presupuesto de deltas:**` bounds corrective work. Default `2`; higher
  values must be justified in Aclaraciones. Without the field, the default
  applies.

