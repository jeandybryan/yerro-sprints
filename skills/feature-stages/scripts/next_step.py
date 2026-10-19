#!/usr/bin/env python3
"""Devuelve la única transición válida de un árbol de feature por etapas.

Uso: next_step.py <feature-root> [--stage NN-slug] [--json] [--all] [--check]

Solo lee. No escribe archivos, no consume tokens y no decide por el agente:
lee el estado desde el índice y los artefactos de cada etapa y devuelve el
siguiente paso que el contrato permite.

Estados públicos: trabajando | verificando | listo | necesita-decision.

Salida: 0 cuando reporta el estado; 1 cuando el árbol no se puede leer.
Con --check, 1 cuando el estado es necesita-decision (uso en CI).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

TRABAJANDO = "trabajando"
VERIFICANDO = "verificando"
LISTO = "listo"
DECISION = "necesita-decision"

CONCILIACION_ABIERTA = ("borrador-corte", "abierta")
ETAPA_ACTIVA = ("conciliando", "implementando", "auditando")
ETAPA_ELEGIBLE = ("borrador", "lista")

INDEX_COLUMNS = ("Carpeta", "Conciliación", "Estado", "Tareas", "Auditoría")
STATE_RE = re.compile(r"\*\*Estado:\*\*\s*([^\n]+)", re.I)
VERDICT_RE = re.compile(r"\*\*Veredicto:\*\*\s*(.+?)\s*$", re.I | re.M)
CIERRA_RE = re.compile(r"\*\*Cierra:\*\*\s*([^\n]+)", re.I)
DELTA_RE = re.compile(r"^TAREAS-delta-(\d{2,})\.md$")
FOLDER_RE = re.compile(r"\]\(([^)/]+)/")

class FeatureError(Exception):
    """El árbol de feature no se puede interpretar."""

def read(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.is_file() else ""

def cell_values(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]

def section(text: str, heading: str) -> str:
    """Cuerpo de una sección de nivel 2, sin incluir el encabezado."""
    match = re.search(
        rf"^##\s+{re.escape(heading)}\s*$(.*?)(?=^##\s+|\Z)", text, re.M | re.S | re.I
    )
    return match.group(1) if match else ""

def bullets(body: str) -> list[str]:
    """Entradas con contenido de una sección de lista, ignorando 'Ninguna'."""
    items = []
    for line in body.splitlines():
        match = re.match(r"^\s*[-*]\s+(.*\S)\s*$", line)
        if not match:
            continue
        value = match.group(1).strip()
        if value.strip("`_. ").lower() in {"ninguna", "ninguno", "ningunas", "ningunos", "n/a"}:
            continue
        items.append(value)
    return items

def parse_state(text: str) -> str | None:
    match = STATE_RE.search(text)
    return match.group(1).strip().strip("*` ") if match else None

def normalize(value: str | None) -> str:
    return (value or "").strip().strip("*` ").lower()

def parse_index(index: str) -> tuple[list[dict[str, str]], dict[str, dict[str, str]]]:
    """Filas del índice por carpeta, y el bloque Ciclo activo."""
    rows: list[dict[str, str]] = []
    header: list[str] | None = None
    for line in index.splitlines():
        if not line.strip().startswith("|"):
            continue
        cells = cell_values(line)
        if header is None:
            if all(column in cells for column in INDEX_COLUMNS):
                header = cells
            continue
        if set("".join(cells)) <= set("-: "):
            continue
        if header and len(cells) < len(header):
            cells += [""] * (len(header) - len(cells))
        rows.append(dict(zip(header, cells)))

    by_folder: dict[str, dict[str, str]] = {}
    for row in rows:
        folder = FOLDER_RE.search(row.get("Carpeta", ""))
        if folder:
            by_folder[folder.group(1)] = row
    return rows, by_folder

def active_goal(index: str) -> list[str]:
    body = section(index, "Ciclo activo")
    match = re.search(r"\*\*Etapas comprometidas:\*\*\s*([^\n]+)", body, re.I)
    if not match:
        return []
    text = match.group(1)
    return [name for name in re.findall(r"\b\d{2}-[a-z0-9][a-z0-9-]*", text, re.I)]

def audit_verdict(audit: str) -> str | None:
    verdicts = [item.strip().lower() for item in VERDICT_RE.findall(audit)]
    return verdicts[-1] if verdicts else None

def delta_files(stage: Path) -> list[Path]:
    return sorted(
        (path for path in stage.glob("TAREAS-delta-*.md") if DELTA_RE.match(path.name)),
        key=lambda path: int(DELTA_RE.match(path.name).group(1)),
    )

def analyze_stage(feature_root: Path, name: str, row: dict[str, str] | None) -> dict:
    """Estado de una etapa según sus artefactos, no según lo que diga el agente."""
    stage = feature_root / name
    conciliation = read(stage / "CONCILIACION.md")
    tasks = read(stage / "TAREAS.md")
    audit = read(stage / "AUDIT.md")
    deltas = delta_files(stage)

    conc_state = normalize(parse_state(conciliation))
    stage_state = normalize((row or {}).get("Estado"))
    tasks_state = normalize(parse_state(tasks))
    verdict = audit_verdict(audit)
    open_questions = bullets(section(conciliation, "Preguntas abiertas"))
    blockers: list[dict[str, str]] = []

    def block(code: str, message: str, resolution: str) -> None:
        blockers.append({"codigo": code, "mensaje": message, "resolucion": resolution})

    if not conciliation:
        block("CONCILIACION_AUSENTE", "la etapa no tiene CONCILIACION.md", "crear la etapa o corregir el índice")
    elif conc_state in CONCILIACION_ABIERTA and open_questions:
        block(
            "PREGUNTAS_ABIERTAS",
            f"{len(open_questions)} pregunta(s) abierta(s): {open_questions[0]}",
            "conciliate-stage: resolver o diferir a una etapa nombrada",
        )
    elif conc_state and conc_state not in CONCILIACION_ABIERTA + ("cerrada",):
        block("CONCILIACION_INVALIDA", f"estado de conciliación desconocido: {conc_state}", "corregir CONCILIACION.md")

    if deltas and "no coincide" not in audit.lower():
        block(
            "DELTA_SIN_AUDIT",
            f"hay {len(deltas)} delta(s) sin una pasada de auditoría con veredicto no coincide",
            "audit-stage: justificar el delta con un veredicto no coincide antes de implementarlo",
        )

    if stage_state == "bloqueada":
        causes = bullets(section(conciliation, "Bloqueos"))
        block(
            "ETAPA_BLOQUEADA",
            "la etapa está bloqueada" + (f": {causes[0]}" if causes else " sin causa escrita"),
            "registrar desbloqueador y evidencia requerida, o desbloquear con decisión del usuario",
        )
    if stage_state == "cerrada" and verdict != "coincide":
        block(
            "INDICE_CERRADO_SIN_COINCIDE",
            "el índice marca la etapa cerrada sin una pasada de auditoría con veredicto coincide",
            "audit-stage: reauditar; no corregir el índice para que el gate pase",
        )
    if verdict == "coincide" and stage_state != "cerrada":
        block(
            "COINCIDE_SIN_CIERRE",
            "la última auditoría coincide pero el índice no marca la etapa cerrada",
            "cerrar la etapa en el índice con la pasada que lo demuestra",
        )

    if conc_state == "cerrada" and tasks and not re.search(r"\*\*Principal:\*\*\s*sí", tasks, re.I):
        block("TAREA_NO_PRINCIPAL", "TAREAS.md no declara Principal: sí", "corregir la lista principal")

    dependency = (row or {}).get("Depende de", "—")
    depends_on = "" if normalize(dependency) in ("—", "-", "", "ninguna") else dependency

    delta_state = normalize(parse_state(read(deltas[-1]))) if deltas else ""
    if blockers:
        state, skill = DECISION, None
    elif not conciliation or conc_state in CONCILIACION_ABIERTA:
        state, skill = TRABAJANDO, "conciliate-stage"
    elif not tasks:
        state, skill = TRABAJANDO, "generate-stage-tasks"
    elif deltas and delta_state in ("", "pendiente", "en curso"):
        state, skill = TRABAJANDO, "implement-stage"
    elif deltas and delta_state in ("implementada", "auditada"):
        state, skill = VERIFICANDO, "audit-stage"
    elif tasks_state in ("", "pendiente", "en curso") and stage_state == "auditando":
        state, skill = VERIFICANDO, "audit-stage"
    elif tasks_state in ("", "pendiente", "en curso"):
        state, skill = TRABAJANDO, "implement-stage"
    elif tasks_state in ("implementada", "auditada"):
        if verdict == "coincide":
            state, skill = LISTO, None
        else:
            state, skill = VERIFICANDO, "audit-stage"
    else:
        state, skill = VERIFICANDO, "audit-stage"

    return {
        "etapa": name,
        "estados": {
            "conciliacion": conc_state or "ausente",
            "etapa": stage_state or "ausente",
            "tareas": tasks_state or "ausente",
            "auditoria": verdict or "ausente",
        },
        "state": state,
        "siguiente": skill,
        "blockers": blockers,
        "preguntas_abiertas": open_questions,
        "deltas": [path.name for path in deltas],
        "depende_de": depends_on,
    }

def select_stage(by_folder: dict[str, dict[str, str]], index: str, requested: str | None) -> str | None:
    if requested:
        return requested
    if not by_folder:
        return None

    def state_of(name: str) -> str:
        return normalize(by_folder.get(name, {}).get("Estado"))

    active = [name for name in by_folder if state_of(name) in ETAPA_ACTIVA]
    if len(active) == 1:
        return active[0]
    if len(active) > 1:
        return sorted(active)[0]

    committed = active_goal(index)
    for name in committed:
        if name in by_folder and state_of(name) in ETAPA_ELEGIBLE:
            return name

    eligible = sorted(
        (name for name in by_folder if state_of(name) in ETAPA_ELEGIBLE),
    )
    if eligible:
        return eligible[0]
    return sorted(by_folder)[-1]

def analyze(feature_root: Path, requested: str | None = None) -> dict:
    index = read(feature_root / "README.md")
    if not index:
        raise FeatureError(f"no hay README.md de índice en {feature_root}")
    _, by_folder = parse_index(index)
    if not by_folder:
        raise FeatureError("el índice no tiene una tabla de etapas con columna Carpeta")
    name = select_stage(by_folder, index, requested)
    if name is None:
        raise FeatureError("el índice no declara etapas")

    multiple = [n for n in by_folder if normalize(by_folder[n].get("Estado")) in ETAPA_ACTIVA]
    result = analyze_stage(feature_root, name, by_folder.get(name))
    for dependency in re.findall(r"\b\d{2}-[a-z0-9][a-z0-9-]*", result["depende_de"], re.I):
        if dependency not in by_folder or dependency == name:
            continue
        if normalize(by_folder[dependency].get("Estado")) != "cerrada":
            result["blockers"].append(
                {
                    "codigo": "DEPENDENCIA_ABIERTA",
                    "mensaje": f"depende de {dependency}, que no está cerrada",
                    "resolucion": "cerrar la dependencia o registrar una excepción justificada en CONCILIACION.md",
                }
            )
            result["state"], result["siguiente"] = DECISION, None
    if len(multiple) > 1 and requested is None:
        result["blockers"].append(
            {
                "codigo": "VARIAS_ETAPAS_ACTIVAS",
                "mensaje": f"{len(multiple)} etapas activas a la vez: {', '.join(sorted(multiple))}",
                "resolucion": "dejar una en implementando/auditando por línea funcional, o anotar la razón",
            }
        )
        result["state"], result["siguiente"] = DECISION, None
    result["feature_root"] = str(feature_root)
    result["etapas"] = {
        other: {
            "conciliacion": normalize(by_folder[other].get("Conciliación")) or "ausente",
            "etapa": normalize(by_folder[other].get("Estado")) or "ausente",
            "seleccionada": other == name,
        }
        for other in sorted(by_folder)
    }
    return result

def render_text(result: dict, all_stages: bool) -> str:
    lines = [
        f"Etapa: {result['etapa']}",
        "Estado: " + " · ".join(f"{key}={value}" for key, value in result["estados"].items()),
        f"Siguiente: {result['siguiente']}" if result["siguiente"] else "Siguiente: ninguno",
        f"Resultado: {result['state']}",
    ]
    if result["blockers"]:
        lines.append("Bloqueos:")
        lines.extend(f"  - [{item['codigo']}] {item['mensaje']} → {item['resolucion']}" for item in result["blockers"])
    if result["deltas"]:
        lines.append("Deltas: " + ", ".join(result["deltas"]))
    if all_stages:
        lines.append("Otras etapas:")
        lines.extend(
            f"  - {name}: conciliación={value['conciliacion']}, etapa={value['etapa']}"
            for name, value in result["etapas"].items()
            if not value.get("seleccionada")
        )
    return "\n".join(lines)

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("feature_root", type=Path)
    parser.add_argument("--stage", help="etapa a analizar (por defecto, la activa o la primera elegible)")
    parser.add_argument("--json", action="store_true", help="salida legible por máquina")
    parser.add_argument("--all", action="store_true", help="listar también las demás etapas")
    parser.add_argument("--check", action="store_true", help="salir con 1 si el estado es necesita-decision")
    args = parser.parse_args(argv)

    try:
        result = analyze(args.feature_root.resolve(), args.stage)
    except FeatureError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(render_text(result, args.all))
    return 1 if args.check and result["state"] == DECISION else 0

if __name__ == "__main__":
    raise SystemExit(main())
