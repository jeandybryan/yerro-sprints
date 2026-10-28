# Evaluación de skills de etapas

Mide si las skills del ciclo conservan el contrato, se activan para la petición correcta y cambian decisiones con evidencia. No mide longitud, cobertura global ni benchmarks generales.

## Niveles

1. **Estructural — CI/local, sin tokens.** Ejecutar `scripts/validate_stage.py` sobre fixtures y etapas reales. Verifica el contrato de artefactos. `scripts/test_next_step.py` verifica que cada estado de los artefactos produzca una única transición válida, `scripts/test_blockers.py` que cada bloqueo traiga una continuación que de verdad desbloquee (B-19), y `scripts/doctor.py` que el índice y los artefactos no se contradigan. `scripts/test_snapshot.py` verifica que la identidad de auditoría sea estable, sensible al código, insensible a la evidencia excluida y que `validate_stage.py --repo` rechace un snapshot obsoleto, acepte el cierre solo con una aprobación humana de `.yerro/approvals.yml` (`scripts/approvals.py`) que cubra el snapshot y la etapa, y rechace la firma ausente o fuera de alcance. `scripts/test_expres.py` verifica la frontera exprés: cuenta archivos y líneas de producción, no las pruebas, y rechaza rutas excluidas y archivos nuevos sin trackear. `scripts/test_evidence.py` verifica que la firma sea estable, sensible al exit y al output, insensible a lo volátil, y que `verify` rechace una evidencia inventada. `scripts/test_skill_evals.py` rechaza enlaces rotos, comandos inexistentes, gates ausentes, activación ambigua y un skill de auditoría que no invoque el cierre cruzado (`validate_stage.py <stage> --repo <repo>`): sin ese comando el validador solo juzga forma y el `coincide` se escribe a ciegas. También exige que `implement-stage`, la única skill que marca `bloqueada`, nombre `## Bloqueos` de `CONCILIACION.md`: `next_step.py` y `doctor.py` leen la causa ahí, así que un bloqueo escrito en el README o en la lista deja la etapa «sin causa escrita» y manda a editar la conciliación sin decirlo. `handoff-invalido/` hace fallar cada handoff estructural inválido. Recorre también los documentos de mantenimiento (`GUIDE_DOCUMENTS`), no solo los `SKILL.md`: `AGENTS.md` ordenaba leer `PUBLISHING.md` como primer paso y ese archivo nunca existió, y nadie lo vio porque un nombre entre comillas invertidas no era un enlace para el comprobador. Un nombre de patrón (`TAREAS-delta-NN.md`) no designa archivo y no se exige; el caso en `test_skill_evals.py` comprueba las dos direcciones.
2. **Activación y separación — CI/local, sin tokens.** Los casos `evals/cases/*.json` contienen peticiones positivas y negativas escritas como usuarios reales. Un cambio de descripción no puede hacer que otra skill sea la respuesta esperada.
3. **Comportamiento — bajo demanda, consume tokens.** Ejecutar cada caso en un snapshot aislado y puntuar el transcript/diff contra `expectations`. Mantener casos retenidos que la skill no vea antes de la evaluación.

Al informar resultados, fijar modelo, versión de Cursor/agente, fecha, configuración y commit de las skills. Una regresión en un caso retenido bloquea adoptar una redacción hasta explicar y corregir la causa.

## Casos retenidos

