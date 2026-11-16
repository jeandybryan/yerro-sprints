# Tareas — etapa 01 plantilla copiada

**Principal:** sí
**Origen:** CONCILIACION.md cerrada 2026-11-16
**Spec:** [SPEC.md](../SPEC.md) §1
**Estado:** implementada

## Listado

- [x] T1 — implementar la salida (CA-01; Origen: S-01; spec §1)
  **Archivos:** `src/salida.py`, `tests/test_salida.py` — las rutas que esta tarea produce.
  Test-first: sí; Test: `pytest -q tests/test_salida.py`;
  Sensibilidad: revertir → rojo → restaurar;
  Impacto: módulos/contratos
  Verificar: nivel `conductual`; ejecutar test focalizado; oráculo observable: exit 0.

## Trazabilidad

| Criterio | Tareas | Verificación prevista |
|----------|--------|-----------------------|
| CA-01 | T1 | test |

## Verificación global

- [x] Tests y lints relevantes.
- [x] Documentación/config/migraciones actualizadas si aplica.
- [x] Sin cambios fuera del alcance aprobado.
