# Deltas y cierre

`coincide` requiere todos los CA principales en `cumple`, verificaciones de
tareas ejecutadas, controles globales correctos, trazabilidad completa y
ninguna desviación bloqueante.

Para un gap contra el baseline sin cambios:

1. comprueba `**Presupuesto de deltas:**`, derivado del riesgo
   (`bajo → 2`, `medio → 1`, `alto → 1`) salvo `**Motivo del presupuesto:**`;
2. si queda presupuesto, crea solo el `TAREAS-delta-NN.md` necesario y enlaza
   pasada, CA y evidencia/hueco; cada tarea del delta declara `**Archivos:**`,
   `Test-first:`, `Test:` y `Verificar:`, como cualquier tarea principal. La
   pasada que lo cierra lo declara en `**Deltas:**` con su ID (`D1`, `D2`):
   un delta que ninguna pasada abre ni declara no tiene origen, y nombrarlo
   en prosa no cuenta. Un delta de verificación —el que existe para demostrar,
   no para corregir— se justifica precisamente así;
3. si el presupuesto se agotó, detén el ciclo y pide decisión: reabrir
   conciliación, aceptar riesgo residual con owner o bloquear la etapa;
4. después de implementar, audita nuevamente contra `TAREAS.md`, no solo contra
   el delta, con snapshot fresco.

Nunca escribas un delta adicional para evitar la decisión ni edites la
conciliación para que el código parezca cumplir.

## Reapertura

Si el alcance se movió **después** del árbol que auditó una pasada anterior
—otra etapa tocó un archivo que esta reclamaba, o la conciliación cambió de
criterio—, la corrección no es un delta: es una reapertura. Escribe una pasada
nueva con `**Reapertura:** <motivo>` y `**Veredicto:** no coincide`; no lleves
`**Veredicto (calidad):**`, no abras delta y no consumas presupuesto. La pasada
dice por qué la conformidad anterior ya no cubre el árbol actual; el `coincide`
de la pasada vieja no se hereda.

Después re-concilia el alcance (`CONCILIACION.md` a `abierta`, índice a
`implementando`) y audita otra vez cuando haya un árbol nuevo. `next_step.py`
devuelve `trabajando` con `conciliate-stage` mientras la última pasada declare
la reapertura; si el índice sigue en `cerrada`, `doctor.py` lo rechaza.
