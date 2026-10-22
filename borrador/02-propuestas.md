# 02 — Propuestas

> Estado de cada propuesta: `abierta` | `acordada` | `descartada` | `diferida`.
> Todas están hoy `abierta`: son material de discusión, no contrato.

Cada propuesta explica: **qué**, **dónde toca** (artefacto/skill/script),
**cómo se verifica** (fixture y caso), **coste** e **impacto**.
La numeración `P1..P10` es estable: se cita desde `03-decisiones.md`.

---

## P1 — Sensibilidad del test como gate

**Estado:** `acordada` ✅ (niveles 1 y 2 implementados; nivel 3 en Fase 2)
**Diagnóstico:** D1, D2
**Impacto:** muy alto — es la propuesta que hace que `coincide` signifique algo.

### Qué

Tres niveles, de menos a más:

1. **Oráculo mínimo exigido.** `Test:` debe invocar un runner y emitir un
   veredicto interpretable. Rechazar explícitamente:
   comandos vacíos, `true`, `echo`, `sleep`, `:` o cualquier comando que no
   produzca un código de salida dependiente del comportamiento. El validador
   no puede ser omnisciente: se define una **lista de comandos prohibidos**
   configurable por el consumidor, más la regla de "debe aparecer un runner".
2. **Prueba de fallo (para riesgo medio/alto).** El ledger `E-NN` registra,
   además del verde, el **fallo observado**:
   - mutación (`mutante: <descripción>`, `resultado: rojo esperado`), o
   - fallo inyectado (`fallo inyectado: <descripción>`), o
   - valor esperado alterado a mano (`oráculo alterado: ...`).
3. **Mutación orientada por riesgo.** Para `alto`, la pasada de auditoría
   incluye al menos una mutación por CA crítico y registra el score
   (mutantes detectados / mutantes generados) o su justificación si la
   herramienta no existe en el proyecto.

### Dónde toca

- `references/decision-traceability.md`: `Test-first:` pasa a tener semántica
  verificable.
- `templates/AUDIT.md`: el ledger gana columnas `Sensibilidad` y
  `Mutante/fallo inyectado`.
- `templates/TAREAS.md`: `Test:` con formato `comando → oráculo esperado`.
- `scripts/validate_stage.py`: rechaza comandos prohibidos y exige el campo de
  sensibilidad para riesgo medio/alto.
- `references/scoring-and-evidence.md` (nuevo o ampliado): define qué cuenta
  como sensibilidad.

### Cómo se verifica

- Fixture `test-decorativo`: `Test: true` con etapa cerrada. Debe **fallar**
  con el contrato nuevo.
- Fixture `sin-sensibilidad-riesgo-alto`: veredicto `coincide`, riesgo alto,
  sin mutante ni fallo inyectado. Debe **fallar**.
- Caso en `test_next_step.py` o nuevo `test_sensibilidad.py`.

**Refuerzo desde gentle-ai:** ODD exige además **un test de regresión
funcional** por cada comando/opción existente que el cambio toca: ejecutar el
comando viejo contra `HEAD` y contra el cambio, comparar `stdout`, `stderr` y
`exit code`, y tratar cualquier diferencia no pedida como regresión. Es la
forma concreta de demostrar sensibilidad sin depender de una herramienta de
mutación.

### Coste

Bajo para los niveles 1 y 2; alto para el 3 (requiere herramienta de mutación
en el proyecto consumidor). El nivel 3 puede ser `diferido` a una segunda
iteración sin bloquear 1 y 2.

### Riesgo de la propuesta

- Falsos positivos: proyectos sin runner "detectable" (scripts ad hoc).
  Mitigación: lista de runners configurable y escape documentado.
- Fricción: escribir mutaciones cuesta. Mitigación: exigirlo solo desde riesgo
  medio.

---

## P2 — Evidencia ejecutable, no narrativa

**Estado:** `acordada` ✅ (implementada en Fase 1; verificación encadenada en Fase 2)
**Diagnóstico:** D10
**Impacto:** muy alto — es la base sobre la que descansan todos los gates.

### Qué

Que el ledger deje de ser texto libre y pase a referenciar **el resultado real**
de una ejecución:

1. Un ayudante (p. ej. `scripts/evidence.py run -- <comando>`) ejecuta el
   comando, captura `exit`, stdout/stderr y un **hash del output normalizado**, y
   escribe una entrada estructurada (JSON o línea de tabla con firma).
