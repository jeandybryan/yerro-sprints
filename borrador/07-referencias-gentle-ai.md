# 07 — Referencias: gentle-ai y la industria

> Estado: en discusión. Este documento **no publica nada** ni copia código.
> Extrae prácticas, contrasta nuestras propuestas y registra qué nos corrige.
>
> Fuente principal: [Gentleman-Programming/gentle-ai](https://github.com/Gentleman-Programming/gentle-ai)
> (MIT, ~7.9k stars, mayo 2025–2026). Docs consultadas: README,
> `docs/trigger-rules.md`, `docs/review-integration.md`,
> `docs/architecture/organic-rdd.md`, `docs/usage.md`, `docs/intended-usage.md`,
> `docs/engram.md`, `docs/skill-registry.md`, `AI_POLICY.md` y
> `docs/architecture/the-organic-rdd-story.md`.

---

## Por qué este proyecto es relevante para nosotros

No es solo "parecido": es el mismo espacio de problemas resuelto con más
kilómetros.

| Concepto YerroSprints | Equivalente en gentle-ai |
| --- | --- |
| `next_step.py` | binario `gentle-ai` que **posee** la transición nativa |
| cuatro estados públicos | **Working / Checking / Ready / Needs your decision** |
| `snapshot.py` + `**Snapshot:**` | "candidate frozen" con lineage + revision + target |
| riesgo congelado | `review assess` → `passive` / `medium` / `high` |
| presupuesto de deltas | **one bounded correction** |
| auditoría que intenta refutar | **refuter** + lentes 4R (Risk, Resilience, Readability, Reliability) |
| `EXPRES.md` | ODD "small work", sin artefacto durable |
| seis fases | ODD (ruta) + RDD (revisión), dos ejes separados |
| `doctor.py` | `gentle-ai doctor` |
| `EVALUATION.md` | `bench/` con corpus ejecutable |

La diferencia de fondo: **ellos tienen un binario que hace cumplir**, nosotros
tenemos scripts de solo lectura que **informan**. `next_step.py` y
`doctor.py` "no rebajan ningún gate", pero tampoco lo imponen. En gentle-ai, Go
*es* la autoridad y el adaptador solo transporta.

---

## Lo que nos confirma (nuestras propuestas P1, P2, P3, P5, P6, P10)

### 1. El determinismo no es una optimización, es el mecanismo

`trigger-rules.md`:

> "The **`gentle-ai` binary** owns native RDD review transitions…
> no model votes on what comes next."

Y su diagrama de estados es literalmente el nuestro. Esto valida B-13 y P16:
la regla determinizable no es economizar tokens, es quitar al modelo la
capacidad de equivocarse.

### 2. La evidencia ligada al candidato ya se implementó (y es duro)

Nosotros proponemos P2 (evidencia ejecutable con firma). Ellos lo hicieron
más profundo: el candidato se **congela en git objects**, el reviewer lee solo
árboles inmutables (nunca el worktree vivo), y la autoridad se **quema** al
cerrar (`acknowledge-approved`). El `snapshot.py` nuestro es un primo débil.

**Conclusión:** P2 está validado como dirección. Su versión completa requiere
materializar el árbol congelado, no solo hashear `HEAD`.

### 3. Corrección acotada = presupuesto de deltas

"Native Go … permits **at most one bounded correction**." Es nuestro
`**Presupuesto de deltas:**` con un default distinto. Confirma B-10 (derivar
del riesgo), aunque su número base es **uno**, no dos, y el `alto` exige
consentimiento humano explícito.

### 4. Aprobación humana con consentimiento por candidato

"Medium and high-risk START may return the typed consent/v3 envelope…
**A decline is not the kill switch.**" Y delivery siempre humano:

> "Review completion is evidence … **not delivery authority**."

Esto valida B-08 y da una pista fuerte a Q3: el consentimiento es **por
candidato y tipado**, no una marca textual que el agente pueda escribir.
El kill switch **no** es el consentimiento, y el consentimiento **no** es
autorización de entrega.

### 5. Riesgo → profundidad de verificación

`high` → 4 lentes canónicas + consentimiento; `medium` → una lente; `passive` →
lectura estructural silenciosa. Es exactamente P4. Su detalle clave: **el
agente solo puede subir el riesgo** (`--escalate-item 1-6`), nunca bajarlo.

Confirma nuestra regla "bajar el riesgo reabre" y añade una buena idea:
una **lista compartida y numerada** de ítems de riesgo alto (datos, seguridad,
contratos, concurrencia, entrega, sin test que lo detecte). Numerada porque
así se puede citar sin ambigüedad.

### 6. Test-first con criterio, no como checkbox

ODD: "observed **RED** before implementation → GREEN → REFACTOR… one RED test
per requested rule… add no other cases."

Y el refuerzo que nos faltaba:

> "For every existing command or option the change touches, add one test
> proving its previous behavior still holds."

Más la prueba de regresión funcional: ejecutar el comando viejo contra
`HEAD` y contra el cambio y **comparar stdout, stderr y exit code**. "Any
difference nobody asked for is a regression."

Esto es P1 + P5 con una receta concreta que podemos adoptar casi tal cual.

---

## Lo que nos corrige (decepciones necesarias)

### C1 — El tamaño de archivo no decide la ruta; el **test de reanudación**
**Afecta:** P9 (etapa ligera) y toda la vía exprés.

> "Classify by task size: **small when understood, risk is contained, and the
> work could be resumed from the request plus `git diff`**… **Counts of files,
> commands, tests, fixes … never decide it.**"

Nuestra vía exprés hoy dice "1 archivo, ≤20 líneas". gentle-ai dice que el
número de archivos es la métrica equivocada: un cambio de 3 archivos bien
entendido y sin riesgo es "small"; uno de 1 archivo en auth no lo es.

**Corrección al borrador:** B-17 propone reemplazar la frontera de P9 y
complementar la vía exprés (ver `03-decisiones.md`). El criterio pasa a ser
reanudabilidad + riesgo contenido, no conteo.

### C2 — ODD: la ruta de trabajo y la revisión son **dos ejes separados**
**Afecta:** toda la estructura de seis fases.

En gentle-ai, ODD (cómo trabajas) y RDD (cómo se revisa) son ortogonales. Puedes
trabajar sin revisión (RDD off) y, si cambias algo grande, se abre un **feature
document**; si es pequeño, **no hay artefacto durable**.

Nosotros metemos todo en un ciclo único de seis fases. Su lección:
**el flujo de trabajo no debería obligarte a elegir entre ceremonia y nada.**
Es lo que P9 intentaba resolver, pero con una taxonomía equivocada (tamaño por
archivos en vez de por reanudabilidad).

### C3 — La revisión solo para riesgo alto es **deliberada**
**Afecta:** P4, P10 y nuestro hábito de auditar cada etapa.

> "automatic review is due only for a **high-risk candidate**… `medium` always
> reports `under_budget`… **size is a reviewer prompt budget, not risk**."

Nosotros auditamos todas las etapas con el mismo ritual. Su posición es
más agresiva: en `medium`, revisión silenciosa; en `passive`, cero lentes. El
coste del ritual puede superar al riesgo.

**Corrección:** no bajar la calidad, pero sí hacer la **profundidad**
proporcional. Es coherente con P4 y con P14, y tiene una consecuencia dura
para nuestra idea de "auditoría por etapa": quizá no toda etapa merece
`AUDIT.md` completo.

### C4 — El presupuesto de contexto no se declara: se **mide y se refusa**
**Afecta:** P12, Q9.

> "The request counts against the lens context budget… **A request that cannot
> fit … is refused by START before any authority exists; it is never truncated.**"

Es más fuerte que nuestro P12 (un número en el contrato). Ellos:
1. tienen un presupuesto real por rol;
2. **rechazan** el trabajo que no cabe en vez de truncarlo;
3. "immutable reviewer context **cannot be truncated**".

Esto confirma P14 ("la omisión es el lado peligroso") con una dureza que
no habíamos escrito: truncar es un fallo, no una degradación.

### C5 — Error tipado con **continuación ejecutable**
**Afecta:** `next_step.py`, `doctor.py`, y nuestro formato de pregunta.

Todos sus bloqueos tienen un código y una **continuación literal ejecutable**.
Y su regla dura, la más transferible de todo el repo:

> "**A message may name a command only if running that command resolves the
> block.**"

Con el caso real: durante meses la herramienta emitió mensajes "para salir de
esto, corre X", con tests verdes que verificaban **que el texto se emitía**,
y **nadie había ejecutado nunca X**. No funcionaba.

Nuestro `next_step.py` ya devuelve bloqueos con "su resolución". Pero no
verifica que esa resolución funcione. **Debe entrar un caso de test que ejecute
la continuación de cada bloqueo.**

### C6 — El benchmark mide **fricción**, no velocidad
**Afecta:** `EVALUATION.md` y P10/P15.

> "The tool counts how often you get stuck… **in band** (tells you what to
> run), **out of band** (nothing), **dead end** (nothing you can do). It does
> not measure speed. Speed depends on the provider and the day; **friction is
> yours**."