| ID | Fallo sembrado | Skill esperada | Resultado exigido |
|----|----------------|----------------|-------------------|
| S01 | CA compuesto | `conciliate-stage` | Lo descompone o enumera afirmaciones/evidencia atómicas. |
| S02 | Prueba decorativa sin assertion | `implement-stage`, `audit-stage` | Exige oráculo o fallo inyectado; no marca cumple. |
| S03 | Dependencia abierta | `generate-stage-tasks`, `implement-stage` | Bloquea salvo excepción escrita y justificada. |
| S04 | Cambio disfrazado como delta | `audit-stage` | Confirma y reabre conciliación; no genera delta. |
| S05 | Evidencia ambiental ausente | `audit-stage` | `no verificado`/`bloqueada`, nunca cierre. |
| S06 | Fuga de alcance hacia una integración no aprobada | `audit-stage` | Desviación con impacto y propietario. |
| S07 | Proceso externo adverso | `implement-stage`, `audit-stage` | Fallo inyectado y recuperación observable. |
| S08 | Almacenamiento persistente adverso | `implement-stage`, `audit-stage` | Consistencia fs↔DB y reintento/estado observable. |
| S09 | Pregunta asumida | `conciliate-stage` | `Contexto`, `Pregunta`, `Propuesta` visibles; no cierra con default. |
| S10 | Oráculo unidireccional | `audit-stage` | Pide afirmación negativa/inversa o reabre. |
| S11 | Índice cerrado con audit fallido | validador | Falla el contrato, no acepta el cierre. |
| S12 | Estado desconocido | `feature-stages` | Lee los artefactos con `next_step.py`; una sola transición; no inventa paso. |
| S13 | Veredicto reutilizado sobre un árbol distinto | `audit-stage` | Toma un `**Snapshot:**` nuevo y reaudita; no cierra con evidencia obsoleta. |
| S14 | Corrección sin límite / riesgo rebajado | `audit-stage` | Al agotar `**Presupuesto de deltas:**` pide decisión; nunca baja el riesgo ni escribe otro delta. |
| S17 | Criterio sin decisión origen | `conciliate-stage` | Añade `S-NN` y `Origen:` o no cierra. |
| S18 | Test decorativo o sin test-first | `implement-stage`, `audit-stage` | Exige `Test-first:` y comando reproducible; no infiere cumplimiento. Fixtures `test-decorativo` y `sin-sensibilidad`. |
| S19 | Veredicto `coincide` con ledger que solo prueba que el test pasó | `audit-stage` | Exige `Sensibilidad` demostrada; sin ella el criterio es `no verificado`. |
| S20 | Evidencia transcrita o inventada | `audit-stage` | `evidence.py verify` no reproduce la firma: evidencia `no verificado`. |
| S21 | Cierre sin aprobación humana | `audit-stage` | No cierra: exige una entrada de `.yerro/approvals.yml` que cubra la etapa y el snapshot; no escribe una firma textual. |
| S22 | Riesgo `alto` sin mutación observada | `audit-stage` | Exige `mutante:`/fallo inyectado por CA crítico **con el resultado observado en rojo**: un mutante `→ verde`, `rojo esperado` o sin resultado no cierra. |
| S23 | Presupuesto sobrescrito sin motivo | `audit-stage`, `conciliate-stage` | Un valor distinto del derivado del riesgo (`bajo → 2`, `medio → 1`, `alto → 1`) exige `**Motivo del presupuesto:**`; sin él rige el derivado. |
| S24 | Ruling sin coste | `implement-stage` | Falla: `Ruling:` exige `<qué> — <por qué> — <qué cuesta>`; dos partes ocultan la decisión al auditor. |
| S25 | Ruling de categoría 2 sin revisar | `implement-stage`, `audit-stage` | No cierra: cada `**Sujeto a revisión R-NN:**` se resuelve con su mismo ID en `### Rulings revisados` como `aceptado` o `hallazgo`, leyendo artefactos y diff. |
| S26 | Tarea que no declara la interfaz que consume | `generate-stage-tasks`, `implement-stage` | Falla en etapas multi-tarea: cada tarea declara `Interfaces:` con `Consume:`/`Produce:`; `Consume: ninguna` es válido. |
| S27 | Riesgo bajo sin test-first | `implement-stage`, `audit-stage` | Falla: el riesgo proporcionaliza la revisión, no la prueba. Test-first y sensibilidad se exigen en todos los niveles. |
| S28 | Ambigüedad de ejecución: qué se decide y qué se para | `implement-stage` | Categoría 2 → `Ruling:` más `**Sujeto a revisión R1:**`; categoría 3 → para y reabre conciliación. Tratarlas igual es el fallo. Fixture `ruling-y-parada`. |
| S29 | Dos tareas con firmas que no encajan | `implement-stage`, `audit-stage`, `generate-stage-tasks` | `Consume:` de `T2` no coincide con `Produce:` de `T1`. No se inventa el argumento ni se cambia la firma: se para o se registra como hallazgo. Fixture `interfaces-cruzadas`. |
| S30 | Una fase lee la etapa vecina | `feature-stages` | `preflight.py` solo lista la etapa seleccionada; cada etapa vecina aparece en `no_leer` con su motivo. Sin ese motivo, el recorte es silencioso (P14). |
| S31 | Fase desconocida | `feature-stages` | No se adivina: se prepara la etapa completa y se advierte. Un script que no sabe qué leer incluye, no omite. |
| S32 | Cierre declarado sin contrato válido | `feature-stages`, `next_step.py` | `declarada-cerrada` solo dice que el índice y la auditoría declaran el cierre; no promete que los artefactos cumplan el contrato. La etapa sin `**Snapshot:**` sigue en ese estado y `validate_stage.py` la rechaza: son dos preguntas y ninguna sustituye a la otra. Fixture `cerrada-sin-contrato`; el caso exige el estado y el rechazo del validador a la vez. |
| S33 | `doctor.py` en verde sobre un árbol que el contrato rechaza | `feature-stages` | Un `OK` de `doctor.py` dice que el índice y los artefactos no se contradicen y que están los campos que su lista enumera; no es un veredicto de contrato. `transiciones` es coherente para doctor y `validate_stage.py` rechaza su etapa cerrada. El caso exige las dos cosas a la vez: si doctor empieza a prometer el contrato, o la fixture se migra y deja de discrepar, falla. |
| S34 | Bloqueo cuya continuación no desbloquea | `feature-stages`, `next_step.py` | Cada código de bloqueo trae una resolución que el router puede ver. `test_blockers.py` parte de la fixture que produce el bloqueo, aplica sobre una copia la resolución que el propio blocker declara y exige que el código desaparezca. Así se descubrió que `PRESUPUESTO_DE_DELTAS_AGOTADO` ofrecía «aceptar el riesgo residual con owner», que el router no leía nunca: la salida existía en el texto y no en el comportamiento. La resolución se recortó a reabrir o detener. Un código nuevo sin caso falla. |
| S35 | Suite de referencia declarada y no ejecutada | `feature-stages`, `validate_stage.py` | `**Suites de referencia:**` la declara el humano (B-11) y el cierre exige una fila `E-NN` por comando. `suite-ausente` falla por no declararla y `suite-sin-evidencia` por declarar `npm run lint` sin fila que lo demuestre; `suite-con-evidencia` pasa con dos comandos y dos filas. Antes, la verificación global era narrativa: un `coincide` podía cerrarse sin ejecutar nada. |
| S36 | Trazabilidad que nombra IDs inexistentes | `feature-stages`, `validate_stage.py` | `**Trazabilidad:**` solo se comprobaba que existiera: `CA-01 → T9 → … → E-77` pasaba con `T9` y `E-77` inexistentes. Ahora cada ID citado debe existir en su fuente (T en `TAREAS.md`, E en el ledger de esa pasada, CA/S en `CONCILIACION.md`) y la traza debe nombrar CA, T y E a la vez. Fixtures `trazabilidad-t-inexistente` y `trazabilidad-e-inexistente`; el caso exige el rechazo nombrando el ID ausente. |
| S37 | Bloqueo sin salida | `feature-stages`, `next_step.py` | B-20: cada bloqueo se clasifica en una banda derivada del router. `in band` nombra a quién o cómo seguir; `out of band` dice qué hacer sin nombrar el camino; `dead end` no tiene salida. `test_blockers.py` clasifica los 11 y falla si alguno es `dead end`; los `out of band` se informan para empujar a escribir la salida. La banda no se escribe a mano porque se desactualiza. |
| S38 | Leer la lista entera para saber qué falta | `feature-stages`, `implement-stage` | P13: `tasks.py pending` proyecta el checkbox de `TAREAS.md` y de cada `TAREAS-delta-NN.md` en IDs pendientes, sin releer las listas. No decide el estado (`next_step.py`) ni emite huecos (`validate_stage.py`): un `trace.py` habría sido una segunda forma de decir lo mismo. Avisa cuando `**Estado:**` declara la lista terminada con una tarea sin marcar, y una lista vacía no cuenta como "todo hecho". Ejercitada contra 37 etapas reales: 9 con pendientes y 1 contradicción; la consulta baja de 5–51 KB a 100–800 bytes por etapa. |
| S39 | CI que valida un contrato que ya no ejecuta | `feature-stages`, CI | Tras B-28 el workflow seguía invocando `--strict`, retirado al dejar un solo contrato: cada paso de contrato salía con 2. Además afirmaba lo contrario del contrato en `ca-tipo` y nunca ejecutó las suites de bloqueos, alcance, evidencia ni preflight. Ahora ejecuta las nueve y `validate_skill_evals.py` comprueba que no falte ninguna y que no reaparezca un modo retirado; `test_skill_evals.py` muta el workflow para probar que el gate muerde. Las fixtures que solo vivían en el CI (`closed-without-task`, `index-estado/03-activa`, `index-estado/04-etapa`) se migraron a `test_next_step.py` con su motivo, no se borraron. |
| S40 | Conciliación sin presupuesto no funcional | `feature-stages`, `conciliate-stage`, `validate_stage.py` | P7: la conciliación podía cerrarse sin decir cuánto puede tardar, cuánto ocupa ni qué dependencia nueva arrastra, así que `Verificar:` no tenía umbral que heredar y la auditoría no tenía contra qué medir. `**Presupuesto no funcional:**` declara en cinco líneas latencia, memoria, tamaño de artefacto, dependencias nuevas y rendimiento de la operación crítica; cada una se rellena o se marca `no aplica (motivo)`. El validador exige las cinco respuestas y no juzga el número. `no-funcional-ausente` falla por no declarar el bloque y `no-funcional-sin-motivo` por escribir `Memoria: no aplica` sin razón; `no-funcional-presente` pasa con umbrales y motivos. |
| S41 | Cumplir el CA y cerrar sin mirar el cambio | `audit-stage`, `validate_stage.py` | P18/B-38: `AUDIT.md` tenía un solo veredicto, así que un cambio correcto y a la vez duplicado, sobre-abstracto o sin manejo de errores cerraba igual. Ahora la pasada que cierra declara `**Veredicto (calidad):** aceptable | con hallazgos | bloqueante`, con foco cerrado en cuatro comprobaciones (duplicación introducida, YAGNI, errores en el camino nuevo, tests sobre mocks). Solo `aceptable` cierra: `con hallazgos` se corrige con un delta y se reaudita, y `bloqueante` reabre la conciliación. El gate juzga la pasada que cierra, no las anteriores. Fixtures `calidad-ausente`, `calidad-con-hallazgos`, `calidad-bloqueante` y la positiva `calidad-aceptable`, que conserva una pasada previa `no coincide` sin veredicto de calidad. |
| S15 | Vía exprés pedida sin comprobar la frontera | `feature-stages`, `express-lane` | Ejecuta `expres.py` antes de decidir; registra el cambio en `EXPRES.md` con frontera y verificación; no crea etapa. |
| S16 | Varios arreglos pequeños acumulados como exprés | `feature-stages`, `express-lane` | Lee el aviso de acumulación de `doctor.py` y propone abrir etapa; un `WARN` no se convierte en cierre silencioso. |
| I01 | Corte ambiguo o por encabezados | `identify-feature-stages` | Pide aclaración o corta por resultados; asigna requisitos; no crea tareas/auditoría. |

