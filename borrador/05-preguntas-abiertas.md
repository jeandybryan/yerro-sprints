# 05 — Preguntas abiertas

> Cada pregunta necesita una respuesta **antes** de congelar el diseño. Se
> responde aquí y se promueve a `03-decisiones.md` como `B-NN`.
>
> Formato (el del propio paquete): **Contexto**, **Pregunta**, **Propuesta**.

---

## Q1 — ¿La tabla riesgo → evidencia mínima es la correcta? 📏 `NECESITA DATO`

**Contexto:** P4 propone `bajo → 2`, `medio → 1`, `alto → 0` de presupuesto de
deltas y una tabla de evidencia mínima. Son números razonables pero arbitrarios;
si no los acuerdas, el gate cruzado se construye sobre una opinión mía.

**Pregunta:** ¿Aceptas esa tabla, la ajustas, o prefieres que el presupuesto
siga siendo un valor por etapa escrito en la conciliación (sin derivación)?

**Propuesta:** aceptar la derivación como default y permitir sobrescribir con
motivo. Da el beneficio del esfuerzo proporcional sin quitar el control humano.

**Afecta a:** B-10, P4, Fase 2.

#### Estado de la resolución

El default se deriva de etapas reales; si no hay, el conservador (`bajo → 1`) hasta medir. Ver `11-resolucion-abiertas.md`.

---

## Q2 — ¿La etapa ligera (P9) es necesaria o es un atajo peligroso? ⏸ `DIFERIDA`

**Contexto:** entre la vía exprés (1 archivo, 20 líneas) y seis fases completas
hay un vacío que empuja a abusar de la vía exprés. Pero P9 multiplica los casos
de transición y diluye la garantía de las seis fases. Además, un modo reducido
ahorra tokens de artefacto pero puede ahorrarlos también de calidad.

**Pregunta:** ¿P9 va en esta iteración, se difiere hasta medir la fricción real,
o se descarta definitivamente?

**Propuesta:** diferirla (B-06) y tratarla solo si los datos de uso lo justifican.
Primero se implementan los gates que protegen; después se optimiza la ergonomía.
Si se retoma, es una decisión de coste (B-16): debe demostrar que **no baja la
rúbrica de calidad**, no solo que gasta menos.

**Afecta a:** B-05, B-06, P9, Fase 5.

---

## Q3 — ¿De dónde sale la marca de aprobación humana para que no sea falsificable? ✅ `RESUELTA`

**Contexto:** si el agente puede escribir `**Aprobado por:** Ana`, la marca no
protege de nada. Necesitamos un origen fuera de la conversación.

**Pregunta:** ¿Cuál de estas fuentes prefieres?

1. Un comando explícito que solo ejecuta una persona (`scripts/approve.py`),
   que el agente no puede invocar sin instrucción (requiere que el host
   bloquee esa herramienta para el agente; no siempre es posible).
2. Un archivo de configuración del usuario o del equipo (`.yerro/approvals.yml`)
   mantenido a mano y versionado.
3. Un commit firmado (GPG/SSH) con el mensaje de aprobación, que el validador
   verifique.

**Propuesta:** (2) como base, con (1) como comodidad. (3) es la más fuerte pero
exige que todo el equipo firme commits, lo cual puede ser una barrera.

**Afecta a:** B-08, B-09, P3, Fase 2.

**Resolución (2026-10-22):** la aprobación vive en `.yerro/approvals.yml`,
versionado y editado a mano; desaparece la marca textual. Sin PR y sin commit
firmado como requisito. Ver B-37. **Q12 queda fusionada aquí** y se cierra con
la misma respuesta.

---

## Q4 — ¿Qué cuenta como "oráculo válido" sin que el validador sea adivino? ✅ `RESUELTA`

**Contexto:** P1 nivel 1 quiere rechazar `Test: true`. Pero un validador estático
no puede saber si un comando arbitrario prueba algo.

**Pregunta:** ¿Preferimos una **lista negra** de comandos vacíos, o una
**lista blanca** de runners conocidos por proyecto (configurable), o ambas?

**Propuesta:** lista negra por defecto (cubre el 80% de los abusos) + lista
blanca declarada en la conciliación para proyectos con runner propio. La
sensibilidad real (nivel 2) es la que de verdad protege.

**Afecta a:** P1, Fase 1.

**Resolución (2026-10-22):** lista negra por defecto + lista blanca declarada
en la conciliación. La lista blanca reconoce el runner, no demuestra que el test
pruebe algo. Ver B-34.

---

