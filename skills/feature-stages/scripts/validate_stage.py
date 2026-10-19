#!/usr/bin/env python3
"""Valida de forma estática artefactos de una etapa de implementación.

Uso: validate_stage.py <stage-directory> [--strict]
Sin --strict, formatos legados se informan como advertencias; con --strict,
incumplen el contrato actual y devuelven salida no nula.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from snapshot import SnapshotError, identity  # noqa: E402

CA_RE = re.compile(r"^\s*-\s*\*\*(CA-\d+)\b", re.M)
DECISION_RE = re.compile(r"^\s*-\s*\*\*(S-\d+)\s+—", re.M)
CA_ORIGIN_RE = re.compile(r"\bOrigen:\s*(S-\d+)", re.I)
TEST_FIRST_RE = re.compile(r"^\s*Test-first:\s*(.+)$", re.I | re.M)
TEST_COMMAND_RE = re.compile(r"(?:^|;\s*)Test:\s*([^;\n]+)", re.I | re.M)
TRACE_RE = re.compile(r"^\s*\*\*Trazabilidad:\*\*\s*(.+)$", re.I | re.M)
E_COMMAND_RE = re.compile(r"\|\s*E-\d+\s*\|.*?\|\s*([^|]+?)\s*\|.*?\|")
TASK_RE = re.compile(
    r"^\s*-\s*\[[ xX]\]\s*((?:D\d+-)?T\d+)\b(.*?)(?=^\s*-\s*\[[ xX]\]|\Z)",
    re.M | re.S,
)
STATE_RE = re.compile(r"\*\*Estado:\*\*\s*([^\n]+)")
# Misma línea del CA: placeholder, una opción entre corchetes, o prosa.
# No basta la palabra suelta «salida» o «invariante» en el cuerpo.
CA_TYPE_RE = re.compile(
    "|".join(
        (
            r"\[condición de salida(?:\s*\|\s*invariante acumulado)?\]",
            r"\[invariante acumulado(?:\s*\|\s*condición de salida)?\]",
            r"\bsalida de etapa\b",
            r"\binvariante acumulada\b",
        )
    ),
    re.I,
)
EVIDENCE_RE = re.compile(r"estructural|conductual|sistema|ambiental", re.I)
SNAPSHOT_RE = re.compile(r"^\s*\*\*Snapshot:\*\*\s*(.+?)\s*$", re.M | re.I)
SNAPSHOT_VALUE_RE = re.compile(
    r"^head=(?:[0-9a-f]{7,40}|sin-head)\s+tree=[0-9a-f]{7,40}\s+dirty=(?:si|no)\s+exclude=\S+$",
    re.I,
)
RISK_RE = re.compile(r"^\s*\*\*Riesgo:\*\*\s*(bajo|medio|alto)\b", re.M | re.I)
AUDITED_RISK_RE = re.compile(r"^\s*\*\*Riesgo auditado:\*\*\s*(bajo|medio|alto)\b", re.M | re.I)
RISK_RANK = {"bajo": 0, "medio": 1, "alto": 2}
VERDICT_RE = re.compile(r"^\s*\*\*Veredicto:\*\*\s*(.+?)\s*$", re.I | re.M)
AUDIT_PASS_RE = re.compile(r"^##\s+Pasada\b.*?$(.*?)(?=^##\s+Pasada\b|\Z)", re.M | re.S | re.I)


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


def split_row(line: str) -> list[str]:
    return [cell.strip() for cell in line.split("|")]


def parse_excludes(snapshot: str) -> tuple[Path, ...]:
    """Rutas excluidas declaradas en el snapshot canónico."""
    match = re.search(r"\bexclude=(\S+)", snapshot, re.I)
    if not match or match.group(1).lower() == "ninguno":
        return ()
    return tuple(Path(item) for item in match.group(1).split(",") if item)


def stage_index_estado(index: str, stage_name: str) -> str | None:
    """Celda Estado de la etapa en el índice, identificada por el enlace de Carpeta."""
    header: list[str] | None = None
    for line in index.splitlines():
        if not line.strip().startswith("|"):
            continue
        cells = split_row(line)
        if "Conciliación" in cells and "Estado" in cells and "Carpeta" in cells:
            header = cells
            break
    if header is None:
        return None
    folder_at = header.index("Carpeta")
    state_at = header.index("Estado")
    link = f"]({stage_name}/"
    for line in index.splitlines():
        if not line.strip().startswith("|"):
            continue
        cells = split_row(line)
        if folder_at >= len(cells) or state_at >= len(cells):
            continue
        if link in cells[folder_at]:
            return cells[state_at]
    return None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("stage", type=Path)
    parser.add_argument("--strict", action="store_true")
    parser.add_argument(
        "--repo",
        type=Path,
        help="verifica que el snapshot de la última pasada coincide con el árbol actual",
    )
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
    decision_ids = DECISION_RE.findall(conciliation)
    result.require(bool(decision_ids), "no hay decisiones S-NN en CONCILIACION.md", legacy=True)
    result.require(len(decision_ids) == len(set(decision_ids)), "hay IDs S-NN duplicados")
    result.require(len(ca_ids) == len(set(ca_ids)), "hay IDs CA duplicados")

    declared_risk = RISK_RE.search(conciliation)
    if closed:
        result.require(
            bool(declared_risk),
            "conciliación cerrada sin **Riesgo:** bajo|medio|alto congelado",
            legacy=True,
        )

    for ca in ca_ids:
        line = next((item for item in conciliation.splitlines() if f"**{ca}" in item), "")
        result.require(
            bool(CA_TYPE_RE.search(line)),
            f"{ca} no declara tipo condición de salida/invariante acumulado",
            legacy=True,
        )
        result.require(
            bool(CA_ORIGIN_RE.search(line)),
            f"{ca} no enlaza una decisión S-NN mediante Origen:",
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
            result.require(bool(TEST_FIRST_RE.search(body)), f"{task_id} no declara Test-first:", legacy=True)
            result.require(bool(TEST_COMMAND_RE.search(body)), f"{task_id} no declara Test:", legacy=True)
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

    verdicts = VERDICT_RE.findall(audit)
    has_coincide = any(item.strip().lower() == "coincide" for item in verdicts)
    passes = AUDIT_PASS_RE.findall(audit) or ([audit] if audit else [])
    coincide_passes: list[str] = []
    last_verdict = ""
    for body in passes:
        found = [item.strip().lower() for item in VERDICT_RE.findall(body)]
        last_verdict = found[-1] if found else ""
        if last_verdict == "coincide":
            coincide_passes.append(body)
    if audit and has_coincide:
        result.require(bool(tasks), "AUDIT coincide sin lista principal")
        for ca in ca_ids:
            result.require(
                bool(re.search(rf"\|\s*{re.escape(ca)}\s*\|.*?\|\s*cumple\s*\|", audit, re.I)),
                f"AUDIT coincide no demuestra {ca}=cumple",
            )
        result.require("### Ledger de evidencia" in audit, "AUDIT coincide sin ledger de evidencia", legacy=True)
        result.require(bool(TRACE_RE.search(audit)), "AUDIT coincide sin **Trazabilidad:** CA → T → E", legacy=True)
        result.require(bool(re.search(r"\bE-\d+\b", audit)), "AUDIT coincide sin evidencia E-NN", legacy=True)
        for body in coincide_passes:
            valid_snapshots = [
                item.strip() for item in SNAPSHOT_RE.findall(body)
                if SNAPSHOT_VALUE_RE.match(item.strip())
            ]
            result.require(
                bool(valid_snapshots),
                "AUDIT coincide sin **Snapshot:** head=… tree=… dirty=… exclude=…",
            )
            audited_risk = AUDITED_RISK_RE.findall(body)
            result.require(bool(audited_risk), "AUDIT coincide sin **Riesgo auditado:**", legacy=True)
            if declared_risk and audited_risk:
                declared = declared_risk.group(1).lower()
                audited = audited_risk[-1].lower()
                result.require(
                    RISK_RANK[audited] >= RISK_RANK[declared],
                    f"AUDIT rebaja el riesgo: declarado {declared}, auditado {audited}",
                )
            if args.repo is not None and valid_snapshots and body is coincide_passes[-1]:
                recorded = valid_snapshots[-1]
                excludes = parse_excludes(recorded)
                try:
                    current = identity(args.repo, excludes)
                except SnapshotError as error:
                    result.warnings.append(f"no se pudo verificar el snapshot: {error}")
                else:
                    result.require(
                        recorded.lower() == current.lower(),
                        f"la pasada auditó {recorded} y el árbol actual es {current}; reauditar",
                    )
    if args.repo is not None and last_verdict and last_verdict != "coincide":
        result.warnings.append(
            "la última pasada no coincide: no hay snapshot que verificar contra el árbol actual"
        )

    index = read(stage.parent / "README.md")
    if index:
        estado = stage_index_estado(index, stage.name)
        if estado is not None:
            result.require(
                "cerrada" not in estado.lower() or has_coincide,
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
