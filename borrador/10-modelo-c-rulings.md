# 10 — Modelo C: rulings de ejecución

> Estado: **acordado** por el usuario el 2026-10-22.
> Norma asociada: B-21, B-25, B-26, B-27 (`03-decisiones.md`).
> Propuesta asociada: P19 (`09-propuestas-superpowers.md`), Fase 5 del plan.
> Este documento es el **diseño operativo**: cómo se escribe, cómo se verifica y
> qué cambia en cada archivo.

---

## La idea en una frase

> La pregunta no es **"¿tengo duda?"** sino **"¿esto cambia lo que el usuario
> recibe o lo que se aceptó?"**. Según la respuesta, se decide, se decide y se
> marca, o se para.

Y la segunda frase, que es la que hace que el modelo sea implementable:

> Un `Ruling:` sin **coste de equivocarse** es una decisión oculta, y una
> decisión oculta es peor que una pregunta.

---

## Las tres categorías

| Categoría | Predicado observable | Qué hace el agente | Cómo se verifica |
| --- | --- | --- | --- |
| **1. Detalle de implementación** | El resultado observable del CA no cambia | Decide, registra `Ruling:` | El ruling tiene tres partes; el diff está en archivos declarados |
| **2. Efecto observable, reversible** | El usuario vería algo distinto, pero es trivial de deshacer y el alcance no cambia | Decide, registra y marca `**Sujeto a revisión:**` | El `AUDIT.md` resuelve cada marca (acepta o convierte en hallazgo) |
| **3. Intención, alcance o criterio** | Cambia lo pedido, lo aceptado o un CA | **Para y reabre `conciliate-stage`** | El diff contiene archivos o superficie que ningún CA menciona |

### Ejemplos por categoría (para que no se confunda)

| Situación | Categoría | Por qué |
| --- | --- | --- |
| Separador `,` o `;` de un CSV | 1 | La cabecera y el contenido no cambian |
| Nombre de una variable interna | 1 | No observable |
| Librería A o B, ambas ya en el proyecto, con la misma API | 1 | No cambia lo que se recibe |
| Orden de dos pasos internos sin efecto externo | 1 | No observable |
| Texto exacto de un mensaje de error nuevo | 2 | Observable, reversible, no cambia el alcance |
| Formato de fecha `2026-10-22` o `22/10/2026` | 2 | Observable, reversible |
| Límite por defecto de una paginación (`50` o `100`) | 2 | Observable, reversible; conviene revisarlo |
| Columna extra en el CSV | 3 | Superficie nueva: alcance |
| Endpoint que ningún CA pide | 3 | Superficie nueva: alcance |
| Cambiar el criterio de aceptación para que el test pase | 3 | Cambia lo que se acepta |
| Refactor de un módulo no tocado por la tarea | 3 | Alcance |
| Borrar datos reales, migración sin vuelta | parada | Irreversible |
| Tocar credenciales, permisos, criptografía | parada | Seguridad |
| `git push`, merge a main, publicar | parada | Fuera del worktree |

El caso del refactor es el más importante y el más incómodo: **un refactor
"de paso" es categoría 3 aunque sea reversible**, porque cambia lo que se
revisa y lo que se acordó. Si se necesita, va a la tarea siguiente o a
conciliación.

---

## El formato del ruling

```text
Ruling: <qué decidí> — <por qué> — <qué cuesta si me equivoco>
```

Las tres partes son obligatorias y el validador las rechaza por separado.
Ejemplos válidos, uno de cada categoría:

```text
Ruling: separador `;` en el CSV — el CA menciona locales europeos en
openspec — coste: una línea en el exportador y el test de formato.
                                   (categoría 1)

**Sujeto a revisión:** límite por defecto 50 en `/items` y no 100 —
coincide con el resto de listados del proyecto — coste: cambiar un
constante y un test de paginación; el usuario vería más resultados.
                                   (categoría 2)
```

Y el inválido, que es el que de verdad importa:

```text
Ruling: usé `;` — convención regional.
```

→ **rechazado**: falta la parte de coste. No se puede evaluar qué se pierde si
está mal.

### Regla de redacción del coste

El coste no es una opinión libre. Se escribe en uno de estos tres términos:

