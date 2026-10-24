# Fixture — interfaces declaradas entre dos tareas

`T1` produce `export(items) -> str` y `T2` la consume nombrando la tarea de la
que viene.

Debe **pasar**: es el positivo de P17. La obligación solo aplica a etapas con
más de una tarea; una etapa de una sola tarea no necesita declarar que no
consume nada.
