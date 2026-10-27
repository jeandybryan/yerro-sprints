# 11 — Resolución de lo abierto

> Estado: **cerrado** el 2026-10-23, **revisado** el 2026-10-27 cuando Q9
> encontró su dato. De las 20 preguntas, 18 quedaron resueltas.
> Q2 y Q13 siguen diferidas por decisión (B-06). Q1 se ratificó el 2026-10-23
> como B-10 con `alto → 1`; Q9 se cerró al medir seis features reales.
>
> Cada bloque conserva **qué cambia** y **qué se pierde**, para que la decisión
> pueda revisarse con su motivo cuando llegue el momento.

---

## Estado final: 20 preguntas, 18 cerradas

| Pregunta | Cómo quedó | Norma |
| --- | --- | --- |
| Q3 + Q12 | Archivo `.yerro/approvals.yml` versionado, sin PR ni commit firmado | B-37 |
| Q4 | Lista negra por defecto + lista blanca declarada | B-34 |
| Q5 | Mutación como procedimiento, sin herramienta obligatoria | B-35 |
| Q6 | Corregir el README: cerrar con evidencia sí requiere Python | B-30 |
| Q7 | `ninguna` solo en riesgo bajo y con motivo | B-36 |
| Q8 | Promoción exprés por par archivo+CA | B-39 |
| Q10 | Los scripts deciden fronteras mecánicas, nunca alcance ni cierre | B-29 |
| Q11 | Universales obligatorios; tokens informativos | B-31 |
| Q14 | Techo duro + reanudabilidad debajo | Q14 §Resolución |
| Q15 | Modelo C (tres categorías de ruling) | B-21, B-25, B-26, B-27 |
| Q16 | Veredicto de calidad con cuatro comprobaciones cerradas | B-38 |
| Q17 | Baseline solo para reglas que cambian comportamiento | B-24 |
| Q18 | Migración dura, sin modo legado | B-28 |
| Q19 | El auditor revisa con artefactos, no con memoria | B-32 |
| Q20 | Aviso a partir de cuatro rulings por tarea | B-33 |
| Q1 | Presupuesto derivado `bajo → 2`, `medio → 1`, `alto → 1`, sobrescribible con motivo | B-10 |
| Q9 | Presupuesto recomendado calibrado sobre trabajo real: `identify`/`audit` 900, `conciliate`/`generate` 300, `implement` 400 | P12, B-15 |
| Q2 | ⏸ Diferida (B-06) | — |
| Q13 | ⏸ Diferida (B-06) | — |

**Consecuencia:** ninguna fase está bloqueada por una pregunta sin responder.
Q9 se resolvió al medir, no al escribir más: el número salió de seis features
reales y entró como recomendación. Q1 se ratificó al implementar, con la
evidencia del gate cruzado (B-10).

## Por qué estas se pudieron cerrar sin elegir nada

### Q10 — ¿El determinismo sustituye a la conciliación?

**Respuesta:** no, y no hace falta cambiar nada para acordarlo.

Un script decide **fronteras mecánicas**: conteos, rutas excluidas, acumulación,
el presupuesto derivado, la coherencia de un snapshot, qué archivo declaró la
tarea. Nunca decide **alcance, riesgo ni cierre**. La persona sigue siendo la
única que aprueba una conciliación.

Y la forma de comprobarlo: **si la regla necesita interpretar intención, no va
a un script.**

### Q6 — ¿La evidencia ejecutable rompe la promesa "sin Python"?

**Respuesta:** sí, y hay que corregir el README en lugar de esconderlo.

`README.md` dice "Python es opcional, solo para validadores estructurales". P2
introduce `evidence.py`, que **ejecuta** comandos, así que el cierre `--strict`
pasaría a requerir Python.

La corrección honesta: *"operar no requiere Python; cerrar con evidencia sí"*.
La alternativa —reimplementar la captura de evidencia en cada host— cuesta más
que la promesa que intenta salvar.

### Q11 — ¿Cómo se mide el coste si el host no expone tokens?

**Respuesta:** se mide lo universal, y los tokens son un extra informativo.

Líneas leídas, número de lecturas, número de ejecuciones: eso lo puede
reproducir CI. Los tokens no, porque dependen del host y del día — es justo lo
que gentle-ai descartó como métrica. Un gate sobre lo irreproducible no es un
gate.

### Q20 — ¿Cuántos rulings antes de que la tarea esté mal escrita?

**Respuesta:** tres. Y es un aviso, no un bloqueo.

El régimen es **> 3 rulings de categoría 1 en una tarea**. No es un número
mágico que aplica a todo: es el punto donde la tarea deja de parecerse a una
tarea con un detalle y empieza a parecerse a una tarea sin `Test:`. Lo calcula
`doctor.py`, que ya recorre artefactos e índice.

Por qué aviso y no bloqueo: una tarea de migración puede producir
legítimamente cuatro detalles (separador, codificación, orden de columnas,
locale). Bloquearla obligaría a partirla en cuatro tareas de una línea, que es
peor. El aviso apunta a `generate-stage-tasks`, que es donde se arregla.

