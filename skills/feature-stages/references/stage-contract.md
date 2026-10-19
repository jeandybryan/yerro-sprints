# Contrato de etapas

Este contrato define los artefactos y transiciones compartidos por las skills del ciclo. Las plantillas modulares de `feature-stages/templates/` son la forma canónica de producirlos; `templates.md` conserva solo el índice compatible.

## Transición única

El estado no se recuerda ni se negocia: se lee de los artefactos.

```bash
python3 <skills-root>/feature-stages/scripts/next_step.py <feature-root> [--stage NN-slug] [--json]
python3 <skills-root>/feature-stages/scripts/doctor.py <feature-root>
python3 <skills-root>/feature-stages/scripts/snapshot.py <repo> --exclude <feature-root>
python3 <skills-root>/feature-stages/scripts/expres.py <repo> [--base REF]
```

Estados públicos: `trabajando`, `verificando`, `listo`, `necesita-decision`. `next_step.py` devuelve uno y la skill siguiente; `doctor.py` informa incoherencias entre el índice y los artefactos. Ambos son de solo lectura y no rebajan ningún gate: ante una discrepancia gana el gate más estricto y la discrepancia se registra como bloqueo. `necesita-decision` detiene el ciclo; no se sustituye por un valor por defecto.

## Estados y baseline

- Conciliación: `borrador-corte` → `abierta` → `cerrada`.
- Etapa: `borrador` → `conciliando` → `lista` → `implementando` → `auditando` → `cerrada`; `bloqueada` requiere causa, desbloqueador, evidencia y próxima revisión.
- `TAREAS.md` es la única lista principal. Un delta solo cierra una brecha contra el mismo baseline; un cambio de intención, alcance o CA reabre la conciliación y actualiza la lista principal.

## Campos obligatorios

Una conciliación cerrada tiene resultado observable, `Entra`, `No entra`, dependencias cerradas o excepcionadas y justificadas, preguntas resueltas o diferidas a una etapa nombrada y CA estables.

Cada `CA-NN` declara: tipo (`salida` o `invariante`), estímulo/precondición, resultado observable, promesa negativa/límite relevante y nivel de evidencia. Un CA ambiental además declara host/perfil, ventana, umbral y artefacto esperado.

Cada tarea principal `Tn` enlaza al menos un CA y contiene `Verificar:` con nivel, procedimiento y oráculo observable. La cobertura es bidireccional: todo CA tiene tarea y toda tarea enlaza un CA.

Un `AUDIT.md` que cierre una etapa conserva cada pasada. El veredicto `coincide` requiere todos los CA principales `cumple`, verificaciones aplicables ejecutadas, controles globales correctos y ningún desvío bloqueante. La evidencia se registra como `E-NN` con procedimiento, esperado, observado/exit, entorno/timestamp, artefacto y limitación.

## Riesgo, snapshot y presupuesto

- `**Riesgo:** bajo | medio | alto` se congela al cerrar la conciliación. `alto` nombra los ítems concretos: datos, seguridad, contratos compartidos, concurrencia, entrega o huecos de prueba. El auditor puede subirlo en `AUDIT.md`; bajarlo reabre la conciliación.
- Cada pasada registra `**Snapshot:**` con la salida exacta de `snapshot.py`. `exclude=` identifica el árbol de la feature para que la evidencia no invalide su propio hash: el snapshot es del código auditado, no del archivo que lo describe.
- Un `coincide` solo vale para el snapshot que auditó. Si el árbol cambió, la pasada está obsoleta y se reaudita; no se reutiliza el veredicto para cerrar. `validate_stage.py <etapa> --repo <repo>` verifica esa coincidencia.
- `**Presupuesto de deltas:**` (dos por defecto) acota la corrección. Agotado el presupuesto, si la auditoría sigue en `no coincide`, `next_step.py` devuelve `necesita-decision` con `PRESUPUESTO_DE_DELTAS_AGOTADO`: reabrir la conciliación, aceptar el riesgo residual con owner o detener la etapa. Escribir otro delta no es una salida.

## Vía exprés