- **cuánto código**: "una constante y un test";
- **qué se revierte**: "se revierte con `git revert` de un commit";
- **qué no se puede recuperar**: "los registros borrados no vuelven" → esto
  **no es un ruling**, es una parada.

Buscar un término concreto es lo que evita el `Ruling: … — porque era mejor —
cuesta poco` universal.

---

## Dónde se registra

Cada `Ruling:` vive **junto a la tarea** que lo produjo, en `TAREAS.md`:

```markdown
### T-03 — Exportar CSV

**Estado:** hecha
**Test-first:** sí
**Test:** `pytest tests/export/test_csv.py::test_cabecera` — E-04

Ruling: separador `;` — el CA menciona locales europeos — coste: una línea
en el exportador y el test de formato.
```

No hay un registro separado de rulings. El ledger de tareas ya es el registro,
y duplicarlo cuesta contexto sin ganar nada (B-13).

---

## Cómo se verifica (las cinco fixtures)

| Fixture | Configuración | Resultado esperado |
| --- | --- | --- |
| `ruling-categoria-1` | Tarea con un detalle sin decidir y un `Ruling:` completo | **pasa** |
| `ruling-sin-coste` | `Ruling:` de dos partes | **falla**: falta el coste |
| `ruling-categoria-3` | Tarea añade una columna que ningún CA menciona | **`necesita-decision`** |
| `ruling-archivo-no-declarado` | El diff toca un archivo que ninguna tarea declara | **falla** |
| `ruling-categoria-2-sin-revision` | Marca `Sujeto a revisión` y `AUDIT.md` no lo resuelve | **falla el cierre** |

Las cinco son estructurales, sin agente: son comparaciones de texto y de
rutas. El único caso conductual es *"ante una ambigüedad de detalle, el agente
no para"*, y se evalúa con el método de `EVALUATION.md` (control, ≥5 reps).

### Qué queda fuera del alcance de las fixtures

- **Que el agente clasifique bien.** Eso es un caso conductual, no un gate.
- **Que el ruling sea "correcto" en el fondo.** El validador comprueba forma y
  coherencia con el diff; el fondo lo revisa el auditor.

---

## Lo que hay que cambiar, archivo por archivo

| Archivo | Cambio | Tipo |
| --- | --- | --- |
| `references/decision-and-questions.md` | Separar pregunta de baseline (conciliar) de ruling (ejecutar), con la tabla de tres categorías | doc |
| `implement-stage/SKILL.md` | Sección "Rulings" con la tabla y la lista de paradas; quitar "si es ambigua, para y pregunta" | doc |
| `templates/TAREAS.md` | Campo `Ruling:` repetible y campo `**Sujeto a revisión:**` | template |
| `templates/AUDIT.md` | Sección `### Rulings revisados`: cada categoría 2 tiene aceptación o hallazgo | template |
| `references/stage-contract.md` | La transición `implement → audit` admite rulings; `implement → conciliate` exige categoría 3 | doc |
| `validate_stage.py` | Tres partes del ruling; diff declarado vs. tocado; categoría 2 sin resolver | código |
| `evals/fixtures/` + `test_validate_stage.py` | Las cinco fixtures | test |
| `EVALUATION.md` | Caso conductual "no para ante un detalle" | doc |

### El único código nuevo de verdad: B-27

`validate_stage.py` necesita saber **qué archivos declara cada tarea** para poder
comparar con el diff. Eso obliga a un campo nuevo en `TAREAS.md`:

```markdown
**Archivos:** `src/export/csv.py`, `tests/export/test_csv.py`
```

Sin ese campo, "archivo no declarado" no se puede detectar. Es el mismo
problema que `next_step.py` resolvió con el índice: **el estado tiene que ser
declarativo para poder comprobarlo**.

Y una consecuencia que hay que aceptar de antemano: **una tarea que hoy no
declara archivos no puede pasar el gate nuevo**. La migración de las features
en curso necesita una decisión (Q18).

---

## Migración: la decisión de Q18

Se migra duro (B-28). No hay etapa que quede a medio camino.

### Lo que hoy ya se puede reutilizar

`validate_stage.py` tiene hoy dos modos: sin `--strict` los formatos antiguos son
**advertencias**, con `--strict` son **errores**. `SKILL.md` ya invoca con
`--strict`, así que en la práctica el camino de advertencia ya existe solo para
las fixtures.

