# YerroSprints

Paquete portable de seis [Agent Skills](https://cursor.com/docs/context/skills)
para llevar una *feature* desde el corte de especificación hasta la auditoría,
con límites claros entre fases y artefactos que se pueden revisar.

No es un framework ni despliega nada. No contiene reglas de dominio: el agente
ejecuta, y estas skills le dan estados, gates y trazabilidad.

## La idea

Partir una feature es fácil de hacer mal: se mezcla alcance con tareas, se
"cierra" sin evidencia o un defecto se disfraza de cambio de criterio.
YerroSprints impone un ciclo con **seis fases de responsabilidad única** y un
contrato común:

- Cada fase produce un artefacto concreto y auditable.
- Los artefactos son la fuente de verdad, no la conversación.
- Un cambio de **intención, alcance o criterio** reabre la conciliación.
- Un desvío contra un baseline acordado se corrige con un **delta**, nunca
  editando la feature para que "encaje".
- La evidencia se reproduce; la auditoría intenta **refutar**, no confirmar.
- El cierre lo aprueba una persona, no el agente.

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
gates, plantillas y evaluación, pero no reemplaza ninguna fase.

| Skill | Función |
| --- | --- |
| `identify-feature-stages` | Corta la especificación en resultados implementables y auditables. |
| `feature-stages` | Define estados, gates, plantillas, contrato y evaluación. |
| `conciliate-stage` | Cierra alcance, decisiones, criterios, riesgos y evidencia. |
| `generate-stage-tasks` | Genera la única lista principal, trazada a los criterios. |
| `implement-stage` | Ejecuta solo la lista aprobada y deja evidencia. |
| `audit-stage` | Intenta refutar el cumplimiento; cierra, bloquea o emite un delta. |

## Requisitos

- Un host con Agent Skills y un agente con shell y lectura/escritura de
  archivos (Cursor, Claude Code, Codex u otro).
- **Python 3** (solo stdlib) para los validadores y para cerrar con evidencia.
  Operar no requiere Python; **cerrar con evidencia sí**.
- **Node.js/npm** solo si instalas con `npx skills`.

## Instalación

### Con `npx skills`

```bash
npx skills add jeandybryan/yerro-sprints --list
npx skills add jeandybryan/yerro-sprints \
  --skill '*' \
  --agent cursor \
  --copy \
  --yes
```

Cambia `--agent cursor` por el host que uses. Verifica en la configuración de
Skills del host que aparezcan las seis.

### Fijar una versión

El CLI separa el repositorio del ref con `#`, no con `@`: el `@` selecciona una
skill (`owner/repo@skill`). Para instalar el árbol de un tag:

```bash
npx skills add 'jeandybryan/yerro-sprints#v0.5.1' \
  --skill '*' \
  --agent cursor \
  --copy \
  --yes
```

`skills-lock.json` graba `"ref": "v0.5.1"`, así que `npx skills update` sigue
ese tag y no salta a `main`. Para subir de versión, vuelve a ejecutar `add` con
el tag nuevo; el lock se reescribe. Sin `#<ref>` el lock queda sin ref y
`update` sigue `main`.

### Proyectos con pnpm

`npx` es `npm exec` y npm rechaza el `devEngines.packageManager` de un proyecto
pnpm (`EBADDEVENGINES`). Usa `pnpm dlx`:

```bash
pnpm dlx skills add jeandybryan/yerro-sprints --list
pnpm dlx skills add jeandybryan/yerro-sprints \
  --skill '*' \
  --agent cursor \
  --copy \
  --yes
```

Con tag, el mismo `#<ref>`: `pnpm dlx skills add
'jeandybryan/yerro-sprints#v0.5.1' ...`.

### Instalación manual

Copia `skills/` al directorio de skills del host. En Cursor puede ser
`.cursor/skills/` o `.agents/skills/` dentro del proyecto.

La instalación global es opcional y personal. No la uses como dependencia de CI
o de equipo: para trabajo compartido, instala a nivel proyecto y versiona el
resultado.

## Cómo usarlo en un proyecto

Trabaja en la raíz de una feature. La especificación es la fuente de verdad:

```text
<feature-root>/
  <SPEC>.md              # qué se quiere
  README.md              # índice de etapas y estado
  NN-slug/
    CONCILIACION.md      # alcance, decisiones, CA, riesgos, evidencia
    TAREAS.md            # lista principal (tras cerrar la conciliación)
    AUDIT.md             # veredicto por pasada, con evidencia
    TAREAS-delta-NN.md   # solo si la auditoría encuentra un hueco
  EXPRES.md              # registro opcional de cambios fuera de etapa
```

En los comandos, `<skills-root>` es la carpeta donde el host instaló las skills.

### 1. Corta la especificación

Pídele al agente: **"divide esta spec en etapas implementables"**.

- Skill: `identify-feature-stages`.
- Produce: `<feature-root>/README.md` con las etapas en `borrador` y, por etapa,
  un borrador de `CONCILIACION.md` en `borrador-corte`.
- **No** crea `TAREAS.md` ni código.

### 2. Concilia una etapa

Pídele: **"conciliemos la etapa NN"** (una a la vez).

- Skill: `conciliate-stage`.
- Produce: `CONCILIACION.md` con `Entra`/`No entra`, decisiones `S-NN`,
  criterios de aceptación `CA-NN`, riesgos y evidencia esperada.
- Al cerrar se congelan `**Riesgo:**` (`bajo`/`medio`/`alto`) y
  `**Presupuesto de deltas:**`, derivado del riesgo (`bajo → 2`,
  `medio → 1`, `alto → 1`). Un valor distinto exige
  `**Motivo del presupuesto:**`.
- También se acuerdan `**Suites de referencia:**` y
  `**Presupuesto no funcional:**` (latencia, memoria, tamaño, dependencias
  nuevas y rendimiento de la operación crítica).
- Solo queda `cerrada` cuando el resultado observable, las dependencias, los
  criterios y el alcance están acordados y no hay preguntas abiertas (o están
  diferidas a una etapa nombrada).

### 3. Genera la lista principal

Pídele: **"genera TAREAS.md"**.

- Skill: `generate-stage-tasks`. **Se niega** si la conciliación no está
  `cerrada`.
- Produce: `TAREAS.md`, la **única** lista principal. Cada tarea declara
  `CA-NN`, `**Archivos:**`, `Test-first:`, `Test:` y `Verificar:`.
- La etapa pasa a `lista`.

### 4. Implementa

Pídele: **"implementa la etapa NN"**.

- Skill: `implement-stage`. **Se niega** sin lista principal válida.
- Ejecuta solo la lista aprobada y deja evidencia por tarea.
- La etapa pasa por `implementando` y queda `auditando` cuando todo su
  `Verificar:` da verde.

### 5. Audita

Pídele: **"audita la etapa NN"**.

- Skill: `audit-stage`. Intenta **refutar** el cumplimiento.
- Cada pasada registra `**Snapshot:**` (identidad del código auditado) y
  `**Riesgo auditado:**`. Un `coincide` solo vale para ese snapshot: si el
  árbol cambió, se reaudita.
- El ledger exige `Sensibilidad`: la prueba de que el test pudo fallar
  (`revertir → rojo → restaurar`, un mutante o una regresión contra `HEAD`).
  Un ledger que solo dice que el test pasó no cierra.
- El cierre exige dos veredictos: `**Veredicto:** coincide` y
  `**Veredicto (calidad):** aceptable`.
- Resultado:
  - `coincide` → la etapa se cierra (`cerrada`).
  - `no coincide` → se escribe `TAREAS-delta-NN.md` y se repiten los pasos
    4–5 contra el mismo baseline. Agotado el presupuesto, el ciclo se detiene
    en `necesita-decision`.
  - Si cambió el producto (intención, alcance o criterio) → se reabre la
    conciliación (paso 2), **no** es un delta.

### Estados

| Conciliación | Etapa |
| --- | --- |
| `borrador-corte` → `abierta` → `cerrada` | `borrador` → `conciliando` → `lista` → `implementando` → `auditando` → `cerrada` |

Una etapa queda `bloqueada` solo con causa, desbloqueador, evidencia y próxima
revisión escritos. El cierre se refleja en el índice después de la evidencia,
nunca antes.

## ¿En qué estado estoy?

No lo recuerdes: léelo de los artefactos.

```bash
python3 <skills-root>/feature-stages/scripts/next_step.py <feature-root>
python3 <skills-root>/feature-stages/scripts/next_step.py <feature-root> --reconcile
python3 <skills-root>/feature-stages/scripts/doctor.py <feature-root>
python3 <skills-root>/feature-stages/scripts/tasks.py pending <stage>
python3 <skills-root>/feature-stages/scripts/preflight.py <feature-root> --fase <skill>
```

- `next_step.py` devuelve un estado público (`trabajando`, `verificando`,
  `declarada-cerrada`, `necesita-decision`), la única skill siguiente y los
  bloqueos con su resolución. `--json` para máquinas, `--stage NN-slug` para una
  etapa concreta, `--check` para CI.
- `--reconcile` resume lo que falta y los commits que tocan la etapa. Es lo que
  se ejecuta al retomar trabajo tras una compactación de contexto, en vez de
  re-ejecutar tareas ya hechas.
- `doctor.py` informa incoherencias entre el índice y los artefactos. Su `OK`
  dice que son coherentes, no que cumplen el contrato.
- `tasks.py pending` dice qué IDs siguen sin marcar, sin releer las listas.
- `preflight.py` lista qué leer y qué omitir en cada fase, con el motivo.

`declarada-cerrada` significa que el índice y la auditoría declaran la etapa
cerrada, no que los artefactos cumplan el contrato. Para eso está
`validate_stage.py`.

## Evidencia y cierre

```bash
# Ejecuta un comando y devuelve la fila del ledger con exit y firma
python3 <skills-root>/feature-stages/scripts/evidence.py run --label E-01 -- <comando>

# Reejecuta lo que la auditoría declaró; una firma que no se reproduce es evidencia inventada
python3 <skills-root>/feature-stages/scripts/evidence.py verify <stage>/AUDIT.md

# Identidad del árbol auditado
python3 <skills-root>/feature-stages/scripts/snapshot.py <repo> \
  --exclude <feature-root> --exclude .yerro/approvals.yml

# Contrato de la etapa
python3 <skills-root>/feature-stages/scripts/validate_stage.py <stage>

# Cierre cruzado: snapshot vigente, aprobación humana y alcance del diff
python3 <skills-root>/feature-stages/scripts/validate_stage.py <stage> --repo <repo>
```

Sin `--repo`, el validador solo mira la forma de los artefactos. Un `coincide`
que no pasó el cierre cruzado no cierra.

### Aprobación humana

El cierre de una etapa requiere una entrada en `.yerro/approvals.yml`, un
archivo versionado que **edita la persona**. Hay dos firmas:

```yaml
- etapa: 01-export
  aprobado-por: Ana Ruiz
  fecha: 2026-10-22
  base: <sha256 del baseline> # firma de plan: al cerrar la conciliación
  alcance: tree=<sha> # firma del árbol, al auditar; completo o en forma corta
```

- **La firma de plan** (`base=`) acepta el baseline —riesgo, alcance,
criterios, presupuesto— al cerrar la conciliación. Se pide **siempre**, en todo
riesgo, y editar el documento después de firmar invalida la firma. Cerrar o
reabrir la etapa no: la línea `**Estado:**` no es baseline.
- **La firma del árbol** (`alcance: tree=`) acepta el código auditado. En
**riesgo bajo no se pide**: la firma de plan basta para cerrar y el ciclo no se
detiene dos veces. En **riesgo medio o alto** sigue siendo obligatoria, en la
misma entrada o en otra.
- Una entrada con `base=` y sin `alcance` no cubre ningún árbol.

Sin las firmas que el riesgo exige, la etapa no cierra. El agente nunca escribe
ese archivo: una firma que el agente puede teclear no es una firma.

No hace falta escribir el bloque de memoria ni copiar el sha: estos comandos lo
imprimen con las claves exactas (el del árbol necesita la pasada ya grabada):

```bash
python3 <skills-root>/feature-stages/scripts/approvals.py <repo> --suggest <stage> --plan --by "Tu Nombre"
python3 <skills-root>/feature-stages/scripts/approvals.py <repo> --suggest <stage> --by "Tu Nombre"
```

Copia la salida y pégala en `.yerro/approvals.yml`. Detecta además el campo
escrito con guion bajo (`aprobado_por`), que antes se leía como una clave
desconocida.

## Vía exprés

No todo merece el ciclo completo. Antes de abrir etapa, comprueba la frontera:

```bash
python3 <skills-root>/feature-stages/scripts/expres.py <repo> [--base REF]
```

Cabe fuera del ciclo solo si cumple **todo**: un archivo de producción, ≤ 20
líneas de producción (las pruebas no cuentan), ninguna ruta excluida
(migraciones, esquemas, auth/seguridad, contratos compartidos, manifiestos de
dependencias) y, a confirmación humana, sin CA nuevo y sin cambio de interfaz
pública.

Si cabe, anota en `EXPRES.md` la frontera, el comando, el resultado con su exit
y quién confirmó las dos condiciones que el diff no puede mostrar. `doctor.py`
rechaza una fila incompleta, la acumulación de tres cambios sobre el mismo CA o
archivo, un cambio exprés sobre un archivo de una etapa abierta y una promoción
a una etapa inexistente.

Si el script dice `no cabe`, o no puedes afirmar las dos confirmaciones, **abre
etapa**: la vía exprés no tiene override.

## Reglas de oro

- `identify-feature-stages` **no** crea `TAREAS.md`.
- `generate-stage-tasks` **no** genera tareas sin conciliación `cerrada`.
- `implement-stage` **no** ejecuta sin lista principal válida.
- `audit-stage` **no** cierra sin evidencia suficiente y no toca el baseline.
- El siguiente paso se lee con `next_step.py`; `necesita-decision` detiene el
  ciclo en vez de asumir un valor por defecto.
- Un `no coincide` se resuelve con un **delta**; un cambio de intención,
  alcance o criterio **reabre la conciliación**.
- El riesgo no se rebaja para evitar reauditar. Subirlo es un hallazgo;
  bajarlo reabre.
- El presupuesto de deltas no se amplía para que una etapa cierre.
- La aprobación de cierre la escribe la persona, no el agente.

## Actualización y versionado

- [Keep a Changelog](CHANGELOG.md) y [SemVer](https://semver.org/lang/es/).
- Última versión: [`v0.5.1`](https://github.com/jeandybryan/yerro-sprints/releases/tag/v0.5.1).
  El comando de instalación fijado al tag está en «Fijar una versión».
- Para actualizar, revisa las release notes y usa `npx skills update` o
  reinstala desde el tag/revisión que tu política permita.
- No publiques scripts no revisados, secretos, resultados locales ni archivos
  compilados. Inspecciona cualquier script antes de ejecutarlo.

## Soporte, implantación y consultoría

YerroSprints se publica bajo licencia MIT. Quien lo necesite puede pedir ayuda
de pago para tres trabajos: implantar el paquete en su repositorio, adaptarlo
a su CI y dar talleres de formación a su equipo. El alcance se acuerda en cada
caso.

El contacto es un mensaje directo en X a
[jeandybryan](https://x.com/jeandybryan), o una issue con la etiqueta
`consultoria` mediante la plantilla
[Solicitud de consultoría](https://github.com/jeandybryan/yerro-sprints/issues/new?template=consultoria.yml&labels=consultoria).

**Apoya el proyecto:** un mensaje directo en X a
[jeandybryan](https://x.com/jeandybryan) o una issue con la etiqueta
`consultoria`.

## Gobernanza y contribución

Las reglas de mantenimiento están en [GOVERNANCE.md](GOVERNANCE.md) y la lista
de salida en [RELEASE_CHECKLIST.md](RELEASE_CHECKLIST.md). Licencia MIT (ver
[LICENSE](LICENSE)), canal canónico en este repositorio, tags `vX.Y.Z` y hosts
soportados por capacidad.

Para contribuir, lee [CONTRIBUTING.md](CONTRIBUTING.md): cambios pequeños, sin
reglas de dominio, con fixture o caso nuevo y validación local. El agente que
mantiene el repositorio sigue [AGENTS.md](AGENTS.md).
