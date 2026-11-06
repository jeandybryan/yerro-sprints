#!/usr/bin/env python3
"""Prueba el arnés del nivel 4 (`evals/level4/`) sin ejecutar agentes.

Uso: test_level4.py

`prepare.py --check` materializa los doce snapshots y verifica que cada uno
arranca en el estado que su caso mide; `score.py` agrega y no acepta un verde
sin transcript, sin puntos o con metadatos vacíos. Ninguna de las dos consume
tokens: lo que se prueba es que el arnés mide lo que dice, no el agente.

Solo stdlib y el binario `git`.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
FEATURE = HERE.parent
LEVEL4 = FEATURE / "evals" / "level4"
CASES = json.loads((LEVEL4 / "cases.json").read_text(encoding="utf-8"))["cases"]

errors: list[str] = []
checked = 0


def fail(message: str) -> None:
    errors.append(message)


def run(*args: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, *args],
        cwd=str(cwd) if cwd else None,
        capture_output=True,
        text=True,
    )


def case_file(label: str) -> Path:
    return LEVEL4 / label


def check_catalog() -> None:
    global checked
    checked += 1
    if not CASES:
        fail("level4: cases.json está vacío")
    ids = [case.get("id") for case in CASES]
    if len(ids) != len(set(ids)):
        fail("level4: hay IDs duplicados en cases.json")
    for case in CASES:
        checked += 1
        for field in ("id", "skill", "title", "setup", "prompt", "expectations", "control"):
            if not case.get(field):
                fail(f"level4: {case.get('id', '?')} no declara {field!r}")
        if case.get("setup") not in {
            "s52", "s53", "s54", "s55", "s56", "s57",
            "s58", "s59", "s60", "s61", "s62", "s63",
        }:
            fail(f"level4: {case.get('id')} usa un setup desconocido: {case.get('setup')}")


def check_prepare(out: Path) -> None:
    """Cada caso arranca en el estado que mide. No consume tokens."""
    global checked
    done = run(str(LEVEL4 / "prepare.py"), "--out", str(out), "--check", "--force")
    checked += 1
    if done.returncode != 0:
        fail(
            "level4: prepare.py --check falló; un caso no arranca en el estado "
            f"que mide:\n{done.stdout}{done.stderr}"
        )
        return
    for case in CASES:
        checked += 1
        case_dir = out / case["id"]
        if not (case_dir / "snapshot").is_dir():
            fail(f"level4: {case['id']} no materializó su snapshot")
        if (case_dir / "snapshot" / "skills" / "feature-stages" / "evals").exists():
            fail(f"level4: {case['id']} copió evals/ dentro del snapshot; el agente vería la rúbrica")
        for name in ("PROMPT.md", "_rubrica/EXPECTATIONS.md", "_rubrica/RESULTADO.json"):
            if not (case_dir / name).is_file():
                fail(f"level4: {case['id']} no escribió {name}")
    index = (out / "INDICE.md").read_text(encoding="utf-8") if (out / "INDICE.md").is_file() else ""
    for case in CASES:
        if case["id"] not in index:
            fail(f"level4: el índice no lista {case['id']}")
    if "`S54/snapshot/`" in index and "| S54 |" not in index:
        fail("level4: la fila del índice con un `|` en el título se partió")


def check_score(out: Path) -> None:
    """Una corrida incompleta sale 1; un verde sin transcript no se acepta."""
    global checked
    incomplete = run(str(LEVEL4 / "score.py"), "--out", str(out))
    checked += 1
    if incomplete.returncode != 1:
        fail("level4: score.py aceptó una corrida incompleta con salida distinta de 1")
    if "incompletos: 12" not in incomplete.stdout:
        fail(f"level4: score.py no informa los doce casos incompletos:\n{incomplete.stdout}")

    allowed = run(str(LEVEL4 / "score.py"), "--out", str(out), "--allow-incomplete")
    checked += 1
    if allowed.returncode != 0:
        fail(f"level4: --allow-incomplete salió {allowed.returncode}")
    report = (out / "REPORTE.md").read_text(encoding="utf-8") if (out / "REPORTE.md").is_file() else ""
    if "REPORTE.md" and not report:
        fail("level4: score.py no escribió REPORTE.md")

    # Un caso "verde" sin transcript ni puntos se rechaza: el falso verde es
    # el fallo que el arnés existe para impedir.
    case_dir = out / CASES[0]["id"] / "_rubrica"
    (case_dir / "RESULTADO.json").write_text(
        json.dumps({"id": CASES[0]["id"], "pasa": True, "puntos": {}, "falso_cierre": False}),
        encoding="utf-8",
    )
    (case_dir / "META.json").write_text(
        json.dumps({"id": CASES[0]["id"], "commit": "", "model": "", "agent": "", "date": ""}),
        encoding="utf-8",
    )
    fake = run(str(LEVEL4 / "score.py"), "--out", str(out), "--allow-incomplete")
    checked += 1
    text = fake.stdout + fake.stderr
    if "pasa sin transcript" not in text:
        fail(f"level4: score.py no rechaza un verde sin transcript:\n{text}")
    if "falta model" not in text and "falta commit" not in text:
        fail(f"level4: score.py no exige los metadatos de la corrida:\n{text}")

    # Un veredicto completo con transcript sí agrega, y el caso cuenta.
    (case_dir / "transcript.md").write_text("transcript\n", encoding="utf-8")
    (case_dir / "RESULTADO.json").write_text(
        json.dumps(
            {
                "id": CASES[0]["id"],
                "pasa": True,
                "puntos": {str(index + 1): 1 for index in range(len(CASES[0]["expectations"]))},
                "falso_cierre": False,
            }
        ),
        encoding="utf-8",
    )
    (case_dir / "META.json").write_text(
        json.dumps(
            {
                "id": CASES[0]["id"],
                "commit": "abc1234",
                "model": "modelo",
                "agent": "host 1.0",
                "date": "2026-11-06",
            }
        ),
        encoding="utf-8",
    )
    for other in CASES[1:]:
        other_dir = out / other["id"] / "_rubrica"
        for name in ("META.json", "RESULTADO.json"):
            data = json.loads((other_dir / name).read_text(encoding="utf-8"))
            if name == "META.json":
                data.update(commit="abc1234", model="modelo", agent="host 1.0", date="2026-11-06")
            else:
                data.update(
                    pasa=False,
                    puntos={str(index + 1): 0 for index in range(len(other["expectations"]))},
                    falso_cierre=False,
                )
            (other_dir / name).write_text(json.dumps(data), encoding="utf-8")
        (other_dir / "transcript.md").write_text("transcript\n", encoding="utf-8")
    done = run(str(LEVEL4 / "score.py"), "--out", str(out))
    checked += 1
    if done.returncode != 0:
        fail(f"level4: una corrida completa salió {done.returncode}:\n{done.stdout}{done.stderr}")
    if "pasan: 1 · fallan: 11" not in done.stdout:
        fail(f"level4: el agregado no cuenta los casos:\n{done.stdout}")


def main() -> int:
    check_catalog()
    with tempfile.TemporaryDirectory(prefix=".tmp-level4-", dir=HERE.parents[2]) as raw:
        out = Path(raw) / "corrida"
        check_prepare(out)
        if not errors:
            check_score(out)
    for error in errors:
        print(f"ERROR: {error}")
    if not errors:
        print(f"OK: arnés del nivel 4 válido ({checked} comprobaciones)")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
