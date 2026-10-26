#!/usr/bin/env python3
"""Comprobaciones de preflight.py (P11, B-15, P14).

Lo que se prueba no es "cuenta bytes": es que el recorte nunca es silencioso y
que lo que el script no sabe decidir lo **incluye**. Un preflight que omite la
etapa vecina por error es un fallo; uno que la incluye con un motivo, una
decisión.
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import next_step  # noqa: E402
import preflight  # noqa: E402

errors: list[str] = []
checked = 0


def fail(message: str) -> None:
    errors.append(message)


def check(condition: bool, message: str) -> None:
    global checked
    checked += 1
    if not condition:
        fail(message)


def stage(root: Path, name: str, *, conciliation: str = "", tasks: str = "", audit: str = "") -> Path:
    folder = root / name
    folder.mkdir(parents=True, exist_ok=True)
    if conciliation:
        (folder / "CONCILIACION.md").write_text(conciliation, encoding="utf-8")
    if tasks:
        (folder / "TAREAS.md").write_text(tasks, encoding="utf-8")
    if audit:
        (folder / "AUDIT.md").write_text(audit, encoding="utf-8")
    return folder


INDEX = """# Feature — prueba

## Estado del corte

| # | Carpeta | Resultado | Depende de | Conciliación | Estado | Trabajo activo | Tareas | Auditoría |
|---|---------|-----------|------------|--------------|--------|----------------|--------|-----------|
{rows}
"""

CONC = """# Etapa {n}

**Estado:** cerrada

## Criterios de aceptación

- **CA-01 — [condición de salida]:** exportar produce un archivo; evidencia `conductual`. Origen: S-01
"""

TASKS = """# Tareas — etapa {n}

**Principal:** sí

## Listado

- [ ] T1 — exportar (CA-01; Origen: S-01)
  **Archivos:** `src/export.py`
  Test-first: sí; Test: pytest -q;
  Verificar: nivel `conductual`; ejecutar; oráculo observable: exit 0.
