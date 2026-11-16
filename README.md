# YerroSprints

Seis skills para que un agente lleve una *feature* desde el corte de
especificación hasta la auditoría, sin cerrar nada que no esté probado.

No es un framework ni despliega nada. El agente ejecuta; estas skills le dan
estados, gates y trazabilidad en archivos que podés leer y revisar.

## Instalación

No hace falta copiar comandos: pegale este prompt a tu agente.

> Instalá las seis skills de YerroSprints (github.com/jeandybryan/yerro-sprints)
> en este proyecto, fijadas al tag v0.5.2.
>
> 1. Pedime el host (Cursor, Claude Code, Codex u otro).
> 2. Instalá con el CLI `skills`:
>    `npx skills add 'jeandybryan/yerro-sprints#v0.5.2' --skill '*' --agent <host> --copy --yes`
>    Si el proyecto usa pnpm, usá `pnpm dlx` en lugar de `npx`.
> 3. Comprobá que aparezcan las seis: identify-feature-stages, feature-stages,
>    conciliate-stage, generate-stage-tasks, implement-stage y audit-stage.
> 4. Verificá Python 3 (solo stdlib). Sin Python se puede implementar, pero no
>    cerrar con evidencia.
>
> No modifiques ninguna skill ni escribas archivos fuera de la carpeta de skills
> del host. Al terminar, decime dónde quedaron y qué comando debo usar para
> actualizar a otro tag.

