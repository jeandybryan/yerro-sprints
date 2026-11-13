#!/usr/bin/env python3
"""Prueba el helper de firma (`approvals.py --suggest`, S64).

Uso: test_approvals.py

El helper imprime el bloque de `.yerro/approvals.yml` con el `tree=` del
snapshot actual, para que la persona no copie el sha a mano. La prueba exige
las dos direcciones: el bloque impreso, pegado tal cual, cubre la pasada que se
graba; un bloque con otro árbol no la cubre; y `--suggest` no escribe el
archivo. También cubre la pista del campo escrito con guion bajo.

`--plan` imprime la firma del baseline (`base=`), que es la que se pide al
cerrar la conciliación: ese bloque no cubre ningún árbol, y una entrada con
`base=` y `alcance:` firma las dos cosas.

Solo stdlib y el binario `git`; no consume tokens.
"""
from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from approvals import ApprovalError, Approval, baseline_of, load, parse # noqa: E402
from snapshot import identity, tree_of  # noqa: E402

APPROVALS = Path(".yerro") / "approvals.yml"
SCRIPT = HERE / "approvals.py"
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
    (repo / "src.txt").write_text("uno\n", encoding="utf-8")
    git(repo, "add", "--", "src.txt")
    git(repo, "commit", "-qm", "código")
    stage = repo / "feature" / "01-alfa"
    stage.mkdir(parents=True)
    (stage / "CONCILIACION.md").write_text("# Conciliación\n", encoding="utf-8")
    git(repo, "add", "--", "feature", APPROVALS.as_posix())
    git(repo, "commit", "-qm", "etapa")

def run(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), str(repo), *args],
        capture_output=True,
        text=True,
    )

def check_suggest_is_read_only_and_covers(repo: Path) -> None:
    """El bloque impreso cubre la pasada y el helper no toca el archivo."""
    global checked
    stage = repo / "feature" / "01-alfa"
    approvals = repo / APPROVALS
    approvals.parent.mkdir(parents=True, exist_ok=True)
    approvals.write_text("", encoding="utf-8")

    before = approvals.read_text(encoding="utf-8")
    result = run(repo, "--suggest", str(stage), "--by", "Ana Ruiz", "--date", "2026-11-09")
    checked += 1
    if result.returncode != 0:
        fail(f"suggest: salió {result.returncode}: {result.stderr}")
        return
    if approvals.read_text(encoding="utf-8") != before:
        fail("suggest: escribió el archivo de aprobaciones")

    block = result.stdout
    if "etapa: 01-alfa" not in block:
        fail(f"suggest: el bloque no nombra la etapa: {block!r}")
    if "aprobado-por: Ana Ruiz" not in block:
        fail(f"suggest: el bloque no lleva el nombre: {block!r}")
    if "fecha: 2026-11-09" not in block:
        fail(f"suggest: el bloque no lleva la fecha: {block!r}")

    expected = tree_of(identity(repo, (stage.parent, APPROVALS))) or ""
    if not expected:
        fail("suggest: la fixture no produjo un tree= reconocible")
        return
    if f"alcance: tree={expected}" not in block:
        fail(f"suggest: el bloque no lleva el árbol del snapshot ({expected}): {block!r}")

    # Pegado tal cual, cubre la pasada: es el contrato del helper.
    approvals.write_text(block, encoding="utf-8")
    checked += 1
    covering = [item for item in load(repo) if item.stage == "01-alfa"]
    if not covering:
        fail("suggest: el archivo con el bloque impreso no se lee")
        return
    if not covering[0].covers(identity(repo, (stage.parent, APPROVALS))):
        fail("suggest: el bloque impreso no cubre el snapshot que acaba de describir")

    # Con una firma vigente no hace falta otra: lo avisa y no duplica.
    checked += 1
    again = run(repo, "--suggest", str(stage), "--by", "Ana Ruiz")
    if again.returncode != 0:
        fail(f"suggest: la segunda llamada salió {again.returncode}: {again.stderr}")
    elif "ya está aprobada" not in again.stderr:
        fail(f"suggest: no avisó de una firma vigente: {again.stderr!r}")

def check_block_with_foreign_tree_does_not_cover(repo: Path) -> None:
    """Control: un bloque con otro árbol no cubre la pasada."""
    global checked
    stage = repo / "feature" / "01-alfa"
    approvals = repo / APPROVALS
    approvals.parent.mkdir(parents=True, exist_ok=True)
    approvals.write_text(
        "- etapa: 01-alfa\n"
        "  aprobado-por: Ana Ruiz\n"
        "  fecha: 2026-11-09\n"
        f"  alcance: tree={'0' * 40}\n",
        encoding="utf-8",
    )
    checked += 1
    snapshot = identity(repo, (stage.parent, APPROVALS))
    items = [item for item in load(repo) if item.stage == "01-alfa"]
    if not items:
        fail("control: el archivo no se leyó")
    elif items[0].covers(snapshot):
        fail("control: un bloque con otro árbol cubrió la pasada")

def check_typo_names_the_field() -> None:
    """Un campo con guion bajo dice cómo se escribe."""
    global checked
    text = (
        "- etapa: 01-alfa\n"
        "  aprobado_por: Ana Ruiz\n"
        "  fecha: 2026-11-09\n"
    )
    checked += 1
    try:
        parse(text)
    except ApprovalError as error:
        message = str(error)
        if "aprobado-por" not in message:
            fail(f"typo: el error no nombra el campo que falta: {message}")
        if "aprobado_por" not in message:
            fail(f"typo: el error no nombra la variante escrita: {message}")
    else:
        fail("typo: aceptó un campo con guion bajo como si fuera el correcto")

