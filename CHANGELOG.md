# Changelog

Todos los cambios notables de este proyecto se documentan en este archivo.

El formato se basa en [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/)
y el proyecto adhiere a [Semantic Versioning](https://semver.org/lang/es/).

## [Unreleased]

### Corregido

- `generate-stage-tasks` ya no pide ejecutar el validador estructural antes de
  escribir `TAREAS.md`: con la conciliación cerrada y sin lista, el contrato
  falla por diseño. Antes de escribir se confirma la transición con
  `next_step.py`; el validador se ejecuta después.
- El validador reconoce el tipo de un CA cuando la línea elige una opción
  (`[condición de salida]`, `[invariante acumulado]`) o lo declara en prosa
  (`Salida de etapa`, `Invariante acumulada`). El placeholder con las dos
  opciones sigue valiendo. Una línea sin esos marcadores sigue avisando.
- El validador del índice marca una etapa como cerrada solo si la celda
  **Estado** de su fila contiene `cerrada`. La conciliación puede estar
  `cerrada` mientras la etapa sigue en `lista`, `implementando` o `auditando`.
- La fila se identifica por el enlace de **Carpeta** (`](NN-slug/`), así una
  mención del nombre en **Trabajo activo** de otra fila no cuenta.

### Añadido

- Contrato ejecutable de solo lectura: `next_step.py` lee los artefactos y
  devuelve el estado público (`trabajando`, `verificando`, `listo`,
  `necesita-decision`), la única skill siguiente y los bloqueos con su
  resolución. `doctor.py` comprueba la coherencia entre el índice y los
  artefactos. Ambos aceptan `--json`; `next_step.py` acepta `--stage` y
  `--check` para CI.
- Fixtures de transición (`transiciones/`) y negativas (`sin-tareas`,
  `abierta`, `inconsistente`, `dependencia`, `bloqueada`, `ambiguo`,
  `cierre-pendiente`, `delta-huerfano`, `sin-conciliacion`,
  `conciliacion-invalida`, `sin-principal`) con `test_next_step.py`, más pasos
  de CI que verifican las transiciones y que `doctor.py` rechaza un índice
  cerrado sin veredicto.
- Fixtures estructurales de `doctor.py` (`doctor-estructural/`, `huerfana/`,
  `indice-sin-tabla/`): cada regla estructural tiene una etapa que la viola, y
  la suite falla si el script deja de reportarla.
- Fixture `index-estado`: `03-activa` y `05-hecha` deben pasar;
  `04-etapa` debe fallar.
- Fixture `ca-tipo`: los CA con marcador no avisan; `CA-05`, sin marcador,
  avisa y con `--strict` falla el proceso.
- `snapshot.py`: identidad content-addressable del código auditado (`head`,
  `tree`, `dirty` y rutas excluidas) calculada con un índice temporal, sin
  tocar el índice real. `--exclude` permite dejar fuera el árbol de la feature
  para que escribir la evidencia no invalide su propio snapshot.
- `**Snapshot:**` obligatorio en cada pasada con veredicto `coincide`; sin él,
  `validate_stage.py` falla, y el snapshot de una pasada anterior no vale.
  `validate_stage.py --repo` recalcula la identidad con las mismas exclusiones
  y rechaza un veredicto obsoleto.
- `**Riesgo:** bajo | medio | alto` congelado en la conciliación cerrada y
  `**Riesgo auditado:**` en la pasada. El auditor puede subirlo, nunca bajarlo:
  un riesgo auditado menor es error del validador.
- `**Presupuesto de deltas:**` (dos por defecto). `next_step.py` devuelve
  `necesita-decision` con `PRESUPUESTO_DE_DELTAS_AGOTADO` cuando la corrección
  supera el presupuesto o la auditoría sigue en `no coincide` tras gastarlo.
- Fixtures `coincide-sin-snapshot`, `riesgo-rebajado`, `riesgo-ausente`,
  `presupuesto-agotado`, `presupuesto-excedido`,
  `presupuesto-excedido-coincide` y `presupuesto-amplio`, con
  `test_snapshot.py` y casos nuevos en `test_next_step.py`.
- Vía exprés: `expres.py` decide desde el diff si un cambio cabe fuera del
  ciclo (1 archivo de producción, ≤ 20 líneas, sin rutas excluidas). Cuenta los
  archivos nuevos sin trackear, no cuenta las pruebas y acepta `--json`.
  `EXPRES.md` registra una fila por cambio con el porqué y la verificación;
  `next_step.py` no lo lee. `doctor.py` avisa, sin bloquear, cuando 3 cambios se
  acumulan sobre el mismo CA o el mismo archivo. Fixtures `expres-sano` y
  `expres-acumulado`, con `test_expres.py` y casos en `test_next_step.py`.

### Cambiado

- La plantilla de `AUDIT.md` reemplaza el identificador informal de
  «commit/working tree» por `**Snapshot:**` y añade `**Riesgo auditado:**`.
  `CONCILIACION.md` declara `**Riesgo:**` y `**Presupuesto de deltas:**`.

## [1.0.0] - 2026-09-30

### Añadido

- Seis skills compatibles con Agent Skills: `identify-feature-stages`,
  `feature-stages`, `conciliate-stage`, `generate-stage-tasks`,
  `implement-stage` y `audit-stage`.
- Contrato y orquestador compartido en `feature-stages`: estados, gates,
  plantillas (`templates.md`), referencias (`stage-contract.md`,
  `skill-maintenance.md`) y rúbrica de evaluación (`EVALUATION.md`).
- Árbol portable de feature por etapas: índice, `CONCILIACION.md`,
  `TAREAS.md` (lista principal), `AUDIT.md` con ledger de evidencia y
  `TAREAS-delta-NN.md`.
- Validadores locales (`scripts/validate_stage.py` y
  `scripts/validate_skill_evals.py`), casos de activación retenidos
  (`evals/cases/*.json`) y fixtures de etapa (incluida la negativa
  `closed-without-task`, que debe fallar).
- Flujo de validación en GitHub Actions (`.github/workflows/validate.yml`).
- Documentación raíz: README, CONTRIBUTING, AGENTS y licencia MIT.