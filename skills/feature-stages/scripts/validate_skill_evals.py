#!/usr/bin/env python3
"""Comprueba que toda skill del ciclo tenga casos de activación mínimos."""
from __future__ import annotations
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ("identify-feature-stages", "feature-stages", "conciliate-stage", "generate-stage-tasks", "implement-stage", "audit-stage")
GATE_TOKENS = ("S-NN", "Origen", "Test-first", "Sensibilidad", "Snapshot", "Riesgo", "Trazabilidad", "E-NN", "Presupuesto de deltas", "Vía exprés")
KNOWN_ROUTES = set(SKILLS) | {"express-lane"}
DOCUMENTS = (
    ROOT / "references" / "stage-contract.md",
    ROOT / "references" / "express-lane.md",
    ROOT / "references" / "decision-traceability.md",
    ROOT / "references" / "decision-and-questions.md",
    ROOT.parent / "audit-stage" / "references" / "audit-procedure.md",
    ROOT.parent / "audit-stage" / "references" / "scoring-and-evidence.md",
    ROOT.parent / "audit-stage" / "references" / "deltas-and-closure.md",
)
def markdown_reference_errors(markdown: Path, skills_root: Path, feature_root: Path) -> list[str]:
    """Enlaces relativos y rutas de script citadas desde un documento."""
    errors: list[str] = []
    text = markdown.read_text()
    try:
        label = str(markdown.relative_to(skills_root))
    except ValueError:
        label = markdown.name
    for target in re.findall(r"\[[^]]+\]\(([^)#]+)(?:#[^)]+)?\)", text):
        if target.startswith(("http://", "https://", "mailto:")):
            continue
        if not (markdown.parent / target).resolve().exists():
            errors.append(f"enlace roto {label} -> {target}")
    for command_path in re.findall(r"`([^`]*(?:skills/|scripts/)[^`]*)`", text):
        candidate = command_path.split()[0].lstrip("<")
        if candidate.startswith("skills/"):
            resolved = skills_root / candidate.removeprefix("skills/")
        elif candidate.startswith("scripts/"):
            resolved = feature_root / candidate
        else:
            continue
        if not resolved.exists():
            errors.append(f"comando o ruta inexistente {markdown.name}: {candidate}")
    return errors

def gate_errors(corpus: str) -> list[str]:
    return [f"falta gate crítico documentado: {token}" for token in GATE_TOKENS if token not in corpus]

def routing_errors(routes: list) -> list[str]:
    errors: list[str] = []
    if len(routes) < 5:
        errors.append("feature-stages: faltan casos de exclusión de routing")
    for route in routes:
        expected = route.get("expected")
        excluded = route.get("excluded") or []
        if not expected or not excluded:
            errors.append("feature-stages: caso de routing incompleto")
            continue
        if any(name not in KNOWN_ROUTES for name in [expected, *excluded]):
            errors.append("feature-stages: activación con skill desconocida")
        if expected in excluded:
            errors.append("feature-stages: activación ambigua")
    return errors

def main() -> int:
    errors=[]
    for document in DOCUMENTS:
        if not document.exists(): errors.append(f"falta referencia normativa {document.relative_to(ROOT)}")
    markdown_files = [ROOT.parent / skill / "SKILL.md" for skill in SKILLS] + [ROOT / "SKILL.md"]
    for markdown in markdown_files:
        if not markdown.exists():
            errors.append(f"falta documento de skill {markdown}")
            continue
        errors.extend(markdown_reference_errors(markdown, ROOT.parent, ROOT))
    corpus = "\n".join(path.read_text() for path in [*markdown_files, *DOCUMENTS] if path.exists())
    errors.extend(gate_errors(corpus))
    for skill in SKILLS:
        path=ROOT/"evals"/"cases"/f"{skill}.json"
        if not path.exists(): errors.append(f"falta caso para {skill}"); continue
        try: data=json.loads(path.read_text())
        except json.JSONDecodeError as exc: errors.append(f"JSON inválido {path.name}: {exc}"); continue
        trigger=data.get("trigger", {})
        if len(trigger.get("positive", [])) < 3: errors.append(f"{skill}: menos de 3 positivos")
        if len(trigger.get("negative", [])) < 2: errors.append(f"{skill}: menos de 2 negativos")
        if not data.get("evals"): errors.append(f"{skill}: falta evaluación conductual")
        if skill == "feature-stages":
            errors.extend(routing_errors(data.get("routing_exclusions", [])))
        for ev in data.get("evals", []):
            if ev.get("kind") == "execution" and not ev.get("files"): errors.append(f"{skill}: execution sin fixture")
    for error in errors: print(f"ERROR: {error}")
    if not errors: print("OK: catálogo de evaluaciones válido")
    return bool(errors)
if __name__ == "__main__": raise SystemExit(main())
