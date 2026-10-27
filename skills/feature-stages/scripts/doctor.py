#!/usr/bin/env python3
"""Informe de salud de solo lectura de un árbol de feature por etapas.

Uso: doctor.py <feature-root> [--json]

Comprueba la coherencia entre el índice, los artefactos de cada etapa y los
deltas, y reutiliza la transición calculada por next_step.py. No escribe ni
repara nada: informa errores, advertencias y el siguiente paso válido.

No juzga el contrato completo de artefactos: comprueba que el índice y los
artefactos no se contradigan y que estén los campos que su lista enumera. Un
`OK` aquí no significa que la etapa cumpla el contrato; eso lo decide
`validate_stage.py`. Presentar la coherencia como veredicto de contrato fue el
defecto: `doctor.py` decía «árbol coherente» sobre cortes reales cuyas nueve
etapas rechazaba el validador.

Salida: 0 sin errores de doctor; 1 con errores.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from next_step import (  # noqa: E402
    DELTA_RE,
    FeatureError,
    analyze,
    delta_files,
    normalize,
    parse_index,
    parse_state,
    read,
)

STAGE_DIR_RE = re.compile(r"^\d{2}-[a-z0-9][a-z0-9-]*$")
NEEDS_TASKS = ("lista", "implementando", "auditando", "cerrada")
NEEDS_AUDIT = ("auditando", "cerrada")
AUDIT_COLUMNS = ("Carpeta", "Conciliación", "Estado", "Tareas", "Auditoría")
EXPRES_COLUMNS = ("#", "Fecha", "Cambio", "Archivos", "CA", "Frontera", "Verificación")
EXPRES_LIMIT = 3
RULINGS_PER_TASK = 3
RULING_RE = re.compile(r"^\s*Ruling:", re.M)
ARCHIVOS_RE = re.compile(r"^\s*\*{0,2}Archivos:\*{0,2}\s*\S", re.M)
TASK_BLOCK_RE = re.compile(
    r"^\s*-\s*\[[ xX]\]\s*((?:D\d+-)?T\d+)\b(.*?)(?=^\s*-\s*\[[ xX]\]|\Z)",
    re.M | re.S,
)


def split_tasks(tasks: str) -> list[tuple[str, str]]:
    """Pares (id, cuerpo) de cada tarea del listado."""
    return TASK_BLOCK_RE.findall(tasks)


def parse_table(text: str, columns: tuple[str, ...]) -> list[dict[str, str]]:
    """Filas de la primera tabla que tenga todas las columnas pedidas."""
    header: list[str] | None = None
    rows: list[dict[str, str]] = []
    for line in text.splitlines():
        if not line.strip().startswith("|"):
            if header is not None and rows:
                return rows
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if header is None:
            if all(column in cells for column in columns):
                header = cells
            continue
        if set("".join(cells)) <= set("-: "):
            continue
        if len(cells) < len(header):
            cells += [""] * (len(header) - len(cells))
        rows.append(dict(zip(header, cells)))
    return rows


def check_expres(root: Path, warnings: list[str]) -> None:
    """Advierte cuando la acumulación delata que el corte estaba mal.

    `EXPRES.md` es un registro, no un gate: nunca produce un error y nunca
    cambia la transición. Solo avisa, porque tres cambios pequeños sobre el
    mismo CA o el mismo archivo significan que eso no era pequeño.
    """
    path = root / "EXPRES.md"
    if not path.is_file():
        return
    rows = parse_table(read(path), EXPRES_COLUMNS)
    if not rows:
        warnings.append("EXPRES.md: no tiene tabla de cambios con sus columnas")
        return

    for column, label in (("CA", "el mismo CA"), ("Archivos", "el mismo archivo")):
        counts: dict[str, int] = {}
        for row in rows:
            for value in re.split(r"[,;]", row.get(column, "")):
                key = value.strip().strip("`")
                if key and key.lower() not in ("ninguno", "ninguna", "—", "-"):
                    counts[key] = counts.get(key, 0) + 1
        for key, count in sorted(counts.items()):
            if count >= EXPRES_LIMIT:
                warnings.append(
                    f"EXPRES.md: {count} cambios sobre {label} {key!r}; "
                    "promover a etapa en vez de seguir acumulando"
                )


def check(root: Path, result: dict | None, errors: list[str], warnings: list[str]) -> dict | None:
    index = read(root / "README.md")
    if not index:
        errors.append("falta README.md: el índice de etapas es obligatorio")
        return result

    _, by_folder = parse_index(index)
    if not by_folder:
        errors.append("el índice no tiene una tabla con las columnas Carpeta/Conciliación/Estado/Tareas/Auditoría")
        return result

    seen_numbers: dict[str, str] = {}
    for name, row in by_folder.items():
        if not STAGE_DIR_RE.match(name):
            errors.append(f"índice: la carpeta {name!r} no sigue el patrón NN-slug")
        number = name.split("-", 1)[0]
        if number in seen_numbers:
            errors.append(f"índice: el número {number} aparece en {seen_numbers[number]} y {name}")
        seen_numbers[number] = name

        stage = root / name
        if not stage.is_dir():
            errors.append(f"índice: la etapa {name} no tiene carpeta")
            continue
        if not (stage / "CONCILIACION.md").is_file():
            errors.append(f"{name}: falta CONCILIACION.md")

        conciliation = read(stage / "CONCILIACION.md")
        conc_state = normalize(parse_state(conciliation))
        stage_state = normalize(row.get("Estado"))
        tasks = read(stage / "TAREAS.md")
        audit = read(stage / "AUDIT.md")
        tasks_state = normalize(parse_state(tasks))

        if conc_state and conc_state not in ("borrador-corte", "abierta", "cerrada"):
            errors.append(f"{name}: estado de conciliación desconocido {conc_state!r}")
        if stage_state and stage_state not in (
            "borrador", "conciliando", "lista", "implementando", "auditando", "cerrada", "bloqueada"
        ):
            errors.append(f"{name}: estado de etapa desconocido {stage_state!r}")
        if stage_state in ("lista", "implementando", "auditando", "cerrada") and conc_state != "cerrada":
            errors.append(
                f"{name}: estado {stage_state} incompatible con conciliación {conc_state or 'ausente'}"
            )

        if stage_state in NEEDS_TASKS and not tasks:
            errors.append(f"{name}: etapa {stage_state} sin TAREAS.md")
        if stage_state in NEEDS_AUDIT and not audit:
            errors.append(f"{name}: etapa {stage_state} sin AUDIT.md")
        if stage_state in ("borrador", "conciliando") and tasks:
            errors.append(f"{name}: TAREAS.md prematuro para etapa {stage_state}")
        if tasks and re.search(r"^[-*] \[", tasks, re.M):
            if not re.search(r"Test-first:\s*(?:sí|si|no)\b", tasks, re.I):
                errors.append(f"{name}: TAREAS.md sin Test-first")
            if not re.search(r"Test:\s*\S+", tasks, re.I):
                errors.append(f"{name}: TAREAS.md sin Test")
        if audit and stage_state in NEEDS_AUDIT:
            for label, pattern in (("Snapshot", r"\*\*Snapshot:\*\*\s*\S+"), ("Trazabilidad", r"\*\*Trazabilidad:\*\*\s*\S+"), ("E-NN", r"\bE-\d{2}\b"), ("Veredicto", r"\*\*Veredicto:\*\*\s*\S+")):
                if not re.search(pattern, audit, re.I):
                    errors.append(f"{name}: AUDIT.md sin {label}")
            if stage_state == "cerrada" and not re.search(r"\*\*Veredicto:\*\*\s*coincide\b", audit, re.I):
                errors.append(f"{name}: cierre sin veredicto coincide")
        # B-28: la migración la hace el humano, pero saber a quién le toca sí se
        # puede automatizar. Una etapa no cerrada cuyo TAREAS.md no declara los
        # archivos de cada tarea todavía no cumple el contrato de alcance.
        if stage_state != "cerrada" and tasks and split_tasks(tasks):
            missing = [task_id for task_id, body in split_tasks(tasks) if not ARCHIVOS_RE.search(body)]
            if missing:
                warnings.append(
                    f"{name}: etapa sin migrar, {', '.join(missing)} sin **Archivos:**; "
                    "migrar re-conciliando el alcance (nunca desde el diff) o cerrarla "
                    "con la versión anterior"
                )
        if tasks and tasks_state and tasks_state not in ("pendiente", "en curso", "implementada", "auditada"):
            errors.append(f"{name}: estado de tareas desconocido {tasks_state!r}")

        for delta in delta_files(stage):
            text = read(delta)
            if not re.search(r"\*\*Cierra:\*\*", text, re.I):
                errors.append(f"{delta.name}: no declara **Cierra:**")
            if not re.search(r"\*\*Hueco:\*\*", text, re.I):
                warnings.append(f"{delta.name}: no declara **Hueco:**")
        for path in stage.glob("TAREAS-delta-*.md"):
            if not DELTA_RE.match(path.name):
                errors.append(f"{path.name}: nombre de delta fuera de NN")

        # B-33: los rulings resuelven ambigüedad residual. Cuatro en la misma
        # tarea no son ambigüedad, son una tarea sin especificar. Avisa, no
        # bloquea: una tarea de migración puede producir varios legítimos.
        for task_id, body in split_tasks(tasks):
            count = len(RULING_RE.findall(body))
            if count > RULINGS_PER_TASK:
                warnings.append(
                    f"{name}/{task_id}: {count} rulings en una tarea "
                    f"(máximo {RULINGS_PER_TASK}); generate-stage-tasks: partir la tarea "
                    "o cerrar la ambigüedad en la conciliación"
                )

    folders = sorted(
        path.name for path in root.iterdir() if path.is_dir() and STAGE_DIR_RE.match(path.name)
    )
    for name in folders:
        if name not in by_folder:
            errors.append(f"carpeta {name} sin fila en el índice")

    if result is None:
        return result
    for item in result["blockers"]:
        errors.append(f"{item['codigo']}: {item['mensaje']} → {item['resolucion']}")
    if result["deltas"]:
        audit = read(root / result["etapa"] / "AUDIT.md").lower()
        if "no coincide" not in audit:
            warnings.append(
                f"{result['etapa']}: hay deltas sin una pasada de auditoría con veredicto no coincide"
            )
    return result

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("feature_root", type=Path)
    parser.add_argument("--stage", help="etapa a inspeccionar (por defecto, la activa)")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    root = args.feature_root.resolve()
    errors: list[str] = []
    warnings: list[str] = []
    result = None
    try:
        result = analyze(root, args.stage)
    except FeatureError as error:
        errors.append(str(error))
    result = check(root, result, errors, warnings)
    check_expres(root, warnings)

    report = {
        "feature_root": str(root),
        "ok": not errors,
        "errores": errors,
        "advertencias": warnings,
        "siguiente": result,
    }
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        for error in errors:
            print(f"ERROR: {error}")
        for warning in warnings:
            print(f"WARN: {warning}")
        if result:
            print(f"INFO: siguiente={result['state']} skill={result['siguiente']} etapa={result['etapa']}")
            print("OK: índice y artefactos coherentes (no es el contrato: validate_stage.py)" if not errors else "FALLA: el árbol no cumple las comprobaciones de doctor")
    return 1 if errors else 0

if __name__ == "__main__":
    raise SystemExit(main())
