#!/usr/bin/env python3
"""Identidad reproducible del código que se está auditando.

Uso: snapshot.py <path> [--exclude PATH]... [--json]

Calcula, sin tocar el índice real de git, una identidad content-addressable
del árbol de trabajo: el commit de HEAD, el árbol que resultaría de incluir el
estado actual y si hay cambios sin commitear. Es la misma identidad que una
pasada de `AUDIT.md` registra en `**Snapshot:**`.

`--exclude PATH` saca una ruta (archivo o carpeta, relativa a la raíz del repo)
del cálculo. Se usa para excluir el árbol de la feature: la evidencia puede
cambiar mientras se escribe el veredicto, y el snapshot debe identificar el
código, no el archivo que lo describe. Sin exclusiones, cualquier escritura en
`AUDIT.md` invalidaría su propia evidencia.

B-49: el índice del panel (`README.md` junto a las carpetas de etapa) se excluye por
forma, sin nombrar etapas: su fila de estado se escribe justo al cerrar la
etapa que documenta, y mantenerla dentro obliga a una pasada nueva para
cambiar una celda. Lo que se audita es el árbol de la etapa; el índice se
juzga por su contenido (estado y veredicto de la fila), no por identidad.

Salida canónica, apta para pegar después de `**Snapshot:**`:

    head=<sha> tree=<sha> dirty=<si|no> exclude=<ninguno|a,b>

`tree=` es la identidad del código auditado; `head=` es el commit desde el que
se partió. Un commit que solo toca rutas excluidas mueve `head` y deja `tree=`
igual: el árbol auditado no cambió, y la pasada sigue siendo válida.

Salida: 0 si calcula la identidad; 2 si la ruta no está en un repositorio git.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

EMPTY_TREE = "4b825dc642cb6eb9a060e54bf8d69288fbee4904"
# Una carpeta de etapa dentro del panel: `07-agente-chat`, `01-export`.
STAGE_DIR_RE = re.compile(r"^\d{2,}-[a-z0-9][a-z0-9-]*$", re.I)


class SnapshotError(Exception):
    """No se puede calcular una identidad reproducible."""


def _run(root: Path, args: list[str], *, env: dict[str, str] | None = None, stdin: str | None = None):
    return subprocess.run(
        ["git", *args],
        cwd=root,
        capture_output=True,
        text=True,
        env=env,
        input=stdin,
        check=False,
    )


def repo_root(path: Path) -> Path:
    result = _run(path, ["rev-parse", "--show-toplevel"])
    if result.returncode != 0 or not result.stdout.strip():
        raise SnapshotError(f"{path} no está dentro de un repositorio git")
    return Path(result.stdout.strip()).resolve()


def _relative(root: Path, path: Path) -> str:
    """Ruta relativa a la raíz del repo; las relativas se interpretan desde ahí."""
    candidate = path if path.is_absolute() else root / path
    try:
        resolved = candidate.resolve()
    except OSError as error:
        raise SnapshotError(f"no se puede resolver {path}: {error}") from error
    try:
        return resolved.relative_to(root).as_posix()
    except ValueError as error:
        raise SnapshotError(f"{path} queda fuera del repositorio {root}") from error


def panel_index(path: Path) -> Path | None:
    """Índice del panel al que pertenece una etapa, si lo hay.

    El índice es el `README.md` de la carpeta que tiene, como hermanas,
    carpetas de etapa (`NN-nombre`). Se reconoce por la forma del nombre y por
    la vecindad, nunca por una ruta de un consumidor: el paquete no conoce sus
    etapas. Solo se mira la propia carpeta y su padre, para no confundir
    cualquier `README.md` de un antepasado ajeno con un índice de panel.
    """
    start = path.resolve()
    if not start.is_dir():
        return None
    for directory in (start, start.parent):
        candidate = directory / "README.md"
        if not candidate.is_file():
            continue
        siblings = [
            child
            for child in directory.iterdir()
            if child.is_dir() and STAGE_DIR_RE.match(child.name)
        ]
        if siblings:
            return candidate
    return None


def identity(path: Path, excludes: tuple[Path, ...] = ()) -> str:
    """Identidad canónica del árbol de trabajo en `path`.

    Con el árbol sucio la identidad es **el árbol de código**: el `tree=` y la
    lista de exclusiones. El `head=` describe el commit desde el que se
    empezó, no lo que se auditó: quien commitea la documentación de la etapa
    —que está excluida— o el índice del panel cambia `head` sin cambiar una
    línea del código auditado, y volver a auditar por eso pedía repetir una
    pasada sobre el mismo árbol (fue lo que pasó con las pasadas 7 y 8 de las
    etapas 07 y 08). Se graba igual para saber de dónde se partió, y el
    validador no lo compara.
    """
    if not path.exists():
        raise SnapshotError(f"{path} no existe")
    root = repo_root(path)
    # B-49: el índice del panel de una etapa se excluye con ella. El cierre
    # toma el snapshot desde la raíz del repo con `--exclude <etapa>`; tomar
    # el snapshot de la etapa directamente es el mismo caso. Se reconocen por
    # forma (`NN-nombre`): ni el paquete ni el snapshot conocen los nombres de
    # las etapas de un consumidor.
    stages = [
        absolute
        for absolute in (
            path.resolve() if path.is_dir() else path.resolve().parent,
            *(item if item.is_absolute() else root / item for item in excludes),
        )
        if absolute.is_dir() and STAGE_DIR_RE.match(absolute.name)
    ]
    panel_excludes = [
        index for index in (panel_index(stage) for stage in stages) if index is not None
    ]
    if panel_excludes:
        excludes = (*excludes, *panel_excludes)
    head = _run(root, ["rev-parse", "--verify", "HEAD"])
    head_sha = head.stdout.strip() if head.returncode == 0 else "sin-head"
    head_tree = None
    if head_sha != "sin-head":
        resolved = _run(root, ["rev-parse", "--verify", "HEAD^{tree}"])
        if resolved.returncode == 0:
            head_tree = resolved.stdout.strip()

    relative_excludes = sorted({_relative(root, item) for item in excludes})
    work = Path(tempfile.mkdtemp(prefix="yerro-snapshot-"))
    env = os.environ.copy()
    env["GIT_INDEX_FILE"] = str(work / "index")
    try:
        read_args = ["read-tree", head_sha] if head_sha != "sin-head" else ["read-tree", "--empty"]
        read = _run(root, read_args, env=env)
        if read.returncode != 0:
            raise SnapshotError(f"git read-tree falló: {read.stderr.strip()}")
        added = _run(root, ["add", "-A", "--", "."], env=env)
        if added.returncode != 0:
            raise SnapshotError(f"git add falló: {added.stderr.strip()}")
        if relative_excludes:
            listed = _run(root, ["ls-files", "--cached", "-z", "--", *relative_excludes], env=env)
            tracked = [item for item in listed.stdout.split("\0") if item]
            if tracked:
                removed = _run(
                    root,
                    ["update-index", "--force-remove", "-z", "--stdin"],
                    env=env,
                    stdin="\0".join(tracked) + "\0",
                )
                if removed.returncode != 0:
                    raise SnapshotError(f"git update-index falló: {removed.stderr.strip()}")
        written = _run(root, ["write-tree"], env=env)
        if written.returncode != 0:
            raise SnapshotError(f"git write-tree falló: {written.stderr.strip()}")
        tree = written.stdout.strip()
    finally:
        shutil.rmtree(work, ignore_errors=True)

    if head_tree is not None:
        dirty = tree != head_tree
    else:
        dirty = tree != EMPTY_TREE
    excluded = ",".join(relative_excludes) if relative_excludes else "ninguno"
    return f"head={head_sha} tree={tree} dirty={'si' if dirty else 'no'} exclude={excluded}"


def code_identity(value: str) -> str:
    """La parte de la identidad que describe el código auditado.

    `tree=`, `dirty=` y `exclude=`. `head=` no entra: es el commit desde el
    que se partió, y un commit que solo escribe rutas excluidas lo mueve sin
    tocar el árbol auditado.
    """
    parts = SNAPSHOT_VALUE_RE.match(value.strip())
    if not parts:
        return value.strip().lower()
    return " ".join(
        parts.group(name).lower() for name in ("tree", "dirty", "exclude")
    )


SNAPSHOT_VALUE_RE = re.compile(
    r"head=(?P<head>\S+)\s+tree=(?P<tree>\S+)\s+dirty=(?P<dirty>\S+)\s+exclude=(?P<exclude>\S+)"
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("path", type=Path, nargs="?", default=Path("."))
    parser.add_argument("--exclude", type=Path, action="append", default=[])
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    try:
        value = identity(args.path, tuple(args.exclude))
    except SnapshotError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2

    if args.json:
        fields = dict(item.split("=", 1) for item in value.split(" "))
        fields["snapshot"] = value
        print(json.dumps(fields, ensure_ascii=False, indent=2))
    else:
        print(value)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
