#!/usr/bin/env python3
"""Dice qué tareas de la etapa siguen sin marcar, sin leer la lista entera (P13).

Uso: tasks.py pending <etapa> [--json]

El agente que implementa necesita saber qué falta, no releer `TAREAS.md` y sus
deltas para descubrirlo. El checkbox es la verdad por tarea: `- [ ]` pendiente,
`- [x]` hecha, y `implement-stage` lo marca solo cuando el `Verificar` de la
tarea pasa. Este script proyecta esa marca; no la juzga ni la corrige.

El título de cada tarea se acota a 80 caracteres. En datos reales la primera
línea de una tarea suele ser un párrafo, y devolverlo entero volvería a cargar
el material que esta consulta existe para no leer. La tarea completa sigue en
su archivo: aquí solo queda la orientación.

Los deltas cuentan: `TAREAS-delta-NN.md` es una lista de tareas más, y quien
trabaja en un delta necesita sus pendientes. Se leen en orden numérico, no
alfabético, porque `delta-10` se escribe después de `delta-02`.

Qué no hace, y por qué:
- no decide si la etapa está terminada: eso es el estado público de
  `next_step.py`, y un segundo veredicto sería un segundo contrato;
- no valida la forma ni la trazabilidad: eso es `validate_stage.py`, que ya
  emite los huecos como líneas `ERROR:`. Un `trace.py` que repitiera esa salida
  sería otra forma de decir lo mismo, así que no existe: la consulta de huecos
  es `validate_stage.py`.

`**Estado:** implementada` o `auditada` con una tarea sin marcar es una
contradicción entre la lista y su resumen. Se informa como `INCOHERENCIA:` y no
se corrige sola: decidir cuál de los dos miente es trabajo del agente, no de un
script que adivina.

Salida: 0 si la etapa se pudo leer, haya o no pendientes; 2 si no hay etapa, no
hay `TAREAS.md` o las listas no contienen tareas (una lista vacía no es un
"todo hecho").
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# Mismo patrón que `validate_stage.py` y `diff_scope.py`: la tarea empieza en su
# checkbox y su título es el resto de esa línea. Las casillas de la verificación
# global no llevan ID (`- [ ] Tests y lints`), así que no entran.
TASK_RE = re.compile(r"^\s*-\s*\[([ xX])\]\s*((?:D\d+-)?T\d+)\b([^\n]*)", re.M)
STATE_RE = re.compile(r"\*\*Estado:\*\*\s*([^\n]+)")
DELTA_NAME_RE = re.compile(r"^TAREAS-delta-(\d{2,})\.md$")
DONE_STATES = ("implementada", "auditada")
TITLE_JUNK_RE = re.compile(r"^[\s:—–-]+")
# Una tarea real puede empezar con un párrafo entero. Devolverlo tal cual
# reimportaría el material que P13 quiere evitar, así que el título se acota:
# orienta sin sustituir a la tarea, que sigue en el archivo. Mismo límite que
# usan los mensajes de `validate_stage.py`.
TITLE_MAX = 80


def short_title(title: str) -> str:
    if len(title) <= TITLE_MAX:
        return title
    return title[: TITLE_MAX - 3].rstrip() + "..."


def task_lists(stage: Path) -> list[Path]:
    """La lista principal y sus deltas, en el orden en que se trabajan."""
    paths: list[Path] = []
    main = stage / "TAREAS.md"
    if main.exists():
        paths.append(main)
    deltas = sorted(
        (path for path in stage.glob("TAREAS-delta-*.md") if DELTA_NAME_RE.match(path.name)),
        key=lambda path: int(DELTA_NAME_RE.match(path.name).group(1)),
    )
    return paths + deltas


def read_list(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    state = STATE_RE.search(text)
    tasks = [
        {
            "id": task_id,
            "hecha": box.lower() == "x",
            "titulo": short_title(TITLE_JUNK_RE.sub("", title).strip()),
        }
        for box, task_id, title in TASK_RE.findall(text)
    ]
    return {
        "archivo": path.name,
        "estado": state.group(1).strip().lower() if state else "",
        "tareas": tasks,
    }


def pending(stage: Path) -> dict:
    """La proyección de los checkboxes, con las contradicciones a la vista."""
    pendientes: list[dict] = []
    hechas: list[dict] = []
    incoherencias: list[dict] = []
    for path in task_lists(stage):
        info = read_list(path)
        for task in info["tareas"]:
            item = {"id": task["id"], "archivo": info["archivo"], "titulo": task["titulo"]}
            (hechas if task["hecha"] else pendientes).append(item)
        sin_marcar = [task["id"] for task in info["tareas"] if not task["hecha"]]
        if info["estado"] in DONE_STATES and sin_marcar:
            incoherencias.append(
                {"archivo": info["archivo"], "estado": info["estado"], "sin_marcar": sin_marcar}
            )
    return {
        "etapa": stage.name,
        "pendientes": pendientes,
        # Las hechas se resumen como conteo: sus títulos son material que esta
        # consulta existe para no cargar, y para "cuánto falta" basta el número.
        "hechas": len(hechas),
        "incoherencias": incoherencias,
        "total": len(pendientes) + len(hechas),
    }


def report(result: dict) -> None:
    for item in result["pendientes"]:
        print(f"{item['id']}\t{item['archivo']}\t{item['titulo']}")
    for item in result["incoherencias"]:
        print(
            f"INCOHERENCIA: {item['archivo']} declara **Estado:** {item['estado']} "
            f"y deja sin marcar {', '.join(item['sin_marcar'])}"
        )
    if not result["pendientes"]:
        print(f"OK: no hay tareas pendientes ({result['hechas']} hecha(s))")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("action", choices=("pending",), help="consulta a ejecutar")
    parser.add_argument("stage", type=Path, help="carpeta de la etapa")
    parser.add_argument("--json", action="store_true", help="salida legible por máquina")
    args = parser.parse_args(argv)

    if not args.stage.is_dir():
        print(f"ERROR: no existe la etapa {args.stage}", file=sys.stderr)
        return 2
    # `TAREAS.md` es la lista principal; los deltas se suman a ella. Un delta
    # huérfano no es una etapa, igual que en `diff_scope.py`.
    if not (args.stage / "TAREAS.md").exists():
        print(f"ERROR: {args.stage} no tiene TAREAS.md", file=sys.stderr)
        return 2

    result = pending(args.stage)
    if not result["total"]:
        print(f"ERROR: las listas de {args.stage} no contienen tareas", file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        report(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
