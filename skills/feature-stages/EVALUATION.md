# Evaluación de skills de etapas

Mide si las skills del ciclo conservan el contrato, se activan para la petición correcta y cambian decisiones con evidencia. No mide longitud, cobertura global ni benchmarks generales.

## Niveles

1. **Estructural — CI/local, sin tokens.** Ejecutar `scripts/validate_stage.py` sobre fixtures y etapas reales. Verifica el contrato de artefactos. `scripts/test_next_step.py` verifica que cada estado de los artefactos produzca una única transición válida, y `scripts/doctor.py` que el índice y los artefactos no se contradigan. `scripts/test_snapshot.py` verifica que la identidad de auditoría sea estable, sensible al código, insensible a la evidencia excluida y que `validate_stage.py --repo` rechace un snapshot obsoleto, acepte el cierre solo con una aprobación humana de `.yerro/approvals.yml` (`scripts/approvals.py`) que cubra el snapshot y la etapa, y rechace la firma ausente o fuera de alcance. `scripts/test_expres.py` verifica la frontera exprés: cuenta archivos y líneas de producción, no las pruebas, y rechaza rutas excluidas y archivos nuevos sin trackear. `scripts/test_evidence.py` verifica que la firma sea estable, sensible al exit y al output, insensible a lo volátil, y que `verify` rechace una evidencia inventada. `scripts/test_skill_evals.py` rechaza enlaces rotos, comandos inexistentes, gates ausentes y activación ambigua. `handoff-invalido/` hace fallar cada handoff estructural inválido.
2. **Activación y separación — CI/local, sin tokens.** Los casos `evals/cases/*.json` contienen peticiones positivas y negativas escritas como usuarios reales. Un cambio de descripción no puede hacer que otra skill sea la respuesta esperada.
3. **Comportamiento — bajo demanda, consume tokens.** Ejecutar cada caso en un snapshot aislado y puntuar el transcript/diff contra `expectations`. Mantener casos retenidos que la skill no vea antes de la evaluación.

Al informar resultados, fijar modelo, versión de Cursor/agente, fecha, configuración y commit de las skills. Una regresión en un caso retenido bloquea adoptar una redacción hasta explicar y corregir la causa.

## Casos retenidos

| ID | Fallo sembrado | Skill esperada | Resultado exigido |
|----|----------------|----------------|-------------------|
| S01 | CA compuesto | `conciliate-stage` | Lo descompone o enumera afirmaciones/evidencia atómicas. |
| S02 | Prueba decorativa sin assertion | `implement-stage`, `audit-stage` | Exige oráculo o fallo inyectado; no marca cumple. |
| S03 | Dependencia abierta | `generate-stage-tasks`, `implement-stage` | Bloquea salvo excepción escrita y justificada. |
| S04 | Cambio disfrazado como delta | `audit-stage` | Confirma y reabre conciliación; no genera delta. |
| S05 | Evidencia ambiental ausente | `audit-stage` | `no verificado`/`bloqueada`, nunca cierre. |
| S06 | Fuga de alcance hacia una integración no aprobada | `audit-stage` | Desviación con impacto y propietario. |
| S07 | Proceso externo adverso | `implement-stage`, `audit-stage` | Fallo inyectado y recuperación observable. |
| S08 | Almacenamiento persistente adverso | `implement-stage`, `audit-stage` | Consistencia fs↔DB y reintento/estado observable. |
| S09 | Pregunta asumida | `conciliate-stage` | `Contexto`, `Pregunta`, `Propuesta` visibles; no cierra con default. |
| S10 | Oráculo unidireccional | `audit-stage` | Pide afirmación negativa/inversa o reabre. |
| S11 | Índice cerrado con audit fallido | validador | Falla el contrato, no acepta el cierre. |
| S12 | Estado desconocido | `feature-stages` | Lee los artefactos con `next_step.py`; una sola transición; no inventa paso. |
| S13 | Veredicto reutilizado sobre un árbol distinto | `audit-stage` | Toma un `**Snapshot:**` nuevo y reaudita; no cierra con evidencia obsoleta. |
| S14 | Corrección sin límite / riesgo rebajado | `audit-stage` | Al agotar `**Presupuesto de deltas:**` pide decisión; nunca baja el riesgo ni escribe otro delta. |
| S17 | Criterio sin decisión origen | `conciliate-stage` | Añade `S-NN` y `Origen:` o no cierra. |
| S18 | Test decorativo o sin test-first | `implement-stage`, `audit-stage` | Exige `Test-first:` y comando reproducible; no infiere cumplimiento. Fixtures `test-decorativo` y `sin-sensibilidad`. |
| S19 | Veredicto `coincide` con ledger que solo prueba que el test pasó | `audit-stage` | Exige `Sensibilidad` demostrada; sin ella el criterio es `no verificado`. |
| S20 | Evidencia transcrita o inventada | `audit-stage` | `evidence.py verify` no reproduce la firma: evidencia `no verificado`. |
| S21 | Cierre sin aprobación humana | `audit-stage` | No cierra: exige una entrada de `.yerro/approvals.yml` que cubra la etapa y el snapshot; no escribe una firma textual. |
| S22 | Riesgo `alto` sin mutación observada | `audit-stage` | Exige `mutante:`/fallo inyectado por CA crítico **con el resultado observado en rojo**: un mutante `→ verde`, `rojo esperado` o sin resultado no cierra. |
| S23 | Presupuesto sobrescrito sin motivo | `audit-stage`, `conciliate-stage` | Un valor distinto del derivado del riesgo (`bajo → 2`, `medio → 1`, `alto → 1`) exige `**Motivo del presupuesto:**`; sin él rige el derivado. |
| S24 | Ruling sin coste | `implement-stage` | Falla: `Ruling:` exige `<qué> — <por qué> — <qué cuesta>`; dos partes ocultan la decisión al auditor. |
| S25 | Ruling de categoría 2 sin revisar | `implement-stage`, `audit-stage` | No cierra: cada `**Sujeto a revisión:**` se resuelve en `### Rulings revisados` como `aceptado` o `hallazgo`, leyendo artefactos y diff. |
| I01 | Corte ambiguo o por encabezados | `identify-feature-stages` | Pide aclaración o corta por resultados; asigna requisitos; no crea tareas/auditoría. |