Nuestra evaluación mide calidad y (con P15) coste. Falta la tercera dimensión:
**¿el bloqueo te dice cómo salir?** Es una métrica binaria, determinista y
barata — ideal para nuestro nivel estructural (nivel 1), sin tokens.

### C7 — "A guard nobody calls is not a guard"
**Afecta:** todo el paquete.

> "The kill switch had one written, documented, and reasoned about… **wired to
> nothing**. Every unit test of it passed."

Es el riesgo exacto de nuestro paquete: `validate_stage.py` verifica
estructura, pero ¿cuántas de sus reglas tienen un test que demuestre que
**bloquean de verdad**? Tenemos fixtures negativas, lo cual ayuda, pero la
lección es añadir una **cobertura de reglas**: cada regla del contrato →
una fixture que la viola → test que falla. Si una regla no tiene fixture, no
existe.

---

## Lo que nos señala como **nueva oportunidad**

### O1 — Memoria persistente entre sesiones
Engram: el agente guarda decisiones y las recupera al inicio, con
`mem_context` / `mem_save`. Nuestro ciclo asume que la sesión vive; si se
corta, el estado se relee de los artefactos (bien), pero **las decisiones
de conversación que no se escribieron se pierden**.

No propongo adoptar Engram. Propongo un `decisiones.md` por etapa que el
agente **lea primero y actualice siempre**, con el formato `S-NN` que ya
tenemos. Introduciría un artefacto nuevo (rompería el "seis fases, cinco
archivos"), así que queda como **pregunta Q12**.

### O2 — Presupuesto de slice de ~400 líneas autoradas
Una heurística explícitamente **advisory**, no gate:

> "about 400 authored changed lines per task is only a planning heuristic,
> not a task acceptance criterion, hard cap…"

Y advierte contra el rework cosmético: "Never delete spaces, blank lines, or
comments for cosmetic savings, omit tests, minify, add gratuitous
abstractions, or split artificially."

Es una buena respuesta a "¿cuándo paro de cortar tareas?" sin convertir el
número en un gate. Coherente con nuestra filosofía de no inventar gates.

### O3 — Índice de skills por ruta, no por resumen
`skill-registry.md`:

> "Compact rules were cheaper per delegation **but could distort skills**.
> The index-first design spends tokens only when a subagent actually needs a
> skill, **and it preserves the complete runtime contract**."

Es exactamente nuestra tensión con P11/P13: ahorrar contexto **sin resumir**.
La respuesta es: indexar y pasar **rutas**, no resúmenes.

> "Delegators pass paths, not digested rules."

Esto debería entrar en P11: `preflight.py` debe emitir **rutas + fragmentos
exactos**, nunca resúmenes generados por el modelo.

### O4 — La lección central
De `the-organic-rdd-story.md`:

> "**Good human decisions do not survive contact with an agent unless something
> enforces them.** A document that states the architecture is a suggestion…
> Phases with explicit contracts, one writer per lane, verify before asserting,
> and a failing existing test that stops the work are not suggestions."

Y la regla que les ahorró el doble de trabajo:

> "**a failing existing test is never edited — you stop and report.** That
> last rule alone caught **nine wrong premises**."

Esta regla no la teníamos. Es pequeña, baratísima y de alto impacto: **un test
existente que falla no se edita para que pase.**

---

## Resumen de impacto sobre nuestro borrador

| Lección | Qué hacemos con ella | Afecta |
| --- | --- | --- |
| Determinismo como autoridad, no como info | Mantener dirección; considerar un modo `--enforce` | B-13 |
| Candidato congelado en git objects | P2 se amplía a materializar el árbol | P2 |
| Corrección acotada = 1 por defecto | Ajustar presupuesto base (Q1) | B-10, P4 |
| Riesgo solo sube, lista numerada | Adoptar la lista de 6 ítems citables | P4, B-12 |
| Test de regresión funcional vs `HEAD` | Adoptar en P1/P5 | P1, P5 |
| El tamaño no decide; la reanudación sí | **P9 cambia de criterio** (B-17) | P9, vía exprés |
| ODD/RDD como ejes separados | Registrar como alternativa de diseño (Q13) | estructura |
| Revisión automática solo en alto | Profundidad proporcional, no ritual fijo | P4, P10 |
| Presupuesto: rechazar, nunca truncar | Fortalecer P12 | P12, P14 |
| Continuación ejecutable por bloqueo | **Nuevo caso de test** | C5 → P6 |
| Benchmark de fricción | Tercera dimensión en `EVALUATION.md` | P10, P15 |
| "Guard nobody calls" | Cobertura regla → fixture → test | P6 |
| Índice de rutas, no resúmenes | Fortalecer P11 | P11 |
| Test que falla no se edita | Regla nueva, CPU barata | P1, P14 |
