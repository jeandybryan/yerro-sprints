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

CLOSING_GATE = "validate_stage.py <stage> --repo <repo>"
def closing_gate_errors(skill: str) -> list[str]:
    """El skill que escribe el veredicto debe invocar el cierre cruzado.

    `validate_stage.py` sin `--repo` juzga la forma; el snapshot, la aprobación
    y el alcance solo se comprueban en el cierre. Un procedimiento de auditoría
    que no ejecute ese comando cierra a ciegas.
    """
    if CLOSING_GATE in skill:
        return []
    return [f"falta el cierre cruzado documentado: `{CLOSING_GATE}`"]

BLOCK_SECTION = "## Bloqueos"
def blocked_gate_errors(skill: str) -> list[str]:
    """El bloqueo se escribe donde el router lo lee.

    `next_step.py` y `doctor.py` toman la causa de `## Bloqueos` en
    `CONCILIACION.md`. Una skill que manda el bloqueo al README o a la lista
    deja la etapa bloqueada «sin causa escrita», y quien la sigue acaba
    editando la conciliación sin que nadie se lo haya dicho.
    """
    if BLOCK_SECTION in skill and "CONCILIACION.md" in skill:
        return []
    return [
        f"falta el sitio del bloqueo documentado: `{BLOCK_SECTION}` en `CONCILIACION.md`"
    ]

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
    audit_skill = ROOT.parent / "audit-stage" / "SKILL.md"
    if audit_skill.exists():
        errors.extend(closing_gate_errors(audit_skill.read_text()))
    implement_skill = ROOT.parent / "implement-stage" / "SKILL.md"
    if implement_skill.exists():
        errors.extend(blocked_gate_errors(implement_skill.read_text()))
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
        # Una evaluación sobre una fixture que no existe no evalúa nada: el
        # evaluador materializaría la nada y puntuaría la conversación.
        for name in ev.get("files", []):
            if not (ROOT / "evals" / "fixtures" / name).is_dir():
                errors.append(f"{skill}: el caso {ev.get('id')} apunta a una fixture inexistente: {name}")
    # Un id de caso que no está en EVALUATION.md es un caso sin rúbrica escrita:
    # se ejecuta, se puntúa "bien" y nadie sabe qué fallo sembraba.
    catalog = ROOT / "EVALUATION.md"
    if catalog.is_file():
        # Un caso cubre uno o varios IDs (`S07-S08`): basta con que todos estén.
        known = set(re.findall(r"^\|\s*([SI]\d{2})\s*\|", catalog.read_text(), re.M))
        def covered(case_id: str) -> bool:
            parts = re.findall(r"[SI]\d{2}", case_id)
            return bool(parts) and all(part in known for part in parts)
        for skill in SKILLS:
            path = ROOT / "evals" / "cases" / f"{skill}.json"
            if not path.exists():
                continue
            try:
                data = json.loads(path.read_text())
            except json.JSONDecodeError:
                continue
            for ev in data.get("evals", []):
                case_id = ev.get("id", "")
                if not covered(case_id):
                    errors.append(f"{skill}: el caso {case_id!r} nombra IDs que no están en el catálogo de EVALUATION.md")
    for error in errors: print(f"ERROR: {error}")
    if not errors: print("OK: catálogo de evaluaciones válido")
    return bool(errors)
if __name__ == "__main__": raise SystemExit(main())
