# Changelog

Todos los cambios notables de este proyecto se documentan en este archivo.

El formato se basa en [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/)
y el proyecto adhiere a [Semantic Versioning](https://semver.org/lang/es/).

## [Unreleased]

### Corregido

- **El presupuesto agotado distingue «usado» de «excedido».** La fixture
  `presupuesto-agotado` tenía dos deltas con riesgo `medio`, cuyo presupuesto
  derivado es 1, así que ejercitaba la rama de exceso igual que
  `presupuesto-excedido`; el mensaje «N delta(s) usados de M» no lo producía
  ninguna fixture. `deltas-and-closure.md` decía «dos por defecto», que
  contradice la derivación por riesgo. La fixture usa ahora el presupuesto justo
  y `test_next_step.py` comprueba que los dos mensajes no se confunden: uno
  prohíbe otro delta, el otro avisa de que ya se escribió de más.
- **El skill que cierra invoca el cierre cruzado.** `audit-stage` ejecutaba
  `validate_stage.py <stage>` sin `--repo`, y ese modo solo juzga la forma: el
  snapshot, la aprobación humana y el alcance del diff no se comprobaban en el
  procedimiento que escribe el `coincide`. La etapa podía cerrarse con un
  snapshot obsoleto y sin firma mientras la skill decía «cerrar». El
  procedimiento ahora ejecuta el cierre con `--repo` después de escribir el
  veredicto, y `validate_skill_evals.py` falla si el skill de auditoría deja de
  nombrar ese comando. Comprobado quitando el comando del `SKILL.md`: el
  catálogo falla nombrándolo.
- **El snapshot de la pasada excluye también `.yerro/approvals.yml`.** Al
  verificar, `validate_stage.py --repo` añadía esa exclusión a la lista grabada,
  pero los cinco sitios que documentaban el comando solo excluían el árbol de la
  feature. El `**Snapshot:**` de una pasada real nunca coincidía, aunque el
  árbol fuera idéntico, y el error mandaba a «reauditar»: repetir la pasada con
  el mismo comando fallaba igual, así que un cierre correcto no tenía salida.
  El comando canónico lleva ahora las dos exclusiones, y el error distingue un
  árbol distinto (reauditar) de una lista de exclusiones corta (volver a tomar
  el snapshot, sin reauditar). Casos nuevos en `test_snapshot.py`; con el
  mensaje anterior, fallan.
- **El gate de alcance ya no se salta con `git commit` (B-44).** `validate_stage.py
  --repo` medía el diff contra `HEAD`; un agente que commiteaba su trabajo dejaba
  el diff vacío y un archivo que ninguna tarea declara pasaba el cierre. La base
  es ahora el commit que abrió la etapa, derivado de la historia de su árbol, y
  `diff_scope.py` y el cierre comparten `scope_base()`. Si la etapa no está
  commiteada no hay base y el cierre avisa de que solo ve lo que sigue sin
  commitear. Casos nuevos en `test_diff_scope.py` y `test_snapshot.py`; con la
  base anterior, ambos fallan.

### Añadido

- **Oráculo mínimo en `Test:`.** `validate_stage.py` rechaza el trivio
  (`true`, `echo`, `sleep`, `:`, `cat`, `bash -c true`, `python -c pass`) y
  acepta los runners que la conciliación declare en `**Runners:**`. Si no hay
  `**Runners:**`, un comando fuera de la lista negra solo avisa.
- **`Sensibilidad` obligatoria en el ledger.** Una pasada `coincide` exige la
  columna `Sensibilidad` con contenido; una celda `no demostrada` deja el
  criterio en `no verificado`. Un ledger que solo prueba que el test pasó no
  cierra.
- `references/evidence.md`: define oráculo, los tres métodos de sensibilidad
  (revertir → rojo → restaurar; mutante; regresión contra `HEAD`), cuándo se
  exige y por qué no se negocia por riesgo.
- `scripts/evidence.py` (`run`, `verify`) y `scripts/test_evidence.py`: la
  evidencia citada para cerrar lleva `exit=` y `firma=` del output
  normalizado; `verify` reejecuta y detecta una transcripción inventada. La
  firma es insensible a timestamps, puertos y rutas temporales.
- Fixtures `test-decorativo` y `sin-sensibilidad`, y casos retenidos `S19` y
  `S20` en `EVALUATION.md`.
- `test_next_step.py` recorre todas las fixtures y falla si el validador se cae
  en vez de juzgar.

- **Alcance comprobado en el diff (B-27).** Cada tarea declara `**Archivos:**`
  con las rutas que produce; `scripts/diff_scope.py <etapa> --repo <repo>`
  compara lo que git ve cambiado contra lo declarado y `validate_stage.py
  <etapa> --repo` aplica el mismo cruce al cerrar. Un archivo que ninguna tarea
  declara es **alcance nuevo** y abre `necesita-decision`, aunque sea
  reversible: un refactor «de paso» también es alcance. Una ruta declarada que
  no cambió solo avisa, porque juzgar si la tarea se cumplió es cierre, no
  alcance (B-29). La evidencia de la etapa y `.yerro/` nunca cuentan como
  código, con la misma exclusión que el snapshot.
- `scripts/test_diff_scope.py`: repositorios git temporales para las dos
  direcciones del cruce, archivos sin trackear, `--base` inexistente y una
  tarea sin migrar. Fixture `cambio-fuera-de-alcance`.

- **Rulings registrados con coste (B-25).** Un `Ruling:` en `TAREAS.md` exige
  las tres partes (`<qué> — <por qué> — <qué cuesta>`); el validador rechaza
  un registro de dos partes. Antes, `implement-stage` decía «si es ambiguo,
  para y pregunta»: el Modelo C sustituye esa parada por decidir, registrar y
  seguir, y el coste es lo que permite al auditor evaluar la decisión. Se
  aceptan `—`, `--` y `–` como separador.
- **Sujetos a revisión resueltos por ID (B-26).** Un
  `**Sujeto a revisión R1:**` (ruling de categoría 2: observable, reversible,
  sin cambio de alcance) obliga a `AUDIT.md` a traer `### Rulings revisados`
  con `- aceptado R1` o `- hallazgo R1`. El cruce es por identificador: contar
  resoluciones dejaba que dos `aceptado` taparan una marca sin leer. Una marca
  sin ID o un ID que apunta a otro sujeto rompe el cierre. Fixtures
  `ruling-sujeto-sin-id` y `ruling-sujeto-id-cruzado`.
- Fixtures `ruling-sin-coste` y `ruling-categoria-2-sin-revision` (negativas),
  `ruling-categoria-1` y `ruling-categoria-2-revisado` (positivas), y casos
  retenidos `S24` y `S25` en `EVALUATION.md`.
- **Interfaces entre tareas (P17).** En una etapa con más de una tarea, cada
  tarea declara `Interfaces:` con `Consume:` y `Produce:`; `Consume: ninguna`
  es una respuesta válida. Una etapa de una sola tarea no lo necesita. Antes,
  quien ejecutaba `T2` tenía que adivinar la firma que dejó `T1`.
- **Casos conductuales de decisión e interfaces (S28, S29).** `ruling-y-parada`
 pone en la misma tarea una ambigüedad de categoría 2 y una de categoría 3:
 el agente acierta si decide la primera y para en la segunda. Un agente que
 para por todo no entrega; uno que decide todo se inventa alcance.
 `interfaces-cruzadas` tiene dos tareas cuyas firmas no encajan (`Consume:` de
 `T2` no es lo que `Produce:` de `T1`). Ambas fixtures pasan el validador a
 propósito: lo que miden no es una marca ausente sino una lectura que nadie
 hizo. Los casos viven en `evals/cases/` y se evalúan por sesión.
- **`validate_skill_evals.py` rechaza una evaluación sobre una fixture
 inexistente.** Antes, una `files:` con un nombre equivocado se materializaba
 como nada y se puntuaba la conversación. `test_skill_evals.py` lo prueba
 borrando una fixture en una copia (10 comprobaciones).
- **`preflight.py`: el contexto de una fase se calcula (P11, P14).** Dada una
 etapa y una fase —deducida de `next_step.py` si no se pide— emite en orden los
 archivos que hay que leer con sus líneas, todo lo que **no** se debe leer con
 su motivo (etapas vecinas, documentos del paquete que no aplican, artefactos
 de otra fase) y una estimación de tokens que declara su margen.
 Tres reglas: una fase no reconocida prepara la etapa completa en vez de
 recortar; ningún recorte es silencioso; las líneas son la medida y los tokens
 son información (B-15).
- **`--check` es el único modo que falla, y solo con presupuesto declarado.**
 Sin `**Presupuesto de contexto:**` en la conciliación el script informa; con
 él, `--check` devuelve error al excederse. El número no se inventa: Q9 sigue
 esperando datos de uso, así que hoy ninguna etapa lo declara.
- `test_preflight.py` (18 comprobaciones), casos retenidos S30 y S31, y
 `preflight.py` citado en el contrato y en las cuatro skills de fase.
- **Fixtures migradas a `**Archivos:**`.** Las 58 listas de
 `evals/fixtures/` declaran ahora los archivos que produce cada tarea, así que
 `--repo` puede comprobar el alcance en todas ellas y no solo en la retenida.
 El veredicto de cada etapa se comparó antes y después de la migración y no
 cambió: es una migración, no un cambio de contrato.
- Fixtures `interfaces-presentes` (pasa) e `interfaces-ausentes` (falla), más
  el caso retenido `S26`.
- **Prueba y revisión como dos ejes (P22).** Test-first, sensibilidad y suite
  de referencia se exigen siempre; el riesgo solo cambia la profundidad de la
  revisión. Fixture `riesgo-bajo-sin-test-first` (falla) y
  `riesgo-bajo-con-test-first-sin-revision-independiente` (pasa); caso `S27`.

- **Aprobación humana fuera del artefacto.** `scripts/approvals.py` lee
`.yerro/approvals.yml` (archivo versionado que edita la persona);
`validate_stage.py <etapa> --repo <repo>` exige una entrada que cubra la etapa
y el snapshot para cerrar. `AUDIT.md` no lleva `**Aprobado por:**`. `.yerro/`
se excluye del snapshot para que firmar no invalide la pasada que firma.
- **El riesgo fija el fondo de la evidencia.** La sensibilidad se exige
siempre; por encima de `bajo` el ledger declara un caso límite o un negativo
demostrado, y en `alto` cada CA crítico registra `mutante:` (o fallo inyectado)
con resultado rojo (B-35: se exige ver el rojo, no una herramienta).
- **El mutante se juzga por su resultado, no por la palabra.** `mutante: X →
verde` (el mutante sobrevivió), `→ rojo esperado` (una predicción) y `mutante:
X` sin resultado no cumplen; un verde en un CA crítico no lo compensa un rojo
en otro. Antes, escribir la palabra `mutante` satisfacía el gate aunque el
resultado declarado fuera `verde`.
- Fixtures `riesgo-alto-mutante-verde` y `riesgo-alto-mutante-esperado`, ambas
negativas, más README para las seis fixtures de roles y riesgo.
- **Presupuesto de deltas derivado del riesgo** (`bajo → 2`, `medio → 1`,
`alto → 1`) en `validate_stage.py` y `next_step.py`. Un valor distinto exige
`**Motivo del presupuesto:**`; sin él rige el derivado. `**Cruza riesgo:** sí`
en una pasada `coincide` también exige el motivo, o la etapa no cierra.
- **Aviso de rulings (B-33).** `doctor.py` advierte cuando una tarea acumula
más de tres `Ruling:` y apunta a `generate-stage-tasks`, sin bloquear. También
avisa, sin bloquear, de una etapa no cerrada cuyas tareas no declaran
`**Archivos:**` (migración pendiente).
- Fixtures `cierre-sin-aprobacion`, `riesgo-alto-sin-mutacion`,
`riesgo-alto-presupuesto-sin-motivo`, el positivo `riesgo-cruzado-con-motivo`,
`rulings-excesivos` y `rulings-aceptados`; casos retenidos `S21`–`S23` en
`EVALUATION.md`.

### Cambiado

- `templates/TAREAS.md` exige `**Archivos:**` bajo cada tarea, derivado del CA y
  nunca del diff ya producido (B-28).
- `implement-stage` gana la sección **Rulings — decide and record**: la
  categoría se decide por lo que cambia, no por la duda; solo la categoría 3 y
  las paradas incondicionales reabren la conciliación.
- `templates/AUDIT.md` gana `### Rulings revisados`; `audit-stage` no cierra con
  una marca sin resolver, y `references/decision-and-questions.md` separa la
  decisión de baseline (`S-NN`) del ruling de ejecución.
- El ledger de `AUDIT.md` gana la columna `Sensibilidad`; `TAREAS.md` gana
  `Sensibilidad:` bajo `Test:`; `CONCILIACION.md` gana `**Runners:**`
  opcional.
- El README declara la promesa real: **operar no requiere Python; cerrar con
  evidencia sí**.
- El ledger de `AUDIT.md` gana `**Deltas:**` y `**Cruza riesgo:**`;
  `CONCILIACION.md` gana `**Motivo del presupuesto:**`.
- `test_snapshot.py` comprueba el gate de aprobación: sin
  `.yerro/approvals.yml`, con una entrada fuera de alcance o con el archivo mal
  formado, la etapa no cierra.

### Corregido

- `templates/README.md` vuelve a ser la plantilla del índice de la feature. El catálogo de plantillas queda en `templates.md`.

- `generate-stage-tasks` ya no pide ejecutar el validador estructural antes de
  escribir `TAREAS.md`: con la conciliación cerrada y sin lista, el contrato
  falla por diseño. Antes de escribir se confirma la transición con
  `next_step.py`; el validador se ejecuta después.
- El validador reconoce el tipo de un CA cuando la línea elige una opción
  (`[condición de salida]`, `[invariante acumulado]`) o lo declara en prosa
  (`Salida de etapa`, `Invariante acumulada`). El placeholder con las dos
  opciones sigue valiendo. Una línea sin esos marcadores sigue avisando.
- El validador del índice marca una etapa como cerrada solo si la celda
  **Estado** de su fila contiene `cerrada`. La conciliación puede estar
  `cerrada` mientras la etapa sigue en `lista`, `implementando` o `auditando`.
- La fila se identifica por el enlace de **Carpeta** (`](NN-slug/`), así una
  mención del nombre en **Trabajo activo** de otra fila no cuenta.

### Añadido

- Glosario de los campos canónicos (`Estado`, `Origen`, `Riesgo`, `Test-first`, `Test`, `Verificar`, `Snapshot`, `Trazabilidad`, `Veredicto`, `E-NN`) en el contrato transversal.
- `doctor.py` rechaza una etapa `lista` o posterior cuya conciliación no está `cerrada`. La fixture `handoff-invalido/` cubre tareas prematuras, tareas sin prueba, auditoría incompleta, cierre sin `coincide` y ese estado incompatible.
- `test_skill_evals.py` comprueba que un enlace roto, un comando inexistente, un gate ausente o una activación ambigua dejan el catálogo en rojo.

- Refactor documental: `feature-stages/SKILL.md` y `audit-stage/SKILL.md` quedan como guías operativas; las reglas detalladas viven en referencias enlazadas y el catálogo verifica que existan.

- Gobernanza del paquete en `GOVERNANCE.md` y checklist reproducible de release en `RELEASE_CHECKLIST.md`. Las decisiones de licencia, distribución, tags, hosts y owner quedan explícitamente pendientes hasta ser acordadas.

- Trazabilidad ejecutable con decisiones `S-NN`, `Origen: S-NN`, `Test-first:` y `Test:` en tareas, y `**Trazabilidad:**` en auditorías.
- Nuevas fixtures negativas para decisión origen, test-first y trazabilidad de evidencia; `validate_stage.py` las rechaza.


- Contrato ejecutable de solo lectura: `next_step.py` lee los artefactos y
  devuelve el estado público (`trabajando`, `verificando`, `listo`,
  `necesita-decision`), la única skill siguiente y los bloqueos con su
  resolución. `doctor.py` comprueba la coherencia entre el índice y los
  artefactos. Ambos aceptan `--json`; `next_step.py` acepta `--stage` y
  `--check` para CI.
- Fixtures de transición (`transiciones/`) y negativas (`sin-tareas`,
  `abierta`, `inconsistente`, `dependencia`, `bloqueada`, `ambiguo`,
  `cierre-pendiente`, `delta-huerfano`, `sin-conciliacion`,
  `conciliacion-invalida`, `sin-principal`) con `test_next_step.py`, más pasos
  de CI que verifican las transiciones y que `doctor.py` rechaza un índice
  cerrado sin veredicto.
- Fixtures estructurales de `doctor.py` (`doctor-estructural/`, `huerfana/`,
  `indice-sin-tabla/`): cada regla estructural tiene una etapa que la viola, y
  la suite falla si el script deja de reportarla.
- Fixture `index-estado`: `03-activa` y `05-hecha` deben pasar;
  `04-etapa` debe fallar.
- Fixture `ca-tipo`: los CA con marcador no avisan; `CA-05`, sin marcador,
  es error.
- `snapshot.py`: identidad content-addressable del código auditado (`head`,
  `tree`, `dirty` y rutas excluidas) calculada con un índice temporal, sin
  tocar el índice real. `--exclude` permite dejar fuera el árbol de la feature
  para que escribir la evidencia no invalide su propio snapshot.
- `**Snapshot:**` obligatorio en cada pasada con veredicto `coincide`; sin él,
  `validate_stage.py` falla, y el snapshot de una pasada anterior no vale.
  `validate_stage.py --repo` recalcula la identidad con las mismas exclusiones
  y rechaza un veredicto obsoleto.
- `**Riesgo:** bajo | medio | alto` congelado en la conciliación cerrada y
  `**Riesgo auditado:**` en la pasada. El auditor puede subirlo, nunca bajarlo:
  un riesgo auditado menor es error del validador.
- `**Presupuesto de deltas:**` derivado del riesgo. `next_step.py` devuelve
  `necesita-decision` con `PRESUPUESTO_DE_DELTAS_AGOTADO` cuando la corrección
  supera el presupuesto o la auditoría sigue en `no coincide` tras gastarlo.
- Fixtures `coincide-sin-snapshot`, `riesgo-rebajado`, `riesgo-ausente`,
  `presupuesto-agotado`, `presupuesto-excedido`,
  `presupuesto-excedido-coincide` y `presupuesto-amplio`, con
  `test_snapshot.py` y casos nuevos en `test_next_step.py`.
- Vía exprés: `expres.py` decide desde el diff si un cambio cabe fuera del
  ciclo (1 archivo de producción, ≤ 20 líneas, sin rutas excluidas). Cuenta los
  archivos nuevos sin trackear, no cuenta las pruebas y acepta `--json`.
  `EXPRES.md` registra una fila por cambio con el porqué y la verificación;
  `next_step.py` no lo lee. `doctor.py` avisa, sin bloquear, cuando 3 cambios se
  acumulan sobre el mismo CA o el mismo archivo. Fixtures `expres-sano` y
  `expres-acumulado`, con `test_expres.py` y casos en `test_next_step.py`.

### Cambiado

- La plantilla de `AUDIT.md` reemplaza el identificador informal de
  «commit/working tree» por `**Snapshot:**` y añade `**Riesgo auditado:**`.
  `CONCILIACION.md` declara `**Riesgo:**` y `**Presupuesto de deltas:**`.

### Eliminado

- **Modo legado del validador.** Se retiran `--strict` y `legacy=`. Hay **un**
contrato y **un** modo de validación: `riesgo-ausente` y `ca-tipo` fallan
siempre, porque describen estados que el contrato rechaza. Las fixtures que
dependían del modo permisivo pasan a negativas o se retiran.


## [1.0.0] - 2026-09-30

### Añadido

- Seis skills compatibles con Agent Skills: `identify-feature-stages`,
  `feature-stages`, `conciliate-stage`, `generate-stage-tasks`,
  `implement-stage` y `audit-stage`.
- Contrato y orquestador compartido en `feature-stages`: estados, gates,
  plantillas (`templates.md`), referencias (`stage-contract.md`,
  `skill-maintenance.md`) y rúbrica de evaluación (`EVALUATION.md`).
- Árbol portable de feature por etapas: índice, `CONCILIACION.md`,
  `TAREAS.md` (lista principal), `AUDIT.md` con ledger de evidencia y
  `TAREAS-delta-NN.md`.
- Validadores locales (`scripts/validate_stage.py` y
  `scripts/validate_skill_evals.py`), casos de activación retenidos
  (`evals/cases/*.json`) y fixtures de etapa (incluida la negativa
  `closed-without-task`, que debe fallar).
- Flujo de validación en GitHub Actions (`.github/workflows/validate.yml`).
- Documentación raíz: README, CONTRIBUTING, AGENTS y licencia MIT.