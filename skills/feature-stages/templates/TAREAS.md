## `TAREAS.md`

Generate **only** when conciliation is `cerrada`. Each item: checkbox,
action, acceptance criterion/source pointer, and verification.

```markdown
# Tareas — etapa NN <nombre>

**Principal:** sí
**Origen:** CONCILIACION.md cerrada <fecha>
**Spec:** …
**Estado:** pendiente | en curso | implementada | auditada

## Listado

- [ ] T1 — … (CA-01; Origen: S-01; spec §…)
  **Archivos:** `src/modulo.py`, `tests/test_modulo.py` — las rutas que esta tarea
  produce. Se derivan del CA, **nunca del diff** ya producido (B-28). Sin este
  campo la etapa no está migrada y el alcance no se puede comprobar.
  Ruling: <qué decido> — <por qué> — <qué cuesta si me equivoco>
  **Sujeto a revisión:** <cambio observable y reversible> — <por qué> — <coste>
  Test-first: sí; Test: <comando que debe fallar antes del cambio>;
  Sensibilidad: revertir → rojo → restaurar | mutante: <qué> → rojo | regresión HEAD;
  Impacto: módulos/contratos | datos/migración | config | lifecycle/recovery |
  observabilidad | perfil/hardware | limpieza/rollback (solo lo aplicable).
  Verificar: nivel `estructural | conductual | sistema | ambiental`; procedimiento
  y oráculo observable.

## Trazabilidad

| Criterio | Tareas | Verificación prevista |
|----------|--------|-----------------------|
| CA-01 | T1 | test / inspección / demostración / medición |

## Verificación global

- [ ] Tests y lints relevantes.
- [ ] Documentación/config/migraciones actualizadas si aplica.
- [ ] Sin cambios fuera del alcance aprobado.

### Notas de implementación (no auditadas)

- Paths, comandos o decisiones útiles para el auditor. No constituyen
  evidencia de cumplimiento.

## Fuera de este listado

Items the agent must not do even if convenient (from “No entra”).
```