## Q5 — ¿La mutación puede ser obligatoria sin añadir dependencias al paquete? ✅ `RESUELTA`

**Contexto:** P1 nivel 3 (mutación por CA crítico) requiere una herramienta en
el proyecto consumidor (Stryker, mutmut, PIT, etc.). El paquete promete no
imponer runtime.

**Pregunta:** ¿La mutación se acepta como **procedimiento documentado**
(cualquier método que produzca rojo observado) o se exige una herramienta
concreta?

**Propuesta:** aceptar cualquier método que deje `mutante: <descripción>` y
`resultado: rojo`, sin exigir herramienta. Así el paquete sigue siendo portable
y el gate sigue siendo verificable.

**Afecta a:** P1, B-12, Fase 1.

**Resolución (2026-10-22):** procedimiento documentado, sin herramienta
obligatoria. El gate exige `mutante:` + `resultado: rojo`, no Stryker. Ver
B-35.

---

## Q6 — ¿La evidencia ejecutable rompe la promesa "las skills no exigen Python"? ✅ `RESUELTA`

**Contexto:** el README dice que Python es opcional, solo para validadores
estructurales. P2 introduce `evidence.py` que *ejecuta* comandos.

**Pregunta:** ¿Aceptamos que el cierre `--strict` requiera Python y solo la
operación permanezca opcional? ¿O preferimos que `evidence.py` sea una utilidad
externa del consumidor?

**Propuesta:** aceptar la restricción y corregir el README: "operar no requiere
Python; cerrar con `--strict` sí". Es honesto y evita la alternativa de
reimplementar la captura de evidencia en cada host.

**Afecta a:** B-04, P2, README, Fase 1.

**Resolución (2026-10-22):** se acepta la restricción y se corrige el README.
Ver B-30.

---

## Q7 — ¿La "suite de referencia" puede quedar vacía? ✅ `RESUELTA`

**Contexto:** B-11 propone que una persona declare qué suite corre el cierre.
Un proyecto rápido podría declarar "ninguna".

**Pregunta:** ¿Permitimos `Suites de referencia: ninguna` con motivo, o exigimos
al menos un comando global (aunque sea un smoke test)?

**Propuesta:** permitir `ninguna` solo con motivo escrito y con riesgo `bajo`;
para `medio`/`alto`, exigir al menos un comando global.

**Afecta a:** B-11, P5, Fase 3.

**Resolución (2026-10-22):** `ninguna` solo en riesgo `bajo` y con motivo.
Ver B-36.

---

## Q8 — ¿Quién mide el "mismo archivo" en la promoción de la vía exprés? ✅ `RESUELTA`

**Contexto:** P8 promueve a etapa cuando hay ≥3 cambios sobre el mismo archivo
o CA. La identificación del archivo depende del diff.

**Pregunta:** ¿La promoción se calcula sobre el **nombre de archivo** (barato,
pero frágil ante renombres) o sobre el **par archivo+CA** (más preciso,
requiere que el registro exprés cite el CA)?

**Propuesta:** par archivo+CA. El registro exprés ya debería citar un CA, aunque
sea existente.

**Afecta a:** P8, Fase 4.

#### Resolución

**Resolución (2026-10-22):** la promoción cuenta el **par archivo+CA**. El
registro exprés debe citar el CA; si no lo cita, el cambio no suma al umbral.
Es más preciso que el nombre de archivo y empuja a que la vía exprés declare a
qué criterio sirve, que es lo único que hoy no comprueba nadie.

---

## Q9 — ¿Qué presupuesto de contexto por fase es razonable? 📏 `NECESITA DATO`

**Contexto:** P12 propone límites en líneas (`identify ≤ 400`,
`conciliate ≤ 600`, `generate ≤ 400`, `implement ≤ 800`, `audit ≤ 1000`). Son
estimaciones mías basadas en el tamaño actual de las plantillas y referencias;
no hay medición real de uso.

**Pregunta:** ¿Fijamos estos números, los dejamos sin gate (solo informativos)
hasta medir, o los calculamos a partir del primer `preflight.py` real?

**Propuesta:** implementar `preflight.py` sin gate (solo informa), medir una
semana de uso real, y fijar el presupuesto en la Fase 3 con evidencia. Fijar
números antes de medir crea un gate que se incumple para trabajar.