Coste: cero. Ya existen el parser y el recorrido.

### Q19 — ¿Quién revisa los rulings de categoría 2?

**Respuesta:** el auditor de la etapa, **pero leyendo solo los artefactos**.

Es la corrección que superpowers aporta (C12): *"implementer self-review never
replaces the task review"*, y el revisor recibe *"precisely crafted context —
never your session's history"*. En nuestra arquitectura eso ya está a medio
hacer: `audit-stage` no lee la conversación, lee `TAREAS.md`, `CONCILIACION.md`
y el diff.

La regla queda: **el auditor no puede usar como justificación "yo lo decidí
porque…".** Solo vale el `Ruling:` escrito y el diff. Si el ruling no explica la
decisión, es un hallazgo — y eso convierte B-25 en algo que se paga solo.

---

## Las que necesitaban un dato (ya lo tienen)

Q9 encontró su dato el 2026-10-27. Q1 ya estaba ratificada como B-10.

### Q9: el presupuesto de contexto se calibró con trabajo real

P12 proponía números (`identify ≤ 400` líneas, `audit ≤ 1000`…) que eran
**estimaciones**. Fijarlos antes de medir crea un gate que se incumple para
poder trabajar.

**Cómo se hizo:** `preflight.py` entró **sin gate**, en modo informe, y el
número esperó al dato. El dato llegó en forma de corpus: seis features reales
—47 etapas, todas implementadas y cerradas con el proceso— medidas fase por
fase. El máximo observado redondeado a la centena da `identify`/`audit` 900,
`conciliate`/`generate` 300, `implement` 400.

**Qué corrigió el dato:**

1. `identify ≤ 400` habría rechazado 2 de 6 árboles reales (679 y 824), que el
   equipo dio por buenos. Un gate que rechaza trabajo aceptado se aprende a
   saltar.
2. `identify` con 400 y `audit` con 1000 era incoherente: ambos leen los mismos
   tres archivos de la etapa y daban el mismo total en las seis features.
   Cualquier etapa entre 400 y 1000 demostraba que uno de los dos sobraba.

**`WARN` o `ERROR`:** con el 100 % del corpus aceptado dentro del presupuesto,
un simple aviso no sirve; el gate debe morder cuando una etapa se desborde de
verdad. Clase `ERROR`.

**Cómo entra:** como **recomendación** en `stage-contract.md`, no como valor por
defecto. `--check` sigue mirando solo las etapas que declaran
`**Presupuesto de contexto:**`, así que ningún trabajo en curso queda bloqueado
retroactivamente por un número que no aceptó.

### Q1: la tabla riesgo → evidencia se deriva, no se inventa

~~P4 propone `bajo → 2`, `medio → 1`, `alto → 0` deltas. Son números míos.~~

**Ratificada el 2026-10-23 como B-10** con `bajo → 2`, `medio → 1`,
`alto → 1`, sobrescribible con `**Motivo del presupuesto:**`. El `alto → 0`
del borrador se descartó: una etapa de riesgo alto sin corrección posible es
una etapa que no se cierra, no una que se cierra sin deltas. Queda anotado aquí
porque esta sección es donde nació la pregunta.

---

## Las que eran decisiones de producto (ya elegidas)

Estas cinco cambiaban lo que el paquete **exige**. Elegiste en todas:

| Pregunta | Elección |
| --- | --- |
| Q3 + Q12 | Archivo versionado en el repo; **sin PR** como requisito |
| Q4 | Lista negra + lista blanca |
| Q5 | Procedimiento sin herramienta |
| Q7 | `ninguna` solo con motivo y riesgo bajo |
| Q14 | Techo duro + reanudabilidad debajo |

Lo de abajo queda como **registro del razonamiento**, no como pregunta pendiente.

### Q4 — ¿Cómo se rechaza un `Test:` decorativo?

**Opciones:**

1. **Lista negra** de comandos vacíos (`true`, `echo`, `sleep`, `:`). Barato,
   cubre el abuso evidente, no cubre el disfrazado (`bash -c true`).
2. **Lista blanca** de runners por proyecto. Más fuerte, pero cada proyecto
   nuevo necesita configuración antes de poder validar.
3. **Ambas**: negra por defecto, blanca declarada en la conciliación.
4. **Ninguna**: la sensibilidad demostrada (P1 nivel 2) es la que protege; el
   análisis estático solo da falsa tranquilidad.

**Mi recomendación: (3)**, porque la negra es gratis y la blanca desaparece el
día que el proyecto tiene un runner raro. Pero (4) es defendible: el gate que
de verdad detecta un `Test:` decorativo es ver el test fallar, no reconocer el
nombre del runner.

**Lo que se pierde con (3):** proyectos sin runner detectable necesitan una
línea de configuración antes de la primera etapa. Con (1) no.

### Q5 — ¿La mutación es obligatoria sin herramienta?

**Opciones:**

1. **Procedimiento documentado**, sin herramienta: cualquier método que deje
   `mutante: <descripción>` + `resultado: rojo`. Portable, verificable a mano
   por el auditor.
