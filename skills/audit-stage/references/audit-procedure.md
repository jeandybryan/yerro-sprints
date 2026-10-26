# Procedimiento de auditoría

1. Lee spec, `CONCILIACION.md` cerrada, `TAREAS.md`, deltas, auditorías previas
   e índice.
2. Confirma con `next_step.py` que la etapa está en `verificando`.
3. Captura un snapshot fresco excluyendo el árbol de la feature y registra el
   valor exacto en la pasada:

   ```bash
   python3 <skills-root>/feature-stages/scripts/snapshot.py <repo> --exclude <feature-root> --exclude .yerro/approvals.yml
   ```

   Las dos exclusiones son obligatorias: el validador excluye siempre
   `.yerro/approvals.yml`, así que un snapshot sin esa exclusión no coincide
   aunque el árbol sea el mismo. Si el validador lo señala, se vuelve a tomar el
   snapshot; no se reaudita una pasada cuyo árbol no cambió.

4. Registra `**Riesgo auditado:**`; puede subir, nunca bajar del riesgo
   congelado.
5. Ejecuta `validate_stage.py` sin `--repo` antes de juzgar el resultado: así se
   comprueba la forma de los artefactos.
6. Descompón cada CA en afirmaciones atómicas y comprueba trazabilidad
   `S → CA → T → test → E`.
7. Ejecuta el método de verificación declarado en cada tarea. No heredes el
   resultado verde del implementador.
8. Añade negativos, límites o fault injection proporcionalmente al riesgo.
9. Escribe una pasada inmutable, conserva las anteriores y valida de nuevo
   antes de `coincide`.
10. Con `**Veredicto:** coincide` escrito, ejecuta el cierre cruzado:

    ```bash
    python3 <skills-root>/feature-stages/scripts/validate_stage.py <stage> --repo <repo>
    ```

    Comprueba que el snapshot es el del árbol actual, que la aprobación
    humana cubre etapa y snapshot, y que ningún archivo queda fuera del
    alcance declarado. Sin `--repo` el validador solo juzga la forma: un
    `coincide` que no pasó este comando no cierra.

La auditoría no implementa ni repara hallazgos en la misma pasada. Un cambio de
intención, alcance o criterio reabre conciliación; no crea un delta.
