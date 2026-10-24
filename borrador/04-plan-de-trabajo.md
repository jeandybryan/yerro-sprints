# 04 — Plan de trabajo

> Orden **sugerido**. Se ajusta cuando `03-decisiones.md` fije los acuerdos y
> cuando aparezcan las ideas nuevas que quieres sumar.
>
> Regla: **nada entra a `skills/` sin fixture.** Este plan describe cómo se
> sacaría el borrador del borrador.

---

## Fases del plan

### Fase 0 — Congelar el alcance (esta conversación)

- [ ] Revisar `01-diagnostico.md`: ¿los huecos son los correctos?
- [ ] Revisar `02-propuestas.md`: ¿faltan mejoras? ¿sobra alguna?
- [ ] Revisar `06-economia-de-tokens.md`: ¿el eje coste/calidad refleja tu
      intención?
- [ ] Revisar `07-referencias-gentle-ai.md`: ¿aceptamos las correcciones que
      nos señala gentle-ai (B-17…B-20)?
- [ ] Resolver las preguntas de `05-preguntas-abiertas.md`.
- [ ] Marcar cada decisión de `03-decisiones.md` como `acordada` o
      `descartada`.
- [ ] **Criterio de salida:** ninguna propuesta queda `abierta` sin dueño de
      decisión; el plan de abajo se reescribe con lo acordado.

### Fase 1b — Contexto determinista (P11 + P14) — en paralelo

Dependencia: ninguna. Se puede hacer junto con la Fase 1.

1. `scripts/preflight.py`: lista mínima de lecturas por fase (sin presupuesto
   todavía), en **rutas y fragmentos exactos**, nunca resúmenes.
2. Regla P14 en `references/skill-maintenance.md`: ningún gate se sustituye por
   heurística; la omisión es el lado peligroso del ahorro.
3. `SKILL.md` de cada fase: una línea que apunte a `preflight.py`.
4. Fixture negativa: plan de lectura que incluye una etapa vecina debe fallar.
5. Regla B-18 en `implement-stage` y `audit-stage`: un test existente que falla
   detiene el trabajo, no se edita.

**Criterio de salida:** el contexto de una fase se calcula con un comando y el
recorte es siempre visible.

### Fase 1 — Endurecer la evidencia (P1 + P2) ✅ **IMPLEMENTADA** (2026-10-22)

Todo lo de abajo está en `skills/` con sus fixtures. Ver `CHANGELOG.md`.

**Lo que se hizo, con su prueba:**

| Cambio | Fixture / caso |
| --- | --- |
| `Test:` decorativo rechazado (lista negra + `**Runners:**`) | `test-decorativo` |
| `Sensibilidad` obligatoria en el ledger | `sin-sensibilidad` |
| `evidence.py run/verify` | `test_evidence.py` (16 comprobaciones) |
| `references/evidence.md` | enlazada desde `stage-contract.md`, `SKILL.md`, `TAREAS.md` |
| Fixtures negativas | `VALIDATE_REJECTED` en `test_next_step.py` |
| Casos retenidos | S19, S20 en `evals/cases/audit-stage.json` + `EVALUATION.md` |

**Evidencia de la fixture RED:** antes del cambio, `validate_stage.py --strict`
sobre `test-decorativo` devolvía `OK: contrato estructural válido` (exit 0).
Después devuelve `ERROR: T1 declara un Test: decorativo (true)`.

**Diferido dentro de la fase (no bloquea, no se pierde):**

- `verify_evidence.py` como script separado: su función vive en
  `evidence.py verify`. Se partió en dos solo si crece.
- Divergencia de la `firma=` entre `evidence.py verify` y el validador: hoy el
  validador comprueba **forma** (columna y contenido) y `verify` comprueba
  **reproducción**. Encadenarlos en `validate_stage.py --repo` es trabajo de la
  Fase 2, junto con `--repo` y la aprobación.
- Mutación obligatoria por CA crítico en riesgo alto: depende de Q1 (Fase 2).
- Test de regresión funcional contra `HEAD`: documentado en `evidence.md` como
  método aceptado; falta la fixture. Se hará en la Fase 2 junto al cruce
  riesgo ↔ evidencia.

