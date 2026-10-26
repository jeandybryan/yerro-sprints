# 06 — Economía de tokens y primacía determinista

> Eje transversal del borrador. No es una propuesta suelta: condiciona el diseño
> de todas las demás (`P1`–`P10`) y de cualquier idea futura.
>
> Regla rectora: **si una regla se puede ejecutar, no se le pide al LLM que la
> recuerde.** Pero el determinismo nunca compra tokens a costa de la calidad:
> un gate barato que aprueba código malo es más caro que el token que ahorró.

---

## Parte A — ¿Cómo se cuenta hoy?

### Lo que el paquete **no** mide

Hoy no existe ninguna medición de coste. Ni de tokens, ni de número de
lecturas, ni de tiempo hasta evidencia suficiente. `EVALUATION.md` define la
rúbrica conductual e incluye "tiempo hasta evidencia suficiente" como métrica,
pero no hay un presupuesto, ni un registro, ni un criterio de "demasiado caro".

Tampoco existe un límite de tamaño por documento: `stage-contract.md` dice
"lee solo lo necesario" (`Política de contexto`), pero es una instrucción
**de cortesía**, no un gate. Un agente puede cargar `GOVERNANCE.md`,
`RELEASE_CHECKLIST.md` y todas las referencias en cada turno sin que nada lo
detecte.

### Lo que el paquete **sí** hace bien (y hay que proteger)

Cinco decisiones actuales ya son optimización de contexto, aunque no se llamen
así:

1. **Un artefacto por fase.** Cada fase lee solo lo que va a escribir.
2. **`next_step.py` en vez de razonar el estado.** La transición se calcula, no
   se infiere. Ahorra un razonamiento largo y evita errores de estado.
3. **Referencias bajo demanda.** `references/` se carga solo cuando se toca ese
   artefacto (`stage-contract.md`, "Política de contexto").
4. **Plantillas separadas por artefacto.** `templates.md` es índice; cada fase
   carga solo su plantilla.
5. **`snapshot.py` en vez de leer el árbol.** La identidad del código es un hash;
   el agente no pasea por el repo para describirlo.

Es decir: **la arquitectura ya va en la dirección correcta**. Lo que falta es
(a) medirlo, (b) presupuestarlo, y (c) extender el patrón a los puntos donde
hoy decide el LLM.

---

## Parte B — Hacia dónde: el test de la "regla determinizable"

Antes de escribir cualquier instrucción en una skill, aplica este filtro:

> **¿Puede un script decidir esto con la información disponible?**

| Si la respuesta es… | Entonces… | Ejemplo |
| --- | --- | --- |
| Sí, y es booleano | **script** | ¿la conciliación está `cerrada`? |
| Sí, y es calculable | **script que emite el valor** | snapshot, presupuesto derivado del riesgo, diff de alcance |
| No, pero es acotable | **script propone, LLM elige** | qué CA cubre una mutación |
| No, requiere criterio producto | **LLM, y humano aprueba** | ¿esta decisión es correcta? |

Corolario: una skill que dice "recuerda comprobar X" es deuda técnica de tokens.
Debería decir `python3 scripts/x.py` o no estar.

---

## Parte C — Propuestas

### P11 — `preflight.py`: el contexto se calcula, no se adivina

**Estado:** `implementada` ✅ (2026-10-26; P12 sigue sin número hasta Q9)
**Relación:** extiende la Política de contexto de `stage-contract.md`; depende de
P6 (trazabilidad) para saber qué citar.

**Qué:** un script de solo lectura que, dada una etapa, emita el **contexto
mínimo** que el agente necesita leer para esa fase:

```bash
python3 scripts/preflight.py <feature-root> --stage NN-slug --phase implement --json
```

Devuelve:

- la fase detectada (o delega en `next_step.py`);
- la **lista exacta de archivos a leer**, en orden, con tamaño en líneas;
- los **fragmentos** relevantes (p. ej. solo los CAs citados por las tareas
  pendientes, no la conciliación entera);
- lo que **no** debe leer (archivos de otras etapas, `GOVERNANCE.md`,
  referencias no aplicables) y por qué;
- los **totales**: líneas, KB, y una estimación de tokens con el margen de
  error declarado (estimación por caracteres, nunca un valor presentado como
  exacto).

