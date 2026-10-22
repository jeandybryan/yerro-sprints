# 08 — Referencias: superpowers y la evidencia antes que la afirmación

> Estado: en discusión. No se copia código; se extraen prácticas y se contrasta.
>
> Fuente: [obra/superpowers](https://github.com/obra/superpowers) (MIT,
> ~304k stars, Jesse Vincent / Prime Radiant). Skills leídas:
> `writing-plans`, `test-driven-development`, `verification-before-completion`,
> `requesting-code-review`, `subagent-driven-development` (+ `fix-loop.md`,
> `resuming.md`), `systematic-debugging`, `writing-skills`
> (+ `bulletproofing.md`), README y `AGENTS.md`.

---

## Por qué este es un tercer punto del triángulo, no un duplicado

| | YerroSprints | gentle-ai | superpowers |
| --- | --- | --- | --- |
| Naturaleza | skills + scripts de solo lectura | binario Go que posee la autoridad | **skills puras + harness** |
| Aporta | contrato de etapas y trazabilidad | determinismo, congelado, revisión proporcional | **disciplina anti-racionalización y diseño de skills** |
| Rigor | estructural (documentos bien formados) | de autoridad (el binario decide) | **behavioral (el agente cumple bajo presión)** |
| Portabilidad | alta | media (requiere binario) | **máxima (Markdown)** |
| Número de skills | 6 | ~18 integraciones | **~19 skills** |

La diferencia clave: gentle-ai resolvió el problema con **código que hace
cumplir**. superpowers lo resolvió con **texto que no deja resquicio**. Los
dos son válidos y se complementan: ninguno sustituye al otro.

Y hay algo en superpowers que ninguno de los otros dos tiene:

> **Un método para escribir y probar las propias skills.**

---

## Lo que confirma nuestras propuestas

### 1. Test-first como ley, no como casilla (P1 — confirmado y reforzado)

```
NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST
```

Con tres detalles que nos faltaban:

- **"If you didn't watch the test fail, you don't know if it tests the right
  thing."** — el fallo debe ser **observado**, no inferido.
- Distinguen **fallar por la razón correcta**: "Test errors? Fix error, re-run
  until it fails correctly". Un test que falla por un typo no prueba nada.
- **Verificación de regresión explícita**:
  ```
  Write → Run (pass) → Revert fix → Run (MUST FAIL) → Restore → Run (pass)
  ```
  Es exactamente la **sensibilidad demostrada** que propusimos en P1, con
  una secuencia concreta que podemos exigir en el ledger `E-NN`.

**Esto nos da la respuesta a Q4** ("¿qué cuenta como oráculo válido?"): el
criterio no es sintáctico, es la secuencia revertir → debe fallar → restaurar.

### 2. "Evidencia antes que afirmación" (P2 — confirmado, más simple)

Su skill `verification-before-completion` es nuestro P2 en versión de proceso:

```
NO COMPLETION CLAIMS WITHOUT FRESH VERIFICATION EVIDENCE
```

La diferencia con nuestra propuesta: ellos **no exigen firma criptográfica**.
Exigen **ejecutar en el mensaje actual**, con `IDENTIFY → RUN → READ → VERIFY
→ CLAIM`. Es más barato que nuestro `evidence.py`, pero depende de la
honestidad del agente.

Su tabla de fallos comunes tiene una fila que nos importa mucho:

> | "Agent completed" | VCS diff shows changes | Agent reports "success" |

Es decir: **el informe de un subagente no es evidencia**. Para nosotros: el
`implement-stage` no puede declarar nada; solo el `audit-stage` con
verificación fresca.

### 3. El error tipado no basta; hace falta la confirmación (B-19 — reforzado)

Superpowers agrega algo que gentle-ai no tiene explícito: **la afirmación de
éxito es en sí misma una trampa**. No es solo que el bloqueo diga qué hacer;
es que **ninguna persona ni agente puede decir "listo" sin haber ejecutado la
verificación en ese momento**.

Combinado con C5 de gentle-ai (la continuación debe funcionar), el resultado
es una regla doble:

