#!/usr/bin/env python3
"""Valida de forma estática artefactos de una etapa de implementación.

Uso: validate_stage.py <stage-directory> [--strict]
Sin --strict, formatos legados se informan como advertencias; con --strict,
incumplen el contrato actual y devuelven salida no nula.
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

CA_RE = re.compile(r"^\s*-\s*\*\*(CA-\d+)\b", re.M)
TASK_RE = re.compile(
    r"^\s*-\s*\[[ xX]\]\s*((?:D\d+-)?T\d+)\b(.*?)(?=^\s*-\s*\[[ xX]\]|\Z)",
    re.M | re.S,
)
STATE_RE = re.compile(r"\*\*Estado:\*\*\s*([^\n]+)")
CA_TYPE_RE = re.compile(r"\[(?:condición de salida\s*\|\s*invariante acumulado|invariante acumulado\s*\|\s*condición de salida)\]", re.I)
EVIDENCE_RE = re.compile(r"estructural|conductual|sistema|ambiental", re.I)


class Result:
    def __init__(self, strict: bool) -> None:
        self.strict = strict
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def require(self, ok: bool, text: str, legacy: bool = False) -> None:
        if not ok:
            (self.warnings if legacy and not self.strict else self.errors).append(text)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("stage", type=Path)
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()

    stage = args.stage.resolve()
    result = Result(args.strict)
    conciliation, tasks, audit = (
        read(stage / name) for name in ("CONCILIACION.md", "TAREAS.md", "AUDIT.md")
    )
    result.require(bool(conciliation), "falta CONCILIACION.md")
    if not conciliation:
        return finish(result)

    state = STATE_RE.search(conciliation)
    closed = bool(state and "cerrada" in state.group(1).lower())
    ca_ids = CA_RE.findall(conciliation)
    result.require(bool(ca_ids), "no hay CA-NN en CONCILIACION.md")
    result.require(len(ca_ids) == len(set(ca_ids)), "hay IDs CA duplicados")

    for ca in ca_ids:
        line = next((item for item in conciliation.splitlines() if f"**{ca}" in item), "")
        result.require(
            bool(CA_TYPE_RE.search(line)),
            f"{ca} no declara tipo condición de salida/invariante acumulado",
            legacy=True,
        )
        result.require(bool(EVIDENCE_RE.search(line)), f"{ca} no declara nivel de evidencia")

    task_bodies: dict[str, str] = {}
    if closed:
        result.require(bool(tasks), "conciliación cerrada sin TAREAS.md")
    if tasks:
        principal = re.search(r"\*\*Principal:\*\*\s*sí", tasks, re.I)
        result.require(bool(principal), "TAREAS.md no declara Principal: sí")
        for task_id, body in TASK_RE.findall(tasks):
            task_bodies[task_id] = body
            result.require(bool(re.search(r"CA-\d+", body)), f"{task_id} no enlaza CA-NN")
            verification = re.search(r"Verificar:\s*(.*)", body, re.I)
            result.require(bool(verification), f"{task_id} no contiene Verificar:")
            if verification:
                value = verification.group(1)
                result.require(bool(EVIDENCE_RE.search(value)), f"{task_id} no declara nivel")
                result.require(
                    ";" in value or "oráculo" in value.lower(),
                    f"{task_id} no separa procedimiento y oráculo",
                    legacy=True,
                )
        result.require(bool(task_bodies), "TAREAS.md no contiene tareas implementables")
        result.require(
            len(task_bodies) == len(set(task_bodies)), "hay IDs de tarea duplicados"
        )
        for ca in ca_ids:
            result.require(
                any(re.search(rf"\b{re.escape(ca)}\b", body) for body in task_bodies.values()),
                f"{ca} no tiene tarea trazable",
            )

    verdicts = re.findall(r"^\s*\*\*Veredicto:\*\*\s*(.+?)\s*$", audit, re.I | re.M)
    has_coincide = any(item.strip().lower() == "coincide" for item in verdicts)
    if audit and has_coincide:
        result.require(bool(tasks), "AUDIT coincide sin lista principal")
        for ca in ca_ids:
            result.require(
                bool(re.search(rf"\|\s*{re.escape(ca)}\s*\|.*?\|\s*cumple\s*\|", audit, re.I)),
                f"AUDIT coincide no demuestra {ca}=cumple",
            )
        result.require("### Ledger de evidencia" in audit, "AUDIT coincide sin ledger de evidencia", legacy=True)

    index = read(stage.parent / "README.md")
    if index:
        row = next((line for line in index.splitlines() if stage.name in line and "|" in line), "")
        if row:
            result.require(
                "cerrada" not in row.lower() or has_coincide,
                "índice marca etapa cerrada sin AUDIT.md con veredicto coincide",
            )
    return finish(result)


def finish(result: Result) -> int:
    for text in result.warnings:
        print(f"WARN: {text}")
    for text in result.errors:
        print(f"ERROR: {text}")
    if not result.errors:
        print("OK: contrato estructural válido")
    return 1 if result.errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