**Dónde toca:** nuevo `scripts/preflight.py`, `stage-contract.md` (Política de
contexto pasa de texto a salida de script), `SKILL.md` de cada fase.

**Cómo se verifica:** fixture con etapa en `implementando` y otra etapa cerrada
al lado; el script debe devolver solo los archivos de la etapa activa. Caso
negativo: incluir la etapa vecina hace fallar el test.

**Restricción desde gentle-ai (`skill-registry.md`):** *"Delegators pass paths,
not digested rules."* `preflight.py` emite **rutas y fragmentos exactos**,
nunca resúmenes generados. Un índice puede ahorrar tokens; un resumen puede
distorsionar el contrato y costar más que los tokens ahorrados.

**Coste:** bajo. **Beneficio:** alto y medible (es el ahorro más grande, porque
evita leer lo que no se usa).

---

### P12 — Presupuesto de contexto por fase, verificado por script

**Estado:** `abierta`
**Relación:** B-11 (el humano declara), P11 (el script mide).

**Qué:** declarar en el contrato un presupuesto máximo de contexto por fase,
medido en **líneas de archivo leído** (determinista, sin dependencia de
tokenizador):

```text
identify   ≤ 400 líneas
conciliate ≤ 600
generate   ≤ 400
implement  ≤ 800  (+ código tocado, que no cuenta)
audit      ≤ 1000
```

`preflight.py --check` devuelve error si el plan de lectura de la fase excede el
presupuesto, y sugiere qué recortar. Sin `--check` solo informa.

**Regla de regresión:** subir el presupuesto exige motivo escrito en
`stage-contract.md`, igual que el presupuesto de deltas. El presupuesto es un
gate del paquete, no una aspiración.

**Corrección desde gentle-ai (C4):** su presupuesto **refusa** lo que no cabe
en vez de truncarlo ("never truncated"). Si nuestro presupuesto solo avisa,
el agente truncará en silencio. Ver Q9 en `05-preguntas-abiertas.md`.

**Por qué líneas y no tokens:** el conteo de tokens depende del host y del
modelo; el de líneas es reproducible en CI. La conversión a tokens es
información, no gate.

---

### P13 — Zero-diff antes de leer: el estado se deriva, no se narra

**Estado:** `abierta`
**Relación:** P5 (diff completo), P8 (vía exprés).

**Qué:** que las preguntas que hoy se responden con una lectura larga se
respondan con un script que emite una **línea**:

| Hoy (tokens) | Propuesta (determinista) |
| --- | --- |
| El agente lee el diff para saber qué cambió | `diff_scope.py --since <snapshot>` → una línea por archivo + clasificación |
| El agente lee `TAREAS.md` para saber qué falta | `tasks.py pending --stage NN` → IDs pendientes |
| El agente compara CA vs tareas vs evidencias | `trace.py --stage NN` → huecos, o `OK` |
| El agente re-ejecuta y describe el resultado | `evidence.py run` → firma (P2) |

Patrón común: **el LLM lee la conclusión, no el material con el que se obtuvo**.
La conclusión se puede verificar (`--check`); el material no se pierde: queda en
los artefactos para el humano.

---

### P14 — Calidad antes que descuento: el determinismo no rebaja gates

**Estado:** `abierta`
**Relación:** contrapeso explícito de P11–P13.

**Qué:** una regla que impida que "ahorrar tokens" se convierta en "cambiar
menos". En concreto:

1. **Ningún gate se sustituye por una heurística más barata.** Si el cierre
   exige sensibilidad (P1), un script que "parece que el test tiene assertion"
   no reemplaza ver el rojo.
2. **El script que no puede decidir, no decide.** `preflight.py` que no sabe si
   un fragmento es relevante debe **incluirlo**, no omitirlo. La omisión es
   siempre el lado peligroso del ahorro.
3. **Todo recorte es visible.** Si una fase lee menos, el `preflight.py` lo
   declara; un recorte silencioso es un defecto.
4. **La calidad se mide aparte del coste.** El ledger registra tokens/contexto
   *junto a* la rúbrica de calidad (P10). Una mejora de coste que empeora la
   rúbrica se descarta, aunque sea más barata.

