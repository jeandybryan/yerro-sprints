#!/usr/bin/env python3
"""Agrega la corrida de nivel 4 y escribe `REPORTE.md`.

Uso:
    score.py --out <dir> [--allow-incomplete]

Lee `<out>/<ID>/_rubrica/{META,RESULTADO}.json` y exige que cada caso esté
completo: puntos por expectation, veredicto, falso cierre y transcript. Un caso
sin transcript no cuenta como evidencia, y un `pasa: true` sin transcript es un
falso verde. Sin `--allow-incomplete` la corrida incompleta sale 1.

No ejecuta agentes ni consume tokens.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

FIELDS = ("commit", "model", "agent", "date")


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--allow-incomplete", action="store_true")
    args = parser.parse_args(argv)

    out = args.out.resolve()
    case_dirs = sorted(path for path in out.glob("S*") if path.is_dir())
    if not case_dirs:
        print(f"ERROR: no hay casos en {out}", file=sys.stderr)
        return 2

    problems: list[str] = []
    rows: list[dict] = []
    metas: list[dict] = []

    for case_dir in case_dirs:
        rub = case_dir / "_rubrica"
        meta_path, result_path = rub / "META.json", rub / "RESULTADO.json"
        if not meta_path.is_file() or not result_path.is_file():
            problems.append(f"{case_dir.name}: falta META.json o RESULTADO.json")
            continue
        meta, result = load(meta_path), load(result_path)
        metas.append(meta)
        points = result.get("puntos") or {}
        missing = [key for key, value in points.items() if value is None]
        if missing:
            problems.append(f"{case_dir.name}: puntos sin puntuar: {', '.join(missing)}")
        if result.get("pasa") is None:
            problems.append(f"{case_dir.name}: falta el veredicto pasa")
        if result.get("falso_cierre") is None:
            problems.append(f"{case_dir.name}: falta declarar falso_cierre")
        transcript = rub / "transcript.md"
        if result.get("pasa") and not transcript.is_file():
            problems.append(f"{case_dir.name}: pasa sin transcript; no es evidencia")
        rows.append(
            {
                "id": case_dir.name,
                "skill": meta.get("skill", ""),
                "pasa": result.get("pasa"),
                "puntos": points,
                "falso_cierre": result.get("falso_cierre"),
                "notas": result.get("notas", ""),
                "transcript": transcript.is_file(),
            }
        )

    for field in FIELDS:
        values = {meta.get(field, "") for meta in metas}
        if len(values) > 1:
            problems.append(f"la corrida mezcla {field}: {sorted(values)}")
        if values == {""}:
            problems.append(f"falta {field} en META.json")

    passed = sum(1 for row in rows if row["pasa"] is True)
    failed = sum(1 for row in rows if row["pasa"] is False)
    incomplete = len(rows) - passed - failed

    lines = [
        "# Reporte — nivel 4",
        "",
        "Corrida de comportamiento de `EVALUATION.md` sobre los casos retenidos",
        "que toca el release. Un caso pasa solo con todas sus expectations en 1 y",
        "sin falso cierre; la varianza se reporta, no se promedia.",
        "",
        "## Configuración",
        "",
    ]
    for field in FIELDS:
        value = next((meta.get(field, "") for meta in metas if meta.get(field)), "")
        lines.append(f"- **{field}:** {value or '—'}")
    lines += [
        "",
        "## Resultado",
        "",
        f"- Casos: {len(rows)} · pasan: {passed} · fallan: {failed} · incompletos: {incomplete}",
        "",
        "| ID | Skill | Pasa | Puntos | Falso cierre | Transcript |",
        "|----|-------|------|--------|--------------|------------|",
    ]
    for row in rows:
        points = row["puntos"]
        score = f"{sum(1 for value in points.values() if value == 1)}/{len(points)}"
        verdict = {True: "sí", False: "no", None: "—"}[row["pasa"]]
        false_close = {True: "sí", False: "no", None: "—"}[row["falso_cierre"]]
        lines.append(
            f"| {row['id']} | `{row['skill']}` | {verdict} | {score} | "
            f"{false_close} | {'sí' if row['transcript'] else 'no'} |"
        )
    lines += ["", "## Notas", ""]
    noted = [row for row in rows if row["notas"]]
    if noted:
        lines += [f"- **{row['id']}:** {row['notas']}" for row in noted]
    else:
        lines.append("- Sin notas.")
    lines += ["", "## Bloqueos de la corrida", ""]
    if problems:
        lines += [f"- {problem}" for problem in problems]
    else:
        lines.append("- Ninguno: todos los casos están completos.")
    lines += [
        "",
        "## Lectura",
        "",
        "Un caso retenido que falla bloquea adoptar la redacción hasta explicar y",
        "corregir la causa. Un caso incompleto deja el release en `no verificado`,",
        "no en `validado`.",
        "",
    ]
    (out / "REPORTE.md").write_text("\n".join(lines), encoding="utf-8")

    print("\n".join(lines))
    if problems and not args.allow_incomplete:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
