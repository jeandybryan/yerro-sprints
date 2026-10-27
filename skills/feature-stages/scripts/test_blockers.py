#!/usr/bin/env python3
"""Prueba que cada bloqueo de next_step.py trae una continuación que desbloquea.

Uso: test_blockers.py

B-19: el router no solo nombra un bloqueo y una resolución; la resolución tiene
que quitar el bloqueo. Para cada código se parte de la fixture que lo produce,
se aplica sobre una copia la resolución escrita en el propio blocker, y se exige
que el código desaparezca.

La resolución se lee del blocker, no se recuerda aquí: si el mensaje cambia y el
test sigue pasando, el test no prueba nada. Donde la resolución ofrece dos
caminos, se ejercita el que el router puede ver (`o`), y el caso declara cuál.

Solo stdlib; no consume tokens.
"""
from __future__ import annotations

import re
import shutil
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
FIXTURES = HERE.parent / "evals" / "fixtures"
sys.path.insert(0, str(HERE))

from next_step import analyze  # noqa: E402

errors: list[str] = []
checked = 0


def fail(message: str) -> None:
    errors.append(message)


def codes(result: dict) -> set[str]:
    return {item["codigo"] for item in result["blockers"]}


def resolution_of(fixture: str, stage: str | None, code: str) -> str:
    """La resolución que el propio blocker declara para `code`."""
    for item in analyze(FIXTURES / fixture, stage)["blockers"]:
        if item["codigo"] == code:
            return item["resolucion"]
    raise AssertionError(f"{fixture}/{stage}: no produce el bloqueo {code}")