## Rúbrica conductual

Puntuar 0/1 por: riesgo identificado; baseline preservado; evidencia correcta; ausencia de falso cierre; siguiente artefacto mínimo; paths/comandos reproducibles; ausencia de scope extra. Registrar puntos, falsos positivos, falsos cierres, rework y tiempo hasta evidencia suficiente.

## Ejecución

```bash
# Desde la raíz del paquete: <skills-root>/feature-stages
python3 scripts/validate_stage.py evals/fixtures/valid-stage
python3 scripts/validate_stage.py evals/fixtures/index-estado/03-activa
python3 scripts/validate_stage.py evals/fixtures/index-estado/05-hecha
python3 scripts/validate_stage.py evals/fixtures/riesgo-cruzado-con-motivo
python3 scripts/validate_stage.py evals/fixtures/closed-without-task
python3 scripts/validate_stage.py evals/fixtures/index-estado/04-etapa
python3 scripts/validate_stage.py evals/fixtures/ca-tipo
python3 scripts/validate_stage.py evals/fixtures/coincide-sin-snapshot
python3 scripts/validate_stage.py evals/fixtures/snapshot-de-pasada-anterior
python3 scripts/validate_stage.py evals/fixtures/riesgo-rebajado
python3 scripts/validate_stage.py evals/fixtures/test-decorativo
python3 scripts/validate_stage.py evals/fixtures/sin-sensibilidad
python3 scripts/validate_stage.py evals/fixtures/riesgo-ausente
python3 scripts/validate_stage.py evals/fixtures/cierre-sin-aprobacion
python3 scripts/validate_stage.py evals/fixtures/riesgo-alto-sin-mutacion
python3 scripts/validate_stage.py evals/fixtures/riesgo-alto-mutante-verde
python3 scripts/validate_stage.py evals/fixtures/riesgo-alto-mutante-esperado
python3 scripts/validate_stage.py evals/fixtures/riesgo-alto-presupuesto-sin-motivo
python3 scripts/validate_stage.py evals/fixtures/ruling-sin-coste
python3 scripts/validate_stage.py evals/fixtures/ruling-categoria-1
python3 scripts/validate_stage.py evals/fixtures/ruling-categoria-2-sin-revision
python3 scripts/validate_stage.py evals/fixtures/ruling-categoria-2-revisado
python3 scripts/test_next_step.py
python3 scripts/test_snapshot.py
python3 scripts/test_expres.py
python3 scripts/test_evidence.py
python3 scripts/test_skill_evals.py
python3 scripts/validate_skill_evals.py
python3 scripts/doctor.py evals/fixtures/transiciones
python3 scripts/doctor.py evals/fixtures/rulings-excesivos
python3 scripts/doctor.py evals/fixtures/rulings-aceptados
```

