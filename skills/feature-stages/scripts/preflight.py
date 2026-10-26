#!/usr/bin/env python3
"""Calcula el contexto mínimo que una fase debe leer, y lo que no debe leer.

Uso: preflight.py <feature-root> [--etapa NN-slug] [--fase <skill>] [--json] [--check]

Solo lee. No ejecuta la fase ni sustituye a `next_step.py`: la fase sale de
`next_step` cuando no se pide una, y una fase desconocida no se adivina.

Tres reglas de P14 gobiernan este script:

1. **Lo que no sabe decidir lo incluye.** Si la etapa no se puede clasificar,
   se prepara la lectura completa de la etapa, no un subconjunto optimista.
2. **Todo recorte es visible.** Cada archivo que se deja fuera aparece en
   `no_leer` con su motivo; el recorte nunca es silencioso.
3. **Las líneas deciden, los tokens informan.** Las líneas son el presupuesto
   (B-15); la estimación de tokens lleva su margen y no se presenta como exacta.

Salida: 0 al informar. Con `--check`, 1 cuando se declara `**Presupuesto de
contexto:**` en la conciliación y lo leído lo excede (P12).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import next_step  # noqa: E402
from next_step import FeatureError  # noqa: E402

# Qué artefacto necesita cada fase, en orden. Es el plan mínimo compartido por
# todas las etapas; un fragmento más preciso por CA llega cuando P6 lo permita.
FASE_LECTURAS = {
    "conciliate-stage": ("CONCILIACION.md",),
    "generate-stage-tasks": ("CONCILIACION.md",),
    "implement-stage": ("TAREAS.md", "CONCILIACION.md"),
    "audit-stage": ("TAREAS.md", "AUDIT.md", "CONCILIACION.md"),
}
# Documentos del paquete que una fase de una etapa no necesita. Se nombran para
# que el recorte se vea, no para esconderlos: si un caso real los pide, se
# declaran en la conciliación y entran por la puerta de los recortes visibles.
NO_LEER_PAQUETE = (
    ("references/express-lane.md", "solo aplica a la vía exprés; esa vía tiene su propio procedimiento"),
    ("GOVERNANCE.md", "mantenimiento del paquete, no del trabajo de una etapa"),
    ("RELEASE_CHECKLIST.md", "publicación del paquete, no del trabajo de una etapa"),
)
BUDGET_RE = re.compile(r"\*\*Presupuesto de contexto:\*\*\s*(\d+)\s*l[ií]neas", re.I)
CIDA_BY_CA_RE = re.compile(r"^\s*-\s*\*\*(CA-\d+)\*\*", re.M)
TOKENS_PER_CHAR = 0.25
TOKENS_MARGIN = "estimación por caracteres (±40 %): el conteo real depende del host y del modelo"


def line_count(path: Path) -> int:
    try:
        return len(path.read_text(encoding="utf-8").splitlines())
    except OSError:
        return 0


def character_count(path: Path) -> int:
    try:
        return len(path.read_text(encoding="utf-8"))
    except OSError:
        return 0


def stage_names(feature_root: Path) -> list[str]:
    index = next_step.read(feature_root / "README.md")
    _, by_folder = next_step.parse_index(index)
    return sorted(by_folder)


def plan(feature_root: Path, requested_stage: str | None, requested_phase: str | None) -> dict:
    """Devuelve el plan de lectura y el recorte, con su motivo."""
    state = next_step.analyze(feature_root, requested_stage)
    stage_name = state["etapa"]
    detected = requested_phase or state["siguiente"] or ""
    warnings: list[str] = []

    if detected in FASE_LECTURAS:
        wanted = FASE_LECTURAS[detected]
    else:
        # Regla 1: una fase que no se reconoce no recorta. Si tampoco hay
        # `next_step` (etapa lista o en decisión), se prepara la etapa entera.
        wanted = ("CONCILIACION.md", "TAREAS.md", "AUDIT.md")
        warnings.append(
            f"fase {detected!r} no reconocida: se prepara la etapa completa en vez de adivinar"
        )

    stage = feature_root / stage_name
    leer: list[dict] = []
    advertencias_por_archivo: list[str] = []
    for name in wanted:
        path = stage / name
        if not path.is_file():
            advertencias_por_archivo.append(f"{name} no existe en {stage_name}: la fase lo esperaba")
            continue
        leer.append(
            {
                "ruta": str(path.relative_to(feature_root)),
                "lineas": line_count(path),
                "bytes": character_count(path),
                "motivo": f"artefacto de la etapa {stage_name} que la fase {detected or 'sin fase'} necesita",
            }
        )

    no_leer: list[dict] = []
    for other in stage_names(feature_root):
        if other == stage_name:
            continue
        no_leer.append(
            {
                "ruta": f"{other}/",
                "motivo": (
                    f"etapa vecina: su estado es {state['etapas'][other]['etapa'] if other in state.get('etapas', {}) else 'desconocido'}; "
                    "leerla no cambia lo que esta fase debe hacer y su contexto se arrastra a la decisión"
                ),
            }
        )
    for relative, reason in NO_LEER_PAQUETE:
        no_leer.append({"ruta": relative, "motivo": reason})
    for name in ("CONCILIACION.md", "TAREAS.md", "AUDIT.md"):
        if name in wanted:
            continue
        no_leer.append(
            {
                "ruta": f"{stage_name}/{name}",
                "motivo": f"la fase {detected or 'detectada'} no lo necesita; si lo necesita, no lee: pide la fase que sí lo hace",
            }
        )

    total_lines = sum(item["lineas"] for item in leer)
    total_chars = sum(item["bytes"] for item in leer)
    budget_match = BUDGET_RE.search(next_step.read(stage / "CONCILIACION.md"))

    return {
        "feature_root": str(feature_root),
        "etapa": stage_name,
        "fase_detectada": detected,
        "siguiente": state["siguiente"],
        "estado": state["state"],
        "leer": leer,
        "no_leer": no_leer,
        "totales": {
            "lineas": total_lines,
            "bytes": total_chars,
            "tokens_estimados": round(total_chars * TOKENS_PER_CHAR),
            "margen": TOKENS_MARGIN,
            "presupuesto_lineas": int(budget_match.group(1)) if budget_match else None,
        },
        "advertencias": warnings + advertencias_por_archivo,
        "blockers": state["blockers"],
    }


def exceeds(result: dict) -> bool:
    """Solo un presupuesto declarado puede excederse; sin él, se informa."""
    budget = result["totales"]["presupuesto_lineas"]
    return budget is not None and result["totales"]["lineas"] > budget


def render(result: dict) -> str:
    lines = [f"Etapa: {result['etapa']} · fase: {result['fase_detectada'] or 'sin fase'} · estado: {result['estado']}"]
    lines.append("Leer, en orden:")
    for item in result["leer"]:
        lines.append(f"  {item['ruta']} — {item['lineas']} líneas")
    lines.append("No leer:")
    for item in result["no_leer"]:
        lines.append(f"  {item['ruta']} — {item['motivo']}")
    total = result["totales"]
    lines.append(
        f"Total: {total['lineas']} líneas · {total['bytes']} bytes · ~{total['tokens_estimados']} tokens ({total['margen']})"
    )
    if total["presupuesto_lineas"] is not None:
        lines.append(f"Presupuesto declarado: {total['presupuesto_lineas']} líneas")
    for warning in result["advertencias"]:
        lines.append(f"WARN: {warning}")
    if exceeds(result):
        lines.append(f"ERROR: {total['lineas']} líneas superan el presupuesto de {total['presupuesto_lineas']}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Contexto mínimo de una fase")
    parser.add_argument("feature_root", nargs="?", default=".")
    parser.add_argument("--etapa", dest="stage", default=None)
    parser.add_argument("--fase", dest="phase", default=None)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    root = Path(args.feature_root).resolve()
    try:
        result = plan(root, args.stage, args.phase)
    except FeatureError as error:
        print(f"ERROR: {error}")
        return 1
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(render(result))
    return 1 if args.check and exceeds(result) else 0


if __name__ == "__main__":
    raise SystemExit(main())
