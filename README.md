# YerroSprints

Paquete portable de seis [Agent Skills](https://cursor.com/docs/context/skills)
para llevar una *feature* desde el corte de especificación hasta la auditoría.

> Gestiona una feature por etapas con límites claros de responsabilidad y
> artefactos auditables. **No** es un framework, no despliega nada por sí mismo
> y **no** contiene reglas de dominio de ningún proyecto: el agente es quien
> ejecuta, y estas skills le dan estados, gates y trazabilidad.

## Qué resuelve

Partir una feature en pedazos es fácil de hacer mal: se mezcla alcance con
tareas, se "cierra" sin evidencia, o un defecto se disfraza de cambio de
criterio. YerroSprints impone un ciclo con **seis fases de responsabilidad
única** y un contrato que todas comparten:

- Cada fase produce un artefacto concreto y auditable.
- Un cambio de **intención, alcance o criterio** reabre la conciliación.
- Un desvío contra un baseline ya acordado se repara con un **delta**, nunca
  editando la feature para que "encaje".

## El ciclo

```text
identify-feature-stages
  → conciliate-stage
  → generate-stage-tasks
  → implement-stage
  → audit-stage
                 └─ no coincide → TAREAS-delta-NN → implement-stage → audit-stage
```

`feature-stages` es el **contrato y orquestador compartido**: define estados,
gates, plantillas y evaluación, pero **no reemplaza ninguna fase**.

## Las seis skills

| Skill | Función |
| ----------------------- | ------------------------------------------------------------------- |
| `identify-feature-stages` | Corta una especificación en resultados implementables y auditables. |
| `feature-stages`          | Define estados, gates, plantillas, contrato y evaluación.           |
| `conciliate-stage`        | Cierra alcance, decisiones, criterios de aceptación, riesgos y evidencia. |
| `generate-stage-tasks`    | Genera la única lista principal de tareas, trazada a los criterios. |
| `implement-stage`         | Ejecuta solo la lista aprobada y deja evidencia para auditoría.     |
| `audit-stage`             | Intenta refutar el cumplimiento; cierra, bloquea o emite un delta.  |

## Requisitos

- Un host compatible con Agent Skills (Cursor, Claude Code, Codex u otro).
- **Python 3** (solo stdlib) únicamente para los validadores estructurales
  opcionales. Las skills no exigen Python para operar.
- **Node.js/npm** solo si instalas o pruebas con `npx skills`.

## Instalación

### Con `npx skills`

Lista lo que ofrece el repositorio:

```bash
npx skills add jeandybryan/yerro-sprints --list
```

Instala las seis skills para Cursor y copia sus archivos al proyecto:

```bash
npx skills add jeandybryan/yerro-sprints \
  --skill '*' \
  --agent cursor \
  --copy \
  --yes
```

La herramienta elige la ruta de instalación para el host. Verifica en la
configuración de Skills de tu host que aparezcan las seis.

### Proyectos con pnpm

La CLI `skills` (de [vercel-labs/skills](https://github.com/vercel-labs/skills))
se instala a sí misma con pnpm. En un proyecto que ya usa pnpm, `npx skills`
puede fallar con `EBADDEVENGINES`: `npx` es `npm exec`, y npm rechaza el
`devEngines.packageManager` del proyecto antes de ejecutar nada.

En un proyecto pnpm, usa `pnpm dlx`:

```bash
pnpm dlx skills add jeandybryan/yerro-sprints --list
pnpm dlx skills add jeandybryan/yerro-sprints \
  --skill '*' \
  --agent cursor \
  --copy \
  --yes
```

Si por convención el equipo insiste en `npx`, antepón `--force` (degrada el
aviso de motor a *warning* y deja correr la CLI):

```bash
npx --force skills add jeandybryan/yerro-sprints --list
```

### Instalación manual

Copia `skills/` al directorio de skills soportado por el host. En Cursor puede
ser `.cursor/skills/` o `.agents/skills/` dentro del proyecto.

La instalación global es opcional y local a una persona:

```bash
npx skills add jeandybryan/yerro-sprints --skill '*' --agent cursor --global --copy --yes
```

No uses la instalación global como dependencia de CI o de un equipo: para
trabajo compartido, instala a nivel proyecto y versiona los resultados, o usa
una fuente/release controlada por el equipo.

## Cómo usarlo en un proyecto (paso a paso)

El ciclo tiene cinco momentos en orden. `feature-stages` define el contrato que
los demás respetan; cada paso solo hace lo suyo y produce un artefacto. Trabaja
en la raíz de una feature:

```text
<feature-root>/
  <SPEC>.md            # fuente de verdad (qué se quiere)
  README.md            # índice de etapas y estado
  NN-slug/
    CONCILIACION.md    # alcance, decisiones, CA, riesgos, evidencia
    TAREAS.md          # lista principal (tras cerrar la conciliación)
    AUDIT.md           # veredicto por pasada, con evidencia
    TAREAS-delta-NN.md # solo si el audit encuentra un hueco
```

### ¿En qué estado estoy?

Antes de elegir un paso, léelo desde los artefactos en vez de recordarlo:

```bash
python3 <skills-root>/feature-stages/scripts/next_step.py <feature-root>
python3 <skills-root>/feature-stages/scripts/doctor.py <feature-root>
```

`next_step.py` devuelve un estado público (`trabajando`, `verificando`,
`listo`, `necesita-decision`), la única skill siguiente y los bloqueos con su
resolución. `--json` para máquinas, `--stage NN-slug` para una etapa concreta y
`--check` para CI. `doctor.py` informa incoherencias entre el índice y los
artefactos. Ambos son de solo lectura y no sustituyen ningún gate.

### 1. Corta la especificación

Pídele al agente: **"divide esta spec en etapas implementables"**.

- Skill: `identify-feature-stages`.
- Resultado: crea la carpeta `<feature-root>/` con el índice `README.md`
  (etapas en estado `borrador`) y, por etapa, un borrador de
  `NN-slug/CONCILIACION.md` en `borrador-corte`.
- **No** crea `TAREAS.md` todavía.

### 2. Concilia cada etapa

Pídele: **"conciliemos la etapa NN"** (una etapa a la vez).

- Skill: `conciliate-stage`.
- Resultado: `CONCILIACION.md` con `Entra`/`No entra`, decisiones, criterios de
  aceptación (`CA-01`, `CA-02`…), riesgos y evidencia esperada.
- Al cerrar se congelan `**Riesgo:**` (`bajo`/`medio`/`alto`) y
  `**Presupuesto de deltas:**` (dos por defecto). El auditor puede subir el
  riesgo; bajarlo reabre la conciliación.
- Estado de la conciliación: `borrador-corte` → `abierta` → `cerrada`.
- Solo queda `cerrada` cuando el resultado observable, las dependencias, los
  criterios y el alcance están acordados y no hay preguntas abiertas (o están
  diferidas a una etapa **nombrada**).

### 3. Genera la lista principal

Pídele: **"genera TAREAS.md"**.

- Skill: `generate-stage-tasks`. **Se niega** si la conciliación no está
  `cerrada`.
- Resultado: `TAREAS.md`, la **única** lista principal, con cada tarea trazada
  a su `CA-NN` y su método de verificación. La etapa pasa a `lista`.

### 4. Implementa

Pídele: **"implementa la etapa NN"**.

- Skill: `implement-stage`. **Se niega** sin lista principal válida.
- Resultado: ejecuta solo la lista aprobada y deja evidencia por tarea. La
  etapa pasa por `implementando` y queda `auditando` cuando todo su
  `Verificar:` propio da verde.

### 5. Audita

Pídele: **"audita la etapa NN"**.

- Skill: `audit-stage`. Intenta **refutar** el cumplimiento, no confirmarlo.
- Cada pasada registra `**Snapshot:**` (identidad del código auditado, vía
  `scripts/snapshot.py`) y `**Riesgo auditado:**`. Un `coincide` solo vale para
  ese snapshot: si el árbol cambió, se reaudita.
- Resultado: `AUDIT.md` con un veredicto:
  - `coincide` → la etapa se cierra (`cerrada`).
  - `no coincide` → se escribe `TAREAS-delta-NN.md` y se repiten los pasos
    4–5 **contra el mismo baseline**. Agotado el presupuesto de deltas, el
    ciclo se detiene en `necesita-decision`: reabrir la conciliación, aceptar
    el riesgo residual con owner o dejar la etapa bloqueada.
  - Si lo que cambió es el producto (intención, alcance o criterio) → se
    reabre la conciliación (vuelve al paso 2), **no** es un delta.

### Estados de referencia

| Conciliación | Etapa |
| ------------ | ----- |
| `borrador-corte` → `abierta` → `cerrada` | `borrador` → `conciliando` → `lista` → `implementando` → `auditando` → `cerrada` |

La conciliación y el trabajo activo se anotan por separado en el índice; una
etapa quedará `bloqueada` solo con una causa y un desbloqueador escritos. El
validador trata la etapa como cerrada solo cuando la celda **Estado** de su
fila lo dice. Una etapa no se considera cerrada si la última pasada de
auditoría no dice `coincide`; el cierre se refleja en el índice después de la
evidencia, nunca antes.

### Reglas de oro

- `identify-feature-stages` **no** crea `TAREAS.md`.
- `generate-stage-tasks` **no** genera tareas sin conciliación `cerrada`.
- `implement-stage` **no** ejecuta sin lista principal válida.
- `audit-stage` **no** cierra sin evidencia suficiente y no toca el baseline.
- El siguiente paso se lee con `next_step.py`; `necesita-decision` detiene el
  ciclo en vez de asumir un valor por defecto.
- Un `no coincide` se resuelve con un **delta**; un cambio de intención, alcance
  o criterio **reabre la conciliación**, no se maquilla como delta.

## Validación local

Desde la raíz del repositorio:

```bash
python3 skills/feature-stages/scripts/validate_skill_evals.py
python3 skills/feature-stages/scripts/test_next_step.py
python3 skills/feature-stages/scripts/test_snapshot.py
python3 skills/feature-stages/scripts/doctor.py \
  skills/feature-stages/evals/fixtures/transiciones
python3 skills/feature-stages/scripts/validate_stage.py \
  skills/feature-stages/evals/fixtures/valid-stage --strict
```

Todos los comandos deben terminar correctamente: el catálogo de evals, las
transiciones de `transiciones/` y la salud del árbol, además del contrato de la
etapa válida. `test_next_step.py` también cubre los negativos `sin-tareas`,
`abierta`, `inconsistente`, `dependencia`, `bloqueada`, `ambiguo`,
`cierre-pendiente`, `delta-huerfano`, `sin-conciliacion`,
`conciliacion-invalida`, `sin-principal`, `presupuesto-agotado`,
`presupuesto-excedido`, `presupuesto-excedido-coincide`, `huerfana` e
`indice-sin-tabla`; un
cambio de `next_step.py` o `doctor.py` que altere una transición o una regla
estructural sin actualizar su caso deja la suite roja. `test_snapshot.py` cubre
la identidad de auditoría: estable, sensible al código, insensible a la ruta
excluida y verificable con `validate_stage.py --repo`.

Estas dos fixtures también deben terminar correctamente: conciliación
`cerrada` con etapa `auditando`, y etapa `cerrada` con veredicto `coincide`.

```bash
python3 skills/feature-stages/scripts/validate_stage.py \
  skills/feature-stages/evals/fixtures/index-estado/03-activa --strict
python3 skills/feature-stages/scripts/validate_stage.py \
  skills/feature-stages/evals/fixtures/index-estado/05-hecha --strict
```

La fixture negativa `closed-without-task` debe fallar: prueba que el gate
rechaza una conciliación cerrada sin lista implementable. `index-estado/04-etapa`
también debe fallar: el índice marca **Estado** `cerrada` sin veredicto
`coincide`.

```bash
if python3 skills/feature-stages/scripts/validate_stage.py \
  skills/feature-stages/evals/fixtures/closed-without-task --strict; then
  echo 'La fixture negativa pasó: el gate está roto' >&2
  exit 1
fi
for fixture in inconsistente doctor-estructural huerfana; do
  if python3 skills/feature-stages/scripts/doctor.py \
    "skills/feature-stages/evals/fixtures/$fixture"; then
    echo "doctor aceptó $fixture: el gate está roto" >&2
    exit 1
  fi
done
if python3 skills/feature-stages/scripts/validate_stage.py \
  skills/feature-stages/evals/fixtures/index-estado/04-etapa --strict; then
  echo 'El índice cerrado pasó sin veredicto coincide: el gate está roto' >&2
  exit 1
fi
```

`ca-tipo` declara el tipo elegido (`[condición de salida]`,
`[invariante acumulado]`, `Salida de etapa`, `Invariante acumulada` y el
placeholder en orden inverso). Sin `--strict` solo avisa `CA-05`, que no
trae marcador. Con `--strict` ese aviso es error y el proceso falla.

`coincide-sin-snapshot`, `snapshot-de-pasada-anterior` y `riesgo-rebajado` deben
fallar: un veredicto `coincide` sin la identidad del código auditado, con el
snapshot de otra pasada, o con un riesgo menor al congelado, no cierra.
`riesgo-ausente` avisa sin `--strict` y falla con él.

```bash
for fixture in coincide-sin-snapshot snapshot-de-pasada-anterior riesgo-rebajado; do
  if python3 skills/feature-stages/scripts/validate_stage.py \
    "skills/feature-stages/evals/fixtures/$fixture" --strict; then
    echo "$fixture pasó: el gate está roto" >&2
    exit 1
  fi
done
python3 skills/feature-stages/scripts/validate_stage.py \
  skills/feature-stages/evals/fixtures/riesgo-ausente
if python3 skills/feature-stages/scripts/validate_stage.py \
  skills/feature-stages/evals/fixtures/riesgo-ausente --strict; then
  echo 'riesgo-ausente con --strict pasó: el gate está roto' >&2
  exit 1
fi
```

```bash
python3 skills/feature-stages/scripts/validate_stage.py \
  skills/feature-stages/evals/fixtures/ca-tipo
if python3 skills/feature-stages/scripts/validate_stage.py \
  skills/feature-stages/evals/fixtures/ca-tipo --strict; then
  echo 'ca-tipo con --strict pasó: el gate está roto' >&2
  exit 1
fi
```

También:

```bash
python3 -m py_compile skills/feature-stages/scripts/*.py
git diff --check
```

Estas verificaciones se ejecutan automáticamente en CI
(`.github/workflows/validate.yml`).

## Actualización, versionado y seguridad

- Usa [Keep a Changelog](CHANGELOG.md) y [SemVer](https://semver.org/lang/es/).
- Para actualizar, revisa las release notes y usa `npx skills update` o
  reinstala desde el tag/revisión que tu política permita.
- No publiques scripts no revisados, secretos, resultados locales ni archivos
  compilados. Inspecciona cualquier script antes de ejecutarlo.

## Cómo contribuir

Consulta [CONTRIBUTING.md](CONTRIBUTING.md). Cambios pequeños, sin reglas de
dominio, con evaluaciones actualizadas y validación local. El agente que
mantiene el repositorio sigue las reglas de [AGENTS.md](AGENTS.md).