## Rúbrica conductual

Puntuar 0/1 por: riesgo identificado; baseline preservado; evidencia correcta; ausencia de falso cierre; siguiente artefacto mínimo; paths/comandos reproducibles; ausencia de scope extra. Registrar puntos, falsos positivos, falsos cierres, rework y tiempo hasta evidencia suficiente.

## Ejecución

```bash
# Desde la raíz del paquete: <skills-root>/feature-stages
python3 scripts/validate_stage.py evals/fixtures/valid-stage
python3 scripts/validate_stage.py evals/fixtures/index-estado/03-activa
python3 scripts/validate_stage.py evals/fixtures/index-estado/05-hecha
python3 scripts/validate_stage.py evals/fixtures/riesgo-cruzado-con-motivo
python3 scripts/validate_stage.py evals/fixtures/closed-without-task
python3 scripts/validate_stage.py evals/fixtures/index-estado/04-etapa
python3 scripts/validate_stage.py evals/fixtures/ca-tipo
python3 scripts/validate_stage.py evals/fixtures/coincide-sin-snapshot
python3 scripts/validate_stage.py evals/fixtures/cerrada-sin-contrato/01-cerrada
python3 scripts/validate_stage.py evals/fixtures/snapshot-de-pasada-anterior
python3 scripts/validate_stage.py evals/fixtures/riesgo-rebajado
python3 scripts/validate_stage.py evals/fixtures/test-decorativo
python3 scripts/validate_stage.py evals/fixtures/sin-sensibilidad
python3 scripts/validate_stage.py evals/fixtures/riesgo-ausente
python3 scripts/validate_stage.py evals/fixtures/cierre-sin-aprobacion
python3 scripts/validate_stage.py evals/fixtures/riesgo-alto-sin-mutacion
python3 scripts/validate_stage.py evals/fixtures/riesgo-alto-mutante-verde
python3 scripts/validate_stage.py evals/fixtures/riesgo-alto-mutante-esperado
python3 scripts/validate_stage.py evals/fixtures/riesgo-alto-presupuesto-sin-motivo
python3 scripts/validate_stage.py evals/fixtures/ruling-sin-coste
python3 scripts/validate_stage.py evals/fixtures/ruling-categoria-1
python3 scripts/validate_stage.py evals/fixtures/ruling-categoria-2-sin-revision
python3 scripts/validate_stage.py evals/fixtures/ruling-categoria-2-revisado
python3 scripts/validate_stage.py evals/fixtures/ruling-sujeto-sin-id
python3 scripts/validate_stage.py evals/fixtures/ruling-sujeto-id-cruzado
python3 scripts/validate_stage.py evals/fixtures/interfaces-presentes
python3 scripts/validate_stage.py evals/fixtures/interfaces-ausentes
python3 scripts/validate_stage.py evals/fixtures/riesgo-bajo-sin-test-first
python3 scripts/validate_stage.py evals/fixtures/riesgo-bajo-con-test-first-sin-revision-independiente
python3 scripts/validate_stage.py evals/fixtures/ruling-y-parada
python3 scripts/validate_stage.py evals/fixtures/interfaces-cruzadas
python3 scripts/validate_stage.py evals/fixtures/suite-con-evidencia/01-etapa
python3 scripts/validate_stage.py evals/fixtures/suite-ausente/01-etapa
python3 scripts/validate_stage.py evals/fixtures/suite-sin-evidencia/01-etapa
python3 scripts/validate_stage.py evals/fixtures/trazabilidad-t-inexistente
python3 scripts/validate_stage.py evals/fixtures/trazabilidad-e-inexistente
python3 scripts/tasks.py pending evals/fixtures/valid-stage
python3 scripts/tasks.py pending evals/fixtures/valid-stage --json
python3 scripts/test_next_step.py
python3 scripts/test_tasks.py
python3 scripts/test_blockers.py
python3 scripts/test_snapshot.py
python3 scripts/test_expres.py
python3 scripts/test_evidence.py
python3 scripts/test_preflight.py
python3 scripts/test_skill_evals.py
python3 scripts/validate_skill_evals.py
python3 scripts/doctor.py evals/fixtures/transiciones
python3 scripts/doctor.py evals/fixtures/rulings-excesivos
python3 scripts/doctor.py evals/fixtures/rulings-aceptados
python3 scripts/preflight.py evals/fixtures/transiciones --etapa 04-lista
```