Al publicar B-27:

- **se elimina `--strict`** y el parámetro `legacy` de `Result.require`;
- las fixtures que hoy viven de esa dualidad (`riesgo-ausente`, `ca-tipo`) pasan
  a ser **positivas o se retiran**;
- `CONTRIBUTING.md`, `EVALUATION.md` y `SKILL.md` dejan de invocar con
  `--strict`.

No hay "soporte legado" que mantener: hay **una** ruta que siempre falla y
**un** conjunto de fixtures que la describe.

### Cómo se migra una etapa, en orden

1. Leer los CA y las tareas de `TAREAS.md`.
2. Escribir `**Archivos:**` por tarea **desde los CA**, no desde el diff.
3. Comprobar que cada CA tiene al menos una tarea y cada archivo declarado tiene
   al menos una tarea que lo produce.
4. Marcar `**Migrada:** AAAA-MM-DD (origen: re-conciliación)`.
5. Ejecutar `validate_stage.py`. Si algo no cierra, la etapa **no estaba lista**;
   el gate está haciendo su trabajo.

Si una etapa ya tenía código implementado, el origen del diff **no** es una
fuente válida para `**Archivos:**`. Rellenarlo así produce un `TAREAS.md` que
describe lo hecho, y entonces B-27 no detecta nada nunca. La alternativa
honesta es re-conciliar el alcance con el humano y seguir, o descartar el
trabajo.

### La migración la hace el humano, no el validador

Es tentador escribir un `--migrate` que proponga los archivos desde el diff. No
lo hacemos: sería automatizar exactamente el atajo que B-27 existe para
detectar.

Lo que sí se puede automatizar sin tocar el juicio es **saber a quién le toca**:
`doctor.py` ya recorre el índice y los artefactos. Se le añade una comprobación
por etapa —¿el `TAREAS.md` de una etapa no cerrada tiene todos los archivos
declarados?— y una lista de las etapas pendientes de migrar. Es la misma función
que ya cumple hoy: informar incoherencias entre el índice y los artefactos, sin
decidir por nadie.

### Lo que aceptamos perder

Una etapa en curso se detiene hasta que alguien la migre. Es un coste real y
único. A cambio, el paquete no arrastra dos contratos indefinidamente ni tiene
que probar cada fixture en dos modos.

---

## Dónde puede fallar el modelo (y qué lo contiene)

| Riesgo | Contención |
| --- | --- |
| El agente clasifica un cambio de alcance como categoría 1 | B-27: se detecta en el diff, no en la confesión |
| El agente escribe "cuesta poco" en todo | B-25 exige la parte de coste; B-26 obliga a revisar las categorías 2 |
| El humano deja de leer porque "todo se decide" | Las categorías 2 y 3 siguen siendo visibles: una en `AUDIT.md`, otra como `necesita-decision` |
| El modelo se usa para salir de un plan roto | Parada 4: "plan tan roto que todo camino es adivinar" |
| Un refactor "de paso" pasa como 1 | La tabla de ejemplos lo pone explícitamente en 3 |
| Una migración escribe `**Archivos:**` desde el diff | B-28: se prohíbe como fuente; la etapa migrada desde el diff se marca y se ve en auditoría |

---

## Relación con las otras propuestas

- **P1 / P2** (evidencia): un ruling no es evidencia de que el test pase. Sigue
  aplicando la regla de que solo el `audit-stage` con verificación fresca cierra.
- **P4 / P22** (riesgo): el riesgo decide **cuánta revisión**, no si se puede
  decidir. Un ruling en riesgo alto se revisa, no se prohíbe.
- **P17** (`Interfaces:`): un `Ruling:` de categoría 1 que cambia un nombre
  público debería haber sido una tarea, no un ruling. Las interfaces declaradas
  son el límite.
- **P18 / B-22** (veredicto doble): la sección de rulings revisados es una
  columna del veredicto de calidad.
- **P20 / B-24** (baseline): el caso conductual "no para ante un detalle" es
  exactamente el tipo de regla que necesita baseline. Superpowers lo dice al
  revés: si el agente **ya no paraba** sin la regla, la regla sobra.