"""


def build(root: Path) -> Path:
    stage(root, "01-cerrada", conciliation=CONC, tasks=TASKS.format(n="01"), audit="\n\n**Veredicto:** coincide\n")
    stage(root, "02-activa", conciliation=CONC.format(n="02"), tasks=TASKS.format(n="02"))
    (root / "README.md").write_text(
        INDEX.format(
            rows="\n".join(
                (
                    "| 01 | [01-cerrada](01-cerrada/CONCILIACION.md) | x | — | cerrada | cerrada | — | TAREAS.md | AUDIT.md |",
                    "| 02 | [02-activa](02-activa/CONCILIACION.md) | x | — | cerrada | implementando | — | TAREAS.md | — |",
                )
            )
        ),
        encoding="utf-8",
    )
    return root


def check_own_stage_only() -> None:
    """P11: la etapa vecina no entra en el plan de lectura."""
    global checked
    with tempfile.TemporaryDirectory() as tmp:
        root = build(Path(tmp))
        plan = preflight.plan(root, "02-activa", "implement")
        checked += 1
        paths = " ".join(item["ruta"] for item in plan["leer"])
        if "01-cerrada" in paths:
            fail(f"preflight incluye la etapa vecina: {paths}")
        if "02-activa" not in paths:
            fail(f"preflight no incluye la etapa activa: {paths}")


def check_neighbour_is_justified() -> None:
    """P14: un recorte sin motivo es el defecto; el motivo lo hace visible."""
    with tempfile.TemporaryDirectory() as tmp:
        root = build(Path(tmp))
        plan = preflight.plan(root, "02-activa", "implement")
        skipped = {item["ruta"]: item["motivo"] for item in plan["no_leer"]}
        check(
            any("01-cerrada" in ruta for ruta in skipped),
            f"la etapa vecina no aparece en no_leer con su motivo: {skipped}",
        )
        check(
            any("vecina" in motivo.lower() for motivo in skipped.values()),
            f"no_leer no explica por qué se omite: {skipped}",
        )


def check_unknown_phase_is_not_a_guess() -> None:
    """Un script que no sabe qué leer incluye todo lo de la etapa, no omite."""
    with tempfile.TemporaryDirectory() as tmp:
        root = build(Path(tmp))
        plan = preflight.plan(root, "02-activa", "fase-inventada")
        check(
            plan["fase_detectada"] != "fase-inventada" or plan["advertencias"],
            "una fase desconocida se acepta en silencio",
        )
        paths = " ".join(item["ruta"] for item in plan["leer"])
        check("TAREAS.md" in paths, f"fase desconocida no incluye TAREAS.md: {paths}")


def check_stage_without_phase_is_silent() -> None:
    """Una etapa sin fase siguiente (lista) no inventa una advertencia."""
    with tempfile.TemporaryDirectory() as tmp:
        root = build(Path(tmp))
        (root / "02-activa" / "TAREAS.md").write_text(
            TASKS.format(n="02").replace("**Principal:** sí", "**Estado:** implementada\n**Principal:** sí"),
            encoding="utf-8",
        )
        (root / "02-activa" / "AUDIT.md").write_text("\n\n**Veredicto:** coincide\n", encoding="utf-8")
        index = (root / "README.md").read_text().replace(
            "| implementando | — | TAREAS.md | — |", "| cerrada | — | TAREAS.md | AUDIT.md |"
        )
        (root / "README.md").write_text(index, encoding="utf-8")
        state = next_step.analyze(root, "02-activa")
        check(state["siguiente"] is None, f"la fixture no está 'lista': siguiente={state['siguiente']}")
        plan = preflight.plan(root, "02-activa", None)
        check(plan["fase_detectada"] == "", f"fase detectada {plan['fase_detectada']!r}, se esperaba vacía")
        check(not plan["advertencias"], f"etapa sin fase siguiente generó avisos: {plan['advertencias']}")
        paths = " ".join(item["ruta"] for item in plan["leer"])
        check("TAREAS.md" in paths and "AUDIT.md" in paths, f"no preparó la etapa completa: {paths}")


def check_phase_derives_from_next_step() -> None:
    """Sin --fase, la fase sale de next_step, no de la narración del agente."""
    with tempfile.TemporaryDirectory() as tmp:
        root = build(Path(tmp))
        plan = preflight.plan(root, None, None)
        check(plan["fase_detectada"] == "implement-stage", f"fase derivada {plan['fase_detectada']!r}, se esperaba implement-stage")


def check_tokens_are_an_estimate() -> None:
    """B-15: líneas deciden, tokens informan, y la estimación dice su margen."""
    with tempfile.TemporaryDirectory() as tmp:
        root = build(Path(tmp))
        plan = preflight.plan(root, "02-activa", "implement")
        total = plan["totales"]
        check(total["lineas"] > 0, "el total de líneas es cero con archivos que leer")
        check("margen" in total and total["margen"], "la estimación de tokens no declara margen")
        check("tokens_estimados" in total, "no hay estimación de tokens")


def check_signature() -> None:
    """REGRESIÓN HEAD: la misma entrada da el mismo plan byte a byte."""
    with tempfile.TemporaryDirectory() as tmp:
        root = build(Path(tmp))
        first = preflight.plan(root, "02-activa", "implement")
        second = preflight.plan(root, "02-activa", "implement")
        check(
            json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True),
            "dos ejecuciones de la misma etapa no dan la misma firma",
        )


def check_signature_ignores_absolute_root() -> None:
    """La firma no depende de dónde esté montado el repo: dos rutas, misma firma."""
    with tempfile.TemporaryDirectory() as first, tempfile.TemporaryDirectory() as second:
        a = preflight.plan(build(Path(first)), "02-activa", "implement")
        b = preflight.plan(build(Path(second)), "02-activa", "implement")
        keys = ("etapa", "fase_detectada", "leer", "no_leer", "totales", "advertencias")
        same = all(a[key] == b[key] for key in keys)
        check(same, "la firma cambia con la ruta absoluta del repositorio")
        json.dumps(a, sort_keys=True)  # serializable: la firma se compara como texto


def check_check_mode_exceeds_budget() -> None:
    """P12: --check es el único modo que falla, y solo si hay presupuesto."""
    with tempfile.TemporaryDirectory() as tmp:
        root = build(Path(tmp))
        result = subprocess.run(
            [sys.executable, str(HERE / "preflight.py"), str(root), "--etapa", "02-activa", "--fase", "implement"],
            capture_output=True,
            text=True,
        )
        check(result.returncode == 0, f"sin --check debe informar y salir 0: {result.returncode} {result.stdout}{result.stderr}")
        check("líneas" in result.stdout, f"la salida no informa líneas: {result.stdout}")


def check_budget_only_fails_with_check() -> None:
    """P12: el informe no falla; --check sí, y solo si hay presupuesto."""
    with tempfile.TemporaryDirectory() as tmp:
        root = build(Path(tmp))
        (root / "02-activa" / "CONCILIACION.md").write_text(
            CONC.format(n="02") + "\n**Presupuesto de contexto:** 5 líneas\n",
            encoding="utf-8",
        )
        base = [sys.executable, str(HERE / "preflight.py"), str(root), "--etapa", "02-activa", "--fase", "implement"]
        report = subprocess.run(base, capture_output=True, text=True)
        check(report.returncode == 0, f"el informe falla al exceder el presupuesto: {report.returncode} {report.stdout}")
        checked_mode = subprocess.run(base + ["--check"], capture_output=True, text=True)
        check(checked_mode.returncode == 1, f"--check no falla con presupuesto excedido: {checked_mode.returncode}")
        check("superan el presupuesto" in checked_mode.stdout, f"--check no explica el exceso: {checked_mode.stdout}")

    with tempfile.TemporaryDirectory() as tmp:
        root = build(Path(tmp))
        base = [sys.executable, str(HERE / "preflight.py"), str(root), "--etapa", "02-activa", "--fase", "implement"]
        checked_mode = subprocess.run(base + ["--check"], capture_output=True, text=True)
        check(checked_mode.returncode == 0, "--check falla sin presupuesto declarado: inventa un número que nadie fijó")


def check_selection_prefers_active() -> None:
    """Con varias etapas, la activa es la que se prepara."""
    with tempfile.TemporaryDirectory() as tmp:
        root = build(Path(tmp))
        plan = preflight.plan(root, None, None)
        check(plan["etapa"] == "02-activa", f"seleccionó {plan['etapa']!r}, se esperaba la etapa activa 02-activa")


def main() -> int:
    check_own_stage_only()
    check_neighbour_is_justified()
    check_unknown_phase_is_not_a_guess()
    check_stage_without_phase_is_silent()
    check_phase_derives_from_next_step()
    check_tokens_are_an_estimate()
    check_signature()
    check_signature_ignores_absolute_root()
    check_check_mode_exceeds_budget()
    check_budget_only_fails_with_check()
    check_selection_prefers_active()
    for error in errors:
        print(f"ERROR: {error}")
    if not errors:
        print(f"OK: {checked} comprobaciones de preflight")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
