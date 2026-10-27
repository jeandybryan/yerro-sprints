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

## Gobernanza y release

Las reglas de mantenimiento están en [GOVERNANCE.md](GOVERNANCE.md) y la
lista de salida en [RELEASE_CHECKLIST.md](RELEASE_CHECKLIST.md). Las skills
operativas apuntan a referencias normativas para mantener el contexto corto
sin duplicar gates. Las decisiones de release están acordadas: licencia MIT
(ver [LICENSE](LICENSE)), canal canónico en este repositorio, tags
`vX.Y.Z`, hosts por capacidad (agente con shell y lectura/escritura de
archivos) y un owner único de mantenimiento y aprobación.

## Requisitos

- Un host compatible con Agent Skills (Cursor, Claude Code, Codex u otro).
- **Python 3** (solo stdlib) para los validadores y para cerrar una etapa con
  evidencia ejecutable. **Operar no requiere Python; cerrar con evidencia sí:**
  `evidence.py` ejecuta los comandos citados y firma lo observado, y
  `validate_stage.py` comprueba el oráculo y la sensibilidad del ledger.
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
  EXPRES.md            # registro opcional de cambios que no abren etapa
```

### ¿En qué estado estoy?

Antes de elegir un paso, léelo desde los artefactos en vez de recordarlo:

```bash
python3 <skills-root>/feature-stages/scripts/next_step.py <feature-root>
python3 <skills-root>/feature-stages/scripts/doctor.py <feature-root>
python3 <skills-root>/feature-stages/scripts/tasks.py pending <stage>
```

`next_step.py` devuelve un estado público (`trabajando`, `verificando`,
`declarada-cerrada`, `necesita-decision`), la única skill siguiente y los
bloqueos con su resolución. `declarada-cerrada` significa que el índice y la
auditoría declaran la etapa cerrada, no que los artefactos cumplan el contrato:
para eso está `validate_stage.py`. `--json` para máquinas, `--stage NN-slug`
para una etapa concreta y `--check` para CI. `doctor.py` informa incoherencias
entre el índice y los artefactos; su `OK` dice que son coherentes, no que
cumplen el contrato. Ninguno de los dos sustituye un gate: el contrato lo juzga
`validate_stage.py`.

`tasks.py pending <stage>` dice qué IDs de tarea siguen sin marcar en
`TAREAS.md` y sus deltas, sin releer las listas; `--json` para máquinas. Avisa
si `**Estado:**` declara la lista `implementada`/`auditada` con una tarea sin
marcar. Proyecta el checkbox y no decide nada: los huecos del contrato siguen
siendo las líneas `ERROR:` de `validate_stage.py`.

### Evidencia ejecutable

```bash
python3 <skills-root>/feature-stages/scripts/evidence.py run --label E-01 -- <comando>
python3 <skills-root>/feature-stages/scripts/evidence.py verify <stage>/AUDIT.md
```

`run` ejecuta el comando y devuelve la fila del ledger con `exit=` y `firma=` del
output normalizado. `verify` reejecuta lo que la auditoría declaró: si la firma
no se reproduce, la evidencia es inventada y el criterio queda `no verificado`.

### ¿Esto necesita una etapa? La vía exprés

No todo merece el ciclo completo. Antes de abrir etapa, comprueba la frontera:

```bash
python3 <skills-root>/feature-stages/scripts/expres.py <repo> [--base REF]
```

Un cambio cabe fuera del ciclo solo si cumple **todo**: 1 archivo de
producción, ≤ 20 líneas de producción (las pruebas no cuentan; los archivos
nuevos sin trackear sí cuentan), ninguna ruta excluida (migraciones, esquemas,
auth/seguridad, contratos compartidos, manifiestos de dependencias) y, a
confirmación humana, sin criterio de aceptación nuevo y sin cambio de interfaz
pública. Si el script dice `no cabe`, o no puedes afirmar las dos
confirmaciones, **abre etapa**: la vía exprés no tiene override.

Si cabe, anota una línea en `EXPRES.md` con el porqué cabía y cómo se verificó.
Es un registro, no un gate: `next_step.py` no lo lee, no cambia ninguna
transición y no bloquea ninguna etapa. `doctor.py` avisa cuando tres cambios se
acumulan sobre el mismo CA o el mismo archivo; esa acumulación significa que el
corte estaba mal: promueve a etapa y marca la línea `→ NN-slug`.

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
  `**Presupuesto de deltas:**`, que se **deriva del riesgo** (`bajo → 2`,
  `medio → 1`, `alto → 1`). Un valor distinto exige
  `**Motivo del presupuesto:**`; sin motivo rige el derivado. El auditor puede
  subir el riesgo; bajarlo reabre la conciliación.
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
  ese snapshot: si el árbol cambió, se reaudita. El snapshot excluye el árbol
  de la feature y `.yerro/approvals.yml`; con menos exclusiones la identidad
  no coincide aunque el código sea el mismo.
- El ledger exige **`Sensibilidad`**: la prueba de que el test pudo fallar
 (`revertir → rojo → restaurar`, un mutante que produce rojo o una regresión
 contra `HEAD`). Un ledger que solo dice que el test pasó no cierra.
 `Test:` debe invocar un runner; `true`, `echo` o `sleep` se rechazan.
- El **riesgo fija el fondo de la evidencia**: por encima de `bajo` el ledger
 declara un caso límite o un negativo demostrado; en `alto`, cada CA crítico
 registra un `mutante:` (o fallo inyectado) con resultado rojo. Un `coincide`
 que baja el criterio más exigente declara `**Cruza riesgo:** sí — …` y
 `**Motivo del presupuesto:** …`, o no cierra.
- El cierre requiere una **aprobación humana** en `.yerro/approvals.yml`, un
 archivo versionado que edita la persona: sin entrada que cubra la etapa y el
 snapshot, la etapa no cierra. El agente nunca escribe ese archivo. El cierre
 se comprueba con `validate_stage.py <etapa> --repo <repo>`: sin `--repo` el
 validador solo mira la forma de los artefactos.
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
- La vía exprés no tiene override: si `expres.py` dice `no cabe`, o hay un CA
  nuevo o un cambio de interfaz pública, se abre etapa.
- Un `no coincide` se resuelve con un **delta**; un cambio de intención, alcance
  o criterio **reabre la conciliación**, no se maquilla como delta.

## Validación local

Desde la raíz del repositorio:

```bash
python3 skills/feature-stages/scripts/validate_skill_evals.py
python3 skills/feature-stages/scripts/test_skill_evals.py
python3 skills/feature-stages/scripts/test_next_step.py
python3 skills/feature-stages/scripts/test_snapshot.py
python3 skills/feature-stages/scripts/test_diff_scope.py
python3 skills/feature-stages/scripts/test_evidence.py
python3 skills/feature-stages/scripts/test_expres.py
python3 skills/feature-stages/scripts/test_tasks.py
python3 skills/feature-stages/scripts/doctor.py \
  skills/feature-stages/evals/fixtures/transiciones
