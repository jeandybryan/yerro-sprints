# Fixture — delta sin prueba

Etapa con un delta escrito por la auditoría. La tarea del delta declara
`**Archivos:**` y `Verificar:`, pero no `Test-first:` ni `Test:`.

Debe **fallar**: el delta es la corrección acotada de un hueco contra el mismo
baseline, y sus tareas se juzgan con el mismo contrato que las principales. Si
`TAREAS-delta-NN.md` pudiera corregir sin prueba, la única lista exenta de
`Test-first:` sería la que nace de una auditoría fallida; además, sin
`**Archivos:**` el archivo que el delta produce sería alcance nuevo y la etapa
no podría cerrar nunca.
