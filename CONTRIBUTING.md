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
- [ ] `test_evidence.py` pasa; la firma es estable, sensible al exit y al output, insensible a lo volátil, y `verify` rechaza una evidencia inventada.
- [ ] `test-decorativo` y `sin-sensibilidad` siguen fallando; `valid-stage` sigue pasando con la columna `Sensibilidad`.
- [ ] `expres-acumulado/` solo avisa y `expres-sano/` no avisa; `EXPRES.md` nunca bloquea ni cambia una transición.
- [ ] `doctor.py` acepta `transiciones/` y rechaza `inconsistente/`, `doctor-estructural/`, `handoff-invalido/` y `huerfana/`.
- [ ] `test_skill_evals.py` pasa; un enlace roto, un comando inexistente o una activación ambigua siguen fallando.
- [ ] La fixture negativa `closed-without-task` sigue fallando.
- [ ] `index-estado/04-etapa` sigue fallando y `03-activa` / `05-hecha` pasan.
- [ ] Hay un solo modo de validación: `--strict` no existe. `riesgo-ausente` y
      `ca-tipo` ahora fallan siempre, porque describen estados que el contrato
      rechaza.
- [ ] `cierre-sin-aprobacion`, `riesgo-alto-sin-mutacion` y
      `riesgo-alto-presupuesto-sin-motivo` siguen fallando y
      `riesgo-cruzado-con-motivo` sigue pasando.
- [ ] `riesgo-alto-mutante-verde` y `riesgo-alto-mutante-esperado` siguen
      fallando: el mutante se juzga por el resultado observado (`rojo`), no
      por la palabra, y un mutante que sobrevive no cierra.
- [ ] `test_diff_scope.py` pasa; un archivo no declarado sigue siendo alcance
      nuevo (error) y uno declarado sin tocar sigue siendo advertencia.
- [ ] `test_snapshot.py` sigue comprobando aprobación: sin `.yerro/approvals.yml`,
      con entrada fuera de alcance o con el archivo ausente, la etapa no cierra.
- [ ] `doctor.py` avisa con cuatro rulings en una tarea y calla con tres; toda
      etapa no cerrada sin `**Archivos:**` aparece como pendiente de migrar.
- [ ] `ruling-sin-coste` y `ruling-categoria-2-sin-revision` siguen fallando;
      `ruling-categoria-1` y `ruling-categoria-2-revisado` siguen pasando: un
      `Ruling:` sin coste y un sujeto a revisión sin resolver no cierran.
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
python3 skills/feature-stages/scripts/test_diff_scope.py
python3 skills/feature-stages/scripts/test_expres.py
python3 skills/feature-stages/scripts/test_evidence.py
python3 skills/feature-stages/scripts/doctor.py \
  skills/feature-stages/evals/fixtures/transiciones
python3 skills/feature-stages/scripts/validate_stage.py \
  skills/feature-stages/evals/fixtures/valid-stage
python3 skills/feature-stages/scripts/validate_stage.py \
  skills/feature-stages/evals/fixtures/index-estado/03-activa
python3 skills/feature-stages/scripts/validate_stage.py \
  skills/feature-stages/evals/fixtures/index-estado/05-hecha
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
  skills/feature-stages/evals/fixtures/closed-without-task ; then
  echo 'La fixture negativa pasó: el gate está roto' >&2
  exit 1
fi
if python3 skills/feature-stages/scripts/validate_stage.py \
  skills/feature-stages/evals/fixtures/index-estado/04-etapa ; then
  echo 'El índice cerrado pasó sin veredicto coincide: el gate está roto' >&2
  exit 1
fi
if python3 skills/feature-stages/scripts/validate_stage.py \
  skills/feature-stages/evals/fixtures/riesgo-rebajado ; then
  echo 'Una auditoría que rebaja el riesgo pasó: el gate está roto' >&2
  exit 1
fi
if python3 skills/feature-stages/scripts/validate_stage.py \
  skills/feature-stages/evals/fixtures/snapshot-de-pasada-anterior ; then
  echo 'Una pasada coincide reutilizó el snapshot de otra pasada: el gate está roto' >&2
  exit 1
fi
if python3 skills/feature-stages/scripts/validate_stage.py \
  skills/feature-stages/evals/fixtures/coincide-sin-snapshot ; then
  echo 'Un veredicto coincide sin Snapshot pasó: el gate está roto' >&2
  exit 1
fi
if python3 skills/feature-stages/scripts/validate_stage.py \
  skills/feature-stages/evals/fixtures/test-decorativo ; then
  echo 'Un Test: decorativo pasó: el gate está roto' >&2
  exit 1
fi
if python3 skills/feature-stages/scripts/validate_stage.py \
  skills/feature-stages/evals/fixtures/sin-sensibilidad ; then
  echo 'Un coincide sin sensibilidad demostrada pasó: el gate está roto' >&2
  exit 1
fi
if python3 skills/feature-stages/scripts/validate_stage.py \
  skills/feature-stages/evals/fixtures/riesgo-ausente; then
  echo 'riesgo-ausente pasó sin modo legado: el gate está roto' >&2
  exit 1
fi
if python3 skills/feature-stages/scripts/validate_stage.py \
  skills/feature-stages/evals/fixtures/ca-tipo; then
  echo 'ca-tipo pasó sin modo legado: el gate está roto' >&2
  exit 1
fi
```
