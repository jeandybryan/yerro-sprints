#!/usr/bin/env python3
"""Comprueba que toda skill del ciclo tenga casos de activación mínimos."""
from __future__ import annotations
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ("identify-feature-stages", "feature-stages", "conciliate-stage", "generate-stage-tasks", "implement-stage", "audit-stage")
GATE_TOKENS = ("S-NN", "Origen", "Test-first", "Snapshot", "Riesgo", "Trazabilidad", "E-NN", "Presupuesto de deltas", "Vía exprés")
DOCUMENTS = (
    ROOT / "references" / "stage-contract.md",
    ROOT / "references" / "express-lane.md",
    ROOT / "references" / "decision-traceability.md",
    ROOT / "references" / "decision-and-questions.md",
    ROOT.parent / "audit-stage" / "references" / "audit-procedure.md",
    ROOT.parent / "audit-stage" / "references" / "scoring-and-evidence.md",
    ROOT.parent / "audit-stage" / "references" / "deltas-and-closure.md",
)
def main() -> int:
    errors=[]
    for document in DOCUMENTS:
        if not document.exists(): errors.append(f"falta referencia normativa {document.relative_to(ROOT)}")
    markdown_files = [ROOT.parent / skill / "SKILL.md" for skill in SKILLS] + [ROOT / "SKILL.md"]
    for markdown in markdown_files:
        if not markdown.exists():
            errors.append(f"falta documento de skill {markdown}")
            continue
        text = markdown.read_text()
        for target in re.findall(r"\[[^]]+\]\(([^)#]+)(?:#[^)]+)?\)", text):
            if target.startswith(("http://", "https://", "mailto:")):
                continue
            resolved = (markdown.parent / target).resolve()
            if not resolved.exists():
                errors.append(f"enlace roto {markdown.relative_to(ROOT.parent)} -> {target}")
        for command_path in re.findall(r"`([^`]*(?:skills/|scripts/)[^`]*)`", text):
            candidate = command_path.split()[0].lstrip("<")
            if candidate.startswith("skills/"):
                resolved = ROOT.parent / candidate.removeprefix("skills/")
            elif candidate.startswith("scripts/"):
                resolved = ROOT / candidate
            else:
                continue
            if not resolved.exists():
                errors.append(f"comando o ruta inexistente {markdown.name}: {candidate}")
    corpus = "\n".join(path.read_text() for path in [*markdown_files, *DOCUMENTS] if path.exists())
    for token in GATE_TOKENS:
        if token not in corpus:
            errors.append(f"falta gate crítico documentado: {token}")
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
            routes = data.get("routing_exclusions", [])
            if len(routes) < 5: errors.append("feature-stages: faltan casos de exclusión de routing")
            for route in routes:
                if not route.get("expected") or not route.get("excluded"):
                    errors.append("feature-stages: caso de routing incompleto")
        for ev in data.get("evals", []):
            if ev.get("kind") == "execution" and not ev.get("files"): errors.append(f"{skill}: execution sin fixture")
    for error in errors: print(f"ERROR: {error}")
    if not errors: print("OK: catálogo de evaluaciones válido")
    return bool(errors)
if __name__ == "__main__": raise SystemExit(main())
