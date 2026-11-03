# Changelog

Todos los cambios notables de este proyecto se documentan en este archivo.

El formato se basa en [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/)
y el proyecto adhiere a [Semantic Versioning](https://semver.org/lang/es/).

## [Unreleased]

### Corregido

- **Una firma con el árbol en forma corta cubre la pasada que aprueba (P12, B-49).** `Approval.covers()` comparaba el árbol firmado y el auditado con igualdad exacta, así que una persona que copiaba `tree=152c3474` de la pasada —la forma corta de `git rev-parse --short`— quedaba sin aprobación: la etapa 08 del consumidor no cerraba con `alcance: tree=152c3474` sobre `tree=152c347487f2c47bd374c2ccfaa73fb096a05191`, y el error acusaba a la firma. Ahora el auditado tiene que empezar por el árbol firmado; un árbol que no es prefijo sigue sin cubrir, y el prefijo literal del snapshot se sigue aceptando para las firmas anteriores. Caso de firma con árbol corto en `check_validate()` de `test_snapshot.py`; contrato y `approvals.py` lo dicen. `Baseline:` la etapa 08 del consumidor. `Reps: 5/5` por variante por la CLI pública. `Control:` una firma con `tree=deadbeef` no cubre la pasada 5 de 5 con los dos códigos. `EVALUATION.md` S63.

- **La identidad de una pasada es el árbol, y la firma se ancla a él (P12, B-49).** Se comparaba `tree=` + `dirty=` + `exclude=` literal: como `exclude=` enumera las carpetas de etapa del panel, dar de alta la etapa 10 dejaba obsoletas las pasadas de la 07 y la 08 sin cambiar una línea de código. Y `Approval.covers()` comparaba un prefijo de la línea entera, que empieza por `head=`: un `alcance: tree=<sha>` no casaba nunca y un `alcance: head=<sha>` dejaba de cubrir en cuanto se commiteaba un documento. Ahora `snapshot.code_identity` compara el árbol y `covers()` ancla el alcance al `tree=` del snapshot (el prefijo literal se sigue aceptando para las firmas anteriores). El snapshot grabado conserva `head=` y `exclude=` como información, y el validador avisa, sin bloquear, si la pasada no declara la exclusión de `.yerro/approvals.yml`. Casos `check_new_stage_does_not_invalidate()` y firma por árbol en `test_snapshot.py`. `Baseline:` la etapa 07 del consumidor. `Reps: 5/5` por variante por la CLI pública. `Control:` un cambio en `src.txt` sigue invalidando la pasada 5 de 5 con los dos códigos. `EVALUATION.md` S62.

- **La pasada de una etapa ya no se invalida por los documentos de la etapa vecina (P12, B-49).** El snapshot de una etapa excluía su propia carpeta y el índice del panel, pero no las carpetas de las demás etapas: escribir el `AUDIT.md` de la etapa 02 cambiaba el árbol que la etapa 01 había auditado, y cada pasada de una etapa obligaba a repetir la de al lado sin un cambio de código. Ahora se excluyen por forma todas las carpetas de etapa del panel y su `README.md`; un archivo del panel que no es de etapa sigue contando, y dos etapas del mismo panel ven el mismo árbol de código. Caso `check_whole_panel_excluded()` en `test_snapshot.py`; contrato y `snapshot.py` lo dicen. `Baseline:` la etapa 07 del consumidor, cuyo `tree=` cambió al commitear el `AUDIT.md` de la 08. `Reps: 5/5` por variante por la CLI pública. `Control:` un cambio en `src.txt` sigue invalidando la pasada 5 de 5 con los dos códigos. `EVALUATION.md` S61.

- **Un commit de documento ya no invalida una pasada que auditó el mismo árbol (P12, B-49).** La pasada graba `head=` y `tree=`, y el validador comparaba la línea entera: cualquier commit que moviera `HEAD` —aunque fuera dentro de las rutas que el snapshot excluye: la carpeta de la etapa, el índice del panel, la aprobación— la declaraba obsoleta. Como grabar la pasada exige escribir en la etapa, commitear esa escritura movía `HEAD` y volvía a invalidarla, así que el `head=` grabado solo coincidía mientras el documento seguía sin commitear; es lo que dejó las pasadas 7 y 8 de las etapas 07 y 08 con un `head=` que ya no era `HEAD`. Ahora la identidad es `tree=` + `dirty=` + `exclude=` (`snapshot.code_identity`, `validate_stage.same_identity`): `head=` se sigue grabando como el commit de partida, pero no se compara, y un `tree=` distinto sigue invalidando la pasada. Caso `check_document_commit()` en `test_snapshot.py`; contrato y plantilla lo dicen. `Baseline:` la pasada 7 de la etapa 07 del consumidor. `Reps: 5/5` por variante por la CLI pública. `Control:` commiteando `src.txt` la pasada sigue invalidándose 5 de 5 con los dos códigos. `EVALUATION.md` S60.

- **Un delta ya puede justificarse con la pasada que lo cierra, y una etapa cerrada con deltas no se reaudita (P12, P21).** `DELTA_SIN_AUDIT` exigía que **alguna** pasada dijera `no coincide` para que un delta existiera, así que el delta de verificación —el que demuestra un criterio sobre otro árbol sin corregir código— no tenía forma: en la etapa 07 del consumidor el delta 01 lo abrió la pasada 1, que cerraba sobre el criterio completo, y los deltas 02/03 los auditó la pasada 6, que cierra con `coincide`. Ahora un delta lo justifica una pasada que lo abre con `no coincide` **o** la pasada que lo cierra declarándolo en `**Deltas:**` con su ID (`declared_deltas()`, `justified_delta()`); nombrarlo en prosa no lo declara y un delta que ninguna pasada nombra sigue bloqueando. Además, con el índice en `cerrada` y la última pasada en `coincide` la rama de deltas se evaluaba antes de la de cierre: una etapa ya cerrada con deltas se reportaba `verificando` → `audit-stage` y pedía reauditar un árbol sin cambios. Ahora es `declarada-cerrada`, y si un delta no estaba auditado la pasada no coincide o el índice no está cerrado. Fixtures `transiciones/08-cerrada-con-delta`, `delta-huerfano/03-cierre-sin-declarar`; caso `check_delta_closure()` en `test_next_step.py`; contrato y `deltas-and-closure.md` lo describen. `Baseline:` la etapa 07 del consumidor devolvía `verificando` con `audit-stage`. `Reps: 5/5` por variante. `Control:` con el `next_step.py` de `HEAD` los casos fallan 5 de 5 (`estado 'necesita-decision', se esperaba 'declarada-cerrada'`, `bloqueos inesperados ['DELTA_SIN_AUDIT']`, `un cierre que declara el delta sigue sin justificarlo` y `next_step no lee **Deltas:**`); el árbol de control que no declara el delta sigue bloqueando con los dos códigos. `EVALUATION.md` S59.

- **Reabrir la conciliación desde la auditoría ya tiene una transición (P12, P21).** Una etapa cerrada reabre cuando el alcance se movió **después** del árbol que auditó una pasada anterior —otra etapa tocó un archivo que esta reclamaba— y un delta no lo cubre: corregiría contra un baseline que ya no es el vigente, y el presupuesto puede estar agotado. El contrato solo sabía leer el cierre como «la última pasada dice `coincide`», así que reabrir exigía reasignar ese veredicto, y con el índice fuera de `cerrada` el router pedía cerrar con `COINCIDE_SIN_CIERRE` mientras `doctor.py` leía el `coincide` viejo con `re.search` sobre el archivo entero. Ahora la pasada que reabre declara `**Reapertura:** <motivo>` con `**Veredicto:** no coincide`: no lleva veredicto de calidad, no abre delta y no consume presupuesto, y `next_step.py` devuelve `trabajando` con `conciliate-stage`. El bloqueo `PRESUPUESTO_DE_DELTAS_AGOTADO` solo mira pasadas `no coincide` **sin** la marca, así que la exención se debe a la reapertura y no a que la última pasada falle. `doctor.py` juzga el cierre por la última pasada y rechaza un índice `cerrada` con la última pasada reabierta. Fixtures `reapertura-auditoria` (positiva, `doctor.py` en verde), `presupuesto-excedido-reabierto` (sin la marca sigue bloqueando) y `reapertura-cerrada` (`doctor.py` falla); `check_reopening()` en `test_next_step.py`; contrato, plantilla de `AUDIT.md`, `audit-stage` y `deltas-and-closure.md` lo describen. `Baseline:` en la etapa 07 del consumidor, la 08 cambió el prompt y `layout.test.mjs` después de la pasada 6 y la última pasada decía `coincide`: el router daba `necesita-decision` por `COINCIDE_SIN_CIERRE` con el índice fuera de `cerrada`, o declaraba cerrada una etapa cuyo alcance ya no era el auditado. `Reps: 5/5` por variante. `Control:` con el `next_step.py`/`doctor.py` de `HEAD` los casos fallan 5 de 5 (`estado 'verificando', se esperaba 'trabajando'`, `siguiente 'audit-stage', se esperaba 'conciliate-stage'`, `no lee **Reapertura:**`, `TAREAS.md prematuro para etapa conciliando` sobre el árbol coherente y `no reporta el cierre reabierto`); con el arreglo pasan 5 de 5. `EVALUATION.md` S58. La marca solo cuenta si la pasada **no** cierra: una pasada `coincide` que vuelve a nombrar `**Reapertura:**` al citar la que resolvió no reabre nada. Fixture `reapertura-resuelta` y `Baseline:` la pasada 7 de la etapa 07 del consumidor, que cierra citando la reapertura de S-13..S-16: con el `next_step.py` de `993c843` la etapa cerrada volvía a `conciliate-stage` 5 de 5. `Reps: 5/5` en las dos variantes. `Control:` la variante idéntica que **no** cita la reapertura cierra 5 de 5 con los dos códigos, así que el fallo lo produce la marca y no el criterio de cierre; con el arreglo las dos variantes cierran 5 de 5.

- **Una fila de evidencia con `|` en el comando ya no se parte al copiarla (P12).** `evidence.py run` escribía el comando tal cual dentro de una celda de tabla markdown: un `|` crudo corta la fila, `verify` leía un fragmento, lo ejecutaba y reportaba un `exit` que nadie corrió —o un `comando no encontrado: p`—. `escape_cell()` escribe `\|`, `split_cells()` parte solo por los `|` no escapados y `unescape_cell()` devuelve el comando original al reejecutar; `truncated_rows()` nombra las filas `E-NN` que declaran más celdas que el encabezado y `verify` las reporta antes de ejecutar nada, en vez de correr basura. Caso `check_pipe_in_command()` en `test_evidence.py`, con las dos direcciones: la fila escapada se reproduce y la cruda se detecta. `Baseline:` una fila con `printf 'a|b\n' | wc -l` se partía en dos celdas y `verify` ejecutaba `p`. `Reps: 5/5` en las dos variantes. `Control:` con el `evidence.py` de `HEAD` el caso falla 5 de 5 por `ImportError: cannot import name 'truncated_rows'`; con un `truncated_rows()` no-op para desbloquear el import, el mismo test falla 5 de 5 con 12 errores, entre ellos `ledger_row no escapó el `|` del comando`, `parse_ledger no devolvió el comando original` y `verify no reejecutó una fila con `|``. Con el arreglo pasa 5 de 5. `EVALUATION.md` S54.

- **Una tarea sin `**Archivos:**` ya no se cierra como si declarara (P12).** `validate_stage.py` solo miraba la dirección «se tocó y nadie lo declara»; una tarea sin `**Archivos:**` devolvía lista vacía y el hueco solo aparecía como aviso de `diff_scope.py` cuando ya había diff, así que la etapa podía cerrar con tareas cuya parte no estaba declarada. `check_task_body()` exige ahora el campo en **toda** tarea —principal y delta— con el mensaje que impide derivarlo del diff ya producido. Fixture `tarea-sin-archivos`. `Baseline:` en la etapa 07 del consumidor los `**Archivos:**` de T1–T10 se escribieron después de ver el diff, que es justo lo que el mensaje prohíbe. `Reps: 5/5` en las dos variantes. `Control:` con el `validate_stage.py` de `HEAD` la fixture nueva se acepta en verde 5 de 5; con el arreglo falla 5 de 5 con `T1 no declara `**Archivos:**`; derívalo de su CA, nunca del diff ya producido`. `EVALUATION.md` S55.

- **El índice del panel ya no obliga a una pasada nueva al cerrar (P12).** La fila de estado de una etapa se escribe en el `README.md` del panel justo al terminar, y mantener ese archivo dentro del snapshot cambiaba `tree=` y forzaba reauditar una etapa que ya estaba cerrada: en la etapa 07 del consumidor fue la causa de la pasada 4. `snapshot.py` excluye por **forma** el índice del panel —el `README.md` de la carpeta que tiene carpetas de etapa `NN-nombre` como hermanas— sin nombrar ninguna ruta de un consumidor, y solo mira la carpeta de la etapa y su padre para no confundir cualquier `README.md` de un antepasado. Lo auditado es el árbol de la etapa; el índice se juzga por su contenido (estado y veredicto de su fila). Caso `check_panel_index_excluded()` en `test_snapshot.py`: editar el índice no cambia la identidad, editar la etapa sí, y un `README.md` que no es panel sigue contando. `Baseline:` la pasada 4 de la etapa 07 se hizo solo para registrar el cambio de una celda del índice. `Reps: 5/5` en las dos variantes. `Control:` con el `snapshot.py` de `HEAD` el caso falla 5 de 5 con `snapshot: el índice del panel no viaja en exclude=` y `snapshot: editar el índice del panel cambió la identidad del árbol auditado`; con el arreglo pasa 5 de 5. `EVALUATION.md` S56.

- **El cruce de alcance atribuye cada ruta a su commit en vez de acusar a la etapa (P12, B-27 intacto).** Con una rama por etapa, medir desde la apertura de esta etapa arrastra lo que las otras commitearon: la etapa 07 del consumidor veía 193 rutas ajenas como alcance nuevo, sin decir de dónde venían, y el único cierre posible era rebajar el gate. `attribute()` lee una vez `git log base..HEAD`, marca como **ajena** la ruta cuyo commit toca cualquier carpeta de etapa del repositorio —reconocida por forma `NN-nombre` y por tener `CONCILIACION.md`, `TAREAS.md` o `AUDIT.md`, no por ser hermana del mismo panel— y no toca esta, y la informa con su hash y su asunto; una ruta de un commit sin etapa (esta implementación), del árbol de trabajo o de un commit mixto sigue bloqueando, y un archivo que vive dentro de otra etapa es ajeno aunque el commit sea mixto. `diff_scope.py` separa `undeclared` (bloquea) de `foreign` (avisa) y `validate_stage.py` hace lo mismo. Caso `check_foreign_attribution()` en `test_diff_scope.py` con los tres órdenes: ajeno no bloquea, propio bloquea, mixto bloquea. `Baseline:` la etapa 07 del consumidor daba 193 rutas sin atribuir de 35 commits; con la regla nueva se atribuyen 82 a su commit y 111 siguen bloqueando (su commit no toca el árbol de ninguna etapa, así que el gate no las absuelve). `Reps: 5/5` en las dos variantes. `Control:` con `diff_scope.py` de `HEAD` el caso falla 5 de 5 (`atribución: un commit mixto absolvió una ruta (1, ['features/02-ajena/NOTA.md', 'src/ajena.py', …])`); con el arreglo pasa 5 de 5. `EVALUATION.md` S57.

- **La base del alcance es la apertura de la etapa, no su primera ruta (P12).** `stage_base()` tomaba la primera aparición de **cualquier** archivo de la carpeta de la etapa. Una etapa puede dejar su `CONCILIACION.md` en un commit de hace semanas, junto a otras etapas, y empezar a implementarse mucho después: medir desde ahí mete en el diff todo lo que las otras etapas commitearon entre medias, y el cruce se vuelve un falso positivo de cientos de archivos que ninguna tarea de esta etapa puede declarar. La base es ahora el commit que añade `TAREAS.md` —la lista que `declared_in()` necesita para juzgar—, con caída a la primera aparición de la carpeta y a `None` si la etapa no está commiteada. Caso `check_base_is_task_list_start()` en `test_diff_scope.py`. `Baseline:` en la etapa 07 del consumidor la base era `fa3e770` (donde apareció de pasada la conciliación, junto a otras etapas) y el cruce daba 460 archivos con 447 no declarados; con el commit que abre la etapa son 260 y 214, y tras declarar los `**Archivos:**` de T1–T10 quedan 193, todos de otras etapas. `Reps: 5/5` en las dos variantes. `Control:` con la regla anterior el caso falla 5 de 5 con `stage_base: debe ser el commit que añade TAREAS.md, obtuvo …, se esperaba …` y arrastra `src/otra-etapa-*.py` al diff; con la nueva pasa 5 de 5. `EVALUATION.md` S52.

- **Un secreto local ya no cuenta como alcance nuevo (P12).** El operador deja sus credenciales de demo en un `.env` local que nunca se versiona, y el cruce de alcance lo trataba como código: bloqueaba el cierre y, para desbloquearlo, empujaba a declarar la credencial en el árbol de la etapa. `_is_local_secret()` excluye `.env`, `.env.*` y `*.local` del diff por **forma**, sin nombrar ningún archivo de ningún consumidor; `.env.example` sigue contando, porque es contrato documentado. Caso `check_local_secrets_ignored()` en `test_diff_scope.py`, con las dos direcciones. `Baseline:` en la etapa 07 del consumidor `console/.env.demo.local` aparecía como B-27 y la única salida que el mensaje ofrecía era declararlo. `Reps: 5/5` en las dos variantes. `Control:` con la regla anterior el caso falla 5 de 5 con `diff_scope: un .env local sin versionar no es alcance nuevo (1, ['console/.env.demo.local'])`; con la nueva pasa 5 de 5 y el `.env.example` sin declarar sigue bloqueando. `EVALUATION.md` S53.

- **Un `Test:` que no ejecuta ningún caso ya no cuenta como prueba (P12).** `validate_stage.py` daba por buena cualquier invocación con `--test-name-pattern`, incluida una que no casa con ningún caso del archivo: el runner sale 0, el `Test:` «pasa» y la tarea se marca sin haber probado nada. El gate cruza ahora el patrón con los nombres de caso declarados en el archivo destino (`find_test_file()`, `case_names()`, `check_pattern_has_cases()`), admite patrones citados y desnudos, y falla nombrando el patrón y el archivo. Fixtures `test-patron-vacio` (falla con ese mensaje) y `test-patron-con-casos` (pasa). `Baseline:` en la etapa 07 del consumidor tres tareas (T2, T7, T9) declararon `Test:` con patrón sin coincidencias y el agente las reportó como verdes. `Reps: 3/5`, los tres casos observados; no se fabricaron repeticiones. `Control:` sin el gate los tres comandos salen 0 y el validador no emite objeción. `EVALUATION.md` S48.

- **Un `**Estado:**` fuera del vocabulario de `TAREAS.md` bloquea en vez de rutear en silencio (P12).** Un valor que el contrato no conoce no se leía como error ni como «quizá pendiente»: caía en el `else` final del router y devolvía `audit-stage` con `exit 0`, con trabajo pendiente y sin aviso. `next_step.py` declara `TAREAS_ESTADOS` (cinco valores) y emite `TAREAS_ESTADO_DESCONOCIDO` antes de decidir, nombrando el archivo, el valor leído y los válidos. Fixture `estado-tareas-desconocido` (`**Estado:** completada` con `T4` sin marcar) exige `necesita-decision` y ese código. `Baseline:` la primera versión de la fixture declaraba `implementada`, un valor válido, y por eso no bloqueaba; se corrigió la fixture, no el gate. `Reps: 1/5`, un caso observado; la carencia se reporta, no se rellena. `Control:` la misma fixture contra una copia del router sin el bloque devuelve `Siguiente: audit-stage`, `Resultado: verificando` y `exit 0`. `EVALUATION.md` S49.

- **La fila del ledger que `run` emite vuelve a poder reejecutarse (P12).** `evidence.py` escribía el comando unido por espacios, así que `--test-name-pattern "panel chat"` perdía las comillas y `verify` reejecutaba otro comando; `verify` partía además la fila con `str.split()` sin lanzar un shell, así que `cd console && npm test` —la forma exacta que exige `**Suites de referencia:**`— moría con «comando no encontrado: cd»; y la firma incluía los tiempos por caso de `node --test`, que cambian entre corridas correctas, así que una fila honesta nunca reproducía. Ahora `command_text()` cita con `shlex.join`, `run` y `verify` ejecutan con `/bin/sh -c`, `normalize()` quita `(12.3ms)` y `duration_ms …`, y la columna del comando se lee del encabezado del ledger en vez de adivinar la primera celda con espacio (una celda `CA-01, CA-03` se leía como comando). Caso nuevo `check_reproducible_rows()` en `test_evidence.py`. `Baseline:` la pasada 1 de la etapa 07 del consumidor registró una fila que `verify` no pudo ejecutar («comando no encontrado: deploy/probe-tool-calling.mjs») y el mismo `panel chat` dio dos firmas distintas en dos corridas verdes. `Reps: 5/5` en las dos variantes. `Control:` el `evidence.py` de `HEAD` falla 5 de 5 con `verify rechazó una fila con un argumento citado (… exit 1, la auditoría registró 0)`, `comando no encontrado: c`, `comando no encontrado: CA-01,` y `la firma incluye el tiempo de cada caso`. `EVALUATION.md` S50.

- **`verify` ya no relanza las pasadas anteriores del `AUDIT.md` (P12).** Reejecutaba todas las filas E-NN del archivo, no las de la pasada que decide: tras un delta la pasada 1 conserva procedimientos que ya ocurrieron —`kill -9` al runtime, `launchctl kill SIGTERM`— y filas de prosa con varios comandos, así que verificar el cierre volvía a matar el proceso y marcaba `no verificado` un cierre honesto. `last_pass()` corta el texto en el último encabezado `## Pasada` y `verify` reejecuta solo esa; sin encabezado, el archivo entero es una pasada. `check_last_pass()` en `test_evidence.py`: la pasada 1 con `/herramienta/que/ya/no/existe` y una pasada 2 que reproduce pasa, y una firma falsa en la pasada 2 sigue fallando. `Baseline:` la etapa 07 del consumidor tiene una pasada 1 `no coincide` y una pasada 2 que la reaudita. `Reps: 5/5` en las dos variantes. `Control:` el `evidence.py` de `HEAD` falla 5 de 5 con `verify relanzó una pasada anterior`. `EVALUATION.md` S51.

## [0.3.0] - 2026-10-28

### Añadido

- **Cambiar una skill exige medirlo antes de publicar (P10).** El nivel conductual de `EVALUATION.md` pasa de «bajo demanda» a requisito de release: un cambio que toca una skill o el contrato no se publica sin la corrida sobre los casos retenidos, con modelo, host, fecha y commit fijados. Sin esa corrida el cambio es `no verificado`, no `validado`. `CONTRIBUTING.md` y `RELEASE_CHECKLIST.md` lo exigen y fijan el criterio de hosts, que sigue siendo por capacidad y no por lista cerrada. Los dos fallos sembrados que el borrador pedía añadir —suite roja declarada `coincide` y cierre sin aprobación humana— ya los cubren S35 y S21: se registran como absorbidos por escrito en vez de duplicarse. Nada de esto es un gate automatizado: la corrida consume tokens y un host con agente real, así que el paquete fija la regla y deja la medición al reporte de release.

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