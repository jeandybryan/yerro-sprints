# Changelog

Todos los cambios notables de este proyecto se documentan en este archivo.

El formato se basa en [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/)
y el proyecto adhiere a [Semantic Versioning](https://semver.org/lang/es/).

## [Unreleased]

### Corregido

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

- Fixture `index-estado`: `03-activa` y `05-hecha` deben pasar;
  `04-etapa` debe fallar.
- Fixture `ca-tipo`: los CA con marcador no avisan; `CA-05`, sin marcador,
  avisa y con `--strict` falla el proceso.

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