2. El ledger `E-NN` cita la firma, no una transcripción.
3. `validate_stage.py --repo` comprueba que la firma del ledger corresponde al
   comando declarado en la tarea y al snapshot auditado.
4. Un `verify_evidence.py` re-ejecuta el comando desde el snapshot y compara la
   firma; si no coincide, la evidencia es `no verificado`.

No se exige que el agente use el ayudante para *pensar*; se exige que toda
evidencia **citada para el cierre** provenga de él.

### Dónde toca

- Nuevo `scripts/evidence.py` y `scripts/verify_evidence.py`.
- `templates/AUDIT.md`: formato del ledger.
- `references/stage-contract.md`: sección de evidencia.
- `validate_stage.py --repo`.
- `test_snapshot.py` / nuevo `test_evidence.py`.

### Cómo se verifica

- Fixture `evidencia-inventada`: `E-01` con firma que no corresponde al
  comando. Debe **fallar**.
- Fixture `evidencia-estable`: misma entrada, mismo comando, firma repetible.
  Debe **pasar**.
- `test_evidence.py` cubre: firma sensible al output, insensible al orden de
  líneas volátiles (timestamps), rechazo de exit distinto.

### Coste

Medio. Es la propuesta con más superficie de implementación, pero la que
convierte el paquete de "protocolo" en "herramienta".

### Riesgo de la propuesta

- Los comandos no deterministas (puertos, fechas) rompen la firma. Mitigación:
  normalización declarada por el proyecto (regex de sanitización) y modo
  `--no-signature` documentado con justificación obligatoria.
- Añade dependencia conceptual del validador con la ejecución; hay que
  mantenerlo read-only respecto a los artefactos.

---

## P3 — Aprobación humana y separación de roles

**Estado:** `abierta`
**Diagnóstico:** D3
**Impacto:** alto

### Qué

1. **Marca de aprobación** obligatoria en dos puntos:
   - `CONCILIACION.md` cerrada: `**Aprobado por:** <persona> · <fecha>`;
   - `AUDIT.md` antes de tocar el índice: `**Aprobado por:** <persona> · <fecha>`
     o `**Cerrado con riesgo residual:** <persona> · <fecha>`.
2. **Separación de roles declarada**, no impuesta por el host (que no la puede
   verificar): el artefacto registra `**Implementado por:**` y
   `**Auditado por:**`; si son el mismo agente/persona, la auditoría debe ir
   acompañada de la marca humana. Es decir: auto-auditoría permitida solo con
   revisión humana.
3. Validación: una etapa `cerrada` sin marca de aprobación falla
   `validate_stage.py --strict`.

### Dónde toca

- `templates/CONCILIACION.md`, `templates/AUDIT.md`.
- `references/stage-contract.md`, `references/decision-and-questions.md`.
- `validate_stage.py` (dos campos nuevos).

### Cómo se verifica

- Fixture `cierre-sin-aprobacion`: etapa cerrada sin `Aprobado por`. Debe
  **fallar**.
- Fixture `aprobacion-conciliacion-ausente`: conciliación `cerrada` sin marca.
  Debe **fallar**.
- Positivo `valid-stage` actualizado con ambos campos.

### Coste

Bajo en código; **alto en proceso**: obliga a que haya una persona. En un repo
personal puede ser el propio dueño; el punto es que quede firmado y no
implícito.

### Riesgo de la propuesta

- Si el agente puede escribir `<persona>`, la marca es falsificable. Mitigación:
  la marca debe venir de un archivo de configuración del usuario
  (`GOVERNANCE`/`.yerro/config`) fuera del alcance del agente, o de un commit
  firmado. **Decisión abierta** (ver Q3 en `05-preguntas-abiertas.md`).

---

## P4 — Riesgo que define el mínimo de evidencia

**Estado:** `abierta`
**Diagnóstico:** D4
**Impacto:** alto

### Qué

| Riesgo | Evidencia mínima obligatoria |
| --- | --- |
| bajo | nivel `estructural` + `conductual`; ≥1 caso negativo |
| medio | + sensibilidad demostrada (P1 nivel 2) + un caso límite |
| alto | + fallo inyectado + recuperación observable + revisión humana (P3) |

`**Presupuesto de deltas:**` deja de tener default silencioso:

- `bajo` → 2; `medio` → 1; `alto` → 0 (cualquier `no coincide` vuelve a
  conciliación).
- Se puede sobrescribir en la conciliación, pero con **motivo escrito**.

El validador cruza: riesgo congelado ↔ nivel de evidencia en el ledger ↔
presupuesto. Una etapa de riesgo alto con presupuesto 3 es un `necesita-decision`
si no hay motivo.

### Dónde toca

- `references/stage-contract.md`.
- `templates/CONCILIACION.md` (casilla de motivo).
- `next_step.py` (derive el presupuesto si no está escrito).
- `validate_stage.py` (cruce riesgo ↔ evidencia).

### Cómo se verifica

- Fixture `riesgo-alto-sin-mutacion`: riesgo alto, ledger sin fallo inyectado.
  Debe **fallar**.
- Fixture `riesgo-alto-presupuesto-2`: presupuesto explícito 3 sin motivo. Debe
  **fallar**.
- Caso en `test_next_step.py` para el presupuesto derivado.

### Coste

Bajo. Es sobre todo tabla de decisión y dos validaciones cruzadas.

### Riesgo de la propuesta

- La tabla es una opinión. Debe acordarse con el usuario antes de fijarla.
  **Decisión abierta** (Q1 en `05-preguntas-abiertas.md`).

---

## P5 — Cierre con suite completa y diff completo

**Estado:** `abierta`
**Diagnóstico:** D5
**Impacto:** alto

### Qué

La "Verificación global" del `AUDIT.md` deja de ser narrativa y pasa a exigir,
como mínimo:

1. **Suite completa** del repo (o el conjunto declarado en la conciliación
   como "suite de referencia") en verde, no solo los `Test:` de las tareas.
2. **Lint/tipado** en verde, con el comando fijado en la conciliación.
3. **Diff completo contra el snapshot base** (`git diff --stat BASE..HEAD` o
   equivalente) revisado y clasificado: cada archivo tocado pertenece a un CA
   o a una tarea; cualquier otro archivo es **desviación de alcance** y debe
   declararse (informativa / requiere revisión / bloqueante).
4. Si el proyecto mide cobertura, **delta de cobertura** de líneas nuevas
   (opcional, declarado en la conciliación).

### Dónde toca

- `templates/AUDIT.md` (bloque global).
- `templates/CONCILIACION.md` (campos: `Suites de referencia:`,
  `Comandos de calidad:`).
- `audit-stage/SKILL.md` (procedimiento).
- Posible `scripts/diff_scope.py` que cruce diff ↔ CAs ↔ tareas.

### Cómo se verifica

- Fixture `cambio-fuera-de-alcance`: diff toca un archivo sin CA ni tarea, el
  audit no lo declara. Debe **fallar**.
- Fixture `suite-roja`: suite de referencia falla y el audit dice `coincide`.
  Debe **fallar** en `--strict`.
- Positivo actualizado con suite verde declarada.

### Coste

Bajo en contrato; medio si se quiere verificar el diff automáticamente.

### Riesgo de la propuesta

- Exigir la suite completa puede ser caro en repos grandes. Mitigación:
  "suite de referencia" declarada por el operador humano, no la completa por
  defecto.

**Refuerzo desde gentle-ai:** para cada comando/opción que el cambio toca,
comparar comportamiento contra `HEAD` (stdout, stderr, exit) y tratar la
diferencia como regresión. Es más barato que la suite completa y encuentra lo
que la suite no cubre.

---

## P6 — Trazabilidad cruzada como invariante

**Estado:** `abierta`
**Diagnóstico:** D6
**Impacto:** medio

### Qué

`validate_stage.py` comprueba mecánicamente:

- todo `CA-NN` citado en `TAREAS.md` y `AUDIT.md` existe en `CONCILIACION.md`;
- todo `CA-NN` tiene ≥1 `T` y ≥1 `E` referenciada;
- toda `E-NN` referenciada tiene fila en el ledger de **esa** pasada;
- toda `S-NN` citada existe y no está duplicada;
- una `T` retirada no se recicla con semántica distinta (se registra
  `retirada: sí` y motivo).

### Dónde toca

- `validate_stage.py`.
- `references/decision-traceability.md` (sección "invariantes verificables").

### Cómo se verifica

- Ampliar `trazabilidad-invalida/` con cinco sub-casos: CA inventado, E
  inventada, S inexistente, ID duplicado, T reciclada.