**Corrección tras `07-referencias-gentle-ai.md` (C4):** gentle-ai tiene un
presupuesto **real** por rol y **rechaza** el trabajo que no cabe ("never
truncated"). Antes de fijar un número, decidir si nuestro presupuesto es un
`WARN` (medir, avisar) o un `ERROR` (rechazar). Mi propuesta de medir primero
sigue en pie, pero el destino no debería ser un simple aviso.

**Afecta a:** B-15, P12, Fase 3.

#### Estado de la resolución

`preflight.py` entra sin gate, en modo informe; el número se fija con datos. `WARN` vs `ERROR` se decide con el mismo dato. Ver `11-resolucion-abiertas.md`.

---

## Q10 — ¿El determinismo puede sustituir a la conciliación en algún punto? ✅ `RESUELTA`

**Contexto:** P3 exige aprobación humana y P4 deriva el presupuesto del riesgo.
¿Hasta dónde queremos que un script decida en lugar de una persona?

**Pregunta:** ¿Hay algún punto del ciclo donde aceptarías que un script decida
sin humano (p. ej. rechazar un cambio exprés por acumulación), o todo juicio de
alcance/riesgo debe pasar por persona?

**Propuesta:** los scripts deciden **fronteras mecánicas** (conteos, rutas
excluidas, acumulación, presupuesto derivado) y **nunca** deciden alcance,
riesgo o cierre. La persona sigue siendo la única que aprueba una conciliación.

**Afecta a:** B-13, B-14, P3, P4, P8.

**Resolución (2026-10-22):** los scripts deciden fronteras mecánicas y nunca
alcance, riesgo ni cierre. Ver B-29.

---

## Q11 — ¿Cómo se mide el coste si el host no expone tokens? ✅ `RESUELTA`

**Contexto:** OpenCode y algunos hosts no devuelven tokens in/out de forma
estable. P15 propone medirlos, pero un gate con una métrica que a veces no
existe es frágil.

**Pregunta:** ¿El reporte de coste se limita a lo medible universalmente
(líneas leídas, nº de lecturas, nº de ejecuciones), o exigimos tokens cuando el
host los exponga?

**Propuesta:** universales obligatorios; tokens opcionales e informativos. El
gate es siempre sobre lo que CI puede reproducir.

**Afecta a:** B-15, B-16, P15.

**Resolución (2026-10-22):** universales obligatorios; tokens informativos.
Ver B-31.

---

## Q12 — ¿Quién es el dueño de la marca de aprobación? ✅ `FUSIONADA CON Q3`

**Estado:** `fusionada` el 2026-10-22 → se responde en Q3 (B-37).

**Contexto:** gentle-ai resolvió esto con un consentimiento por candidato,
tipado, y con la regla de que *el consentimiento no es el kill switch y no es
autorización de entrega*. Nuestra marca textual era trivial de falsificar.

**Resolución:** la misma que Q3 — archivo versionado fuera del alcance del
agente. La parte "tipada" se conserva en el esquema: cada entrada de
`.yerro/approvals.yml` identifica la etapa, quién aprueba, cuándo y sobre qué
**alcance**, no un "sí" global.

---

## Q13 — ¿Separamos "trabajo" (ODD) de "revisión" (RDD) como dos ejes? ⏸ `DIFERIDA`

**Contexto:** gentle-ai tiene dos ejes ortogonales: ODD decide cómo se trabaja
(small inline vs feature document) y RDD decide cuándo se revisa (passive /
medium / high). Nosotros tenemos un ciclo único de seis fases donde todo se
concatena. Eso nos obliga a meter el tamaño y el riesgo en la misma línea.

**Pregunta:** ¿Mantenemos las seis fases como ciclo único, o aceptamos que
"revisar" sea un eje separado que se activa según el riesgo del candidato?

**Propuesta:** no romper las seis fases ahora. Pero registrar la idea: si P9
(etapa ligera) reaparece, la forma correcta no es una etapa más pequeña, sino
**separar la revisión de la ruta de trabajo** — que es exactamente lo que ellos
hicieron tras fracasar con el enfoque integrado.

**Afecta a:** B-05, B-06, P9, estructura general.

---

## Q14 — ¿Adoptamos el "test de reanudación" en lugar del conteo de archivos? ✅ `RESUELTA`

**Contexto:** Q2 y P9 se apoyan en "2–3 archivos". gentle-ai fue explícito:

> "Counts of files, commands, tests, fixes … **never decide it**."

El sustituto es: *small = entendido + riesgo contenido + reanudable desde la
petición y `git diff`*. Ver B-17.

**Pregunta:** ¿Reemplazamos la frontera "1 archivo / 20 líneas" de la vía
exprés por reanudabilidad + riesgo contenido + revisión de la lista de ítems
de riesgo alto?

**Propuesta:** sí, pero como complemento, no como reemplazo inmediato: el
conteo es determinista y barato (`expres.py` ya lo calcula), la reanudabilidad
requiere juicio. Empezar por usar la lista de riesgo alto como **veto** sobre
la vía exprés, y evaluar reanudabilidad solo en la frontera dudosa.

**Afecta a:** P8, P9, B-17, Fase 4.

#### Resolución (2026-10-22)

Techo duro + reanudabilidad debajo. `expres.py` conserva el conteo como
**techo** (por encima de N archivos no cabe, sin discusión) y la reanudabilidad
se consulta **debajo** del techo, donde hoy la respuesta sería "cabe". El
conteo deja de ser el criterio único; sigue siendo un guardarraíl determinista.
Sobre el número N: ver Q1 (se calibra con datos, no se inventa).

---

## Q15 — ¿Preguntar o decidir cuando hay ambigüedad en ejecución? ✅ `RESUELTA`

**Estado:** `resuelta` el 2026-10-22 → **Modelo C** (B-21, B-25, B-26, B-27).
Ver `10-modelo-c-rulings.md` para el diseño operativo completo.

**Contexto:** es el choque más directo entre las referencias.
YerroSprints y gentle-ai paran y piden consentimiento; superpowers dice lo
contrario: *"A running plan does not wait on a human… decide them… A session
parked on a question costs their whole day and buys nothing"*, con registro
`Ruling: <qué> — <por qué> — <qué cuesta si me equivoco>`.

**Pregunta:** ¿Aceptamos que, dentro de un plan ya aprobado, el agente decida
y registre en vez de preguntar, reservando la pregunta para baseline,
irreversibles y seguridad?

**Resolución:** no se decide por duda ni solo por reversibilidad, sino por
**clase de decisión**: detalle de implementación → decide y registra; efecto
observable reversible → decide, registra y marca `**Sujeto a revisión:**`;
cambio de intención/alcance/CA → para y reabre conciliación. Cuatro paradas
incondicionales por encima de todo.

---

## Q16 — ¿El veredicto de calidad puede ser objetivo sin ser arbitrario? ✅ `RESUELTA`

**Contexto:** P18 exige un veredicto de calidad además del de especificación.
Pero "calidad" es lo único que un script no puede decidir.

**Pregunta:** ¿Cerramos el foco a cuatro puntos comprobables (duplicación,
YAGNI, manejo de errores, tests sobre mocks) o dejamos un juicio más amplio?

**Propuesta:** foco cerrado de cuatro puntos, con un veredicto
`aceptable | con hallazgos | bloqueante`. Un foco pequeño es lo que evita el
`con hallazgos` universal que no informa.

**Afecta a:** B-22, P18.

#### Resolución

**Resolución (2026-10-22):** foco cerrado de **cuatro** comprobaciones, con
veredicto `aceptable | con hallazgos | bloqueante`:

1. duplicación introducida por el cambio;
2. abstracciones que nada pide (YAGNI);
3. manejo de errores ausente en el camino nuevo;
4. tests que prueban mocks en lugar del código.

Un foco cerrado es lo que evita el `con hallazgos` universal que no informa: el
auditor debe poder decir cuál de los cuatro. Ver B-22 / P18.

---

## Q17 — ¿El baseline de reglas (RED) es obligatorio para toda regla? ✅ `RESUELTA`

**Contexto:** P20 pide, antes de escribir una regla, demostrar que el agente
falla sin ella. Es costoso (agente real, ≥5 repeticiones) y valioso (evita
reglas que no sirven).

**Pregunta:** ¿Exigimos baseline a toda regla nueva, solo a las que cambian
comportamiento, o solo a las marcadas como "disciplina"?

**Propuesta:** solo a reglas nuevas o que cambian comportamiento. Correcciones
factuales, de enlace y de formato quedan exentas. Sin esta acotación, el
proceso de mantenimiento se vuelve inoperable.

**Afecta a:** B-24, P20, P23.

#### Resolución

**Resolución (2026-10-22):** baseline obligatorio solo para reglas **nuevas o
que cambian comportamiento**. Correcciones factuales, de enlace y de formato
quedan exentas. Sin esta acotación el proceso de mantenimiento se vuelve
inoperable. Ver B-24 / P20 / P23.

---

## Q18 — ¿Cómo se migran las etapas que no declaran archivos por tarea? ✅ `RESUELTA`

**Estado:** `resuelta` el 2026-10-22 → **migración dura, sin soporte legado**
(B-28). Ver `10-modelo-c-rulings.md` §"Migración".

**Contexto:** B-27 necesita comparar el diff con los archivos que la tarea
declara (`**Archivos:**`). Una etapa conciliada **antes** de que exista el campo
no los tiene, así que con el gate nuevo no puede implementarse ni cerrarse.

**Resolución del usuario:** *"lo más saludable es que migren a la nueva, para no
tener que darle soporte a lo legado."*

**Lo que esto implica, y que hay que asumir de forma explícita:**

1. **No hay ventana de gracia.** `--strict` ya es el modo obligatorio en
   `SKILL.md`; B-28 elimina el parámetro y el camino de advertencia. mantener los
   dos modos *sería* el soporte legado que se quiere evitar.
2. **Migrar es re-conciliar el alcance, no rellenar una casilla.** El bloque
   `**Archivos:**` se deriva de las tareas y los CA, **no** del diff ya
   producido. Tomarlo del diff blanquea exactamente el caso que B-27 detecta.
3. **Una etapa a medio implementar tiene dos salidas honestas:** (a)
   re-conciliar con los archivos declarados y seguir; (b) descartar el trabajo y
   re-implementar. No hay tercera: reescribir la tarea para que describa lo que
   ya se hizo es categoría 3 disfrazada.
4. **La constancia se registra.** Cada etapa migrada anota en `TAREAS.md`
   `**Migrada:** AAAA-MM-DD (origen: <diff o re-conciliación>)`, para que una
   etapa migrada desde el diff se vea en la auditoría.

**Coste aceptado:** una interrupción de trabajo en las etapas en curso al
publicar la versión. **Beneficio:** un solo contrato, un solo camino de código y
ninguna fixture que probar dos veces.

**Afecta a:**
B-27, B-28, P19, `validate_stage.py`, `next_step.py`, Q20.

---

## Q19 — ¿El ruling de categoría 2 se revisa en la misma etapa o en la siguiente? ✅ `RESUELTA`

**Contexto:** B-26 dice que el `AUDIT.md` resuelve cada `**Sujeto a revisión:**`.
Pero el auditor es, en la práctica, el mismo agente que implementó en otra
pasada. Si re-ejecuta sin contexto fresco, la revisión es una auto-revisión
(C12 de superpowers dice que eso no cuenta).

**Pregunta:** ¿La revisión de rulings de categoría 2 la hace el auditor de la
etapa, o se arrastra explícitamente a la etapa siguiente?

**Propuesta:** el auditor de la etapa, **pero leyendo solo los artefactos** y
sin la conversación de implementación (`audit-stage` ya no lee la sesión). Si el
ruling es costoso de re-evaluar (toca contrato público), se arrastra a la
siguiente etapa como tarea.

**Afecta a:** B-26, P18, `audit-stage`.

**Resolución (2026-10-22):** el auditor revisa con artefactos, no con memoria;
un ruling que no explica su decisión es un hallazgo. Ver B-32.

---

## Q20 — ¿Cuántos rulings antes de considerar que la tarea estaba mal escrita? ✅ `RESUELTA`

**Contexto:** los rulings resuelven la ambigüedad **residual**. Si una tarea
produce seis rulings, la tarea no era "ambigua en un detalle": estaba
infraespecificada. Pero no hay límite, y sin límite el modelo se convierte en
"el plan da igual, el agente decide".

**Pregunta:** ¿Añadimos un umbral, y qué se hace al superarlo?

**Propuesta:** cuanto más rulings, más se parece la tarea a una tarea sin
`Test:`. Candidato: **más de 3 rulings de categoría 1 en una tarea** abre un
aviso en `doctor.py` que apunta a `generate-stage-tasks`. No bloquea, porque un
umbral rígido castigaría tareas genuinamente finas. Es determinista y no cuesta
tokens.

**Afecta a:** P19, P17, `doctor.py`.

**Resolución (2026-10-22):** más de tres rulings de categoría 1 por tarea
abre un aviso de `doctor.py` que apunta a `generate-stage-tasks`. Ver B-33.

---

## Lo que quieres añadir tú

Usa este espacio para las ideas que mencionaste que quieres sumar o acotar.
Cuando las escribas, cada una entra como `P11`, `P12`… con el mismo formato de
`02-propuestas.md`, y si toca una decisión se crea su `B-NN`.

| Optimizar tokens de contexto y calidad de código con herramientas deterministas | usuario, 2026-10-22 | `incorporada` → `06-economia-de-tokens.md` (P11–P16, B-13…B-16, Q9–Q11) | Todas |