**Criterio de salida cumplido:** las dos fixtures negativas fallan;
`valid-stage` pasa con el formato nuevo; la suite completa sigue verde
(97 + 8 + 8 + 17 + 16 comprobaciones).

### Fase 2 — Roles y riesgo (P3 + P4) ✅ **IMPLEMENTADA** (2026-10-23)

Lo que se hizo, con su prueba:

| Cambio | Fixture / caso |
| --- | --- |
| Aprobación humana en `.yerro/approvals.yml` (B-37) | `test_snapshot.py`: sin archivo, fuera de alcance, mal formado |
| Riesgo → fondo de la evidencia (B-12, B-35) | `riesgo-alto-sin-mutacion`, `riesgo-alto-mutante-verde`, `riesgo-alto-mutante-esperado` |
| Presupuesto derivado del riesgo (B-10) | `riesgo-alto-presupuesto-sin-motivo`, `presupuesto-amplio`, `riesgo-cruzado-con-motivo` |
| Criterio rebajado sin motivo | `cierre-sin-aprobacion` |
| Casos retenidos | S21–S23 en `EVALUATION.md` |

**Desfase corregido al implementar:** el gate de mutación aceptaba la palabra
`mutante` aunque el resultado declarado fuera `verde`. Un mutante que sobrevive
decía que el oráculo no cubre el comportamiento y la etapa cerraba igual. Ahora
se juzga el resultado observado (`rojo`); `verde`, `rojo esperado` y sin
resultado no cumplen, y un verde no lo compensa un rojo en otro CA.

**Diferido a la Fase 5:** los campos `**Implementado por:**` y `**Auditado
por:**` (B-08 seguirá `propuesta`). La aprobación humana ya es obligatoria para
cerrar, que es lo que B-08 protegería; registrar los roles sirve para decidir
*cuándo* basta la firma, y eso depende de B-26, que vive en la Fase 5.

**Criterio de salida cumplido:** sin aprobación humana la etapa no cierra; sin
la evidencia que el nivel exige, tampoco; la suite completa sigue verde (121
comprobaciones).

### Fase 2 — Plan original (P3 + P4)

Dependencia: Q1 y Q3 resueltas.

1. Campos `Aprobado por`, `Implementado por`, `Auditado por`.
2. Tabla riesgo → evidencia mínima en `stage-contract.md`.
3. Presupuesto de deltas derivado del riesgo (con motivo obligatorio para
   sobrescribir).
4. `validate_stage.py`: cruces riesgo ↔ ledger ↔ presupuesto.
5. `next_step.py`: presupuesto derivado.
6. Fixtures: `cierre-sin-aprobacion`, `riesgo-alto-sin-mutacion`,
   `riesgo-alto-presupuesto-sin-motivo`.
7. Casos en `test_next_step.py` y `test_skill_evals.py`.

**Criterio de salida:** no se puede cerrar una etapa sin firma humana ni una
etapa de riesgo alto sin la evidencia que su nivel exige.

### Fase 3 — Cierre completo (P5 + P6 + P7)

Dependencia: B-11 para "suite de referencia".

1. `Suites de referencia:` y `Comandos de calidad:` en `CONCILIACION.md`.
2. Bloque `Presupuesto no funcional` obligatorio (o `no aplica` con motivo).
3. Verificación global del `AUDIT.md` con suite, lint y diff.
4. `scripts/diff_scope.py`: cruce diff ↔ CA ↔ tarea.
5. Trazabilidad cruzada en `validate_stage.py` (P6, cinco sub-casos).
6. Fixtures: `sin-presupuesto-no-funcional`, `cambio-fuera-de-alcance`,
   `suite-roja`, y ampliación de `trazabilidad-invalida/`.
7. B-19: un caso que **ejecute la continuación** de cada código de bloqueo de
   `next_step.py` y compruebe que el bloqueo desaparece.
8. B-20: clasificación `in band` / `out of band` / `dead end` de cada bloqueo de
   fixture en `EVALUATION.md`; un `dead end` es error.
7. Consultas deterministas de estado (P13): `trace.py`, `tasks.py pending`.
8. Presupuesto de contexto por fase (P12) sobre `preflight.py`.

