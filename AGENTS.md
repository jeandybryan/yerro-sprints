# AGENTS.md — Instrucciones para el agente que mantiene este repositorio

Eres el agente encargado de mantener YerroSprints, un paquete portable de seis
skills para gestionar una feature desde el corte de especificación hasta la
auditoría.

## Reglas de mantenimiento

- Nunca mezcles reglas de dominio en `skills/`. Si una regla describe un
  producto, servicio, módulo o archivo de un consumidor, no pertenece a este
  paquete.
- Preserva las seis fases y sus límites de responsabilidad. No elimines ni
  fundas fases para simplificar el paquete.
- No rebajes un gate para que una fixture pase. Una prueba negativa que dejó de
  fallar es un gate roto, no una victoria.
- Ejecuta las validaciones locales antes de editar el changelog o declarar el
  paquete listo. No declares verde una validación que no ejecutaste.
- Trata un cambio de baseline (intención, alcance o criterio de aceptación)
  como reapertura de la conciliación, no como un delta.
- Si una decisión de diseño no está acordada (nombre/owner/licencia, canales de
  distribución, política de tags, agentes soportados), pregunta antes de
  escribirla o publicarla.
- Mantén el README para humanos y los `SKILL.md` concisos para agentes.
- Conserva la evidencia de los comandos ejecutados en la descripción del PR o
  release, no dentro de los `SKILL.md`.

## Antes de tocar un archivo

1. Lee `PUBLISHING.md` si no lo conoces.
2. Identifica qué fase o documento vas a modificar y por qué.
3. Determina si el cambio es de comportamiento (requiere fixture/caso nuevo) o
   de documentación (requiere mantener la coherencia en README, CONTRIBUTING y
   CHANGELOG).
4. Ejecuta las validaciones locales y confirma que la fixture negativa sigue
   fallando.

## Árbol que debes preservar

```
skills/
  identify-feature-stages/SKILL.md
  feature-stages/{SKILL.md,templates.md,EVALUATION.md,references/,scripts/,evals/}
  conciliate-stage/SKILL.md
  generate-stage-tasks/SKILL.md
  implement-stage/SKILL.md
  audit-stage/SKILL.md
```