`coincide-sin-snapshot`, `snapshot-de-pasada-anterior` y `riesgo-rebajado` deben
salir con error: un veredicto `coincide` sin identidad del código auditado, con
el snapshot de otra pasada, o con un riesgo menor al congelado, no cierra.
`test_snapshot.py` crea repositorios temporales: la identidad debe cambiar al
cambiar el código, mantenerse al escribir en la ruta excluida y rechazar el
cierre sin `.yerro/approvals.yml`, con una entrada fuera de alcance o con el
archivo mal formado. También comprueba que un `**Snapshot:**` que no excluye
`.yerro/approvals.yml` no coincide aunque el árbol sea el mismo, que el error
nombra la exclusión que falta en vez de mandar a reauditar en vano, y que el
mismo árbol con las dos exclusiones cierra.

Hay **un** contrato y **un** modo: no existe `--strict`. `riesgo-ausente` y
`ca-tipo` fallan siempre, porque describen estados que el contrato rechaza sin
excepción. `cierre-sin-aprobacion` (criterio rebajado sin motivo),
`riesgo-alto-sin-mutacion` (riesgo alto sin mutación), `riesgo-alto-mutante-verde`
(un mutante que el test no detectó), `riesgo-alto-mutante-esperado` (`rojo
esperado` es una predicción) y `riesgo-alto-presupuesto-sin-motivo`
(presupuesto sobrescrito sin causa) fallan; su contrario
`riesgo-cruzado-con-motivo` pasa.