**Criterio de salida:** los gates cruzados funcionan y el positivo sigue verde
sin relleno artificial; el contexto de cada fase tiene presupuesto verificado.

### Fase 4 — Vía exprés y adopción (P8 + P10)

Dependencia: B-07, y para P10 los hosts soportados (`GOVERNANCE.md`).

1. `EXPRES.md`: `Comando`, `Resultado`, `Confirmado por`.
2. `doctor.py`: fila incompleta = `ERROR`; acumulación = `ERROR` con acción
   "abrir etapa".
3. B-17: veto por ítem de riesgo alto (lista numerada de 6) y test de
   reanudación en la frontera exprés.
3. Casos conductuales nuevos en `EVALUATION.md` para los fallos sembrados de
   Fase 1–3.
4. `RELEASE_CHECKLIST.md`: nivel 3 obligatorio.

**Criterio de salida:** un uso abusivo de la vía exprés no puede seguir sin abrir
etapa, y una release sin evaluación conductual no se publica.

### Fase 5b — Etapa ligera (P9) — **diferida**

Solo si las fases 1–4 demuestran que la fricción sigue siendo el problema
dominante. Antes de retomarla: medir cuántas veces `expres.py` devuelve
`no cabe` y cuántas etapas se abren para 2–3 archivos.

---

### Fase 5 — Disciplina de ejecución (P19 + P22 + P17)  ·  **Q15 resuelta: Modelo C**

**Parcialmente implementada (2026-10-23): B-21/B-25/B-26 (rulings) y B-27 (alcance en el diff).**

| Cambio | Fixture / caso |
| --- | --- |
| `diff_scope.py`: diff real vs. `**Archivos:**` declarado | `test_diff_scope.py` (15 comprobaciones) |
| Cruce en `validate_stage.py --repo` | `test_snapshot.py`: `colado.py` rechaza la pasada |
| `**Archivos:**` obligatorio en `templates/TAREAS.md` | `cambio-fuera-de-alcance` |
| `Ruling:` de tres partes | `ruling-sin-coste` (falla), `ruling-categoria-1` (pasa), casos del parser en `test_next_step.py` |
| `**Sujeto a revisión:**` resuelto al cerrar | `ruling-categoria-2-sin-revision` (falla), `ruling-categoria-2-revisado` (pasa) |
| Sección "Rulings" en `implement-stage`; `### Rulings revisados` en `templates/AUDIT.md` | — (documentación) |

B-27 se hizo **antes** que los rulings porque B-28 ya había eliminado
`--strict`: el contrato único quedaba **más débil** que antes, sin ningún gate
que mirase el diff. Un alcance sin comprobar no es un cierre, es una promesa.

Decisiones tomadas al implementar: `--base` por defecto `HEAD`, y la etapa se
interpreta relativa a la raíz del repo. Una ruta declarada que no cambió **no
bloquea**; B-27 solo veta lo que aparece sin declarar, porque juzgar si la tarea
se cumplió es cierre y no alcance (B-29).

De los rulings, la forma implementada concreta:

- El separador del `Ruling:` acepta `—`, `--` y `–`; se exigen **tres tramos no
  vacíos**, no una longitud mínima. El error nombra la parte que falta en prosa.
- La sección se llama `### Rulings revisados` y cada resolución empieza por
  `- aceptado` o `- hallazgo`. El cierre exige tantas resoluciones como marcas
  `**Sujeto a revisión:**` haya. No se cruza cada marca con su resolución: el
  conteo es lo que un validador puede juzgar sin leer el argumento.
- La categoría 3 no tiene gate propio porque B-27 ya la cubre: lo que ningún CA
  ni tarea declara aparece en el diff.

**Lo que queda de la Fase 5:** P22, P17 y la migración de las fixtures que aún
no declaran `**Archivos:**`.

Hecho:

1. ~~P19 / B-21 + B-25~~: sección "Rulings" en `implement-stage` con las tres
   categorías; `Ruling:` de tres partes obligatorias en `TAREAS.md`;
   `validate_stage.py` rechaza un ruling incompleto.
