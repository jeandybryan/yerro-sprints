#!/usr/bin/env python3
"""Prueba la frontera exprés (`expres.py`).

Uso: test_expres.py

Construye repositorios git temporales y comprueba que el comprobador deja
pasar un cambio pequeño, y rechaza por el motivo correcto un cambio con más
archivos, más líneas o una ruta excluida. También verifica que las pruebas no
consumen presupuesto. Solo stdlib y el binario `git`; no consume tokens.
"""
from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))

from expres import MAX_LINES, ExpressError, changed, evaluate  # noqa: E402

errors: list[str] = []
checked = 0


def fail(message: str) -> None:
    errors.append(message)


def git(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True)


def init_repo(repo: Path) -> None:
    created = git(repo, "init", "-q")
    if created.returncode != 0:
        raise RuntimeError(f"git init falló en {repo}: {created.stderr.strip()}")
    git(repo, "config", "user.email", "fixture@example.com")
    git(repo, "config", "user.name", "Fixture")
    git(repo, "config", "commit.gpgsign", "false")
    write(repo, "app.py", 3)
    git(repo, "add", "-A")
    git(repo, "commit", "-qm", "inicial")


def write(repo: Path, name: str, lines: int) -> None:
    path = repo / name
    path.parent.mkdir(parents=True, exist_ok=True)
    body = "".join(f"linea_{index} = {index}\n" for index in range(lines))
    path.write_text(body, encoding="utf-8")


def stage(repo: Path) -> None:
    """Marca los cambios para que `git diff <base>` los vea, incluidos los nuevos."""
    git(repo, "add", "-A", "-N")
    git(repo, "add", "-A")


def base(repo: Path) -> str:
    return git(repo, "rev-parse", "HEAD").stdout.strip()


def verdict(repo: Path, reference: str) -> dict:
    return evaluate(changed(repo, reference))


def reset(repo: Path, reference: str) -> None:
    git(repo, "reset", "-q")
    git(repo, "checkout", "-q", "--", ".")
    git(repo, "clean", "-qfd")


def check_codes(report: dict, expected: list[str], label: str) -> None:
    global checked
    checked += 1
    got = [item["codigo"] for item in report["motivos"]]
    if got != expected:
        fail(f"{label}: motivos {got}, se esperaba {expected}")


def check_small(repo: Path) -> None:
    global checked
    start = base(repo)
    write(repo, "nuevo.py", 5)
    stage(repo)
    report = verdict(repo, start)
    checked += 1
    if not report["cabe"]:
        fail(f"express/pequeno: no cabía un cambio de 5 líneas: {report['motivos']}")
    if not report["confirmar_a_mano"]:
        fail("express/pequeno: un cambio que cabe debe listar lo que se confirma a mano")
    if report["lineas_produccion"] != 5:
        fail(f"express/pequeno: contó {report['lineas_produccion']} líneas, se esperaban 5")
    reset(repo, start)


def check_untracked(repo: Path) -> None:
    """Un archivo nuevo sin `git add` no puede esquivar la frontera."""
    global checked
    start = base(repo)
    write(repo, "nuevo.py", 5)
    report = verdict(repo, start)
    checked += 1
    if not report["cabe"] or report["archivos_produccion"] != 1:
        fail(f"express/sin-trackear: no contó el archivo nuevo: {report}")
    elif report["lineas_produccion"] != 5:
        fail(f"express/sin-trackear: contó {report['lineas_produccion']} líneas, se esperaban 5")
    reset(repo, start)

    start = base(repo)
    write(repo, "nuevo.py", MAX_LINES + 1)
    check_codes(verdict(repo, start), ["LINEAS"], "express/sin-trackear/lineas")
    reset(repo, start)

    start = base(repo)
    write(repo, "tests/test_nuevo.py", 300)
    report = verdict(repo, start)
    checked += 1
    if not report["cabe"]:
        fail(f"express/sin-trackear/tests: las pruebas no deben consumir presupuesto: {report['motivos']}")
    elif (report["archivos_prueba"], report["lineas_prueba"]) != (1, 300):
        fail(f"express/sin-trackear/tests: separó mal las pruebas: {report}")
    reset(repo, start)

    start = base(repo)
    write(repo, "app/auth/session.py", 1)
    check_codes(verdict(repo, start), ["RUTA_EXCLUIDA"], "express/sin-trackear/excluida")
    reset(repo, start)


