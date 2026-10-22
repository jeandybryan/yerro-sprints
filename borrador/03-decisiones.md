# 03 — Decisiones

> Formato inspirado en el propio paquete: cada decisión tiene ID estable
> `B-NN` (borrador), fecha, motivo y consecuencias. **No se recicla un ID.**
>
> Aquí solo entran decisiones **del diseño del endurecimiento**. Las decisiones
> de producto (licencia, distribución, tags, hosts, owner) siguen fuera, en
> `GOVERNANCE.md`, y no se tocan desde esta carpeta.

Estados: `propuesta` | `acordada` | `descartada`. Las que necesitan tu visto
bueno están marcadas **⚠ requiere acuerdo**.

---

## Decisiones de forma

### B-01 — La carpeta `borrador/` es no normativa
**Fecha:** 2026-10-22
**Estado:** `acordada`
**Motivo:** permite iterar sin que las skills publiquen algo no cerrado, y sin
que `validate_skill_evals.py` lo inspeccione por error.
**Consecuencias:** nada de aquí se enlaza desde `README.md`, skills o
`templates.md` hasta que se decida publicar. No se añade a `.gitignore` por
defecto: es trabajo a versionar salvo que se decida lo contrario.

### B-02 — Una mejora que cambia un gate no se publica como documentación
**Fecha:** 2026-10-22
**Estado:** `acordada`
**Motivo:** regla vigente de `AGENTS.md` (fixture antes que script).
**Consecuencias:** cada P* que se acepte trae, en el mismo PR: fixture que falla
con el contrato viejo, caso de test, fila en `EVALUATION.md`, entrada en
`CHANGELOG.md`.

### B-03 — La evidencia se mide por sensibilidad, no por presencia
**Fecha:** 2026-10-22
**Estado:** `propuesta` ⚠
**Motivo:** es la tesis del borrador; sin esto, el resto es ornamento.
**Consecuencias:** si se acuerda, `Test-first:` deja de ser una casilla y pasa
a ser una propiedad verificable. Afecta a `validate_stage.py`,
`decision-traceability.md`, `AUDIT.md` y `TAREAS.md`.