`coincide-sin-snapshot`, `snapshot-de-pasada-anterior` y `riesgo-rebajado` deben
salir con error: un veredicto `coincide` sin identidad del código auditado, con
el snapshot de otra pasada, o con un riesgo menor al congelado, no cierra.
`test_snapshot.py` crea repositorios temporales: la identidad debe cambiar al
cambiar el código, mantenerse al escribir en la ruta excluida y rechazar el
cierre sin `.yerro/approvals.yml`, con una entrada fuera de alcance o con el
archivo mal formado.

Hay **un** contrato y **un** modo: no existe `--strict`. `riesgo-ausente` y
`ca-tipo` fallan siempre, porque describen estados que el contrato rechaza sin
excepción. `cierre-sin-aprobacion` (criterio rebajado sin motivo),
`riesgo-alto-sin-mutacion` (riesgo alto sin mutación), `riesgo-alto-mutante-verde`
(un mutante que el test no detectó), `riesgo-alto-mutante-esperado` (`rojo
esperado` es una predicción) y `riesgo-alto-presupuesto-sin-motivo`
(presupuesto sobrescrito sin causa) fallan; su contrario
`riesgo-cruzado-con-motivo` pasa.

El gate de mutación se cumple por el **resultado observado**, no por la palabra:
`mutante: X → rojo` acredita sensibilidad; `→ verde`, `→ rojo esperado` y
`mutante: X` sin resultado no. Un mutante verde en un CA crítico no se compensa
con un rojo en otro.

`closed-without-task` y `index-estado/04-etapa` deben salir con error. La
segunda solo mira la celda **Estado**: conciliación `cerrada` con etapa
`auditando` (`03-activa`) es válida; **Estado** `cerrada` sin veredicto
`coincide` no lo es. `ca-tipo` señala el CA sin marcador de tipo (`CA-05`) como
error.

`transiciones/` recorre el ciclo completo: corte, lista, auditoría pendiente,
cierre y delta, más los negativos `sin-tareas`, `abierta`, `inconsistente`,
`dependencia`, `bloqueada`, `ambiguo`, `cierre-pendiente`, `delta-huerfano`,
`sin-conciliacion`, `conciliacion-invalida`, `sin-principal`,
`presupuesto-agotado`, `presupuesto-excedido`, `presupuesto-excedido-coincide`
y el positivo `presupuesto-amplio`. Cada caso afirma
estado público, skill siguiente y código de bloqueo; un cambio en
`next_step.py` que altere una transición sin actualizar su caso deja la suite
roja.

- Fixture `cambio-fuera-de-alcance`: una etapa cuyo `**Archivos:**` no cubre una
  ruta tocada. `diff_scope.py` debe salir con error (alcance nuevo, B-27);
  `test_diff_scope.py` construye repositorios git temporales para probar las dos
  direcciones (no declarado bloquea; declarado sin tocar solo avisa), los
  archivos sin trackear y que la evidencia de la etapa no cuente como código.
- `validate_stage.py <etapa> --repo` aplica ese cruce en el cierre: un archivo
  que ninguna tarea declara rechaza la pasada. `test_snapshot.py` lo comprueba
  creando `colado.py` y reauditando.

`rulings-excesivos` (cuatro rulings en una tarea) debe avisar y apuntar a
`generate-stage-tasks` sin bloquear; `rulings-aceptados` (tres) debe callar.

`ruling-sin-coste` (un `Ruling:` de dos partes) debe fallar: las tres partes
son obligatorias y el error dice cuál falta. `ruling-categoria-1` (las tres,
bien escritas) pasa. `ruling-categoria-2-sin-revision` (un `**Sujeto a
revisión:**` y ninguna sección `### Rulings revisados`) no cierra;
`ruling-categoria-2-revisado` es el mismo estado con una resolución `aceptado`
y pasa. Los tres separadores que un agente puede teclear (`—`, `--`, `–`)
cuentan; dos partes nunca.
Una etapa no cerrada cuyo `TAREAS.md` no declara `**Archivos:**` aparece como
pendiente de migrar, también sin bloquear.

`doctor-estructural/`, `huerfana/` e `indice-sin-tabla/` cubren las reglas
estructurales de `doctor.py` (etapa sin lista, sin auditoría o sin
conciliación, delta mal nombrado o sin `Cierra:`, carpeta sin fila, índice sin
tabla). Una regla nueva sin fixture que la viole no cuenta como cubierta.

Para comportamiento, materializar la fixture indicada en un repositorio temporal, dar el `prompt` a un agente con la skill objetivo y aplicar la rúbrica a la conversación y artefactos. Los casos de activación se revisan al editar `description` de cualquier skill: al menos tres positivos, dos negativos con propietario y una evaluación conductual por skill modificada.