def edit(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    if old not in text:
        raise AssertionError(f"{path.name}: no se encontró {old!r}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


# --- Reparaciones: cada una aplica la resolución declarada por el blocker. ---

def close_index_stage(root: Path) -> None:
    """COINCIDE_SIN_CIERRE: cerrar la etapa en el índice con la pasada."""
    edit(root / "README.md", "| auditando |", "| cerrada |")


def create_missing_conciliation(root: Path) -> None:
    """CONCILIACION_AUSENTE: crear la etapa (su artefacto basal)."""
    stage = next(p for p in sorted(root.iterdir()) if p.is_dir())
    (stage / "CONCILIACION.md").write_text(
        "# Etapa — reparada\n\n**Estado:** cerrada\n\n## Aclaraciones\n\n"
        "- `Ninguna`\n\n## Criterios de aceptación\n\n- `Ninguno`\n",
        encoding="utf-8",
    )


def fix_conciliation_state(root: Path) -> None:
    """CONCILIACION_INVALIDA: corregir CONCILIACION.md."""
    stage = next(p for p in sorted(root.iterdir()) if p.is_dir())
    edit(stage / "CONCILIACION.md", "**Estado:** en-revision", "**Estado:** cerrada")


def justify_delta_with_verdict(root: Path, stage: str) -> None:
    """DELTA_SIN_AUDIT: una pasada con veredicto no coincide justifica el delta."""
    path = root / stage / "AUDIT.md"
    text = path.read_text(encoding="utf-8") if path.exists() else "# Auditoría\n"
    text += "\n## Pasada 1\n\n**Snapshot:** head=0 tree=0 dirty=no exclude=ninguno\n"
    text += "\n**Veredicto:** no coincide\n"
    path.write_text(text, encoding="utf-8")


def close_dependency(root: Path) -> None:
    """DEPENDENCIA_ABIERTA: cerrar la dependencia."""
    edit(root / "README.md", "| borrador-corte | borrador |", "| cerrada | cerrada |")


def register_unblocker(root: Path) -> None:
    """ETAPA_BLOQUEADA: el estado lo marca el índice; se desbloquea ahí."""
    edit(root / "README.md", "| bloqueada |", "| auditando |")


def reaudit(root: Path) -> None:
    """INDICE_CERRADO_SIN_COINCIDE: reauditar, sin tocar el índice."""
    stage = next(p for p in sorted(root.iterdir()) if p.is_dir())
    (stage / "AUDIT.md").write_text(
        "# Auditoría\n\n## Pasada 1\n\n"
        "**Snapshot:** head=0 tree=0 dirty=no exclude=ninguno\n\n"
        "**Veredicto:** coincide\n",
        encoding="utf-8",
    )


def answer_questions(root: Path) -> None:
    """PREGUNTAS_ABIERTAS: resolver las preguntas."""
    stage = next(p for p in sorted(root.iterdir()) if p.is_dir())
    edit(stage / "CONCILIACION.md", "## Preguntas abiertas", "## Preguntas abiertas\n\n- `Ninguna`\n\n## Resueltas")


def accept_residual_risk(root: Path) -> None:
    """PRESUPUESTO_DE_DELTAS_AGOTADO: reabrir la conciliación (cambia el veredicto).

    La resolución ya no ofrece «aceptar el riesgo residual con owner» porque el
    router no leía ese campo: solo reabrir o detener la etapa mueven el estado.
    """
    stage = next(p for p in sorted(root.iterdir()) if p.is_dir())
    path = stage / "AUDIT.md"
    text = path.read_text(encoding="utf-8")
    path.write_text(text.replace("no coincide", "coincide"), encoding="utf-8")


# Qué salida de la resolución ejercita cada reparación. El test exige que este
# texto esté contenido en la resolución que el router emite: si el router deja
# de ofrecer esa salida, el caso falla en vez de probar un camino inventado.
EXERCISED = {
    "COINCIDE_SIN_CIERRE": "cerrar la etapa en el índice",
    "CONCILIACION_AUSENTE": "crear la etapa",
    "CONCILIACION_INVALIDA": "corregir CONCILIACION.md",
    "DELTA_SIN_AUDIT": "veredicto no coincide",
    "DEPENDENCIA_ABIERTA": "cerrar la dependencia",
    "ETAPA_BLOQUEADA": "desbloquear con decisión del usuario",
    "INDICE_CERRADO_SIN_COINCIDE": "reauditar",
    "PREGUNTAS_ABIERTAS": "resolver o diferir",
    "PRESUPUESTO_DE_DELTAS_AGOTADO": "reabrir la conciliación",
    "TAREA_NO_PRINCIPAL": "corregir la lista principal",
    "VARIAS_ETAPAS_ACTIVAS": "dejar una en implementando/auditando",
}


def fix_principal(root: Path) -> None:
    """TAREA_NO_PRINCIPAL: corregir la lista principal."""
    stage = next(p for p in sorted(root.iterdir()) if p.is_dir())
    edit(stage / "TAREAS.md", "# Tareas", "# Tareas\n\n**Principal:** sí")


def name_one_stage(root: Path) -> None:
    """VARIAS_ETAPAS_ACTIVAS: anotar la razón (aquí, dejando una activa)."""
    text = (root / "README.md").read_text(encoding="utf-8")
    # La resolución admite anotar la razón; el router no lee la razón, así que
    # el camino que sí desbloquea es dejar una sola etapa activa.
    rows = text.splitlines()
    seen = False
    for i, row in enumerate(rows):
        if "| implementando |" in row or "| auditando |" in row:
            if seen:
                rows[i] = row.replace("| implementando |", "| lista |").replace("| auditando |", "| lista |")
            seen = True
    (root / "README.md").write_text("\n".join(rows) + "\n", encoding="utf-8")


# --- Casos: fixture, etapa, código, reparación ---

CASES = [
    ("cierre-pendiente", None, "COINCIDE_SIN_CIERRE", close_index_stage),
    ("sin-conciliacion", None, "CONCILIACION_AUSENTE", create_missing_conciliation),
    ("conciliacion-invalida", None, "CONCILIACION_INVALIDA", fix_conciliation_state),
    ("delta-huerfano", "01-sin-audit", "DELTA_SIN_AUDIT", justify_delta_with_verdict),
    ("dependencia", "02-dependiente", "DEPENDENCIA_ABIERTA", close_dependency),
    ("bloqueada", None, "ETAPA_BLOQUEADA", register_unblocker),
    ("inconsistente", None, "INDICE_CERRADO_SIN_COINCIDE", reaudit),
    ("abierta", None, "PREGUNTAS_ABIERTAS", answer_questions),
    ("presupuesto-agotado", None, "PRESUPUESTO_DE_DELTAS_AGOTADO", accept_residual_risk),
    ("sin-principal", None, "TAREA_NO_PRINCIPAL", fix_principal),
    ("ambiguo", None, "VARIAS_ETAPAS_ACTIVAS", name_one_stage),
]


def check_resolutions() -> None:
    global checked
    for fixture, stage, code, repair in CASES:
        label = f"{fixture}/{stage or 'auto'}"
        # 1. La fixture produce el bloqueo y trae una resolución escrita.
        try:
            resolution = resolution_of(fixture, stage, code)
        except AssertionError as error:
            fail(f"{label}: {error}")
            continue
        checked += 1
        if not resolution.strip():
            fail(f"{label}: {code} se declara sin resolución")

        # 2. La salida que el caso ejercita tiene que ser una que el router ofrece.
        salida = EXERCISED.get(code, "")
        checked += 1
        if not salida:
            fail(f"{label}: {code} no declara qué salida de su resolución ejercita")
        elif salida not in resolution:
            fail(
                f"{label}: el caso ejercita {salida!r}, pero la resolución del "
                f"router no lo ofrece: {resolution!r}"
            )

        # 3. La reparación, sobre una copia, quita el bloqueo.
        work = Path(tempfile.mkdtemp(prefix="yerro-blocker-"))
        try:
            root = work / fixture
            shutil.copytree(FIXTURES / fixture, root)
            try:
                if repair is justify_delta_with_verdict:
                    repair(root, stage)
                else:
                    repair(root)
            except AssertionError as error:
                fail(f"{label}: la reparación declarada no aplica: {error}")
                continue
            checked += 1
            after = analyze(root, stage)
            remaining = codes(after)
            if code in remaining:
                fail(
                    f"{label}: la resolución {resolution!r} no desbloquea; "
                    f"{code} sigue tras aplicarla (bloqueos: {sorted(remaining)})"
                )
        finally:
            shutil.rmtree(work, ignore_errors=True)


def check_every_code_has_a_case() -> None:
    """Un código nuevo sin caso de desbloqueo es un gate sin probar."""
    global checked
    source = (HERE / "next_step.py").read_text(encoding="utf-8")
    declared = sorted(set(re.findall(r'"([A-Z]{2,}(?:_[A-Z]+)+)"', source)))
    covered = {code for _, _, code, _ in CASES}
    checked += 1
    missing = sorted(set(declared) - covered)
    if missing:
        fail(f"códigos de bloqueo sin caso de desbloqueo: {missing}")
    checked += 1
    extra = sorted(covered - set(declared))
    if extra:
        fail(f"casos para códigos que el router ya no emite: {extra}")


def main() -> int:
    check_every_code_has_a_case()
    check_resolutions()
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print(f"OK: {checked} comprobaciones de desbloqueo")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
