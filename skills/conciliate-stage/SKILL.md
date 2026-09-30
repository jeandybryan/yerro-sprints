---
name: conciliate-stage
description: >-
  Conciliates one implementation stage: updates CONCILIACION.md with in/out
  of scope, chat clarifications, and open questions. Use when the user is
  discussing a stage or clarifying product/feature decisions,
  or closing conciliation. Do not generate TAREAS.md until estado is
  cerrada. Do not implement code in this skill.
---

# Conciliate stage

Read [feature-stages](../feature-stages/SKILL.md),
[stage-contract.md](../feature-stages/references/stage-contract.md),
[templates.md](../feature-stages/templates.md) and the stage
`CONCILIACION.md`. Spec is source of truth; chat **clarifies**, it does not
silently override § decisiones cerradas.

## Ask when in doubt

Do not fill Entra, CA, evidence level or Aclaraciones with a guessed
answer. If the spec and the user have not settled it, ask first (see
[feature-stages](../feature-stages/SKILL.md) **Ask when in doubt**).

**Contexto** and **Propuesta** must be visible in the chat. AskQuestion is
only the option picker: its card may hide or truncate the prompt. Never
leave those two blocks only inside the tool.

Visible Spanish reply (required every time you ask, before any tool call):

**Contexto:** 1–2 sentences — what is at stake and what cannot proceed.
**Pregunta:** one explicit question.
**Propuesta:** recommended option — one-sentence why (spec pointer when
it exists).

If AskQuestion is available, call it **after** that text (directly; do not
discover the tool instead of writing the labels):

- `title`: short topic. Not a substitute for Contexto.
- `prompt`: the same **Contexto**, **Pregunta** and **Propuesta**, labels
  included. A prompt that is only the question is a bug.
- ≥3 distinct options; recommended first, suffix ` (Recomendado)`.
- `Other` remains available.

Do not omit **Propuesta** because the first option is recommended. Do not
close or treat a default as agreed until the user chooses. Just enough to
decide; do not pad.

Example of the required chat text:

**Contexto:** La interfaz entre dos componentes no está cerrada; sin esto no
se pueden escribir CA-07 ni definir Entra.
**Pregunta:** ¿Qué datos y transiciones expone el componente productor en la
primera versión?
**Propuesta:** una entidad con identificador estable y eventos explícitos de
inicio y cierre; evita que el consumidor tenga que inferir su ciclo de vida.

## Do

1. Work **one** stage folder. Select it in this order: user-named; committed
   in `Ciclo activo`; named delta that unblocks it; documented priority; only
   then first `borrador-corte` or `abierta`. Record `Por qué ahora` in the index.
2. Set conciliation `abierta` and stage `conciliando`.
3. Agree one **Resultado observable** and verify dependencies.
4. Append decisions with date, decision, reason and consequences
   (verbatim wording when the user gave an exact rule). Point at spec.
   If a decision changes or contradicts the spec, update the spec in the
   same change and record that fact; do not leave two sources in conflict.
5. Turn the agreed outcome into stable, atomic acceptance criteria
   (`CA-01`, `CA-02`...). Each criterion names precondition/stimulus,
   observable result, relevant failure/limit or negative promise, evidence
   level (`estructural`, `conductual`, `sistema` or `ambiental`), and whether
   it is a condición de salida o invariante acumulado. Include a few
   representative examples for complex behaviour; do not impose Gherkin.
6. Record important risks/regressions and how they will be observed.
7. Move resolved questions out of **Preguntas abiertas**.
8. Keep **No entra** honest: later stages or out of V1 stay named.
9. Close (`cerrada`) only when the user agrees, dependencies are `cerrada`
   or have a named justified exception, criteria are clear, and open
   questions are empty or deferred to a named stage.
10. Update the feature README: stage `lista` only after `TAREAS.md` exists;
    until then keep `conciliando` and show conciliation `cerrada`.

## Do not

- Write `TAREAS.md` until `cerrada` (then tell the user to run `generate-stage-tasks`).
- Implement application code.
- “Close” or write criteria by assuming answers; ask instead.
- Ask with only a question and option buttons. **Contexto** and **Propuesta**
  must be in the chat; AskQuestion does not replace them.
- Hide a product change in a task or delta. Reopen conciliation when
  intent, scope or acceptance changes after closure.
- Rewrite the specification to justify an implementation shortcut.
- Import product-specific constraints into this generic workflow; apply the
  relevant domain skill or project rule separately.
