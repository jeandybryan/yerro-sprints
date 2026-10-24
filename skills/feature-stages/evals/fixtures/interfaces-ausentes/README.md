# Fixture — etapa con dos tareas y sin interfaces

`T2` consume lo que produce `T1`, pero no declara `Consume:` ni `Produce:`.

Debe **fallar** (P17): en una etapa con más de una tarea, quien la ejecute sin
contexto tiene que saber qué firma recibe y qué firma deja. `Consume: ninguna`
es una respuesta válida; el silencio no.
