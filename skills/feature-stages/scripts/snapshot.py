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

Salida canónica, apta para pegar después de `**Snapshot:**`:

    head=<sha> tree=<sha> dirty=<si|no> exclude=<ninguno|a,b>

Salida: 0 si calcula la identidad; 2 si la ruta no está en un repositorio git.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

EMPTY_TREE = "4b825dc642cb6eb9a060e54bf8d69288fbee4904"


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


def identity(path: Path, excludes: tuple[Path, ...] = ()) -> str:
    """Identidad canónica del árbol de trabajo en `path`."""
    if not path.exists():
        raise SnapshotError(f"{path} no existe")
    root = repo_root(path)
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