python3 skills/feature-stages/scripts/validate_stage.py \
  skills/feature-stages/evals/fixtures/valid-stage
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
excluida y verificable con `validate_stage.py --repo`. `test_expres.py` cubre
la frontera exprés: un cambio pequeño cabe; más archivos, más líneas, una ruta
excluida o un archivo nuevo sin trackear no caben; las pruebas no consumen
presupuesto.

Estas dos fixtures también deben terminar correctamente: conciliación
`cerrada` con etapa `auditando`, y etapa `cerrada` con veredicto `coincide`.

```bash
python3 skills/feature-stages/scripts/validate_stage.py \
  skills/feature-stages/evals/fixtures/index-estado/03-activa
python3 skills/feature-stages/scripts/validate_stage.py \
  skills/feature-stages/evals/fixtures/index-estado/05-hecha
```

La fixture negativa `closed-without-task` debe fallar: prueba que el gate
rechaza una conciliación cerrada sin lista implementable. `index-estado/04-etapa`
también debe fallar: el índice marca **Estado** `cerrada` sin veredicto
`coincide`.

```bash
if python3 skills/feature-stages/scripts/validate_stage.py \
  skills/feature-stages/evals/fixtures/closed-without-task ; then
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
  skills/feature-stages/evals/fixtures/index-estado/04-etapa ; then
  echo 'El índice cerrado pasó sin veredicto coincide: el gate está roto' >&2
  exit 1
fi
```

`ca-tipo` declara el tipo elegido (`[condición de salida]`,
`[invariante acumulado]`, `Salida de etapa`, `Invariante acumulada` y el
placeholder en orden inverso). El CA sin marcador (`CA-05`) es error: hay **un**
contrato y **un** modo, y no existe `--strict`. Por lo mismo, `riesgo-ausente`
falla siempre.

`coincide-sin-snapshot`, `snapshot-de-pasada-anterior` y `riesgo-rebajado` deben
fallar: un veredicto `coincide` sin la identidad del código auditado, con el
snapshot de otra pasada, o con un riesgo menor al congelado, no cierra.
`cierre-sin-aprobacion` (criterio rebajado sin motivo), `riesgo-alto-sin-mutacion`
(riesgo alto sin fallo inyectado) y `riesgo-alto-presupuesto-sin-motivo`
(presupuesto sobrescrito sin causa) también deben fallar; su contrario
`riesgo-cruzado-con-motivo` debe pasar.

```bash
for fixture in coincide-sin-snapshot snapshot-de-pasada-anterior riesgo-rebajado \
  cierre-sin-aprobacion riesgo-alto-sin-mutacion \
  riesgo-alto-presupuesto-sin-motivo ; do
  if python3 skills/feature-stages/scripts/validate_stage.py \
    "skills/feature-stages/evals/fixtures/$fixture" ; then
    echo "$fixture pasó: el gate está roto" >&2
    exit 1
  fi
done
if python3 skills/feature-stages/scripts/validate_stage.py \
  skills/feature-stages/evals/fixtures/riesgo-ausente ; then
  echo 'riesgo-ausente pasó sin modo legado: el gate está roto' >&2
  exit 1
fi
if python3 skills/feature-stages/scripts/validate_stage.py \
  skills/feature-stages/evals/fixtures/ca-tipo ; then
  echo 'ca-tipo pasó sin modo legado: el gate está roto' >&2
  exit 1
fi
python3 skills/feature-stages/scripts/validate_stage.py \
  skills/feature-stages/evals/fixtures/riesgo-cruzado-con-motivo
```

`test_snapshot.py` comprueba además el gate de aprobación: sin
`.yerro/approvals.yml`, con una entrada fuera de alcance o con el archivo
mal formado, la etapa no cierra.

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
