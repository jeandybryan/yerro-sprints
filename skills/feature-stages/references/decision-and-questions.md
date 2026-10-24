# Decisiones y preguntas

No se debe adivinar intención de producto, alcance, nivel de evidencia ni una
decisión cerrada.

Antes de una pregunta bloqueante, la respuesta visible contiene:

1. **Contexto:** por qué importa y qué queda bloqueado.
2. **Pregunta:** una decisión explícita.
3. **Propuesta:** opción recomendada y motivo.

AskQuestion solo selecciona opciones; no reemplaza esos bloques ni convierte un
default en acuerdo.

## Dos momentos que no se confunden

- **Conciliar** (`conciliate-stage`): se decide **con el humano** y se escribe
  como `S-NN`. No se cierra con supuestos.
- **Implementar** (`implement-stage`): se ejecuta el plan aprobado. Una
  ambigüedad de detalle **no detiene** el trabajo: se decide, se registra como
  `Ruling:` y sigue. Es el Modelo C.

La pregunta al humano se reserva para el baseline y para las paradas
incondicionales: operación irreversible, seguridad, efecto fuera del worktree,
plan tan roto que todo es adivinar, o cambio de intención/alcance/criterio.
Lo demás se decide en ejecución y se registra con su coste de equivocarse.

Las decisiones acordadas se escriben como `S-NN`. Una pregunta aplazada debe
nombrar la etapa que la resolverá.