def check_missing_stage_fails(repo: Path) -> None:
    """Una etapa que no existe no inventa un bloque."""
    global checked
    checked += 1
    result = run(repo, "--suggest", str(repo / "feature" / "99-nada"))
    if result.returncode == 0:
        fail("suggest: inventó un bloque para una etapa que no existe")
    elif result.stderr.strip() == "":
        fail("suggest: falló sin decir por qué")

def check_non_stage_folder_fails(repo: Path) -> None:
    """Una carpeta que no es `NN-nombre` no imprime un árbol vacío."""
    global checked
    checked += 1
    result = run(repo, "--suggest", str(repo / "feature"))
    if result.returncode == 0:
        fail("suggest: aceptó la raíz de la feature como etapa")
    elif "no parece una etapa" not in result.stderr:
        fail(f"suggest: falló por otro motivo: {result.stderr!r}")

def check_plan_signature_is_read_only_and_signed(repo: Path) -> None:
    """`--plan` imprime la firma del baseline y no la confunde con el árbol.

    S66/B2: la persona firma el baseline al cerrar la conciliación. El helper
    imprime `base=` para que no lo copie a mano; el bloque no escribe nada, no
    duplica una firma vigente y no cubre un árbol.
    """
    global checked
    stage = repo / "feature" / "01-alfa"
    approvals = repo / APPROVALS
    approvals.parent.mkdir(parents=True, exist_ok=True)
    approvals.write_text("", encoding="utf-8")

    before = approvals.read_text(encoding="utf-8")
    result = run(repo, "--suggest", str(stage), "--plan", "--by", "Ana Ruiz", "--date", "2026-11-11")
    checked += 1
    if result.returncode != 0:
        fail(f"suggest --plan: salió {result.returncode}: {result.stderr}")
        return
    if approvals.read_text(encoding="utf-8") != before:
        fail("suggest --plan: escribió el archivo de aprobaciones")

    block = result.stdout
    expected = baseline_of(stage)
    if f"base: {expected}" not in block:
        fail(f"suggest --plan: el bloque no lleva el baseline ({expected}): {block!r}")
    if len(expected) != 64:
        fail(f"suggest --plan: el baseline no es un sha256 completo: {expected!r}")
    if "alcance:" in block:
        fail(f"suggest --plan: el bloque de plan trae un alcance: {block!r}")

    # Pegado tal cual, firma el baseline y no el árbol: la persona puede
    # seguir el flujo con riesgo bajo sin añadir nada.
    approvals.write_text(block, encoding="utf-8")
    checked += 1
    items = [item for item in load(repo) if item.stage == "01-alfa"]
    if not items:
        fail("suggest --plan: el archivo con el bloque impreso no se lee")
        return
    snapshot = identity(repo, (stage.parent, APPROVALS))
    if not items[0].covers_plan(expected):
        fail("suggest --plan: el bloque impreso no cubre el baseline que describe")
    checked += 1
    if items[0].covers(snapshot):
        fail("suggest --plan: una firma de plan cubrió un árbol")

    # El baseline ignora `**Estado:**`: cerrar la etapa no invalida la firma.
    conciliation = stage / "CONCILIACION.md"
    text = conciliation.read_text(encoding="utf-8")
    conciliation.write_text(
        text.replace("# Conciliación\n", "# Conciliación\n**Estado:** cerrada\n"),
        encoding="utf-8",
    )
    checked += 1
    if baseline_of(stage) != expected:
        fail("suggest --plan: escribir **Estado:** movió el baseline firmado")

    # Con una firma de plan vigente no hace falta otra: lo avisa y no duplica.
    checked += 1
    again = run(repo, "--suggest", str(stage), "--plan", "--by", "Ana Ruiz")
    if again.returncode != 0:
        fail(f"suggest --plan: la segunda llamada salió {again.returncode}: {again.stderr}")
    elif "ya tiene la firma de plan" not in again.stderr:
        fail(f"suggest --plan: no avisó de una firma de plan vigente: {again.stderr!r}")

    # Editar el baseline después de firmar pide firma nueva.
    checked += 1
    conciliation.write_text(text.replace("Conciliación", "Conciliación (ampliada)"), encoding="utf-8")
    edited = run(repo, "--suggest", str(stage), "--plan", "--by", "Ana Ruiz")
    if "ya tiene la firma de plan" in edited.stderr:
        fail("suggest --plan: dio por vigente una firma de un baseline que cambió")

def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        repo = Path(tmp) / "repo"
        repo.mkdir()
        init_repo(repo)
        check_suggest_is_read_only_and_covers(repo)
        check_block_with_foreign_tree_does_not_cover(repo)
        check_plan_signature_is_read_only_and_signed(repo)
        check_missing_stage_fails(repo)
        check_non_stage_folder_fails(repo)
    check_typo_names_the_field()

    if errors:
        print(f"FALLAN {len(errors)} comprobaciones de {checked}:")
        for error in errors:
            print(f" - {error}")
        return 1
    print(f"test_approvals.py OK: {checked} comprobaciones")
    return 0

if __name__ == "__main__":
    sys.exit(main())