2. **Herramienta concreta** (Stryker / mutmut / PIT). Fuerte, pero rompe la
   promesa de portabilidad y presupone el lenguaje.
3. **Solo para riesgo alto**, y solo si el proyecto ya la tiene.

**Mi recomendación: (1).** El objetivo del gate es **ver el rojo**, no instalar
mutmut. Superpowers lo dice de otra forma pero con el mismo criterio: *"If you
didn't watch the test fail, you don't know if it tests the right thing"* — lo
que importa es la observación, no el instrumento.

### Q7 — ¿Puede quedar vacía la suite de referencia?

**Opciones:**

1. Libre, incluso vacía, con motivo.
2. `ninguna` solo con motivo **y riesgo bajo**.
3. Siempre al menos un comando global.

**Mi recomendación: (2).** Riesgo `medio`/`alto` con suite "ninguna" es el
escenario exacto donde el falso cierre vive. Pero forzar un comando en un
proyecto de riesgo bajo crea ceremonia sin valor.

### Q3 + Q12 — ¿Quién firma la aprobación?

Las dos preguntas tienen la misma respuesta; propongo fusionarlas.

| Opción | Falsificable por el agente | Coste humano |
| --- | --- | --- |
| Marca textual `Aprobado por:` | **Sí** | Ninguno |
| Archivo de configuración versionado (`.yerro/approvals.yml`) | No, si el agente no puede escribirlo | Bajo: editar y comitear |
| Comando que solo corre una persona (`approve.py`) | No, si el host bloquea la herramienta | Bajo, pero depende del host |
| Commit firmado (GPG/SSH) | No | Alto: todo el equipo firma |

**Mi recomendación: el archivo de configuración como base, el commit firmado
como opción para equipos, y el comando como comodidad.** El texto libre
desaparece: una marca que el agente puede escribir no es una marca.

**Lo que se pierde:** el flujo de "una línea en el artefacto". A cambio, la
aprobación pasa a ser un cambio revisable en un PR, que es donde se ve.

### Q14 — ¿El conteo de archivos sigue decidiendo la vía exprés?

**Opciones:**

1. **Se queda el conteo** (hoy `expres.py`: 1 archivo, ≤20 líneas).
2. **Solo la lista de riesgo alto como veto**, sin conteo.
3. **Reanudabilidad** (¿se entiende desde la petición y el `git diff`?) como
   criterio principal, conteo como techo de seguridad.

**Mi recomendación: (3)**, porque el conteo es un proxy y gentle-ai tiene razón
en que *"counts of files, commands, tests, fixes … never decide it"*. Pero tiene
un problema práctico: **la reanudabilidad requiere juicio, y `expres.py` no
tiene juicio.**

Por eso la forma concreta: `expres.py` **sigue midiendo** (es determinista y
gratis) y emite un **techo duro** (por encima de N archivos no cabe, sin
discusión). La reanudabilidad se consulta solo **debajo del techo**, donde hoy
la respuesta es "cabe" y podría ser "no cabe porque no se entiende".

Esto añade un paso humano a la vía exprés, que es lo que lo hacía barato. **Es
el intercambio real**, y conviene que lo decidas tú, no yo.

---

## Lo que queda por delante

Nada de este documento bloquea el plan.

- **Q9** quedó cerrada el 2026-10-27. El dato no era el `Total:` de una etapa: existía ya en seis features reales del corpus (47 etapas, todas implementadas y cerradas). El máximo por fase, redondeado a la centena, da `identify`/`audit` 900, `conciliate`/`generate` 300, `implement` 400, y entra en `stage-contract.md` como **recomendación**: `--check` sigue mirando solo las etapas que declaran `**Presupuesto de contexto:**`. El dato corrigió dos cosas del borrador: `identify ≤ 400` habría rechazado 2 de 6 árboles reales, y `identify`/`audit` no pueden tener presupuestos distintos porque leen los mismos archivos.
- **Q2 y Q13** siguen diferidas hasta medir la fricción (B-06).
- El siguiente trabajo es **implementar**, no seguir diseñando.
- **Los IDs internos se citan en lo que se distribuye, pero no viajan con él.** `skills/` cita **23 IDs distintos en 107 apariciones** —`B-27` diecisiete veces, `B-26` once, `B-35` nueve, `P17` ocho…— como procedencia de sus reglas, y `npx skills add` copia solo `skills/`: quien instala el paquete no puede resolver ninguno. No es una referencia rota como `PUBLISHING.md` —la frase se entiende sin abrirla— pero sí una dependencia invisible. Decidido 2026-10-27: se anota y no se toca; hacerlos resolubles dentro del paquete o quitarlos es una decisión de producto pendiente.

Y una advertencia sobre el propio método: las dieciocho decisiones de arriba
fueron acordadas en conversación, no probadas. Antes de escribir la primera
regla en `skills/` hay que ver al agente fallar sin ella (B-24) y, sobre todo,
alfilerar con fixtures que hoy **fallan** con el contrato viejo (B-02). Sin
fixture, una decisión acordada es solo una buena intención.
