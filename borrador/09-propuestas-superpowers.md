# 09 — Propuestas derivadas de superpowers

> Anexo de `02-propuestas.md`, originado en `08-referencias-superpowers.md`.
> Misma convención de estados (`abierta` | `acordada` | `descartada` |
> `diferida`) y numeración estable: continúa en `P17`, tras `P16`.

---

## P17 — Un plan debe ser ejecutable por quien no tiene contexto

**Estado:** `acordada` ✅ (B-41, 2026-10-23)
**Origen:** C8. `writing-plans` (superpowers).
**Relación:** B-22, `generate-stage-tasks`, `templates/TAREAS.md`.

### Qué

Cada tarea de `TAREAS.md` gana un bloque **`Interfaces:`** con:

- **Consume:** firmas exactas que usa de tareas anteriores.
- **Produce:** nombres, parámetros y tipos que tareas posteriores darán por
  hechos.

Y dos reglas de forma, que actúan como antídoto contra los dos extremos:

1. **Una tarea es ambigua si no permite escribir exactamente una cosa
   razonable.** No exige ser completa.
2. **Una lista más larga que el código que describe ha escrito el código en
   lugar de describirlo.** Las líneas que no deciden nada ("manejar casos
   borde", "añadir validación apropiada", "TBD") son el fallo opuesto.

### Dónde toca

- `templates/TAREAS.md`: bloque `Interfaces:` obligatorio **solo en etapas con
  más de una tarea**; `Consume: ninguna` es un valor válido.
- `references/skill-maintenance.md`: regla de proporción.
- `generate-stage-tasks/SKILL.md`: verificación de interfaces entre tareas.

### Cómo se verifica

- Fixture `tarea-sin-interfaces`: tarea que consume una función de la tarea
  anterior sin declararla. Debe **fallar**.
- Fixture `tarea-vacia`: paso con "TBD" o "manejar casos borde". Debe
  **fallar**.
- Positivo con dos tareas enlazadas por `Interfaces:`.

### Coste
Bajo. **Beneficio:** alto; sin esto, un subagente tiene que inventar nombres.

---

## P18 — Veredicto doble: conformidad con la especificación y calidad

**Estado:** `implementada` (2026-10-27)
**Origen:** C9.
**Relación:** B-22, B-38, `audit-stage`, `templates/AUDIT.md`, P10.

**Hecho:** `AUDIT.md` conserva `**Veredicto:** coincide | no coincide` para la
especificación y gana `**Veredicto (calidad):** aceptable | con hallazgos |
bloqueante`. `validate_stage.py` juzga la pasada que cierra: exige el segundo
veredicto y solo acepta `aceptable`. `audit-stage/SKILL.md` y la plantilla
llevan la sección de cuatro comprobaciones, y un hallazgo que no nombra cuál es
queda fuera por revisión. Fixtures `calidad-ausente`, `calidad-con-hallazgos`,
`calidad-bloqueante` y `calidad-aceptable`; `EVALUATION.md` S41.

**Lo que no entra todavía:** el validador no comprueba que el hallazgo nombre
uno de los cuatro puntos. Ese cruce sería un gate que nunca puede fallar solo
—un veredicto distinto de `aceptable` ya no cierra—, así que la disciplina vive
en la skill y en la revisión, no en un error que no cambia el resultado.

### Qué

`AUDIT.md` deja de tener un único veredicto `coincide | no coincide` y pasa a
tener **dos**:

```text
**Veredicto (especificación):** cumple | no cumple | no verificado
**Veredicto (calidad):** aceptable | con hallazgos | bloqueante
```

Regla de cierre: se cierra solo si **ambos** son positivos.

La revisión de calidad tiene un foco pequeño y explícito (no es una revisión
general):

- duplicación introducida;
- abstracciones que nada pide (YAGNI);
- manejo de errores ausente en el camino nuevo;
- tests que prueban mocks en lugar de código.

### Dónde toca

- `templates/AUDIT.md`.
- `audit-stage/SKILL.md` (dos veredictos, no uno).
- `validate_stage.py` (el cierre exige ambos).
- Una skill de revisión o una referencia `quality-review.md`.

### Cómo se verifica

- Fixture `audit-spec-ok-calidad-mala`: CA `cumple` con un veredicto de calidad
  ausente. Debe **fallar** en `--strict`.
- Fixture `audit-calidad-bloqueante-no-cierra`: veredicto de calidad bloqueante
  con el índice cerrado. Debe **fallar**.
- Positivo con ambos veredictos.

### Coste
Medio: introduce un criterio subjetivo (calidad). Mitigación: foco cerrado de
cuatro puntos.

---

## P19 — `Ruling:` en ejecución: decidir y registrar en vez de parar

**Estado:** `acordada` ✅ (Modelo C; ver `10-modelo-c-rulings.md`)
**Origen:** C11, Q15.
**Relación:** B-21, B-25, B-26, B-27, `implement-stage`, `conciliate-stage`.

### Qué

Durante `implement-stage`, una ambigüedad no detiene el trabajo por sí misma.
La decisión se clasifica y cada clase tiene una respuesta obligatoria:

| Categoría | Qué es | Qué hace el agente |
| --- | --- | --- |
| 1. Detalle de implementación | No cambia lo que el usuario recibe | Decide y registra `Ruling:` con coste |
| 2. Efecto observable, reversible | Visible pero trivial de deshacer, sin cambio de alcance | Decide, registra y marca `**Sujeto a revisión R1:**` |
| 3. Intención, alcance o criterio | Cambia lo pedido o lo aceptado | **Para y reabre conciliación** |

Formato cerrado, las tres partes obligatorias:

```text
Ruling: <qué decidí> — <por qué> — <qué cuesta si me equivoco>
```

Cuándo **sí** se para, por encima de las categorías (lista cerrada):

1. operación irreversible o destructiva;
2. acción sensible a seguridad;
3. efecto fuera del worktree (merge, push, publicación);
4. dependencia externa nueva (librería, servicio o modelo): llega con sus CVE y
   su licencia;
5. plan tan roto que todo camino es adivinar;
6. categoría 3 — cambio de intención, alcance o criterio de aceptación.

La regla de `conciliate-stage` ("no cerrar con supuestos") no cambia: sigue
aplicando al **baseline**.

### Dónde toca

- `implement-stage/SKILL.md`: sección "Rulings" con las tres categorías.
- `templates/TAREAS.md`: campo `Ruling:` (repetible) y
  `**Sujeto a revisión R1:**` por tarea.
- `references/decision-and-questions.md`: distinguir "pregunta de baseline" de
  "ruling de ejecución".
- `validate_stage.py`: tres partes del `Ruling:`; diff declarado vs. tocado.
- `templates/AUDIT.md`: sección de rulings a revisar (B-26).

### Cómo se verifica

- Fixture `ruling-categoria-1`: separador de CSV sin decidir. Debe **pasar** y
  exigir `Ruling:` con las tres partes.
- Fixture `ruling-sin-coste`: `Ruling:` sin "qué cuesta". Debe **fallar**.
- Fixture `ruling-categoria-3`: columna extra no pedida por ningún CA. Debe
  **abrir `necesita-decision`**.
- Fixture `ruling-archivo-no-declarado`: toca un archivo que ninguna tarea
  declara. Debe **fallar** (B-27).
- Fixture `ruling-categoria-2-sin-revision`: marca `Sujeto a revisión` y el
  `AUDIT.md` no lo resuelve. Debe **fallar el cierre**.
- Fixture `ruling-y-parada`: dos ambigüedades en la misma tarea —una de
  categoría 2 y una de categoría 3— en `evals/cases/implement-stage.json`.
  El agente acierta si las trata **distinto**.

### Coste
Nulo en código para la política. **Medio** para B-27 (comparación diff vs.
alcance declarado). Alto en redacción, porque cambia la política.

---

## P20 — Toda regla nueva necesita su baseline (RED antes de escribir)

**Estado:** `abierta`
**Origen:** O5, O7. `writing-skills` (superpowers).
**Relación:** B-24, `EVALUATION.md`, `CONTRIBUTING.md`, `AGENTS.md`.

### Qué

Una regla nueva en una skill solo entra si trae **evidencia de que el agente
falla sin ella**:

```text
Regla: <texto>
Baseline: <qué hizo el agente sin la regla; cita verbatim>
Reps: <n ≥ 5 por variante>
Control: <si el control no falla, la regla no entra>
```

Y la regla dura:

> Si el control negativo no exhibe el fallo, **no hay nada que corregir**:
> la regla no se escribe.

Esto ataca directamente el riesgo de que el paquete crezca sin que cada regla
demuestre servir. Complementa el nivel conductual de `EVALUATION.md`.

### Dónde toca

- `EVALUATION.md`: nuevo nivel "RED de regla" previo al conductual.
- `CONTRIBUTING.md` y `AGENTS.md`: una regla nueva sin baseline no se acepta.
- `references/skill-maintenance.md`.

### Cómo se verifica
Es una regla de proceso del paquete, no un gate de fixture. Se verifica en
revisión de PR: un PR que añade una regla sin baseline es **incompleto**.

### Coste
Alto en ejecución (tokens + agente). **Bajo en código.**
Mitigación: baseline solo para reglas **nuevas o que cambian comportamiento**,
no para correcciones de redacción ni fixes factuales.

---

## P21 — Regla de reconciliación tras compactación

**Estado:** `abierta`
**Origen:** C10.
**Relación:** `TAREAS.md`, `next_step.py`, P13, P21.

### Qué

Una regla explícita en cada `SKILL.md` operativo:

> El contexto no sobrevive a la compactación. El estado se relee de
> `README.md`, `TAREAS.md` y `git log`; **no se recuerda**.

Y `next_step.py` gana un modo `--reconcile` que imprime, en pocas líneas, lo
que falta y los commits desde el último registro. Un agente que perdió el hilo
lo ejecuta antes de actuar.

Métrica asociada: el fallo más caro observado por superpowers fue
**re-ejecutar tareas completas que se perdieron de contexto**. Debe ser un caso
retenido del nivel conductual.

### Dónde toca

- `next_step.py` (`--reconcile`).
- `SKILL.md` de las fases operativas.
- `EVALUATION.md`: caso "contexto compactado".

### Cómo se verifica
- Fixture con `TAREAS.md` donde T1–T3 están hechas y T4 pendiente. El script
  debe indicar T4 y **no** reabrir T1–T3.

### Coste
Bajo. **Beneficio:** elimina el fallo más caro conocido.

---

## P22 — Test-first no se proporcionaliza; la revisión sí

**Estado:** `acordada` ✅ (B-42, 2026-10-23)
**Origen:** C13.
**Relación:** B-23, P4, P1.

### Qué

Separar explícitamente dos ejes que hoy mezclamos:

| Nivel | Siempre | Proporcional al riesgo |
| --- | --- | --- |
| Test-first | ✅ | — |
| Sensibilidad demostrada (revertir → fallar → restaurar) | ✅ | — |
| Suite de referencia | ✅ antes de cerrar | — |
| Revisión independiente | | ✅ `passive` / `medium` / `high` |

Corrige el exceso de P4: en riesgo `bajo` exijamos menos **revisión**, no menos
**prueba**.

### Dónde toca
- `references/stage-contract.md`: tabla de dos ejes.
- P4 (`02-propuestas.md`): corregir la tabla "riesgo → evidencia".

### Cómo se verifica
- Fixture `riesgo-bajo-sin-test-first`. Debe **fallar**.
- Fixture `riesgo-bajo-con-test-first-sin-revision-independiente`. Debe
  **pasar**.

### Coste
Bajo: es corrección de doctrina y de una tabla.

---

## P23 — El control negativo y la varianza en la evaluación

**Estado:** `abierta`
**Origen:** O7.
**Relación:** P10, P15, P20.

### Qué

Todo experimento de redacción o de cambio de skill se reporta con:

- **control sin la guía** (si el control no falla, no se mide);
- **≥5 repeticiones por variante** (una muestra miente);
- **varianza**: si cinco repeticiones dan cinco interpretaciones, la redacción
  no obliga, aunque cada una "parezca bien".

Un resultado sin control no cuenta como evidencia de mejora.

### Dónde toca
- `EVALUATION.md` (nivel conductual y de redacción).
- `RELEASE_CHECKLIST.md`.

### Cómo se verifica
En el reporte de release: cada cambio de skill cita control, reps y varianza.

### Coste
Medio en ejecución. **Beneficio:** impide declarar mejoras que solo son azar.

---

## P24 — La forma de la regla depende del tipo de fallo

**Estado:** `abierta`
**Origen:** O8.
**Relación:** redacción de todas las skills.

### Qué

Antes de escribir una regla, clasificar el fallo:

| Fallo | Forma correcta |
| --- | --- |
| Salta la regla bajo presión | prohibición + tabla de racionalizaciones + red flags |
| Output con forma equivocada | receta positiva (el output ES esto, en orden) |
| Omite un elemento | campo obligatorio en la plantilla |
| Depende de condición | condicional con predicado observable |

Y dos prohibiciones de redacción:

1. **sin cláusulas de matiz** ("no hagas X salvo que importe" reabre la
   negociación);
2. **las excepciones no se escriben como cláusulas**: son otro condicional
   con predicado observable.

### Dónde toca
- `references/skill-maintenance.md`.
- Revisión de `conciliate-stage` y `audit-stage`, que hoy tienen mucho "No
  hagas" donde quizá corresponda plantilla.

### Cómo se verifica
Caso en `test_skill_evals.py`: una regla de forma escrita como prohibición
para un fallo de forma se marca como aviso en el catálogo.

### Coste
Bajo. **Beneficio:** las reglas existentes empiezan a funcionar donde hoy no.

---

## Prioridad de estas propuestas

| ID | Mejora | Prioridad sugerida | Depende de |
| --- | --- | --- | --- |
| P19 | `Ruling:` en ejecución | 1 | Q15 |
| P18 | Veredicto doble | 2 | P10 |
| P17 | Interfaces en tareas | 2 | — |
| P21 | Reconciliación tras compactación | 2 | — |
| P22 | Test-first vs revisión | 2 | Q1 |
| P20 | Baseline de regla (RED) | 3 | P10, P23 |
| P24 | Forma según el fallo | 3 | — |
| P23 | Control negativo y varianza | 4 | P10, P15 |