2. ~~P19 / B-26~~: `**Sujeto a revisión:**` y su sección de revisión en
   `AUDIT.md`; cierre bloqueado mientras haya uno sin resolver.
3. ~~P19 / B-27~~: comparación diff tocado vs. alcance declarado; archivo no
   declarado ⇒ `necesita-decision`.

Pendiente:

1. P22: corregir la tabla de P4 a dos ejes (prueba siempre, revisión
   proporcional).
2. P17: `Interfaces:` obligatorio en cada tarea.
3. ~~Fixtures de P19~~: `ruling-categoria-1`, `ruling-sin-coste`,
   `ruling-categoria-2-sin-revision`, `ruling-categoria-2-revisado`. La
   categoría 3 no tiene fixture propia: se cubre con `cambio-fuera-de-alcance`
   (B-27), porque lo que ningún CA ni tarea declara aparece en el diff. Los dos
   conductuales (decidir vs. parar; interfaces entre tareas) siguen pendientes y
   necesitan una sesión real, no una fixture estática.

~~B-28 — migración dura.~~ Hecho en el release del contrato: `--strict` y el
parámetro `legacy` ya no existen, `riesgo-ausente` y `ca-tipo` fallan siempre,
`doctor.py` avisa de una etapa no cerrada sin `**Archivos:**`, y `AGENTS.md`
prohíbe un gate con modo legado.

**Antes de publicar:** migrar las etapas en curso de los repos consumidores
(re-conciliar el alcance, nunca derivar del diff) o cerrarlas con la versión
anterior. Es la única operación de este plan que toca trabajo humano fuera del
paquete.

**Criterio de salida:** una ambigüedad de detalle no detiene la etapa y deja
ruling completo; una de alcance la detiene; ningún cierre pasa con un ruling
de categoría 2 sin revisar; `validate_stage.py` tiene un único modo y ninguna
fixture depende de `--strict`.

### Fase 6 — Calidad y mantenimiento del paquete (P18 + P20 + P21 + P23 + P24)

Dependencia: P10, Q16, Q17.

1. P18: veredicto doble en `AUDIT.md` y en el validador.
2. P21: `next_step.py --reconcile` y regla de reconciliación.
3. P24: forma de la regla según el tipo de fallo; revisar skills existentes.
4. P20 + P23: baseline y control negativo en `EVALUATION.md`,
   `CONTRIBUTING.md` y `AGENTS.md`.

**Criterio de salida:** no se puede cerrar una etapa sin veredicto de calidad,
y no se acepta una regla nueva sin baseline.

---

## Mapa de dependencias

```text
Fase 1b (P11, P14) ─── independiente, en paralelo ───┐
│
Fase 1 (P1, P2) ──> Fase 2 (P3, P4) ──> Fase 3 (P5, P6, P7, P12, P13) ──> Fase 4 (P8, P10, P15)
│
├──> Fase 5 (P19 [Modelo C], P22, P17)      ← desbloqueada: Q15 resuelta
└──> Fase 6 (P18, P20, P21, P23, P24)       ← espera Q16 y Q17
     │
     └── Fase 5b (P9, etapa ligera) diferida hasta medir fricción (B-06)
```

Nota: P19 no puede ir sola. B-26 necesita la sección de rulings de `AUDIT.md`,
que pertenece a Fase 6 (P18). Si se quiere entregar el Modelo C antes, se abre
`AUDIT.md` con solo esa sección y el resto del veredicto doble espera a P18.

P2 y P5 comparten la noción de "snapshot base del diff"; conviene diseñarlos
juntos aunque se implementen en fases distintas. P11/P14 son independientes: si
se retrasan, el coste de contexto se paga en todas las fases intermedias.

---

## Lo que NO hace este plan

- No rompe las seis fases ni añade una skill.
- No rebaja ningún gate existente (snapshot, riesgo congelado, presupuesto).
- No decide licencia, distribución, tags, hosts ni owner.
- No publica el borrador.

## Multiplicador de test por fase

Cada gate nuevo duplica el espacio de fixtures (estado positivo y negativo).
El plan asume que las fases se publican **de una en una**, con la suite entera
en verde entre fases. Publicar dos fases juntas implica un PR sin punto de
retorno claro: se desaconseja.