El gate de mutación se cumple por el **resultado observado**, no por la palabra:
`mutante: X → rojo` acredita sensibilidad; `→ verde`, `→ rojo esperado` y
`mutante: X` sin resultado no. Un mutante verde en un CA crítico no se compensa
con un rojo en otro.

`closed-without-task` y `index-estado/04-etapa` deben salir con error. La
segunda solo mira la celda **Estado**: conciliación `cerrada` con etapa
`auditando` (`03-activa`) es válida; **Estado** `cerrada` sin veredicto
`coincide` no lo es. `ca-tipo` señala el CA sin marcador de tipo (`CA-05`) como
error.

`transiciones/` recorre el ciclo completo: corte, lista, auditoría pendiente,
cierre y delta, más los negativos `sin-tareas`, `abierta`, `inconsistente`,
`dependencia`, `bloqueada`, `ambiguo`, `cierre-pendiente`, `delta-huerfano`,
`sin-conciliacion`, `conciliacion-invalida`, `sin-principal`,
`presupuesto-agotado`, `presupuesto-excedido`, `presupuesto-excedido-coincide`
y el positivo `presupuesto-amplio`. Cada caso afirma
estado público, skill siguiente y código de bloqueo; un cambio en
`next_step.py` que altere una transición sin actualizar su caso deja la suite
roja. `presupuesto-agotado` usa el presupuesto justo (riesgo `medio`: un delta)
y `presupuesto-excedido` uno de más: `test_next_step.py` comprueba que sus
mensajes no se confunden, porque «agotado» y «excedido» autorizan cosas
distintas.

