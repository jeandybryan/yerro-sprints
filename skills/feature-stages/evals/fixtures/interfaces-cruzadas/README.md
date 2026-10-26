# Fixture — dos tareas y una interfaz que no encaja

`T1` produce `export(rows, sep) -> str`; `T2` declara consumir
`export(rows) -> str` y documenta esa firma.

Ambas declaran `Interfaces:`, así que pasan la comprobación de presencia de P17.
El defecto es otro: la firma que `T2` da por hecha **no existe**. Un subagente
que solo mira su propia tarea no tiene con qué notarlo.

Comportamiento esperado en una sesión real, aplicando `EVALUATION.md`:

- **`implement-stage` ejecutando `T2`:** detecta el desajuste antes de escribir
  la llamada. No inventa el argumento que falta ni cambia `T1` por su cuenta; lo
  trata como categoría 3 —el contrato que el plan daba por hecho cambia— y se
  detiene.
- **`audit-stage` sobre la etapa implementada:** lo registra como hallazgo; no
  cierra mientras la documentación y el código no hablen de la misma firma.
- **`generate-stage-tasks`:** no debería haber producido este par; al revisarlo,
  corrige la firma de `T2` o la de `T1` antes de la lista final.

La fixture pasa `validate_stage.py` a propósito: la coherencia entre firmas no
es una comprobación que un script deba hacer sin entender el código. Lo que
verifica el mecanismo es que la interfaz **esté declarada**; lo que verifica el
caso conductual es que alguien la **lea**.

Mecanismo: materializar en un repositorio temporal, dar el `prompt` a un agente
con la skill objetivo y puntuar con la rúbrica conductual.