- Un cambio fuera del ciclo solo puede ser una corrección pequeña: un archivo de producción y como máximo 20 líneas de producción; las pruebas no cuentan.
- Migraciones, esquemas, seguridad/auth, contratos compartidos, interfaces públicas, dependencias nuevas y CA nuevos siempre abren etapa.
- `expres.py` decide los límites mecánicos. La ausencia de CA nuevo y de cambio de interfaz pública se confirma en la fila correspondiente de `EXPRES.md`.
- `EXPRES.md` es opcional y registral: `next_step.py` no lo lee, no cambia transiciones y no bloquea etapas. Cada fila conserva el cambio, la frontera y su verificación.
- Tres o más registros sobre el mismo CA o archivo generan `WARN` en `doctor.py`; es señal de promoción a etapa, no un gate.
- Si la comprobación mecánica dice `no cabe`, o no se pueden confirmar las dos condiciones manuales, se abre etapa sin override.

## Selección de trabajo

La prioridad es: (1) etapa nombrada por el usuario; (2) etapa comprometida en `Ciclo activo`; (3) delta que desbloquea ese objetivo; (4) etapa lista con mayor prioridad documentada; (5) primera elegible del índice. Registrar el motivo como `Por qué ahora`.

## Preguntas y evidencia

Antes de una pregunta bloqueante, la respuesta visible contiene `Contexto`, `Pregunta` y `Propuesta`. La selección en un formulario no reemplaza esos bloques.

`estructural` prueba forma; `conductual`, una rama y su oráculo; `sistema`, integración; `ambiental`, el host u operación acordados. No se puede sustituir un nivel requerido por uno inferior sin que el CA deje de cumplir.

## Ownership y handoff

| Fase | Entrada mínima | Puede modificar | No modifica | Entrega | Siguiente |
|---|---|---|---|---|---|
| `identify-feature-stages` | spec y contexto de feature | `README.md`, borradores `CONCILIACION.md` | `TAREAS.md`, `AUDIT.md`, código | árbol de etapas propuesto | `conciliate-stage` |
| `conciliate-stage` | spec y etapa seleccionada | `CONCILIACION.md`, índice operativo | `TAREAS.md`, código, `AUDIT.md` | baseline cerrado | `generate-stage-tasks` |
| `generate-stage-tasks` | conciliación cerrada | `TAREAS.md`, índice operativo | conciliación, código, auditoría | lista principal trazada | `implement-stage` |
| `implement-stage` | tareas o delta aprobado | código, tests, estado operativo | baseline, criterios, auditoría | implementación verificable | `audit-stage` |
| `audit-stage` | código, tareas y evidencia | `AUDIT.md`, delta, cierre del índice | código, baseline, criterios | `coincide`, `no coincide` o bloqueo | `implement-stage` o cierre |
| `feature-stages` | árbol completo | nada | todos los artefactos | transición calculada | skill indicada |

`README.md` puede actualizarse por la fase que cambia el estado operativo, pero
la fase no puede usar ese índice para ocultar un artefacto inválido. El handoff
se acepta solo cuando la entrada mínima y los gates del artefacto de salida
están satisfechos. `next_step.py` es la autoridad de transición; ninguna skill
inventa una siguiente fase.

## Política de contexto

Lee primero el `SKILL.md` activo, el contrato y los artefactos de entrada. Lee
una referencia temática o la plantilla específica solo cuando vayas a escribir
ese artefacto o resolver el caso que cubre. No cargues `templates.md`,
`GOVERNANCE.md` o referencias de otras fases por defecto.

| Fase | Lee primero | Carga bajo demanda |
|---|---|---|
| Identify | su skill y este contrato | plantilla de índice/conciliación |
| Conciliate | su skill, contrato y conciliación | decisiones/preguntas y plantilla de conciliación |
| Generate | contrato y conciliación cerrada | plantilla de tareas |
| Implement | contrato y `TAREAS.md` | delta, código y tests afectados |
| Audit | contrato y procedimiento de auditoría | scoring, evidencia y deltas |
| Router | routing y estado calculado | referencia solicitada explícitamente |
