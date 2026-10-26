# Deltas y cierre

`coincide` requiere todos los CA principales en `cumple`, verificaciones de
tareas ejecutadas, controles globales correctos, trazabilidad completa y
ninguna desviación bloqueante.

Para un gap contra el baseline sin cambios:

1. comprueba `**Presupuesto de deltas:**`, derivado del riesgo
   (`bajo → 2`, `medio → 1`, `alto → 1`) salvo `**Motivo del presupuesto:**`;
2. si queda presupuesto, crea solo el `TAREAS-delta-NN.md` necesario y enlaza
   pasada, CA y evidencia/hueco;
3. si el presupuesto se agotó, detén el ciclo y pide decisión: reabrir
   conciliación, aceptar riesgo residual con owner o bloquear la etapa;
4. después de implementar, audita nuevamente contra `TAREAS.md`, no solo contra
   el delta, con snapshot fresco.

Nunca escribas un delta adicional para evitar la decisión ni edites la
conciliación para que el código parezca cumplir.