1. todo bloqueo trae una continuación ejecutable (B-19);
2. **toda afirmación de cumplimiento cita evidencia producida en esta pasada**
   (P2).

### 4. La corrección acotada tiene un número mágico distinto (P4 — nuevo dato)

gentle-ai: **una** corrección acotada. Superpowers:
**cinco rondas por tarea**, con escalada:

> "Rounds 1-3 — resume the original implementer… **Rounds 4-5 — dispatch a
> fresh implementer on a more capable model**."

Y el "breaker" cuando se agota:

> "When round 5's re-review still leaves findings open… **Adjudicate each open
> finding yourself**… Every adjudication is a ledger entry — **a silent discard
> is forbidden**."

Esto es más matizado que nuestro binario "delta o reapertura". Aporta tres
ideas:

- el número depende de la **complejidad de la corrección**, no solo del riesgo;
- cuando se escala, se cambia también **el modelo**, no solo el intento;
- el agotamiento termina en **adjudicación registrada**, no en bloqueo muerto.

**Nos corrige Q1:** nuestro presupuesto de deltas debería tener una **regla de
escalada** (mismo agente → agente fresco con más capacidad) y una
**adjudicación explícita al final**, no solo `necesita-decision`.

---

## Lo que nos corrige (el aporte más fuerte)

### C8 — Un plan debe ser ejecutable por quien no tiene contexto
**Afecta:** `generate-stage-tasks` (y toda nuestra idea de "tarea").

`writing-plans` describe el destinatario con una precisión brutal:

> "an enthusiastic junior engineer with poor taste, no judgement, no project
> context, and an aversion to testing."

Y define qué hace un paso:

> "A step is done when the implementer can write **exactly one reasonable
> thing** from it. That is the whole requirement: **unambiguous, not
> complete**."

Nuestras tareas hoy declaran `Test:` y `Verificar:`, pero **no declaran las
interfaces que consumen ni producen**. Su bloque `Interfaces:` es la clave para
que un subagente no invente nombres:

> "All task implementers see only their own task; this block is how they learn
> the names and types neighboring tasks use."

**Además tiene un antídoto contra dos fallos que nosotros cometemos:**