**Cómo se verifica:** casos retenidos en `EVALUATION.md` con dos columnas:
resultado de calidad y coste. Un caso que baja la calidad con menor coste es
**regresión**, no mejora.

---

### P15 — Medir el coste de los eval, no solo puntuarlos

**Estado:** `abierta`
**Relación:** P10, `EVALUATION.md` nivel 3.

**Qué:** la evaluación conductual hoy puntúa 0/1 por rúbrica. Añadir por caso:

- líneas de contexto cargadas (vía `preflight.py`);
- número de lecturas de archivo;
- número de tool calls;
- (si el host lo expone) tokens in/out;
- tiempo hasta evidencia suficiente.

Y una regla: **un caso retenido que pase pero duplique el contexto de otro
pase idéntico es una regresión de coste**, no un empate. Se informa en el
reporte de release.

**Por qué importa:** sin esta fila, la primera propuesta que ahorre tokens y
baje la calidad parecerá una victoria en el reporte.

---

### P16 — Herramienta determinista para lo que el LLM hace mal por naturaleza

**Estado:** `abierta`
**Relación:** P1, P2, P6.

**Qué:** tres tareas donde el LLM no solo cuesta, sino que **falla
sistemáticamente**, y que hoy se le piden igual:

1. **Validar formato.** `validate_stage.py` ya lo hace para el contrato; falta
   extenderlo a todo lo nuevo (P6, P7). Mientras el agente tenga que
   "acordarse" del formato, cada turno paga tokens en recordárselo.
2. **Calcular identidad.** `snapshot.py` ya lo hace. Cualquier cosa con hash,
   timestamp, conteo o diff debe ser script. El LLM es malo en aritmética y
   reproduciblemente malo en "comparar dos cosas largas".
3. **Ejecutar y registrar.** `evidence.py` (P2). Pedirle al LLM que
   "re-ejecute y transcriba" es el peor de los dos mundos: paga tokens y puede
   alucinar el `exit`.

**Test de decisión** (Parte B aplicado): si el resultado es un valor
computable, el LLM no debe producirlo.

---

## Parte D — Cómo se traduce en la práctica

### Antes de agregar una instrucción a una skill

```text
¿Es una condición?         → script con exit code
¿Es un valor?              → script que lo emite
¿Es una decisión producto? → LLM, con formato de pregunta (Contexto/Pregunta/Propuesta)
¿Es un juicio de calidad?  → LLM, con humano que firma (P3)
```

### Lo que cambia en el contrato

- `stage-contract.md → Política de contexto` deja de ser prosa y pasa a tener
  presupuesto numérico y salida de `preflight.py`.
- Cada `SKILL.md` gana una línea: "el contexto de esta fase se calcula con
  `preflight.py`".
- `EVALUATION.md` gana la métrica de coste (P15) junto a la rúbrica de calidad.
- `README.md` gana una sección "Coste y determinismo" para que el usuario sepa
  qué esperar.

### Lo que **no** se hace

- No se acorta un artefacto quitándole contenido que el humano necesita
  (conciliación, audit, ledger).
- No se comprime la especificación.
- No se sustituye una lectura por un resumen que se pueda desincronizar del
  original: el script cita la fuente.
- No se promete un ahorro en tokens que el host no expone: se mide en líneas.

---

## Resumen para la tabla de prioridad

| ID | Mejora | Coste | Beneficio | Prioridad sugerida |
| --- | --- | --- | --- | --- |
| P11 | `preflight.py` (contexto calculado) | Bajo | Muy alto | 1 |
| P12 | Presupuesto de contexto por fase | Bajo | Alto | 2 |
| P13 | Consultas deterministas (estado, pendientes, huecos) | Medio | Alto | 2 |
| P14 | Calidad no se rebaja por coste | Nulo (regla) | Alto | 1 |
| P15 | Coste medido en la evaluación | Bajo | Medio | 3 |
| P16 | Determinismo donde el LLM falla | Medio | Alto | Con P1/P2 |

> P11 y P14 no dependen de nada y se pueden implementar en paralelo con la
> Fase 1. P12 y P13 requieren que P6 y P5 existan. P15 requiere P10.
