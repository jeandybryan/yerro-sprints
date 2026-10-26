#!/usr/bin/env python3
"""Mutation checks del catálogo documental.

Cada gate nuevo debe fallar cuando se le quita la condición que lo sostiene:
un enlace roto, un comando inexistente, un gate ausente o una activación
ambigua. El árbol real debe seguir pasando.
"""
from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from validate_skill_evals import (  # noqa: E402
    GATE_TOKENS,
    gate_errors,
    markdown_reference_errors,
    routing_errors,
)

errors: list[str] = []
checked = 0


def fail(message: str) -> None:
    errors.append(message)


def check(condition: bool, message: str) -> None:
    global checked
    checked += 1
    if not condition:
        fail(message)


def check_catalog() -> None:
    result = subprocess.run([sys.executable, str(HERE / "validate_skill_evals.py")], capture_output=True, text=True)
    check(result.returncode == 0, f"catálogo real: salida {result.returncode}: {result.stdout}{result.stderr}")


def check_mutations() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        skills = Path(tmp) / "skills"
        feature = skills / "feature-stages"
        feature.mkdir(parents=True)
        markdown = feature / "SKILL.md"
        markdown.write_text("Ver [contrato](references/no-existe.md) y `scripts/no-existe.py`.\n")
        reported = markdown_reference_errors(markdown, skills, feature)
        check(any("enlace roto" in item and "references/no-existe.md" in item for item in reported), f"enlace roto no detectado: {reported}")
        check(any("scripts/no-existe.py" in item for item in reported), f"comando inexistente no detectado: {reported}")

    missing = gate_errors("documento sin gates")
    check(len(missing) == len(GATE_TOKENS), f"gates ausentes: {missing}")
    check(gate_errors(" ".join(GATE_TOKENS)) == [], "un corpus completo no debe fallar gates")

    ambiguous = routing_errors(
        [{"prompt": "implementa y audita", "expected": "implement-stage", "excluded": ["implement-stage"]} for _ in range(5)]
    )
    check(any("activación ambigua" in item for item in ambiguous), f"activación ambigua no detectada: {ambiguous}")

    unknown = routing_errors(
        [{"prompt": "hazlo", "expected": "skill-inexistente", "excluded": ["audit-stage"]} for _ in range(5)]
    )
    check(any("skill desconocida" in item for item in unknown), f"skill desconocida no detectada: {unknown}")

    incomplete = routing_errors([{"prompt": "sigue", "expected": "feature-stages"} for _ in range(5)])
    check(any("routing incompleto" in item for item in incomplete), f"routing incompleto no detectado: {incomplete}")


def check_broken_fixture_reference() -> None:
    """Una evaluación sobre una fixture borrada no evalúa nada."""
    with tempfile.TemporaryDirectory() as tmp:
        copy = Path(tmp) / "feature-stages"
        shutil.copytree(HERE.parent / "evals", copy / "evals")
        shutil.rmtree(copy / "evals" / "fixtures" / "interfaces-cruzadas")
        result = subprocess.run(
            [
                sys.executable,
                "-c",
                "import sys, pathlib; sys.path.insert(0, sys.argv[2]); "
                "import validate_skill_evals as v; v.ROOT = pathlib.Path(sys.argv[1]); "
                "sys.exit(v.main())",
                str(copy),
                str(HERE),
            ],
            capture_output=True,
            text=True,
        )
        check(result.returncode == 1, f"fixture borrada: salida {result.returncode}, se esperaba 1")
        check(
            "interfaces-cruzadas" in result.stdout,
            f"fixture borrada no nombrada en el error: {result.stdout}{result.stderr}",
        )


def main() -> int:
    check_catalog()
    check_mutations()
    check_broken_fixture_reference()
    for error in errors:
        print(f"ERROR: {error}")
    if not errors:
        print(f"OK: {checked} comprobaciones documentales")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