- Caso en `test_next_step.py` o nuevo `test_trazabilidad.py`.

### Coste

Bajo. Es parsing sobre lo que ya se lee.

### Riesgo de la propuesta

- Ninguno relevante. Es la de menor riesgo de todas: puro endurecimiento de lo
  que ya se hace.

---

## P7 — Presupuesto no funcional en la conciliación

**Estado:** `abierta`
**Diagnóstico:** D7
**Impacto:** medio

### Qué

Bloque obligatorio en `CONCILIACION.md`:

```text
**Presupuesto no funcional:**
- Latencia: p95 ≤ … ms   | no aplica (motivo)
- Memoria: ≤ … MB        | no aplica (motivo)
- Tamaño/artefacto: ≤ …  | no aplica (motivo)
- Dependencias nuevas: 0 | justificadas
- Rendimiento de operación crítica: …
```

Regla: cada línea se rellena **o** se marca `no aplica` con motivo. El
validador exige el bloque; no juzga los números (eso es del humano en la
conciliación).

`Verificar:` de las tareas hereda el umbral correspondiente; la auditoría
mide y compara.

### Dónde toca

- `templates/CONCILIACION.md`.
- `references/stage-contract.md`.
- `validate_stage.py` (presencia del bloque).
- `templates/TAREAS.md` (referencia al umbral).

### Cómo se verifica

- Fixture `sin-presupuesto-no-funcional`: conciliación cerrada sin el bloque.
  Debe **fallar**.
- Fixture `presupuesto-no-aplica-mudo`: `no aplica` sin motivo. Debe fallar.
- Positivo con bloque completo.

### Coste

Bajo; el coste real es de disciplina, no de código.

### Riesgo de la propuesta

- Se puede llenar con `no aplica` en todo y no medir nada. Es aceptable: el
  contrato registra la decisión, y una auditoría humana puede discutirla.

---

## P8 — Vía exprés con verificación y promoción automática

**Estado:** `abierta`
**Diagnóstico:** D8
**Impacto:** medio

### Qué

1. Cada fila de `EXPRES.md` añade `**Comando:**` y `**Resultado:**` (exit y
   propósito de la prueba). Sin estos campos la fila no es válida: `doctor.py`
   lo trata como `ERROR`, no como `WARN`.
2. **Promoción automática** (pasa de `WARN` a `ERROR`):
   - ≥3 cambios sobre el mismo archivo o CA;
   - cambio en un segundo archivo de producción del mismo CA;
   - cambio exprés dentro de una ventana en la que ya se abrió etapa sobre ese
     archivo.
3. Las dos confirmaciones humanas (`sin CA nuevo`, `sin interfaz pública
   cambiada`) se registran como `**Confirmado por:** <persona> · <fecha>`.
   Sin eso, la fila es inválida.

### Dónde toca

- `templates/EXPRES.md`.
- `scripts/expres.py` (no decide promoción: solo cuenta).
- `scripts/doctor.py` (regla de promoción).
- `references/express-lane.md`.

### Cómo se verifica

- Fixture `expres-sin-verificacion`. Debe **fallar**.
- Fixture `expres-acumulado` (ya existe): pasa de `WARN` a `ERROR`.
- `test_expres.py`: nuevos casos.

### Coste

Bajo.

### Riesgo de la propuesta

- El `ERROR` por acumulación puede bloquear trabajo legítimo. Mitigación: la
  promoción es "abrir etapa" con el registro como contexto; no impide
  mergear, impide **seguir sin etapa**.

---

## P9 — Etapa ligera intermedia

**Estado:** `abierta` — **la de mayor riesgo de complicar el paquete**
**Diagnóstico:** D9
**Impacto:** medio (a discutir si no es alto)

### Qué

Un modo declarado en el índice (`Modo: ligera`) para features con:

- 2–3 archivos de producción (el número se acota, ver Q2);
- riesgo `bajo`;
- sin migraciones, auth, contratos compartidos ni interfaz pública.

Diferencia con la etapa normal:

- `CONCILIACION.md` de una página: resultado + CA + no-funcional "no aplica";
- `TAREAS.md` de una tabla;
- **sin delta posible**: si el audit no coincide, se reabre la conciliación
  (el presupuesto es 0 de todos modos por riesgo bajo… o se necesita una
  excepción; ver Q2);