Si preferís hacerlo a mano, los comandos están en
[CONTRIBUTING.md](CONTRIBUTING.md#instalación) y la versión vigente es
[`v0.5.2`](https://github.com/jeandybryan/yerro-sprints/releases/tag/v0.5.2).

## Cómo se usa

Una vez instalado, tres prompts te bastan para empezar:

```text
Divide esta spec en etapas implementables.
```

```text
Conciliemos la etapa 01.
```

```text
¿Qué sigue?
```

El agente lee el estado con `next_step.py` y propone la fase siguiente. No hay
que recordar dónde estaba el trabajo: lo dicen los artefactos.

| Pedido | Skill | Resultado |
| --- | --- | --- |
| «Dividí esta spec en etapas» | `identify-feature-stages` | Índice de etapas en borrador. |
| «Conciliemos la etapa NN» | `conciliate-stage` | Alcance, decisiones, criterios, riesgo y presupuesto acordados. |
| «Generá las tareas» | `generate-stage-tasks` | La única lista principal, trazada a los criterios. |
| «Implementá la etapa NN» | `implement-stage` | Solo lo aprobado, con evidencia por tarea. |
| «Auditá la etapa NN» | `audit-stage` | Intenta refutar el cumplimiento: cierra, bloquea o pide un delta. |

## Por qué existe

Partir una feature es fácil de hacer mal: se mezcla alcance con tareas, se
«cierra» sin evidencia o un defecto se disfraza de cambio de criterio.

YerroSprints impone un ciclo de fases con responsabilidad única y un contrato
común:

- Cada fase produce un artefacto concreto; los artefactos son la fuente de
  verdad, no la conversación.
- Un cambio de intención, alcance o criterio **reabre** la conciliación.
- Un desvío se corrige con un **delta** acotado, nunca editando el baseline
  para que el código «encaje».
- La evidencia se reproduce; la auditoría intenta **refutar**.
- El cierre lo firma una persona, no el agente.

## El ciclo

```text
identify-feature-stages
→ conciliate-stage
→ generate-stage-tasks
→ implement-stage
→ audit-stage
└─ no coincide → TAREAS-delta-NN → implement-stage → audit-stage
```

`feature-stages` es el contrato compartido: define estados, gates, plantillas y
evaluación, pero no sustituye a ninguna fase.

| Skill | Función |
| --- | --- |
| `identify-feature-stages` | Corta la especificación en resultados implementables y auditables. |
| `feature-stages` | Define estados, gates, plantillas, contrato y evaluación. |
| `conciliate-stage` | Cierra alcance, decisiones, criterios, riesgos y evidencia. |
| `generate-stage-tasks` | Genera la única lista principal, trazada a los criterios. |
| `implement-stage` | Ejecuta solo la lista aprobada y deja evidencia. |
| `audit-stage` | Intenta refutar el cumplimiento; cierra, bloquea o emite un delta. |

## Qué te deja en el repositorio

```text
<feature-root>/
  <SPEC>.md               # qué se quiere
  README.md               # índice de etapas y estado
  NN-slug/
    CONCILIACION.md       # alcance, decisiones, criterios, riesgos, evidencia
    TAREAS.md             # lista principal, tras cerrar la conciliación
    AUDIT.md              # veredicto por pasada, con evidencia
    TAREAS-delta-NN.md    # solo si la auditoría encuentra un hueco
  EXPRES.md               # registro opcional de cambios fuera de etapa
```

## El contrato en cinco reglas

- Cada criterio `CA-NN` enlaza una decisión `S-NN`; cada tarea declara
  `**Archivos:**`, `Test-first:`, `Test:` y `Verificar:`.
- La evidencia demuestra **sensibilidad**: el test pudo fallar
  (`revertir → rojo → restaurar`, un mutante o una regresión contra `HEAD`).
- Un `coincide` vale solo para el árbol que auditó. Si el código cambió, se
  reaudita.
- El riesgo (`bajo`/`medio`/`alto`) decide el fondo de la evidencia y el
  presupuesto de deltas. No se rebaja para evitar reauditar.
- El cierre lo firma la persona en `.yerro/approvals.yml`; el agente nunca
  escribe ese archivo.

## Ver el estado sin adivinar

```bash
python3 <skills-root>/feature-stages/scripts/next_step.py <feature-root>
python3 <skills-root>/feature-stages/scripts/doctor.py <feature-root>
```

`next_step.py` devuelve el estado, la única skill siguiente y los bloqueos con
su resolución; `--json` para máquinas, `--reconcile` para retomar trabajo tras
compactar el contexto. `doctor.py` informa incoherencias entre el índice y los
artefactos.

## Requisitos

- Un host con Agent Skills y un agente con shell y lectura/escritura de
  archivos (Cursor, Claude Code, Codex u otro).
- **Python 3** (solo stdlib) para los validadores y el cierre con evidencia.
- **Node.js/npm** solo para instalar con `npx`.

## Actualización y versionado

- [Keep a Changelog](CHANGELOG.md) y [SemVer](https://semver.org/lang/es/).
- Última versión: [`v0.5.2`](https://github.com/jeandybryan/yerro-sprints/releases/tag/v0.5.2).
- Para actualizar, vuelve a correr el prompt con el tag nuevo: `npx skills add`
  reescribe `skills-lock.json` y el lock sigue ese ref.
- Inspeccioná cualquier script antes de ejecutarlo. No publiques secretos,
  resultados locales ni archivos compilados.

## Soporte y contribución

YerroSprints se publica bajo licencia MIT. Quien lo necesite puede pedir ayuda
de pago para implantarlo en su repositorio, adaptarlo a su CI o dar un taller
de formación. El contacto es un mensaje directo en X a
[jeandybryan](https://x.com/jeandybryan) o una issue con la etiqueta
`consultoria` mediante la plantilla
[Solicitud de consultoría](https://github.com/jeandybryan/yerro-sprints/issues/new?template=consultoria.yml&labels=consultoria).

**Apoya el proyecto:** un mensaje directo en X a
[jeandybryan](https://x.com/jeandybryan).

Las reglas de mantenimiento están en [GOVERNANCE.md](GOVERNANCE.md), la lista de
salida en [RELEASE_CHECKLIST.md](RELEASE_CHECKLIST.md) y cómo contribuir en
[CONTRIBUTING.md](CONTRIBUTING.md).

## Documentación

| Documento | Para qué |
| --- | --- |
| [skills/feature-stages/references/stage-contract.md](skills/feature-stages/references/stage-contract.md) | El contrato completo: estados, gates, firmas y riesgo. |
| [skills/feature-stages/SKILL.md](skills/feature-stages/SKILL.md) | El contrato que el agente carga primero. |
| [skills/feature-stages/EVALUATION.md](skills/feature-stages/EVALUATION.md) | Cómo se evalúa y qué casos cubren el comportamiento. |
| [CHANGELOG.md](CHANGELOG.md) | Qué cambió en cada versión. |
| [GOVERNANCE.md](GOVERNANCE.md) | Licencia, canal, tags y aprobadores. |
