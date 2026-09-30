#!/usr/bin/env python3
"""Comprueba que toda skill del ciclo tenga casos de activación mínimos."""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ("identify-feature-stages", "feature-stages", "conciliate-stage", "generate-stage-tasks", "implement-stage", "audit-stage")
def main() -> int:
    errors=[]
    for skill in SKILLS:
        path=ROOT/"evals"/"cases"/f"{skill}.json"
        if not path.exists(): errors.append(f"falta caso para {skill}"); continue
        try: data=json.loads(path.read_text())
        except json.JSONDecodeError as exc: errors.append(f"JSON inválido {path.name}: {exc}"); continue
        trigger=data.get("trigger", {})
        if len(trigger.get("positive", [])) < 3: errors.append(f"{skill}: menos de 3 positivos")
        if len(trigger.get("negative", [])) < 2: errors.append(f"{skill}: menos de 2 negativos")
        if not data.get("evals"): errors.append(f"{skill}: falta evaluación conductual")
        for ev in data.get("evals", []):
            if ev.get("kind") == "execution" and not ev.get("files"): errors.append(f"{skill}: execution sin fixture")
    for error in errors: print(f"ERROR: {error}")
    if not errors: print("OK: catálogo de evaluaciones válido")
    return bool(errors)
if __name__ == "__main__": raise SystemExit(main())