- la auditoría sigue exigiendo sensibilidad (P1 nivel 1) y suite de referencia
  (P5).

No es una séptima skill: es una **variante de plantilla** que el propio
`validate_stage.py` reconoce por el campo `Modo`.

**Revisión tras `07-referencias-gentle-ai.md` (C1/C2):** la frontera "2–3
archivos" es la métrica equivocada según gentle-ai ("counts of files … never
decide it"). Si P9 se retoma, debe clasificar por **reanudabilidad + riesgo
contenido** (B-17), no por número de archivos. Ver Q14.

### Dónde toca

- `templates/README.md` (campo `Modo`).
- `templates/CONCILIACION.md`, `templates/TAREAS.md` (variantes compactas).
- `validate_stage.py` (campos requeridos según modo).
- `references/stage-contract.md`.

### Cómo se verifica

- Fixture `etapa-ligera-valida`. Debe **pasar**.
- Fixture `etapa-ligera-con-alto-riesgo`. Debe **fallar**.
- Fixture `etapa-ligera-con-migracion`. Debe **fallar**.
- Hmm: la comprobación "2-3 archivos de producción" requiere el diff del
  snapshot, así que **depende de P2/P5**.

### Coste

Medio-alto si depende del diff; medio si se limita a campos declarados.

### Riesgo de la propuesta

- **Seis fases son el contrato.** Añadir un modo con menos artefactos puede
  diluir la garantía y multiplicar los casos de test (todas las transiciones ×
  dos modos). Mi recomendación inicial es `diferida`: primero se implementa
  P1, P3, P5, P6 y P7; si la fricción sigue siendo real, se retoma P9 con
  medición de por qué la vía exprés no basta.

---

## P10 — Gate conductual de adopción

**Estado:** `abierta`
**Diagnóstico:** D1, D2, D10
**Impacto:** alto a largo plazo

### Qué

Convertir el nivel 3 de `EVALUATION.md` (evaluación conductual bajo demanda) en
**gate de adopción del paquete**: al modificar una skill o el contrato, la
evaluación conductual de los casos retenidos (S01–S18, I01) debe ejecutarse y
pasar antes de publicar. Mientras no se ejecute, el cambio es `no verificado`.

Añadir a los casos retenidos los nuevos fallos sembrados de este borrador:

- test decorativo con `Test: true` (P1);
- evidencia inventada con firma falsa (P2);
- cierre sin aprobación humana (P3);
- riesgo alto sin mutación (P4);
- suite roja declarada `coincide` (P5).

### Dónde toca

- `EVALUATION.md` (nivel 3 pasa de "bajo demanda" a "requerido para release").
- `RELEASE_CHECKLIST.md`.
- `evals/cases/*.json` y `evals/fixtures/`.
- `CONTRIBUTING.md`.

### Cómo se verifica

- El propio checklist de release: una release sin resultados de nivel 3 no se
  publica.
- `test_skill_evals.py` verifica que cada caso tenga expectativas y fixture.

### Coste

Alto en ejecución (tokens + modelo fijo); casi nulo en código.

### Riesgo de la propuesta

- Requiere fijar modelo, versión del host y fecha (ya lo pide `EVALUATION.md`).
- Es la que más se beneficia de la decisión de "hosts soportados" que sigue
  pendiente en `GOVERNANCE.md`.

---

## Tabla resumen
| ID | Mejora | Prioridad sugerida | Estado | Depende de |
| --- | --- | --- | --- | --- |
| P1 | Sensibilidad del test | 1 | `abierta` | — |
| P2 | Evidencia ejecutable | 1 | `abierta` | P1 (parcial) |
| P3 | Aprobación humana / roles | 2 | `abierta` | Q3 |
| P4 | Riesgo → evidencia | 2 | `abierta` | Q1 |
| P5 | Suite + diff completo | 2 | `abierta` | — |
| P6 | Trazabilidad cruzada | 3 | `abierta` | — |
| P7 | Presupuesto no funcional | 3 | `abierta` | — |
| P8 | Vía exprés verificable | 3 | `abierta` | — |
| P9 | Etapa ligera | 4 | `abierta` | P5, Q2 |
| P10 | Gate conductual de adopción | 4 | `abierta` | P1–P5, hosts |

> La prioridad es **mi recomendación**, no una decisión. La discusión y el
> orden real viven en `04-plan-de-trabajo.md` y `03-decisiones.md`.
