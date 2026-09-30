# Contribuir a YerroSprints

Gracias por querer mejorar YerroSprints. Este paquete publica seis skills que
gestionan una feature desde el corte de especificación hasta la auditoría. Su
valor está en la claridad de los límites entre fases y en la trazabilidad de
los artefactos.

## Principios

- Mantén los cambios pequeños y enfocados. Un PR grande que mezcla fases o
  formatos es difícil de revisar.
- Revisa el solapamiento entre skills: cada responsabilidad debe vivir en exactamente
  una fase. `feature-stages` solo orquesta y define el contrato; no ejecuta fases.
- No introduzcas reglas de dominio, nombres de productos, servicios, módulos o
  archivos de un consumidor dentro de `skills/`. El paquete es genérico.
- Todo cambio de comportamiento debe añadir o actualizar una fixture o caso
  retenido que demuestre el comportamiento esperado.

## Checklist antes de abrir un PR

- [ ] No se introdujeron reglas de dominio ni referencias a un consumidor.
- [ ] Las seis fases y sus límites de responsabilidad se preservan.
- [ ] Ningún gate fue rebajado para que una fixture pase.
- [ ] Se ejecutaron las validaciones locales (ver README, sección de validación).
- [ ] La fixture negativa `closed-without-task` sigue fallando.
- [ ] Cualquier cambio de descripción revisa los casos de activación positivos
      y negativos.
- [ ] Cualquier cambio de flujo, plantilla o validador añadió una prueba de regresión.

## Validación local

```bash
python3 skills/feature-stages/scripts/validate_skill_evals.py
python3 skills/feature-stages/scripts/validate_stage.py \
  skills/feature-stages/evals/fixtures/valid-stage --strict
python3 -m py_compile skills/feature-stages/scripts/*.py
git diff --check
```

La fixture negativa debe fallar:

```bash
if python3 skills/feature-stages/scripts/validate_stage.py \
  skills/feature-stages/evals/fixtures/closed-without-task --strict; then
  echo 'La fixture negativa pasó: el gate está roto' >&2
  exit 1
fi
```