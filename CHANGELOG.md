# Changelog

Todos los cambios notables de este proyecto se documentan en este archivo.

El formato se basa en [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/)
y el proyecto adhiere a [Semantic Versioning](https://semver.org/lang/es/).

## [Unreleased]

### Añadido

- **La vía exprés deja prueba de que se probó (P8).** El modo más usado del paquete era el único que no acreditaba nada: una fila de `EXPRES.md` decía por qué cabía y nada más. Cada fila declara ahora `Comando`, `Resultado` y `Confirmado por`; el resultado tiene que nombrar el exit o el recuento de la prueba, porque `ok` no distingue «pasó» de «no se ejecutó», y la confirmación es la firma humana de las dos condiciones que el diff no puede mostrar. Una fila incompleta es error de `doctor.py`, no aviso. La acumulación de tres cambios sobre el mismo CA o archivo, un cambio exprés sobre un archivo que declara una tarea de una etapa en `lista`/`implementando`/`auditando`, y una promoción `→ NN-slug` a una etapa fuera del índice pasan también a error: en los tres casos el corte estaba mal y el trabajo pertenece a una etapa. Una etapa cerrada no cuenta, porque sus archivos son histórico. `EXPRES.md` sigue sin cambiar transiciones: `next_step.py` no lo lee. Fixtures `expres-sin-verificacion`, `expres-resultado-sin-exit`, `expres-promocion-rota`, `expres-etapa-abierta` y `expres-etapa-cerrada`, con `expres-sano` y `expres-acumulado` migradas. `EVALUATION.md` S45.

- **La forma de la regla depende del fallo que corrige (P24).** Una regla de forma escrita como prohibición no arregla un output con forma equivocada, y un matiz la reabre cuando el agente está bajo presión. `skill-maintenance.md` clasifica el fallo antes de escribir: saltar bajo presión pide prohibición con racionalizaciones y red flags; output con forma equivocada, una receta positiva; un elemento omitido, un campo obligatorio en la plantilla; una condición, un condicional con predicado observable. Las excepciones dejan de ser cláusulas: son otro condicional cuyo predicado se puede comprobar («si `**Motivo del presupuesto:**` está escrito»). Se verifica en la revisión del PR, no con un linter: sin metadata por regla no hay forma de clasificar el fallo, así que el caso prometido en `test_skill_evals.py` se retira en vez de escribirse sin poder fallar. La revisión de las seis skills encontró dos cosas: la excepción pegada a la prohibición de `audit-stage`, ahora dos condicionales, y que `feature-stages` no nombraba el veredicto de calidad entre los gates de cierre.

- **Una regla nueva ya no entra por parecer razonable: entra si el agente falla sin ella (P20, P23).** El paquete crecía con reglas que consumían contexto sin cambiar ninguna decisión, y nada distinguía una regla que corrige un fallo real de una que solo suena bien. Una regla nueva o que cambia comportamiento cita ahora `Baseline:` (qué hizo el agente sin ella, con la cita verbatim), `Reps:` (≥5 repeticiones por variante) y `Control:` (qué falló sin la guía). Si el control no exhibe el fallo, **no hay nada que corregir** y la regla no se escribe. Un resultado sin control no cuenta como mejora, y la varianza se reporta: cinco repeticiones con cinco interpretaciones dicen que la redacción no obliga, aunque cada una parezca razonable. Entra como nivel 3 de `EVALUATION.md` —«RED de regla», previo al conductual—, en `CONTRIBUTING.md`, `AGENTS.md`, `RELEASE_CHECKLIST.md` y `references/skill-maintenance.md`. Las correcciones factuales, de enlace y de formato quedan exentas (B-24): sin esa acotación el mantenimiento se vuelve inoperable.

- **Retomar una etapa ya no significa re-ejecutar lo hecho (P21).** El fallo más caro observado al usar el paquete fue re-ejecutar tareas completas que se perdieron al compactar el contexto. `next_step.py <feature-root> --reconcile` imprime, en pocas líneas, la transición del router, los IDs de tarea pendientes y los últimos commits que tocan la etapa, de modo que un agente que perdió el hilo relee el estado en vez de recordarlo. Reutiliza la proyección de `tasks.py` en lugar de inventar un segundo veredicto del estado, degrada a `sin repositorio git` fuera de un repositorio en vez de fallar, y no combina con `--json` ni `--all`: existe para releer, no para alimentar un esquema. La regla «el contexto no sobrevive a la compactación» está en los seis `SKILL.md` y `validate_skill_evals.py` falla si desaparece de alguno. Fixture `reconcile-contexto` con T1–T3 hechas y T4 pendiente.

- **Cumplir el criterio ya no basta para cerrar: el cambio también se mira (P18, B-38).** `AUDIT.md` tenía un solo veredicto, así que un cambio correcto y a la vez duplicado, sobre-abstracto o sin manejo de errores en el camino nuevo cerraba igual. La pasada que cierra declara ahora `**Veredicto (calidad):** aceptable | con hallazgos | bloqueante`, con foco cerrado en cuatro comprobaciones: duplicación introducida por el cambio, abstracción que nada pide (YAGNI), manejo de errores ausente en el camino nuevo y tests que prueban mocks en lugar del código. Solo `aceptable` cierra: `con hallazgos` se corrige con un delta dentro del presupuesto y se reaudita, y `bloqueante` no cabe en un delta, así que reabre la conciliación. El gate juzga la pasada que cierra y no reescribe la historia: una pasada `no coincide` no necesita veredicto de calidad. Fixtures `calidad-ausente`, `calidad-con-hallazgos`, `calidad-bloqueante` y `calidad-aceptable`; las 42 auditorías de fixture que cierran conservan su veredicto.

- **El presupuesto no funcional es un campo del corte, no una sección que se escribe si hay tiempo (P7).** La conciliación podía cerrarse sin decir cuánto puede tardar, cuánto ocupa o qué dependencia nueva arrastra: `Verificar:` no tenía umbral que heredar y la auditoría no tenía contra qué medir. `**Presupuesto no funcional:**` declara en cinco líneas latencia, memoria, tamaño de artefacto, dependencias nuevas y rendimiento de la operación crítica. Cada línea se rellena o se marca `no aplica (motivo)`; `no aplica` sin razón es una línea vacía con más palabras, y conservar el `…` de la plantilla tampoco responde. `validate_stage.py` exige las cinco respuestas y **no juzga el número**: el umbral lo acuerda el humano en la conciliación. Fixtures `no-funcional-ausente`, `no-funcional-sin-motivo` y `no-funcional-presente`; las 79 conciliaciones de fixture migradas conservan su veredicto y el gate se mutó a no-op para comprobar que muerde.

- **Saber qué tareas faltan ya no exige leer la lista entera (P13).** `tasks.py pending <etapa>` proyecta el checkbox de `TAREAS.md` y de cada `TAREAS-delta-NN.md` en IDs pendientes, con `--json` para máquinas. No decide el estado —eso es `next_step.py`— ni emite los huecos del contrato —eso es `validate_stage.py`—: por eso **no** hay `trace.py`, que habría sido una segunda forma de decir lo mismo. Avisa cuando `**Estado:**` declara la lista `implementada`/`auditada` y queda una tarea sin marcar, y una lista vacía sale con 2 en vez de un `OK` falso. El título se acota a 80 caracteres para no reimportar el párrafo que la consulta existe para no leer. En 37 etapas reales: 9 con pendientes y 1 contradicción; la consulta pasa de 5–51 KB a 100–800 bytes por etapa.

- **La trazabilidad de la auditoría tiene que ser cierta, y cada bloqueo se clasifica (P6, B-20).** `**Trazabilidad:**` solo se comprobaba que existiera, así que `CA-01 → T9 → test_focal.py → E-77` pasaba con `T9` y `E-77` inexistentes: la cadena que la auditoría declara era decorativa. Ahora cada ID citado debe existir en su fuente —`T` en `TAREAS.md`, `E` en el ledger de esa pasada, `CA`/`S` en `CONCILIACION.md`— y la traza debe nombrar CA, T y E a la vez. Fixtures `trazabilidad-t-inexistente` y `trazabilidad-e-inexistente`. Y B-20 añade una dimensión de fricción al catálogo: `test_blockers.py` clasifica cada bloqueo como `in band` (nombra el camino), `out of band` (dice qué hacer sin nombrar a quién) o `dead end` (sin salida); un `dead end` falla y los `out of band` se informan. La banda se deduce de la resolución que el router emite, no se escribe a mano: una tabla fija se desactualiza al siguiente cambio de mensaje. Hoy los 11 códigos están `in band`.

- **La suite de referencia ya no es narrativa: se declara y se ejecuta.** `### Verificación global` del `AUDIT.md` era texto libre que `validate_stage.py` no leía, así que una etapa podía cerrarse con `coincide` sin haber corrido nada. Ahora `CONCILIACION.md` declara `**Suites de referencia:**` con los comandos que deben pasar, y el cierre exige una fila `E-NN` en el ledger por cada uno, en la forma en que se invocan. La elige el humano y no el agente (B-11): exigir «toda la suite» en un repo grande es caro, y «nada» no protege. `ninguna` solo vale con `**Motivo de la suite:**` escrito, la misma forma que el contrato usa para un presupuesto ampliado, para que «no ejecuté nada» no pase en silencio. Fixtures `suite-ausente` (no la declara), `suite-sin-evidencia` (declara `npm run lint` y el ledger no lo tiene) y `suite-con-evidencia` (positiva, dos comandos y dos filas). Las 42 conciliaciones de fixture que cierran declaran ahora el comando que su ledger ya registraba.

- **El presupuesto de contexto por fase ya tiene número, y salió de medir trabajo real.** `Q9` bloqueaba `P12` desde el principio: los límites (`identify ≤ 400`, `audit ≤ 1000`…) eran estimaciones y fijarlos antes de medir crea un gate que se incumple para poder trabajar. `preflight.py` entró sin gate y el número esperó al dato. El dato apareció al usar el paquete contra seis features reales —47 etapas, todas implementadas y cerradas—: midiendo el plan de lectura de la etapa activa en cada fase, el máximo observado fue 824 (`identify`/`audit`), 268 (`conciliate`/`generate`) y 380 (`implement`). El presupuesto recomendado es el máximo redondeado a la centena —**900, 300 y 400**— porque calibrar por debajo del trabajo aceptado habría rechazado etapas que el equipo dio por buenas. El dato corrigió dos cosas de la propuesta: `identify ≤ 400` rechazaba 2 de 6 árboles reales, e `identify`/`audit` compartían archivos pero no número, así que cualquier etapa entre 400 y 1000 demostraba que uno de los dos no significaba nada. Entra como **recomendación** en `stage-contract.md`: `--check` sigue mirando solo las etapas que declaran `**Presupuesto de contexto:**`, para no imponer un número retroactivamente.

### Cambiado

- **El estado `listo` pasa a `declarada-cerrada`, porque no prometía lo que comprobaba.** `next_step.py` devolvía `listo` cuando el índice marcaba la etapa `cerrada` y su auditoría decía `coincide`: eso es una declaración de los artefactos, no una verificación del contrato. En un corte real de seis features, once etapas mostraban «nada por hacer» mientras `validate_stage.py` las rechazaba en todas sus tareas. Renombrar era la corrección barata y honesta: exigir el contrato en el router habría acoplado el estado a un gate completo y habría dejado sin salida cualquier árbol escrito con el contrato anterior, que es justo el patrón que Q9 descartó. `declarada-cerrada` dice lo que el router mira —índice cerrado más veredicto `coincide`— y deja el contrato a `validate_stage.py`. Fixture nueva `cerrada-sin-contrato`: un cierre declarado con `**Snapshot:**` ausente, que el router acepta como terminado y el validador rechaza; el caso exige las dos cosas a la vez para que el nombre no vuelva a prometer de más.

### Corregido

- **Todo bloqueo trae ahora una continuación que desbloquea de verdad.** `next_step.py` listaba bloqueos «con su resolución», pero nada probaba que la resolución resolviera: el test solo comprobaba que el código aparecía. `test_blockers.py` parte de la fixture que produce cada bloqueo, aplica sobre una copia la resolución que el propio blocker declara y exige que el código desaparezca; un código nuevo sin caso falla. El caso encontró uno real: `PRESUPUESTO_DE_DELTAS_AGOTADO` ofrecía «aceptar el riesgo residual con owner», y el router no lee ese campo en ningún sitio. Un agente que eligiera esa salida —la que el mensaje le ofrece— se quedaba bloqueado para siempre. La resolución se recortó a lo que el router puede ver: reabrir la conciliación o detener la etapa.
- **`doctor.py` ya no presenta la coherencia como veredicto de contrato.** Imprimía `OK: árbol de feature coherente` y, en caso contrario, `FALLA: el árbol no cumple el contrato`: dos frases que se leían como si describieran lo mismo, cuando el script comprueba un subconjunto —coherencia del índice, vocabulario de estados, presencia de artefactos, `Test-first:`/`Test:` y cuatro campos de `AUDIT`— y no mira `S-NN`, `Origen:`, `Interfaces:`, el ledger ni el presupuesto de deltas. Sobre el corte real de seis features decía árbol coherente mientras `validate_stage.py` rechazaba etapas. Ahora el `OK` nombra su alcance y remite al validador, y el aviso de fallo dice «no cumple las comprobaciones de doctor», no «el contrato». El caso de `test_next_step.py` ejecuta doctor sobre `transiciones` y exige a la vez su `OK` y el rechazo de `06-cerrada` por el validador: si doctor empieza a prometer el contrato, o la fixture deja de discrepar, el caso falla. Caso `S33`.

- **El CI llevaba roto desde B-28 y validaba menos de lo que decía.** El workflow seguía invocando `validate_stage.py --strict`, retirado al dejar un solo contrato, así que cada paso de contrato salía con 2; sus pasos además afirmaban lo contrario del contrato en `ca-tipo` y nunca ejecutaron las suites de bloqueos, alcance, evidencia ni preflight. Ahora ejecuta las nueve suites, y `validate_skill_evals.py` comprueba que no falte ninguna y que no reaparezca un modo retirado. Las tres fixtures que solo ejercitaba el CI se migraron a `test_next_step.py` con su motivo, no se borraron. Tabla S39.

## [0.2.0] - 2026-10-27

### Corregido

- **La serie publicada es `0.x`, y el CHANGELOG ya lo dice.** La entrada del import inicial estaba como `## [1.0.0] - 2026-09-30`, mientras `GOVERNANCE.md` declara que la serie publicada es `0.x` mientras el contrato pueda cambiar. Desde ese import el contrato cambió en cosas que rompen compatibilidad —el alcance lee también los deltas, el ledger no se juzga sin pasada, el cierre exige `--repo`—, que es exactamente lo que `0.x` significa. Pasa a `0.1.0`, y este bloque se publica como `0.2.0`. Ningún tag existía, así que no hay release que corregir.
- **`AGENTS.md` ya no manda a un documento que no existe.** Su primer paso antes de tocar un archivo era «Lee `PUBLISHING.md` si no lo conoces», y ese archivo nunca existió: `git log --all -- PUBLISHING.md` está vacío. El paso que debía orientar al mantenedor apuntaba a la nada, y sobrevivió porque el comprobador de enlaces solo recorría los `SKILL.md` y siete documentos de `references/`, y porque un nombre entre comillas invertidas no era un enlace para nadie. Ahora apunta a `GOVERNANCE.md` y `RELEASE_CHECKLIST.md`, que es donde están esas reglas, y `validate_skill_evals.py` recorre también los documentos de mantenimiento y exige que cada `.md` que nombran exista. Los nombres de patrón (`TAREAS-delta-NN.md`) quedan fuera de la regla a propósito. Caso con las dos direcciones en `test_skill_evals.py`.
- **La evaluación conductual se puede materializar.** La receta decía «materializar la fixture indicada en un repositorio temporal», y copiar la carpeta entera copia también su `AUDIT.md`, que afirma `coincide` sobre un árbol que no lo cumple: al ejecutar `S28` y `S29` por primera vez, tres de los cuatro casos pararon en `COINCIDE_SIN_CIERRE` antes de medir nada, y hubo que rehacer el montaje a mano. `EVALUATION.md` dice ahora qué se materializa por caso —sin pasada para implementar y revisar la lista, con pasada para auditar, que es su fallo sembrado— y por qué el caso de auditoría se lanza con `audit-stage` en vez de seguir `siguiente`. `test_next_step.py` monta los tres casos y exige `trabajando`; copiar la pasada en uno de implementación lo pone en rojo.
- **El validador ya no exige el ledger de una etapa que no se ha auditado.** `risk_evidence_gaps()` corría sobre una auditoría vacía, así que una etapa en riesgo `medio` o `alto` sin `AUDIT.md` fallaba con «el ledger no declara un caso límite ni un negativo demostrado». `implement-stage` ejecuta ese validador antes del relevo y tiene prohibido escribir la auditoría: el único modo de callar el error era fabricar la pasada, que es el falso cierre que el paquete persigue. Sin pasada no hay ledger que juzgar y el fondo no se reclama; el gate no se apaga, porque el mismo ledger real, quitándole el caso límite, sigue rechazándose. Fixture `antes-de-auditar` y caso en `test_next_step.py`.
- **`implement-stage` dice dónde se escribe el bloqueo.** La skill mandaba «the feature README or task list», pero `next_step.py` y `doctor.py` leen la causa de `## Bloqueos` en `CONCILIACION.md`: seguir la skill dejaba la etapa bloqueada «sin causa escrita» y empujaba a editar la conciliación sin que nadie lo hubiera dicho. Ahora la skill nombra esa sección y aclara que es operativa, no baseline. `validate_skill_evals.py` falla si deja de nombrarla.
- **El alcance incluye los deltas, y una tarea de delta se prueba como cualquier otra.** `TAREAS.md` era la única lista que `diff_scope.py` y el cierre de `validate_stage.py` leían: el archivo que producía un `TAREAS-delta-NN.md` salía como «alcance nuevo» y una etapa corregida con un delta que añade archivo no podía cerrar nunca. El alcance es ahora la unión de la lista principal y sus deltas (`declared_in()`), y `validate_stage.py` aplica a `D0N-TN` el mismo contrato que a `TN` (`**Archivos:**`, `Test-first:`, `Test:`, `Verificar:`), porque el delta es la corrección acotada de un hueco, no una lista de segunda. Alinea el template de delta, el contrato y `deltas-and-closure.md`; nuevas fixtures `delta-sin-prueba` y casos en `test_diff_scope.py`, `test_snapshot.py` y `test_next_step.py`. Las fixtures de delta existentes declaran ahora esos campos.
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


- La plantilla de `AUDIT.md` reemplaza el identificador informal de
  «commit/working tree» por `**Snapshot:**` y añade `**Riesgo auditado:**`.
  `CONCILIACION.md` declara `**Riesgo:**` y `**Presupuesto de deltas:**`.

### Eliminado

- **Modo legado del validador.** Se retiran `--strict` y `legacy=`. Hay **un**
contrato y **un** modo de validación: `riesgo-ausente` y `ca-tipo` fallan
siempre, porque describen estados que el contrato rechaza. Las fixtures que
dependían del modo permisivo pasan a negativas o se retiran.

## [0.1.0] - 2026-09-30

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