def check_test_lines_free(repo: Path) -> None:
    global checked
    start = base(repo)
    write(repo, "nuevo.py", MAX_LINES)
    write(repo, "tests/test_nuevo.py", 300)
    stage(repo)
    report = verdict(repo, start)
    checked += 1
    if not report["cabe"]:
        fail(f"express/tests: las pruebas no deben consumir presupuesto: {report['motivos']}")
    if report["lineas_prueba"] != 300:
        fail(f"express/tests: contó {report['lineas_prueba']} líneas de prueba, se esperaban 300")
    checked += 1
    if report["archivos_prueba"] != 1:
        fail("express/tests: no separó el archivo de prueba del de producción")
    reset(repo, start)


def check_file_limit(repo: Path) -> None:
    start = base(repo)
    write(repo, "uno.py", 2)
    write(repo, "dos.py", 2)
    stage(repo)
    check_codes(verdict(repo, start), ["ARCHIVOS"], "express/archivos")
    reset(repo, start)


def check_line_limit(repo: Path) -> None:
    start = base(repo)
    write(repo, "uno.py", MAX_LINES + 1)
    stage(repo)
    check_codes(verdict(repo, start), ["LINEAS"], "express/lineas")
    reset(repo, start)


def check_excluded(repo: Path) -> None:
    global checked
    cases = {
        "db/migrations/0002_add.sql": "migración",
        "app/auth/session.py": "seguridad o auth",
        "contracts/pedido.proto": "contrato compartido",
        "package.json": "manifiesto de dependencias",
        "esquema.sql": "esquema",
    }
    for name, label in cases.items():
        start = base(repo)
        write(repo, name, 1)
        stage(repo)
        report = verdict(repo, start)
        got = [item["codigo"] for item in report["motivos"]]
        checked += 1
        if got != ["RUTA_EXCLUIDA"]:
            fail(f"express/excluida {name}: motivos {got}, se esperaba ['RUTA_EXCLUIDA']")
        elif label not in report["motivos"][0]["mensaje"]:
            fail(f"express/excluida {name}: el motivo no nombra {label!r}")
        reset(repo, start)
    checked += 1
    if MAX_LINES != 20:
        fail(f"express/frontera: el umbral de líneas cambió a {MAX_LINES}")


def check_clean(repo: Path) -> None:
    global checked
    report = verdict(repo, base(repo))
    checked += 1
    if not report["cabe"] or report["archivos_produccion"] != 0:
        fail(f"express/limpio: un diff vacío debe caber: {report}")
    checked += 1
    try:
        changed(repo, "ref/que-no-existe")
    except ExpressError:
        pass
    else:
        fail("express/base-invalida: una base inexistente no produjo ExpressError")


def main() -> int:
    if shutil.which("git") is None:
        print("SKIP: git no está disponible")
        return 0
    with tempfile.TemporaryDirectory(prefix=".tmp-expres-", dir=REPO_ROOT) as raw:
        repo = Path(raw) / "repo"
        repo.mkdir()
        init_repo(repo)
        check_small(repo)
        check_untracked(repo)
        check_test_lines_free(repo)
        check_file_limit(repo)
        check_line_limit(repo)
        check_excluded(repo)
        check_clean(repo)
    for error in errors:
        print(f"ERROR: {error}")
    if not errors:
        print(f"OK: {checked} comprobaciones de frontera exprés")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