### B-04 — El contrato sigue siendo la fuente de verdad; las herramientas también
**Fecha:** 2026-10-22
**Estado:** `acordada`
**Motivo:** el paquete declara que Python es opcional ("solo para
validadores estructurales"). Las nuevas herramientas (evidencia, diff) no deben
romper esa propiedad.
**Consecuencias:** toda verificación nueva es **opcional para operar** y
**requerida para cerrar** con `--strict`. El flujo manual sigue siendo posible;
el flujo automático es el que presume.

---

## Decisiones de alcance

### B-05 — No se añade una séptima skill
**Fecha:** 2026-10-22
**Estado:** `propuesta` ⚠
**Motivo:** el README y `AGENTS.md` fijan seis fases. P9 (etapa ligera) se
propone como **variante de plantilla**, no como fase nueva.
**Consecuencias:** si P9 se acepta, `validate_stage.py` conoce un campo `Modo`
y la etapa ligera comparte transiciones. Si se decide que P9 merece una skill,
esto se revierte explícitamente.

### B-06 — La etapa ligera (P9) se difiere
**Fecha:** 2026-10-22
**Estado:** `propuesta` ⚠ (mi recomendación)
**Motivo:** reduce fricción, pero multiplica los casos de transición y diluye
la garantía de las seis fases. Primero se mide si P1/P3/P5/P7 basta.
**Consecuencias:** P9 queda `diferida` en esta iteración salvo objeción. Se
retoma con datos: cuántas veces se usa la vía exprés por encima de su frontera.

### B-07 — La vía exprés gana verificación, no gate de etapa
**Fecha:** 2026-10-22
**Estado:** `propuesta` ⚠
**Motivo:** hoy el modo más usado no deja prueba de que se probó. La solución
mínima es exigir comando + resultado y confirmación humana; no convertir la
vía exprés en una etapa encubierta.
**Consecuencias:** `doctor.py` gana errores (no solo `WARN`) por acumulación y
por fila incompleta.

---

## Decisiones sobre roles

### B-08 — Auto-auditoría permitida solo con revisión humana
**Fecha:** 2026-10-22
**Estado:** `propuesta` ⚠
**Motivo:** el host no puede verificar quién escribe; fingir separación de
roles sería teatro. Lo que sí se puede exigir es una **marca humana** cuando
quien audita es quien implementó.
**Consecuencias:** `AUDIT.md` registra implementador, auditor y aprobador. Si
implementador = auditor, la aprobación humana es obligatoria para cerrar.

### B-09 — La marca de aprobación no se auto-rellena por el agente
**Fecha:** 2026-10-22
**Estado:** `propuesta` ⚠ (ver Q3)
**Motivo:** si el agente puede escribir `<persona>`, la marca es falsificable y
no protege de nada.
**Consecuencias:** se necesita un origen externo a la conversación
(configuración del usuario, commit firmado, o un comando explícito tipo
`python3 scripts/approve.py --stage NN --by <nombre>` que el agente no
invoca sin instrucción). La solución exacta es Q3.

---

## Decisiones sobre evidencia y riesgo

### B-10 — El presupuesto de deltas se deriva del riesgo
**Fecha:** 2026-10-22
**Estado:** `propuesta` ⚠ (los números exactos son Q1)
**Motivo:** una constante global trata igual un cambio cosmético y uno de
seguridad.
**Consecuencias:** `bajo → 2`, `medio → 1`, `alto → 0` (recomendación). Un
valor distinto exige motivo escrito en la conciliación.

### B-11 — La suite de referencia la declara el humano
**Fecha:** 2026-10-22
**Estado:** `propuesta` ⚠
**Motivo:** exigir "toda la suite" en repos grandes es caro; exigir "nada" no
protege. La suite de referencia es una decisión de operador, no del agente.
**Consecuencias:** nuevo campo `Suites de referencia:` y `Comandos de calidad:`
en `CONCILIACION.md`; el audit los ejecuta y registra.

### B-12 — La mutación obligatoria empieza en riesgo `medio`
**Fecha:** 2026-10-22
**Estado:** `propuesta` ⚠
**Motivo:** el coste de escribir un mutante es real; riesgo `bajo` se cubre con
oráculo mínimo + caso negativo.
**Consecuencias:** riesgo `alto` exige mutación por CA crítico o justificación
de herramienta ausente.

---

## Decisiones sobre coste y determinismo

### B-13 — El determinismo es el default; el LLM es la excepción justificada
**Fecha:** 2026-10-22
**Estado:** `propuesta` ⚠
**Motivo:** un gate que el agente debe recordar se paga en cada turno y falla
en silencio; un script se paga una vez y falla ruidosamente.
**Consecuencias:** ninguna instrucción nueva entra a `skills/` sin pasar el test
de la "regla determinizable" (`06-economia-de-tokens.md`, Parte B). Una
instrucción que podría ser un script es deuda de tokens.

### B-14 — La calidad no se negocia con el presupuesto de contexto
**Fecha:** 2026-10-22
**Estado:** `propuesta` ⚠
**Motivo:** el ahorro tiene un lado peligroso: omitir. Un gate barato que
aprueba código malo cuesta más que el token que ahorró.
**Consecuencias:** (1) ningún gate se sustituye por heurística; (2) ante la
duda, el script que no sabe decidir **incluye** el contexto, no lo omite;
(3) todo recorte es visible en el artefacto; (4) una mejora de coste que baja
la rúbrica de calidad se trata como regresión (P14).

### B-15 — El presupuesto de contexto se mide en líneas, no en tokens
**Fecha:** 2026-10-22
**Estado:** `propuesta` ⚠
**Motivo:** el conteo de tokens depende del host y del modelo; el de líneas es
reproducible en CI. Un presupuesto que no se puede medir en CI no es un gate.
**Consecuencias:** `preflight.py` emite líneas (gate) y una estimación de
tokens (informativa, con margen de error declarado). Subir un presupuesto exige
motivo escrito, igual que el presupuesto de deltas.

### B-16 — El coste es una dimensión de la evaluación, no la única
**Fecha:** 2026-10-22
**Estado:** `propuesta` ⚠
**Motivo:** sin métrica de coste, la primera mejora barata parecerá una victoria
aunque empeore la calidad; sin la rúbrica, el coste se optimiza a costa del
resultado.
**Consecuencias:** P10/P15 registran calidad **y** coste por caso. Un caso que
pasa con menos contexto y peor rúbrica es regresión, no mejora.

### B-17 — El tamaño no decide la ruta; la reanudación sí
**Fecha:** 2026-10-22
**Estado:** `propuesta` ⚠
**Origen:** `07-referencias-gentle-ai.md` C1 (gentle-ai, `docs/trigger-rules.md`).
**Motivo:** "Counts of files, commands, tests, fixes … **never decide it**."
Nuestra vía exprés (1 archivo, ≤20 líneas) mide lo más barato de medir y lo
menos relacionado con el riesgo. Un cambio de tres archivos entendido y sin
riesgo es pequeño; uno de una línea en auth no lo es.
**Consecuencias:** la vía exprés mantiene el conteo como **criba inicial**
(barata y determinista), pero añade dos vetos:
1. la **lista de ítems de riesgo alto** (datos, seguridad, contratos
   compartidos, concurrencia, entrega, sin test que detecte la regresión);
2. el **test de reanudación**: ¿se podría retomar desde la petición + `git diff`?
Un cambio que falla cualquiera de los dos **abre etapa**, sin override.

### B-18 — Un test existente que falla no se edita; se detiene y se reporta
**Fecha:** 2026-10-22
**Estado:** `propuesta` ⚠
**Origen:** `07-referencias-gentle-ai.md` O4. En su caso, esa regla sola
"caught **nine wrong premises**".
**Motivo:** es la regla de menor coste del conjunto. Un test que falla suele
tener razón; el agente bajo presión lo "arregla" cambiando el test.
**Consecuencias:** `implement-stage` y `audit-stage` la incorporan como
prohibición explícita. Si un test preexistente falla, la etapa pasa a
`necesita-decision` con el test citado, no se toca el test.

### B-19 — Todo bloqueo debe traer una continuación que funcione
**Fecha:** 2026-10-22
**Estado:** `propuesta` ⚠
**Origen:** `07-referencias-gentle-ai.md` C5. Su caso: mensajes "corre X" con
tests verdes que verificaban que el texto se emitía, y **nadie había ejecutado
X**; no funcionaba durante meses.
**Motivo:** `next_step.py` ya lista bloqueos "con su resolución", pero nada
prueba que la resolución resuelva.
**Consecuencias:** cada código de bloqueo gana un caso de test que **ejecuta la
continuación declarada** y comprueba que el bloqueo desaparece. Una
continuación que no desbloquea es un defecto, no un texto.

### B-20 — La evaluación mide también la fricción
**Fecha:** 2026-10-22
**Estado:** `propuesta` ⚠
**Origen:** `07-referencias-gentle-ai.md` C6.
**Motivo:** el benchmark de gentle-ai clasifica cada bloqueo como *in band*
(dice qué ejecutar), *out of band* (no dice nada) o *dead end* (no hay salida).
No mide velocidad "porque depende del proveedor y del día; la fricción es tuya".
**Consecuencias:** `EVALUATION.md` gana una tercera dimensión, determinista y sin
tokens: todo bloqueo de fixture debe clasificarse en una de las tres bandas.
Un `dead end` es error estructural, no un aviso.

---

## Decisiones derivadas de superpowers

### B-21 — En ejecución se decide y se registra; no se detiene (Modelo C)
**Fecha:** 2026-10-22
**Estado:** `acordada` ✅ (usuario, 2026-10-22)
**Origen:** `08-referencias-superpowers.md` C11, matizado por la conversación
sobre Q15.
**Motivo:** "A session parked on a question costs their whole day." Una
ambigüedad resoluble dentro del plan aprobado no justifica detener al humano.
Pero "reversible ⇒ decide" a secas permitiría colar alcance nuevo como
`Ruling:`. Por eso se decide **por clase de decisión**, no por duda.
**Consecuencias:** durante `implement-stage` hay tres categorías con respuesta
obligatoria distinta:

| Categoría | Qué es | Qué hace el agente |
| --- | --- | --- |
| 1. Detalle de implementación | No cambia lo que el usuario recibe: separador de CSV, nombre interno, librería equivalente, orden interno de pasos | Decide y registra `Ruling:` con coste |
| 2. Efecto observable, reversible | Cambia algo visible pero deshacer es trivial y el alcance no cambia: texto de error, formato de fecha, límite por defecto | Decide, registra y marca `**Sujeto a revisión:**`; el auditor puede convertirlo en hallazgo |
| 3. Intención, alcance o criterio | Cambia lo pedido o lo aceptado: columna extra, endpoint nuevo, otro CA | **Para y reabre `conciliate-stage`.** Sin excepciones |

Por encima de las categorías, cuatro paradas incondicionales: operación
irreversible o destructiva, seguridad, efecto fuera del worktree (merge, push,
publicación) y plan tan roto que todo es adivinar.
La regla de `conciliate-stage` de no cerrar con supuestos **no cambia**: aplica
al baseline. La diferencia es el **momento**: conciliar = decidir con el humano;
implementar = ejecutar y registrar.
La categoría 3 se puede **comprobar** en el diff (¿aparece algo que ningún CA
menciona?), así que no depende solo de la honestidad del agente (B-27).

> **Pendiente de tu respuesta:** en la conversación de Q15 elegiste
> explícitamente el Modelo C y la marca de la categoría 2. Para las categorías 1
> y 3 no hubo elección: están contenidas en el Modelo C tal como lo describí.
> Las cuatro paradas incondicionales son la única parte donde podrías querer
> otra cosa (por ejemplo, añadir "cambio de dependencia externa").

### B-25 — Un `Ruling:` sin coste de equivocarse es inválido
**Fecha:** 2026-10-22
**Estado:** `acordada` ✅ (usuario, 2026-10-22)
**Origen:** Trampa 2 de Q15.
**Motivo:** un `Ruling:` sin la tercera parte **oculta** la decisión en lugar de
exponerla: el humano no sabe qué evaluar al revisar el diff. Un registro flojo es
peor que una pregunta.
**Consecuencias:** el formato es cerrado y las tres partes son obligatorias:
`Ruling: <qué decidí> — <por qué> — <qué cuesta si me equivoco>`.
`validate_stage.py` rechaza un `Ruling:` al que le falte una parte. Una decisión
tomada sin registro no cuenta como decidida.

### B-26 — La categoría 2 existe para no forzar todo a los extremos
**Fecha:** 2026-10-22
**Estado:** `acordada` ✅ (usuario, 2026-10-22)
**Origen:** Respuesta del usuario a la pregunta 2 de Q15.
**Motivo:** sin categoría 2, cualquier cosa visible obligaría a preguntar, y con
ello volveríamos al Modelo A en la práctica. La marca `**Sujeto a revisión:**`
mantiene la visibilidad sin detener el trabajo.
**Consecuencias:** `AUDIT.md` gana una sección de rulings revisados; un ruling de
categoría 2 no resuelto (ni aceptado ni convertido en hallazgo) **impide el
cierre**. La categoría 1 no requiere revisión del auditor; solo queda en el
ledger.

### B-27 — El cambio de alcance se detecta en el diff, no en la confesión
**Fecha:** 2026-10-22
**Estado:** `acordada` ✅ (usuario, 2026-10-22)
**Origen:** Trampa 1 de Q15; coherente con B-13 (determinista antes que LLM).
**Motivo:** si la única barrera contra un ruling de categoría 3 es que el agente
se clasifique bien a sí mismo, la regla es una promesa. El diff sí es
comprobable.
**Consecuencias:** el validador compara los archivos y símbolos tocados por la
etapa contra el alcance declarado en `TAREAS.md`. Un archivo que ninguna tarea
declara, o una superficie nueva que ningún CA menciona, abre
`necesita-decision` con la evidencia enlazada. Los rulings no se validan por
texto libre: se validan por **coherencia con el diff declarado**.

### B-28 — Migración dura: un solo contrato, sin soporte legado
**Fecha:** 2026-10-22
**Estado:** `acordada` ✅ (usuario, 2026-10-22)
**Origen:** Q18.
**Motivo:** *"lo más saludable es que migren a la nueva, para no tener que darle
soporte a lo legado."* Mantener `--strict` y su alternativa de advertencias es,
literalmente, soporte legado: dos caminos de código y cada fixture probada dos
veces.
**Consecuencias:**
1. Al publicar B-27 desaparece `--strict` y el camino de advertencia. Hay **un**
   contrato y **un** modo de validación. Las fixtures legadas (las que hoy
   dependen de "avisa sin `--strict` y falla con él", como `riesgo-ausente` y
   `ca-tipo`) se convierten en **positivas**: deben pasar siempre, o se eliminan
   si no describen un estado que el contrato nuevo permita.
2. **No hay etapa "a medio migrar".** Una etapa a la que le falta `**Archivos:**`
   no valida. La migración se hace antes de publicar o la etapa se cierra con la
   versión anterior del paquete.
3. **Migrar es re-conciliar el alcance, no rellenar una casilla.** `**Archivos:**`
   se deriva de tareas y CA, nunca del diff ya producido; derivarlo del diff
   blanquea justo el caso que B-27 persigue.
4. Cada etapa migrada registra `**Migrada:** AAAA-MM-DD (origen: diff |
   re-conciliación)` en `TAREAS.md`, para que una migración desde el diff se vea
   en auditoría. La marca es informativa, no es un gate.
5. `AGENTS.md` gana la regla: **un gate nuevo no deja modo legado**; si necesita
   convivencia, se implementa como feature de una versión con fecha de retirada,
   no como parámetro eterno.

### B-29 — Los scripts deciden fronteras mecánicas, nunca alcance ni cierre
**Fecha:** 2026-10-22
**Estado:** `acordada` ✅ (Q10, 2026-10-22)
**Origen:** Q10; refuerza B-13 y B-14.
**Motivo:** el eje "determinista antes que LLM" necesita una frontera explícita,
o cada propuesta nueva discute si un script puede decidir la suya.
**Consecuencias:** un script puede decidir **conteos, rutas excluidas,
acumulación, presupuesto derivado, coherencia de snapshot y qué archivo declaró
la tarea**. No puede decidir **alcance, riesgo ni cierre**: esos los aprueba una
persona. La prueba de la frontera: *si la regla necesita interpretar intención,
no va a un script.*

### B-30 — Operar no requiere Python; cerrar con evidencia sí
**Fecha:** 2026-10-22
**Estado:** `acordada` ✅ (Q6, 2026-10-22)
**Origen:** Q6.
**Motivo:** P2 introduce `evidence.py`, que **ejecuta** comandos. Mantener la
promesa "Python es opcional" obligaría a reimplementar la captura de evidencia
en cada host, que cuesta más que corregir una frase.
**Consecuencias:** `README.md` se corrige a *"operar no requiere Python; cerrar
con evidencia sí"*. El validador y `evidence.py` se declaran herramienta de
cierre, no de operación.

### B-31 — El coste se mide en lo reproducible; los tokens son informativos
**Fecha:** 2026-10-22
**Estado:** `acordada` ✅ (Q11, 2026-10-22)
**Origen:** Q11, coherente con B-15.
**Motivo:** los tokens dependen del host y del día; un gate sobre una métrica
que CI no puede reproducir no es un gate.
**Consecuencias:** el reporte de coste obliga **líneas leídas, número de
lecturas y número de ejecuciones**. Los tokens se registran si el host los
expone, y nunca deciden nada.

### B-32 — El auditor revisa rulings solo con artefactos, no con memoria
**Fecha:** 2026-10-22
**Estado:** `acordada` ✅ (Q19, 2026-10-22)
**Origen:** Q19, `08-referencias-superpowers.md` C12.
**Motivo:** *"implementer self-review never replaces the task review"*, y el
revisor recibe *"precisely crafted context — never your session's history"*.
**Consecuencias:** la revisión de un `**Sujeto a revisión:**` la hace el
`audit-stage` leyendo `TAREAS.md`, `CONCILIACION.md` y el diff. **No vale** el
argumento "lo decidí porque…" que no esté escrito en el `Ruling:`. Un ruling que
no explica su decisión es un hallazgo: así B-25 se paga sola.

### B-33 — Más de tres rulings por tarea es una tarea mal escrita
**Fecha:** 2026-10-22
**Estado:** `acordada` ✅ (Q20, 2026-10-22)
**Origen:** Q20.
**Motivo:** los rulings resuelven ambigüedad **residual**. Cuatro no son
ambigüedad, son una tarea sin especificar disfrazada de tarea.
**Consecuencias:** `doctor.py` avisa cuando una tarea acumula **más de tres**
rulings de categoría 1 y apunta a `generate-stage-tasks`. Es **aviso, no
bloqueo**: una tarea de migración puede producir cuatro detalles legítimos y
partirla en cuatro tareas de una línea sería peor.

### B-34 — Una `Test:` debe invocar un runner conocido; lista negra y blanca
**Fecha:** 2026-10-22
**Estado:** `acordada` ✅ (Q4, 2026-10-22)
**Origen:** Q4, P1 nivel 1.
**Motivo:** el validador no puede juzgar si un comando arbitrario prueba algo,
pero sí puede rechazar el vacío evidente y reconocer el runner del proyecto.
**Consecuencias:**
1. **Lista negra** por defecto: `true`, `false`, `:`, `echo`, `sleep`, `cat`,
   `ls` y `bash -c` de trivio. Rechazo directo.
2. **Lista blanca** declarada en `CONCILIACION.md` (`Runners: pytest | npm test |
   …`) para proyectos con runner propio.
3. La lista blanca **no sustituye** a la sensibilidad de P1 nivel 2: reconoce el
   instrumento, no demuestra que el test pruebe algo. `pytest -q` sobre un test
   vacío pasa la lista y falla la sensibilidad.
4. Si el proyecto no declara runners y el comando no está en la negra, se
   **avisa**; con B-28 (sin modo legado) ese aviso es la única transición
   posible y debe resolverse declarando el runner.

### B-35 — La mutación es un procedimiento, no una herramienta
**Fecha:** 2026-10-22
**Estado:** `acordada` ✅ (Q5, 2026-10-22)
**Origen:** Q5, P1 nivel 3.
**Motivo:** el objetivo del gate es **ver el rojo**, no instalar mutmut. Exigir
herramienta rompe la portabilidad y presupone el lenguaje del proyecto.
**Consecuencias:** para riesgo `alto` cada CA crítico registra en el ledger
`mutante: <descripción>` y `resultado: rojo`, con el procedimiento que sea
(herramienta, edición manual, fallo inyectado, oráculo alterado). Si el auditor
no puede reproducir el procedimiento, el criterio es `no verificado`, no
`cumple`.

### B-36 — `Suites de referencia: ninguna` solo en riesgo bajo y con motivo
**Fecha:** 2026-10-22
**Estado:** `acordada` ✅ (Q7, 2026-10-22)
**Origen:** Q7, B-11, P5.
**Motivo:** riesgo `medio`/`alto` con suite vacía es exactamente el escenario
donde vive el falso cierre; en riesgo bajo, forzar un comando es ceremonia.
**Consecuencias:** `CONCILIACION.md` admite `Suites de referencia: ninguna`
**solo** si el riesgo congelado es `bajo` y hay motivo escrito. Para `medio` y
`alto` exige al menos un comando global. El validador cruza riesgo ↔ suite.

### B-37 — La aprobación vive en un archivo versionado fuera del alcance del agente
**Fecha:** 2026-10-22
**Estado:** `acordada` ✅ (Q3 + Q12, 2026-10-22)
**Origen:** Q3, Q12, B-08, B-09.
**Motivo:** una marca textual que el agente puede escribir no es una marca.
El usuario descartó el flujo de PR como requisito; el archivo versionado da la
misma garantía sin PR y sin firmar commits.
**Consecuencias:**
1. La aprobación vive en **`.yerro/approvals.yml`** (ruta configurable), fuera de
   la carpeta de la etapa y del árbol que el agente edita.
2. Se **edita a mano y se versiona**. No hay PR, ni commit firmado, ni
   herramienta: es un archivo más del repo, como `.gitignore`.
3. El validador lee la entrada de la etapa (`id`, `aprobado-por`, `fecha`,
   `alcance`) y la cruza con el snapshot auditado. Sin entrada, la etapa no
   cierra.
4. **Desaparece la marca textual** `**Aprobado por:**` de `CONCILIACION.md` y
   `AUDIT.md`. Si el agente puede escribirla, el archivo también tendría que
   poder escribirla; por eso el archivo se declara **no escribible por el
   agente** y su edición es del humano.
5. El commit firmado y `approve.py` quedan como **extensiones opcionales** de
   equipo, no como base.

> ⚠ **Riesgo explícito:** un archivo en el repo lo puede editar cualquier
> proceso con acceso al repo, agente incluido, **salvo que el host lo impida**.
> La garantía es social y de revisión del diff, no criptográfica. Si algún día
> se necesita garantía fuerte, se sube a commit firmado sin cambiar el resto.

### B-38 — El veredicto de calidad tiene cuatro comprobaciones cerradas
**Fecha:** 2026-10-22
**Estado:** `acordada` ✅ (Q16, 2026-10-22)
**Origen:** Q16, B-22, P18.
**Motivo:** "calidad" es lo único que un script no puede decidir. Un juicio
abierto produce el `con hallazgos` universal que no informa; un foco cerrado
hace que dos auditores lleguen al mismo veredicto sobre el mismo diff.
**Consecuencias:** el veredicto de calidad evalúa **solo** estas cuatro cosas,
y el auditor debe decir cuál de las cuatro disparó el hallazgo:

1. duplicación **introducida por el cambio** (no la preexistente);
2. abstracciones que nada pide (YAGNI);
3. manejo de errores ausente **en el camino nuevo**;
4. tests que prueban mocks en lugar del código.

Veredicto: `aceptable | con hallazgos | bloqueante`. Un hallazgo que no
identifica su punto es inválido.

### B-39 — La vía exprés promociona por par archivo+CA
**Fecha:** 2026-10-22
**Estado:** `acordada` ✅ (Q8, 2026-10-22)
**Origen:** Q8, P8, B-17.
**Motivo:** contar solo el nombre de archivo es frágil ante renombres y no
distingue "tocamos este archivo tres veces por tres motivos" de "tres cambios
al mismo criterio". El par archivo+CA mide lo segundo, que es lo que se acumula
hasta merecer una etapa.
**Consecuencias:** el registro de `EXPRES.md` debe citar el CA. Sin CA citado el
cambio no suma al umbral de promoción. `expres.py` gana `--promotion` para
leer el registro y contar pares; sigue sin decidir: informa cuándo se cruzó el
umbral.

### B-22 — Cumplir el CA no es suficiente para cerrar
**Fecha:** 2026-10-22
**Estado:** `propuesta` ⚠
**Origen:** C9.
**Motivo:** "spec compliance **AND** task quality are both required". Hoy un
cambio puede ser correcto y a la vez duplicado, sobre-abstracto o sin manejo
de errores.
**Consecuencias:** `AUDIT.md` tiene dos veredictos; el cierre exige ambos.

### B-23 — Test-first no se negocia; la revisión sí
**Fecha:** 2026-10-22
**Estado:** `propuesta` ⚠
**Origen:** C13.
**Motivo:** superpowers aplica TDD siempre y proporcionaliza la revisión;
gentle-ai proporcionaliza también la verificación básica. La primera es más
segura para un paquete cuyo problema raíz es el falso cierre.
**Consecuencias:** corrige la tabla de P4: en riesgo `bajo` baja la
**revisión independiente**, nunca el test-first ni la sensibilidad demostrada.

### B-24 — Una regla nueva sin baseline no entra
**Fecha:** 2026-10-22
**Estado:** `propuesta` ⚠
**Origen:** O5, O7. "If you didn't watch an agent fail without the skill, you
don't know if the skill teaches the right thing."
**Motivo:** evita que el paquete crezca con reglas que no cambian
comportamiento y que solo consumen contexto.
**Consecuencias:** `AGENTS.md` y `CONTRIBUTING.md` exigen `Baseline:`, `Reps:`
y `Control:` para reglas nuevas o que cambian comportamiento. Las correcciones
factuales, de redacción o de formato quedan exentas.

---

## Plantilla para decisiones futuras

```markdown
### B-NN — <título>
**Fecha:** AAAA-MM-DD
**Estado:** propuesta | acordada | descartada
**Motivo:** <por qué; cita al diagnóstico o a la propuesta>
**Consecuencias:** <qué cambia en skills, templates, scripts, fixtures>
```
