# YerroSprints — paquete portable de skills

Este directorio es la fuente de YerroSprints, una futura distribución pública
de Agent Skills para gestionar una feature desde el corte de especificación
hasta la auditoría.
No contiene reglas de dominio, arquitectura ni convenciones de un proyecto
consumidor.

## Ciclo

```text
identify-feature-stages
  → conciliate-stage
  → generate-stage-tasks
  → implement-stage
  → audit-stage
                 └─ no coincide → TAREAS-delta-NN → implement-stage → audit-stage
```

`feature-stages` es el contrato y orquestador compartido: no reemplaza ninguna
fase. Un delta repara implementación o evidencia contra un baseline sin cambios;
cualquier cambio de intención, alcance o criterio reabre la conciliación.

## Contenido

| Skill | Función |
|-------|---------|
| `identify-feature-stages` | Corta una especificación en resultados implementables y auditables. |
| `feature-stages` | Define estados, gates, plantillas, contrato y evaluación. |
| `conciliate-stage` | Cierra alcance, decisiones, CA, riesgos y evidencia. |
| `generate-stage-tasks` | Genera la única lista principal, trazada a CA. |
| `implement-stage` | Ejecuta solo la lista aprobada y deja evidencia para auditoría. |
| `audit-stage` | Intenta refutar cumplimiento; cierra, bloquea o emite delta. |

## Desarrollo en este repositorio

```bash
python3 feature-stages/scripts/validate_skill_evals.py
python3 feature-stages/scripts/validate_stage.py \
  feature-stages/evals/fixtures/valid-stage --strict
```

El segundo comando debe terminar correctamente. La fixture
`closed-without-task` debe terminar con error: prueba que el gate rechaza una
conciliación cerrada sin lista implementable.

## Extraer a un repositorio público

Consulta [docs/PUBLISHING.md](docs/PUBLISHING.md). Contiene el árbol final,
comandos de instalación con `npx skills`, validaciones, releases y checklist
para agentes.
