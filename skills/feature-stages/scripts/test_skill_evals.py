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
    SCRIPTS,
    WORKFLOW,
    closing_gate_errors,
    reconcile_errors,
    document_name_errors,
    gate_errors,
    markdown_reference_errors,
    routing_errors,
    workflow_errors,
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

    # El skill que escribe el veredicto tiene que invocar el cierre cruzado: sin
    # `--repo` el validador no mira snapshot, aprobación ni alcance.
    blind = closing_gate_errors("valida con validate_stage.py <stage> a secas")
    check(bool(blind), "un cierre sin `--repo` no se detecta")
    check(
        closing_gate_errors("validate_stage.py <stage> --repo <repo>") == [],
        "el cierre cruzado no debe fallar",
    )

    # P21: sin la regla, el agente que perdió el contexto re-ejecuta lo hecho.
    check(bool(reconcile_errors("documento sin la regla")), "un skill sin --reconcile no se detecta")
    check(
        reconcile_errors("next_step.py <feature-root> --reconcile") == [],
        "un skill con --reconcile no debe fallar",
    )

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


def check_unlisted_case_id() -> None:
    """Un caso cuyo ID no está en EVALUATION.md no tiene rúbrica escrita."""
    with tempfile.TemporaryDirectory() as tmp:
        copy = Path(tmp) / "feature-stages"
        shutil.copytree(HERE.parent / "evals", copy / "evals")
        shutil.copy(HERE.parent / "EVALUATION.md", copy / "EVALUATION.md")
        case = copy / "evals" / "cases" / "implement-stage.json"
        case.write_text(case.read_text().replace('"id": "S29"', '"id": "S99"'))
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
        check(result.returncode == 1, f"ID fuera de catálogo: salida {result.returncode}, se esperaba 1")
        check("S99" in result.stdout, f"el ID fuera de catálogo no se nombra: {result.stdout}{result.stderr}")


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


def check_document_names() -> None:
    """Un documento que manda a un `.md` inexistente se reporta.

    El caso es real: `AGENTS.md` ordenaba leer `PUBLISHING.md` como primer
    paso antes de tocar un archivo, y ese documento nunca existió. Los
    enlaces markdown ya se comprobaban, pero un nombre entre comillas
    invertidas no era un enlace para nadie.

    El control negativo importa tanto como el positivo: `TAREAS-delta-NN.md`
    es un nombre de patrón, no un archivo, y una regla que lo exigiera
    obligaría a crear archivos falsos para callarla.
    """
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        doc = root / "AGENTS.md"
        doc.write_text("1. Lee `PUBLISHING.md` si no lo conoces.\n")
        reported = document_name_errors(doc, root)
        check(
            any("PUBLISHING.md" in item for item in reported),
            f"documento inexistente no detectado: {reported}",
        )

        (root / "README.md").write_text("# índice\n")
        doc.write_text("Ver `TAREAS-delta-NN.md` y `README.md`.\n")
        reported = document_name_errors(doc, root)
        check(reported == [], f"un nombre de patrón no puede fallar: {reported}")

def check_workflow() -> None:
    """Un CI que se queda atrás no protege: dice verde sobre lo que no ejecutó."""
    real = workflow_errors(WORKFLOW, SCRIPTS)
    check(real == [], f"workflow real: {real}")
    with tempfile.TemporaryDirectory() as tmp:
        base = WORKFLOW.read_text(encoding="utf-8")
        missing = Path(tmp) / "sin-suite.yml"
        missing.write_text(base.replace("test_tasks.py", "tareas.py"), encoding="utf-8")
        reported = workflow_errors(missing, SCRIPTS)
        check(any("test_tasks.py" in item for item in reported), f"suite ausente no detectada: {reported}")

        strict = Path(tmp) / "con-strict.yml"
        strict.write_text(base.replace("test_expres.py", "test_expres.py --strict"), encoding="utf-8")
        reported = workflow_errors(strict, SCRIPTS)
        check(any("--strict" in item for item in reported), f"modo retirado no detectado: {reported}")


def main() -> int:
    check_catalog()
    check_mutations()
    check_unlisted_case_id()
    check_broken_fixture_reference()
    check_document_names()
    check_workflow()
    for error in errors:
        print(f"ERROR: {error}")
    if not errors:
        print(f"OK: {checked} comprobaciones documentales")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