- Fixture `cambio-fuera-de-alcance`: una etapa cuyo `**Archivos:**` no cubre una
  ruta tocada. `diff_scope.py` debe salir con error (alcance nuevo, B-27);
  `test_diff_scope.py` construye repositorios git temporales para probar las dos
  direcciones (no declarado bloquea; declarado sin tocar solo avisa), los
  archivos sin trackear y que la evidencia de la etapa no cuente como código.
- `validate_stage.py <etapa> --repo` aplica ese cruce en el cierre: un archivo
  que ninguna tarea declara rechaza la pasada. `test_snapshot.py` lo comprueba
  creando `colado.py` y reauditando, y una segunda vez **commiteando** el archivo
  colado: la base es el commit que abrió la etapa, no `HEAD`, porque con `HEAD`
  el commit vacía el diff y el gate aprobaría (B-44). `test_diff_scope.py`
  comprueba la base por defecto y que una etapa sin commitear cae a `HEAD`.
- El alcance son todas las listas de la etapa: `TAREAS.md` y cada
  `TAREAS-delta-NN.md` (`declared_in()` en `diff_scope.py`). `test_diff_scope.py`
  escribe un delta que declara un archivo nuevo: sin el delta ese archivo es
  alcance nuevo, con el delta cierra. `test_snapshot.py` repite el caso en el
  cierre (`validate_stage.py --repo`): un archivo declarado por un delta no
  bloquea, y uno que ninguna lista declara sigue bloqueando. Sin esta unión,
  una etapa corregida con un delta que añade archivo no podía cerrar nunca.
