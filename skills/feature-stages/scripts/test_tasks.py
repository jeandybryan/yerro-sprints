#!/usr/bin/env python3
"""Prueba la consulta de tareas pendientes (`tasks.py`, P13).

Uso: test_tasks.py

Construye etapas temporales y comprueba que la consulta proyecta el checkbox
sin juzgarlo: separa pendientes de hechas, incluye los deltas en orden numérico,
avisa cuando `**Estado:**` dice terminada pero queda una tarea sin marcar, y
sale con 2 cuando no hay lista que leer o está vacía (una lista sin tareas no es
un "todo hecho"). No consume tokens.
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[2]
SCRIPT = HERE / "tasks.py"

errors: list[str] = []
checked = 0


def fail(message: str) -> None:
    errors.append(message)


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args], capture_output=True, text=True
    )


def build(root: Path, name: str, tareas: str | None, deltas: dict[str, str] | None = None) -> Path:
    path = root / name
    path.mkdir(parents=True)
    if tareas is not None:
        (path / "TAREAS.md").write_text(tareas, encoding="utf-8")
    for filename, body in (deltas or {}).items():
        (path / filename).write_text(body, encoding="utf-8")
    return path


def rows(stdout: str) -> list[list[str]]:
    return [line.split("\t") for line in stdout.splitlines() if "\t" in line]


def check_pending(root: Path) -> None:
    """Solo las tareas sin marcar, y las hechas no se cuelan."""
    global checked
    path = build(
        root,
        "mixta",
        "# Tareas\n\n**Principal:** sí\n\n"
        "- [x] T1 — hecha (CA-01)\n"
        "- [ ] T2 — falta (CA-01)\n"
        "- [X] T3 — hecha también (CA-02)\n"
        "- [ ] T4 — falta dos (CA-02)\n",
    )
    result = run("pending", str(path))
    checked += 1
    if result.returncode != 0:
        fail(f"mixta: salida {result.returncode}: {result.stderr}")
        return
    ids = [row[0] for row in rows(result.stdout)]
    if ids != ["T2", "T4"]:
        fail(f"mixta: pendientes {ids}, se esperaban ['T2', 'T4']")


def check_titulo_y_archivo(root: Path) -> None:
    """La línea dice ID, archivo y título: el agente no relee la tarea."""
    global checked
    path = build(root, "titulo", "- [ ] T7 — exportar el informe (CA-03)\n")
    result = run("pending", str(path))
    checked += 1
    if result.returncode != 0:
        fail(f"titulo: salida {result.returncode}: {result.stderr}")
        return
    parts = rows(result.stdout)
    esperado = [["T7", "TAREAS.md", "exportar el informe (CA-03)"]]
    if parts != esperado:
        fail(f"titulo: filas {parts}, se esperaba {esperado}")


def check_titulo_acotado(root: Path) -> None:
    """Un párrafo como título se acota: no reimporta el material que se evita."""
    global checked
    path = build(root, "largo", f"- [ ] T9 — {'x' * 200} (CA-04)\n")
    result = run("pending", str(path), "--json")
    checked += 1
    if result.returncode != 0:
        fail(f"largo: salida {result.returncode}: {result.stderr}")
        return
    try:
        titulo = json.loads(result.stdout)["pendientes"][0]["titulo"]
    except (json.JSONDecodeError, KeyError, IndexError) as error:
        fail(f"largo: no se pudo leer el título ({error}): {result.stdout!r}")
        return
    if len(titulo) > 80:
        fail(f"largo: el título mide {len(titulo)}, se esperaba <= 80")
    if not titulo.endswith("..."):
        fail(f"largo: el título truncado no lo indica: {titulo[-12:]!r}")


def check_deltas_en_orden(root: Path) -> None:
    """Los deltas entran, y por número, no alfabético.

    El caso usa 99 y 100 a propósito: con nombres de dos dígitos (`02` y `10`)
    el orden alfabético coincide con el numérico y el caso no distinguiría nada.
    """
    global checked
    path = build(
        root,
        "deltas",
        "- [ ] T1 — principal (CA-01)\n",
        {
            "TAREAS-delta-100.md": "- [ ] D100-T1 — delta cien (CA-01)\n",
            "TAREAS-delta-99.md": "- [ ] D99-T1 — delta noventa y nueve (CA-01)\n",
        },
    )
    result = run("pending", str(path))
    checked += 1
    if result.returncode != 0:
        fail(f"deltas: salida {result.returncode}: {result.stderr}")
        return
    order = [(row[1], row[0]) for row in rows(result.stdout)]
    esperado = [
        ("TAREAS.md", "T1"),
        ("TAREAS-delta-99.md", "D99-T1"),
        ("TAREAS-delta-100.md", "D100-T1"),
    ]
    if order != esperado:
        fail(f"deltas: orden {order}, se esperaba {esperado}")


def check_todo_hecho(root: Path) -> None:
    """Sin pendientes lo dice, y no inventa una incoherencia."""
    global checked
    path = build(
        root,
        "hecha",
        "**Estado:** implementada\n\n- [x] T1 — hecha (CA-01)\n- [x] T2 — hecha (CA-02)\n",
    )
    result = run("pending", str(path))
    checked += 1
    if result.returncode != 0:
        fail(f"hecha: salida {result.returncode}: {result.stderr}")
        return
    if "no hay tareas pendientes" not in result.stdout:
        fail(f"hecha: no informa que no queda nada: {result.stdout!r}")
    if "INCOHERENCIA" in result.stdout:
        fail(f"hecha: marca incoherencia sin contradicción: {result.stdout!r}")


def check_incoherencia(root: Path) -> None:
    """`Estado: implementada` con una tarea sin marcar se avisa, no se corrige."""
    global checked
    path = build(
        root,
        "contradice",
        "**Estado:** implementada\n\n- [x] T1 — hecha (CA-01)\n- [ ] T2 — sin marcar (CA-02)\n",
    )
    result = run("pending", str(path))
    checked += 1
    if result.returncode != 0:
        fail(f"contradice: salida {result.returncode}: {result.stderr}")
        return
    if "INCOHERENCIA" not in result.stdout or "T2" not in result.stdout:
        fail(f"contradice: no avisa del Estado implementada con T2 sin marcar: {result.stdout!r}")
    # El aviso no esconde la respuesta: T2 sigue siendo lo pendiente.
    if not result.stdout.startswith("T2\t"):
        fail(f"contradice: T2 no abre la lista de pendientes: {result.stdout!r}")


def check_json(root: Path) -> None:
    """La forma legible por máquina separa pendientes, hechas y total."""
    global checked
    path = build(root, "json", "- [x] T1 — hecha (CA-01)\n- [ ] T2 — falta (CA-02)\n")
    result = run("pending", str(path), "--json")
    checked += 1
    if result.returncode != 0:
        fail(f"json: salida {result.returncode}: {result.stderr}")
        return
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError as error:
        fail(f"json: la salida no es JSON ({error}): {result.stdout!r}")
        return
    if [item["id"] for item in payload.get("pendientes", [])] != ["T2"]:
        fail(f"json: pendientes {payload.get('pendientes')}, se esperaba ['T2']")
    if payload.get("hechas") != 1:
        fail(f"json: hechas {payload.get('hechas')!r}, se esperaba el conteo 1")
    if payload.get("total") != 2:
        fail(f"json: total {payload.get('total')}, se esperaba 2")
    # Una tarea hecha no reimporta su título: el JSON es la consulta, no el archivo.
    if "T1" in result.stdout:
        fail(f"json: la tarea hecha T1 se coló en la salida: {result.stdout!r}")


def check_sin_lista(root: Path) -> None:
    """Sin `TAREAS.md` no hay consulta posible, y se dice por qué."""
    global checked
    path = build(root, "sin-lista", None)
    result = run("pending", str(path))
    checked += 1
    if result.returncode != 2 or "TAREAS.md" not in result.stderr:
        fail(
            f"sin-lista: salida {result.returncode}, stderr {result.stderr!r}; "
            "se esperaba 2 nombrando TAREAS.md"
        )


def check_solo_delta(root: Path) -> None:
    """Un delta sin lista principal no es una etapa: falta `TAREAS.md`."""
    global checked
    path = build(root, "solo-delta", None, {"TAREAS-delta-01.md": "- [ ] D01-T1 — x (CA-01)\n"})
    result = run("pending", str(path))
    checked += 1
    if result.returncode != 2 or "no tiene TAREAS.md" not in result.stderr:
        fail(
            f"solo-delta: salida {result.returncode}, stderr {result.stderr!r}; "
            "se esperaba 2: el delta no sustituye a la lista principal"
        )


def check_lista_vacia(root: Path) -> None:
    """Una lista sin tareas no es un 'todo hecho'."""
    global checked
    path = build(root, "vacia", "# Tareas\n\n**Principal:** sí\n\n## Listado\n")
    result = run("pending", str(path))
    checked += 1
    if result.returncode != 2:
        fail(f"vacia: salida {result.returncode}; se esperaba 2, no un OK falso")
    if "no contienen tareas" not in result.stderr:
        fail(f"vacia: no explica por qué: {result.stderr!r}")


def check_etapa_inexistente(root: Path) -> None:
    global checked
    result = run("pending", str(root / "no-existe"))
    checked += 1
    if result.returncode != 2 or "no existe la etapa" not in result.stderr:
        fail(f"no-existe: salida {result.returncode}, stderr {result.stderr!r}")


def main() -> int:
    with tempfile.TemporaryDirectory(prefix=".tmp-tasks-", dir=REPO_ROOT) as raw:
        root = Path(raw)
        check_pending(root)
        check_titulo_y_archivo(root)
        check_titulo_acotado(root)
        check_deltas_en_orden(root)
        check_todo_hecho(root)
        check_incoherencia(root)
        check_json(root)
        check_sin_lista(root)
        check_solo_delta(root)
        check_lista_vacia(root)
        check_etapa_inexistente(root)
    for error in errors:
        print(f"ERROR: {error}")
    if not errors:
        print(f"OK: {checked} comprobaciones de consulta de tareas")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
