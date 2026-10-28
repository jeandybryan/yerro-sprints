# AGENTS.md — Instrucciones para el agente que mantiene este repositorio

Eres el agente encargado de mantener YerroSprints, un paquete portable de seis
skills para gestionar una feature desde el corte de especificación hasta la
auditoría.

## Reglas de mantenimiento

- Nunca mezcles reglas de dominio en `skills/`. Si una regla describe un
  producto, servicio, módulo o archivo de un consumidor, no pertenece a este
  paquete.
- Preserva las seis fases y sus límites de responsabilidad. No elimines ni
  fundas fases para simplificar el paquete.
- No rebajes un gate para que una fixture pase. Una prueba negativa que dejó de
  fallar es un gate roto, no una victoria.
- Ejecuta las validaciones locales antes de editar el changelog o declarar el
  paquete listo. No declares verde una validación que no ejecutaste.
- Trata un cambio de baseline (intención, alcance o criterio de aceptación)
  como reapertura de la conciliación, no como un delta.
- Si una decisión de diseño no está acordada (nombre/owner/licencia, canales de
  distribución, política de tags, agentes soportados), pregunta antes de
  escribirla o publicarla.
- Mantén el README para humanos y los `SKILL.md` concisos para agentes.
- Conserva la evidencia de los comandos ejecutados en la descripción del PR o
  release, no dentro de los `SKILL.md`.
- El siguiente paso del ciclo se lee con
  `python3 skills/feature-stages/scripts/next_step.py <feature-root>`; no lo
  inventes ni lo deduzcas de la conversación. `doctor.py` informa incoherencias
  entre el índice y los artefactos.
- Toda transición, bloqueo o estado de etapa nuevo necesita un caso en
  `skills/feature-stages/evals/fixtures/` y su fila en `test_next_step.py`.
- La evidencia de cierre se congela: `**Snapshot:**` identifica el árbol
  auditado y `**Riesgo:**` el nivel aceptado. No reutilices un `coincide` sobre
  otro árbol ni rebajes el riesgo; ambos son gates del validador.
- `**Presupuesto de deltas:**` acota la corrección. Agotarlo es
  `necesita-decision`, no un delta más.
- Una regla nueva o que cambia comportamiento trae `Baseline:`, `Reps:` (≥5
  por variante) y `Control:`. Si el control no exhibe el fallo, la regla no se
  escribe; un resultado sin control no cuenta como mejora y la varianza se
  reporta, no se promedia. Es criterio de PR, no un gate de fixture.
- Un gate nuevo no deja modo legado. Hay **un** contrato y **un** modo de
  validación: si un cambio necesita convivencia, se implementa como feature de
  una versión con fecha de retirada, nunca como parámetro eterno (`--strict`,
  `--compat`, `legacy=`). Las fixtures que dependían del modo antiguo pasan a
  positivas o se retiran.
- La aprobación humana vive en `.yerro/approvals.yml`, fuera del árbol de la
  etapa, y **solo la edita la persona**. No escribas ese archivo, no añadas un
  campo `**Aprobado por:**` en los artefactos y no presentes una firma que
  escribiste como aprobación.
- El presupuesto de deltas se deriva del riesgo (`bajo → 2`, `medio → 1`,
  `alto → 1`); un valor distinto necesita `**Motivo del presupuesto:**`. No lo
  amplíes para que una etapa cierre.
- Un cambio en `snapshot.py` o en la verificación con `--repo` necesita su caso
  en `test_snapshot.py`.
- `**Archivos:**` de una tarea se deriva de su CA y **nunca** del diff ya
  producido: derivarlo del diff blanquea el caso que B-27 detecta. Un cambio en
  `diff_scope.py` o en el cruce de alcance necesita su caso en
  `test_diff_scope.py`.

## Antes de tocar un archivo

1. Lee `GOVERNANCE.md` y `RELEASE_CHECKLIST.md` si no los conoces: las
   decisiones de licencia, distribución, tags y agentes soportados están ahí.
2. Identifica qué fase o documento vas a modificar y por qué.
3. Determina si el cambio es de comportamiento (requiere fixture/caso nuevo) o
   de documentación (requiere mantener la coherencia en README, CONTRIBUTING y
   CHANGELOG).
4. Si toca una transición, agrega o ajusta la fixture antes de cambiar el
   script: el caso debe fallar con el contrato viejo.
5. Ejecuta las validaciones locales y confirma que la fixture negativa sigue
   fallando.

## Árbol que debes preservar

```
skills/
  identify-feature-stages/SKILL.md
  feature-stages/{SKILL.md,templates.md,EVALUATION.md,references/,scripts/,evals/}
  conciliate-stage/SKILL.md
  generate-stage-tasks/SKILL.md
  implement-stage/SKILL.md
  audit-stage/SKILL.md
```
- Cada CA nuevo debe enlazar una decisión `S-NN`; cada tarea nueva debe declarar `Test-first:` y `Test:`; una auditoría debe conservar la cadena `S → CA → T → test → E`.

- Antes de declarar una release, revisa `GOVERNANCE.md` y `RELEASE_CHECKLIST.md`; las decisiones de licencia, distribución, tags y agentes soportados requieren acuerdo explícito.
