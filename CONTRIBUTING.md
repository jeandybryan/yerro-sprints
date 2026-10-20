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
- [ ] `test_next_step.py` pasa; toda transición, bloqueo o regla estructural nueva tiene su caso en `evals/fixtures/`.
- [ ] `test_expres.py` pasa; todo cambio de frontera (umbral, ruta excluida, pruebas o archivos sin trackear) tiene su caso.
- [ ] `expres-acumulado/` solo avisa y `expres-sano/` no avisa; `EXPRES.md` nunca bloquea ni cambia una transición.
- [ ] `doctor.py` acepta `transiciones/` y rechaza `inconsistente/`, `doctor-estructural/`, `handoff-invalido/` y `huerfana/`.
- [ ] `test_skill_evals.py` pasa; un enlace roto, un comando inexistente o una activación ambigua siguen fallando.
- [ ] La fixture negativa `closed-without-task` sigue fallando.
- [ ] `index-estado/04-etapa` sigue fallando y `03-activa` / `05-hecha` pasan.
- [ ] `ca-tipo` sin `--strict` solo avisa `CA-05`; con `--strict` falla.
- [ ] Cualquier cambio de descripción revisa los casos de activación positivos
      y negativos.
- [ ] Cualquier cambio de flujo, plantilla o validador añadió una prueba de regresión.
- [ ] Se revisaron [GOVERNANCE.md](GOVERNANCE.md) y [RELEASE_CHECKLIST.md](RELEASE_CHECKLIST.md); las decisiones de licencia, distribución, tags y hosts no se inventaron.

## Validación local

```bash
python3 skills/feature-stages/scripts/validate_skill_evals.py
python3 skills/feature-stages/scripts/test_skill_evals.py
python3 skills/feature-stages/scripts/test_next_step.py
python3 skills/feature-stages/scripts/test_snapshot.py
python3 skills/feature-stages/scripts/test_expres.py
python3 skills/feature-stages/scripts/doctor.py \
  skills/feature-stages/evals/fixtures/transiciones
python3 skills/feature-stages/scripts/validate_stage.py \
  skills/feature-stages/evals/fixtures/valid-stage --strict
python3 skills/feature-stages/scripts/validate_stage.py \
  skills/feature-stages/evals/fixtures/index-estado/03-activa --strict
python3 skills/feature-stages/scripts/validate_stage.py \
  skills/feature-stages/evals/fixtures/index-estado/05-hecha --strict
python3 -m py_compile skills/feature-stages/scripts/*.py
git diff --check
```

Las fixtures negativas deben fallar:

```bash
for fixture in inconsistente doctor-estructural huerfana; do
  if python3 skills/feature-stages/scripts/doctor.py \
    "skills/feature-stages/evals/fixtures/$fixture"; then
    echo "doctor aceptó $fixture: el gate está roto" >&2
    exit 1
  fi
done
if python3 skills/feature-stages/scripts/validate_stage.py \
  skills/feature-stages/evals/fixtures/closed-without-task --strict; then
  echo 'La fixture negativa pasó: el gate está roto' >&2
  exit 1
fi
if python3 skills/feature-stages/scripts/validate_stage.py \
  skills/feature-stages/evals/fixtures/index-estado/04-etapa --strict; then
  echo 'El índice cerrado pasó sin veredicto coincide: el gate está roto' >&2
  exit 1
fi
if python3 skills/feature-stages/scripts/validate_stage.py \
  skills/feature-stages/evals/fixtures/riesgo-rebajado --strict; then
  echo 'Una auditoría que rebaja el riesgo pasó: el gate está roto' >&2
  exit 1
fi
if python3 skills/feature-stages/scripts/validate_stage.py \
  skills/feature-stages/evals/fixtures/snapshot-de-pasada-anterior --strict; then
  echo 'Una pasada coincide reutilizó el snapshot de otra pasada: el gate está roto' >&2
  exit 1
fi
if python3 skills/feature-stages/scripts/validate_stage.py \
  skills/feature-stages/evals/fixtures/coincide-sin-snapshot --strict; then
  echo 'Un veredicto coincide sin Snapshot pasó: el gate está roto' >&2
  exit 1
fi
python3 skills/feature-stages/scripts/validate_stage.py \
  skills/feature-stages/evals/fixtures/riesgo-ausente
if python3 skills/feature-stages/scripts/validate_stage.py \
  skills/feature-stages/evals/fixtures/riesgo-ausente --strict; then
  echo 'riesgo-ausente con --strict pasó: el gate está roto' >&2
  exit 1
fi
python3 skills/feature-stages/scripts/validate_stage.py \
  skills/feature-stages/evals/fixtures/ca-tipo
if python3 skills/feature-stages/scripts/validate_stage.py \
  skills/feature-stages/evals/fixtures/ca-tipo --strict; then
  echo 'ca-tipo con --strict pasó: el gate está roto' >&2
  exit 1
fi
```