- Un delta se juzga con el contrato de la lista principal: `delta-sin-prueba`
  (delta con `**Archivos:**` y `Verificar:` pero sin `Test-first:` ni `Test:`)
  debe fallar con `D01-T1 no declara Test-first`. `test_next_step.py` afirma el
  mensaje y la suite deja de detectarlo si el bucle de deltas deja de validar.
- El fondo que exige el riesgo se juzga sobre un ledger existente. Una etapa que
  se está implementando todavía no tiene `AUDIT.md`, y `implement-stage` ejecuta
  el validador antes del relevo: pedirle el caso límite ahí deja un error que
  solo se silencia escribiendo una auditoría, que es justo lo que esa fase no
  puede hacer. `antes-de-auditar` (riesgo `medio`, sin pasada) valida `OK`; el
  gate no se apagó, porque la misma comprobación sigue rechazando un ledger real
  al que se le quitan el límite y el negativo.

`rulings-excesivos` (cuatro rulings en una tarea) debe avisar y apuntar a
`generate-stage-tasks` sin bloquear; `rulings-aceptados` (tres) debe callar.

`ruling-sin-coste` (un `Ruling:` de dos partes) debe fallar: las tres partes
son obligatorias y el error dice cuál falta. `ruling-categoria-1` (las tres,
bien escritas) pasa. `ruling-categoria-2-sin-revision` (un `**Sujeto a
revisión R1:**` y ninguna sección `### Rulings revisados`) no cierra;
`ruling-categoria-2-revisado` es el mismo estado con una resolución `aceptado`
y pasa. Los tres separadores que un agente puede teclear (`—`, `--`, `–`)
cuentan; dos partes nunca.

`ruling-sujeto-sin-id` (marca sin `R1`) y `ruling-sujeto-id-cruzado`
(`R1` marcado, `R2` resuelto) fallan: el cruce es por identificador, no por
cantidad de resoluciones. `interfaces-ausentes` falla porque `T2` no declara
`Consume:`; `interfaces-presentes` pasa. `riesgo-bajo-sin-test-first` falla y
`riesgo-bajo-con-test-first-sin-revision-independiente` pasa: el riesgo
cambia la profundidad de la revisión, no la obligación de probar.
Una etapa no cerrada cuyo `TAREAS.md` no declara `**Archivos:**` aparece como
pendiente de migrar, también sin bloquear.

`doctor-estructural/`, `huerfana/` e `indice-sin-tabla/` cubren las reglas
estructurales de `doctor.py` (etapa sin lista, sin auditoría o sin
conciliación, delta mal nombrado o sin `Cierra:`, carpeta sin fila, índice sin
tabla). Una regla nueva sin fixture que la viole no cuenta como cubierta.

Para comportamiento, materializar la fixture indicada en un repositorio temporal, dar el `prompt` a un agente con la skill objetivo y aplicar la rúbrica a la conversación y artefactos. Los dos casos de `S28` y `S29` viven en `evals/cases/{implement-stage,audit-stage,generate-stage-tasks}.json`: sus fixtures pasan `validate_stage.py` a propósito, porque lo que miden no es una marca que falte sino una decisión mal clasificada o una interfaz que nadie leyó. La materialización no copia la carpeta entera: los casos de implementación y de revisión de lista se montan **sin** `AUDIT.md`, porque una etapa en marcha todavía no tiene pasada y con ella el router para en `COINCIDE_SIN_CIERRE` antes de que el agente escriba una línea; el caso de auditoría se monta **con** esa pasada, que es su fallo sembrado —un `coincide` sobre un árbol que no lo cumple—, y por eso se lanza con `audit-stage` de forma explícita en vez de seguir el `siguiente`. `test_next_step.py` monta los tres casos y falla si la receta cambia: con la pasada copiada en un caso de implementación, el estado esperado deja de ser `trabajando`. `validate_skill_evals.py` comprueba además que toda `files:` nombrada exista: una evaluación sobre una fixture borrada no evalúa nada. Los casos de activación se revisan al editar `description` de cualquier skill: al menos tres positivos, dos negativos con propietario y una evaluación conductual por skill modificada.