> "A plan **longer than the code it describes** has written the code instead.
> Lines that decide nothing ('TBD', 'handle edge cases', 'add appropriate
> validation') are the opposite failure."

Es la regla que nos falta para que `TAREAS.md` no se hinche ni se quede vacío.

### C9 — La revisión de especificación y la de calidad son **dos veredictos**
**Afecta:** `audit-stage`, que hoy tiene un solo veredicto.

> "never accept a report missing either verdict — **spec compliance AND task
> quality are both required**."

Nuestro `AUDIT.md` dice `coincide` / `no coincide` sobre la conformidad con los
CA. Eso es solo **spec compliance**. Un cambio puede cumplir el CA y ser código
de mala calidad (duplicación, abstracciones innecesarias, sin manejo de errores).

**Consecuencia:** P10 gana una segunda dimensión. El veredicto debería ser
`(spec, calidad)`, no un único `coincide`.

### C10 — El ledger sobrevive a la compactación; el todo-list no
**Afecta:** `TAREAS.md`, `next_step.py` y la economía de contexto (P13).

> "Conversation memory does not survive compaction. In real sessions,
> controllers that lost their place **have re-dispatched entire completed task
> sequences** — the single most expensive failure observed."

> "The ledger is your recovery map: the commits it names exist in git even when
> your context no longer remembers creating them. **After compaction, trust the
> ledger and `git log` over your own recollection.**"

Nuestro `TAREAS.md` ya es un ledger de facto, y `next_step.py` deriva el
estado. Pero no tenemos una regla explícita de **reconciliación tras
compactación**: si el contexto se pierde, el agente debe leer el índice + git,
no recordar.

**Y la métrica que dan:** "re-dispatched entire completed task sequences" es el
fallo **más caro** observado. Eso debería ser un caso de evaluación nuestro
(Q11 relacionada con coste).

### C11 — "Rulings, not stalls": decidir y registrar, no parar
**Afecta:** nuestra regla de preguntar y `necesita-decision`.

> "A running plan does not wait on a human… **decide them**… Record every
> decision in the ledger as `Ruling: <what you decided> — <why> — <what it
> costs if wrong>`… **A session parked on a question costs their whole day.**"

Esto **choca frontalmente** con nuestra regla "cuando hay duda, pregunta" (y
con `conciliate-stage`, que prohíbe cerrar con supuestos).

Pero no es un choque: operan en fases distintas.

| Fase | superpowers | nosotros | Veredicto |
| --- | --- | --- | --- |
| Diseño (`brainstorming`) | pregunta mucho | pregunta (conciliación) | iguales |
| Ejecución (plan ya aprobado) | **decide y registra** | pregunta | **ellos tienen razón** |
| Operaciones irreversibles | para | para | iguales |

Su regla de cuándo parar es corta y buena: **irreversible, seguridad, efecto
fuera del worktree, plan roto**. Todo lo demás se decide.

**Corrección al borrador:** `implement-stage` no debería detenerse ante una
ambigüedad resoluble; debería **registrar la decisión** con el formato
`Ruling:` y seguir. Solo el cambio de **intención/alcance/CA** va a conciliación.
Es coherente con nuestra regla ("un cambio de baseline reabre") y nos quita
la fricción de parar por dudas de implementación.

### C12 — La revisión que el ejecutor se hace a sí mismo no cuenta
**Afecta:** P3, y la regla de "intenta refutar".

> "Implementer self-review never replaces the task review; both are needed."

Y del lado del implementador: "The dispatch carries the no-subagents contract:
**the implementer never dispatches subagents** — not helpers, and never a
reviewer."

Ya intuíamos que auto-auditoría era débil. Ellos lo hacen explícito: el
revisor y el ejecutor son **roles distintos**, y el ejecutor ni siquiera puede
fabricarse uno.

Refuerza B-08, y añade un detalle operativo: **el revisor recibe contexto
curado, nunca el historial de la sesión** ("never your session's history").
Para nosotros: `audit-stage` no lee la conversación, lee los artefactos.

### C13 — La restricción por riesgo no se aplica de forma probabilística
**Afecta:** P4 (riesgo → evidencia).

superpowers no escalona por riesgo: **aplica TDD siempre** y luego
proporcionaliza la **revisión**. gentle-ai proporcionaliza también la
verificación básica (passive → cero lentes).

Esto nos da una tabla de tres niveles más honesta que la nuestra:

| Nivel | Quién lo exige | Coste |
| --- | --- | --- |
| Test-first | siempre, sin excepción | atómico, bajo |
| Suite completa | siempre antes de cerrar | variable |
| Revisión independiente | proporcional al riesgo | alto |

**Corrección al borrador:** en P4 habíamos hecho proporcional *también* la
evidencia. superpowers sugiere lo contrario: **el test-first nunca se
negocia**; lo que se proporcionaliza es la **revisión**.

---

## Lo que nos señala como **nueva oportunidad**

### O5 — Escribir skills es TDD aplicado a documentación
**Esto es lo que ninguno de los otros dos tiene.**

`writing-skills`:

> "Writing skills IS Test-Driven Development applied to process
> documentation… If you didn't watch an agent fail **without** the skill, you
> don't know if the skill teaches the right thing."

Y la ley:

```
NO SKILL WITHOUT A FAILING TEST FIRST
```

Nosotros tenemos `EVALUATION.md` con casos retenidos (S01–S18). Eso es el
**lado GREEN**. Nos falta el lado **RED**: documentar, para cada regla nueva,
**cómo se comporta el agente sin la regla**.

**Consecuencia para nuestro proceso de mantenimiento:**
toda regla nueva en una skill debe traer el **baseline**: qué hizo el agente
cuando la regla no estaba. Sin eso, no sabemos si la regla enseña algo o solo
ocupa contexto.

Y su regla de forma:

> "If it's enforceable with regex/validation, **automate it** — save
> documentation for judgment calls."

Es otra enunciación de nuestra regla determinizable (B-13). Confirma que el
eje es correcto y que la frontera es la misma.

### O6 — El flowchart solo cuando la decisión no es obvia
`writing-skills`:

> "Small flowchart only if decision non-obvious."
> Anti-patrón: "Code in Flowcharts — Can't copy-paste, hard to read."

Nosotros tenemos pocos gráficos. Es una regla de forma barata: un grafo de
decisión solo si el agente dudaría leyendo el texto.

### O7 — El control negativo: nunca medir sin comparar
El método de `writing-skills` para micro-tests de redacción:

> "**Always include a no-guidance control.** If the control doesn't exhibit the
> failure, there is nothing to fix — **stop, don't author the guidance**."
>
> "**5+ reps per variant.** Single samples lie."
>
> "**Variance is a metric.** When guidance lands, reps converge on the same
> shape. Five different interpretations across five reps means the wording
> isn't binding."

Esto es directamente aplicable a nuestra Fase 0: **no escribir la regla si el
baseline ya se comporta bien**. Y es el antídoto contra el paquete de reglas
que crece sin evidencia de que cada regla sirva.

### O8 — La clasificación del fallo determina la forma de la regla
`bulletproofing.md` / "Match the Form to the Failure":

| Fallo baseline | Forma correcta | Forma incorrecta |
| --- | --- | --- |
| Salta una regla bajo presión | prohibición + tabla de racionalizaciones + red flags | guía suave ("prefiere") |
| Cumple, pero con forma equivocada | receta positiva: el output ES esto | lista de prohibiciones |
| Omite un elemento | campo obligatorio en la plantilla | recordatorio en prosa |
| Comportamiento condicional | condicional con predicado observable | regla + excepciones |

> "**No nuance clauses.** 'Don't X unless it matters' reopens the negotiation".

Esto es una lección directa para nosotros: `conciliate-stage` tiene reglas
correctas, pero varias están escritas como listas de "No hagas". Si el fallo
es "comete un error de forma", la solución es la plantilla, no otra
prohibición.

Y el caso medido que lo demuestra: en sus tests de redacción, **la variante
con prohibición produjo más contenido no deseado que el control sin
instrucción**.

---

## Conflicto abierto: preguntar vs. decidir (Q15)

Este es el único punto donde las dos referencias nos dan consejos
radicalmente distintos y hay que elegir:

| | gentle-ai / YerroSprints | superpowers |
| --- | --- | --- |
| Ambigüedad en ejecución | consentimiento humano | `Ruling:` y seguir |
| Coste de parar | "regulation cost" | "costs their whole day" |
| Quién decide | humano | agente, registrado |

Mi lectura: no son incompatibles si se separan por **reversibilidad**:

- **Reversible + dentro del plan** → decidir y registrar (`Ruling:`) → Q15.
- **Irreversible, seguridad, fuera de alcance** → parar → `necesita-decision`.

Eso es más fino que cualquiera de las dos posiciones solas.

---

## Resumen de impacto sobre el borrador

| Lección | Qué hacemos | Afecta |
| --- | --- | --- |
| Secuencia revertir → fallar → restaurar | Es la sensibilidad de P1 | P1, Q4 |
| Evidencia fresca, no informe de agente | `implement-stage` no declara; solo audit | P2 |
| Plan ejecutable sin contexto | `Interfaces:` en cada tarea | C8 → P17 |
| Veredicto doble (spec + calidad) | `AUDIT.md` gana segunda columna | C9 → P18 |
| Ledger sobrevive compactación | Regla de reconciliación tras compactar | C10 → P21 |
| `Ruling:` en ejecución | Cambia la política de preguntar | C11 → P19, Q15 |
| Auto-revisión no vale | Roles separados, contexto curado | C12, P3 |
| Test-first no se proporcionaliza | Solo la revisión se escala por riesgo | C13 → P22 |
| RED antes de escribir una skill | Baseline obligatorio por regla | O5 → P20, Q17 |
| Control negativo | No hay regla sin caso que la justifique | O7 → P23 |
| Forma según el fallo | Reglas de redacción, no solo contenido | O8 → P24 |
