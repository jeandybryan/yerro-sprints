#!/usr/bin/env python3
"""Compara el diff real de git contra el alcance declarado por la etapa.

El alcance son todas las listas de la etapa: `TAREAS.md` y cada
`TAREAS-delta-NN.md`. Un delta cierra una brecha de la etapa auditada, y sus
tareas producen archivos igual que las principales.

Uso: diff_scope.py <etapa> --repo <repo> [--base REF] [--json]

B-27: un cambio de alcance se detecta en el diff, no en la confesión. Cada
tarea declara `**Archivos:**` con las rutas que produce; este script lee lo que
git dice que se tocó y compara. Un archivo tocado que ninguna tarea declara es
alcance nuevo, y necesita una decisión: reabrir la conciliación, no añadir la
ruta a la tarea después de haberla tocado (B-28).

La comparación es **mecánica** (B-29): el script dice qué rutas sobran y cuáles
faltan. No juzga si el cambio es correcto ni si merece cerrar; eso es riesgo y
cierre, y lo aprueba una persona.

La base por defecto es el commit que abrió la etapa, derivado de su historia:
medir contra `HEAD` dejaría ciego el gate en cuanto el agente commitea su
trabajo (B-44). Si la etapa no está commiteada se usa `HEAD`, que es lo único
que puede verse.

Qué cuenta como tocado:
- archivos modificados, añadidos, borrados o renombrados respecto de `--base`;
- archivos sin trackear, que git no vería en un `diff` normal.

Qué no cuenta, y por qué:
- el árbol de la propia feature (`CONCILIACION.md`, `TAREAS.md`, `AUDIT.md`…) y
  `.yerro/`: son la evidencia, no el código que se audita. Misma exclusión que
  `snapshot.py`, para que el diff y el snapshot hablen del mismo árbol.

Salida: 0 si el diff cabe en el alcance declarado; 1 si hay rutas no
declaradas (alcance nuevo, B-27); 2 si no se puede leer el diff.

Una ruta declarada que no cambió **no bloquea**: es una tarea incompleta, y
decidir si la tarea se cumplió es cierre, no alcance (B-29). Se informa como
advertencia para que el auditor lo vea.

Solo stdlib. No consume tokens.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from snapshot import SnapshotError, _run, repo_root # noqa: E402

# Una tarea empieza por `- [ ] T1` / `- [x] T1` / `- [ ] D1-T1`; su cuerpo
# llega hasta la tarea siguiente. Mismo patrón que `validate_stage.py`.
TASK_RE = re.compile(
    r"^\s*-\s*\[[ xX]\]\s*((?:D\d+-)?T\d+)\b(.*?)(?=^\s*-\s*\[[ xX]\]|\Z)",
    re.M | re.S,
)
# `**Archivos:** a, b` o `Archivos: a; b`; las rutas van entre acentos abiertos
# o desnudas, con comas o punto y coma como separador.
# `TAREAS-delta-01.md`: un delta es una lista de tareas, no solo un archivo
# narrativo. Su `**Archivos:**` cuenta tanto como el de `TAREAS.md`.
DELTA_NAME_RE = re.compile(r"^TAREAS-delta-(\d{2,})\.md$")
ARCHIVOS_RE = re.compile(r"^\s*\*{0,2}Archivos:?\*{0,2}\s*(.+?)\s*$", re.M | re.I)
BACKTICK_RE = re.compile(r"`([^`]+)`")

# Rutas que son evidencia, no código auditado.
EVIDENCE_NAMES = ("README.md", "CONCILIACION.md", "TAREAS.md", "AUDIT.md")
EVIDENCE_PREFIXES = (".yerro/",)


class ScopeError(Exception):
    """No se puede comparar el diff con el alcance declarado."""


def declared_files(tasks: str) -> dict[str, list[str]]:
    """Rutas declaradas por tarea, en el orden en que aparecen.

    Una tarea sin `**Archivos:**` devuelve lista vacía: es una etapa sin
    migrar, y el diff entero quedaría fuera de alcance. Se informa aparte para
    no confundir "no declara nada" con "declara otra cosa".
    """
    declared: dict[str, list[str]] = {}
    for task_id, body in TASK_RE.findall(tasks):
        match = ARCHIVOS_RE.search(body)
        if not match:
            declared[task_id] = []
            continue
        raw = match.group(1)
        quoted = BACKTICK_RE.findall(raw)
        # Sin acentos: rutas desnudas separadas por coma o punto y coma.
        items = quoted or [item for item in re.split(r"[,;]", raw) if item.strip()]
        declared[task_id] = [item.strip().strip("`").strip() for item in items if item.strip()]
    return declared



def stage_lists(stage: Path) -> list[Path]:
    """Las listas de tareas de la etapa: `TAREAS.md` y sus deltas, en orden.

    Un delta es la lista que el auditor escribió para cerrar la brecha: sus
    tareas producen archivos, y esos archivos están dentro del alcance aunque
    la lista principal no los nombre. Leer solo `TAREAS.md` dejaría que un
    delta no pudiera declarar ni un archivo nuevo, y lo que git vería como
    alcance nuevo nunca tendría declaración que lo cubriera.
    """
    principal = stage / "TAREAS.md"
    deltas = sorted(
        (path for path in stage.glob("TAREAS-delta-*.md") if DELTA_NAME_RE.match(path.name)),
        key=lambda path: int(DELTA_NAME_RE.match(path.name).group(1)),
    )
    return ([principal] if principal.exists() else []) + deltas


def declared_in(stage: Path) -> dict[str, list[str]]:
    """Rutas declaradas por la etapa entera, principal y deltas.

    La unión es por ID de tarea: los IDs de delta son `D0N-TN`, así que dos
    listas nunca chocan. Se fusionan en orden de aparición y la primera
    declaración de una ruta gana, como en `compare`.
    """
    declared: dict[str, list[str]] = {}
    for path in stage_lists(stage):
        for task_id, files in declared_files(path.read_text(encoding="utf-8")).items():
            declared.setdefault(task_id, files)
    return declared

def _normalize(path: str) -> str:
    """Ruta comparable: sin `./` inicial, separadores POSIX.

    `lstrip("./")` borraría caracteres, no el prefijo: `.yerro/x` quedaría
    `yerro/x` y dejaría de coincidir con `.yerro/`. Por eso se usa `removeprefix`.
    """
    value = path.replace("\\", "/")
    while value.startswith("./"):
        value = value[2:]
    return value


def _is_evidence(path: str) -> bool:
    name = path.rsplit("/", 1)[-1]
    return name in EVIDENCE_NAMES or path.startswith(EVIDENCE_PREFIXES)


def touched_files(root: Path, base: str, excludes: tuple[Path, ...]) -> list[str]:
    """Rutas que git ve cambiadas respecto de `base`, sin las de evidencia."""
    # `git diff` con `--no-index` no sirve aquí: se compara contra un ref.
    result = _run(
        root,
        ["diff", "--name-only", "--no-renames", "-z", base, "--", "."],
    )
    if result.returncode != 0:
        raise ScopeError(
            f"no se pudo calcular el diff contra {base!r}: {result.stderr.strip() or 'referencia inexistente'}"
        )
    changed = {item for item in result.stdout.split("\0") if item}

    # Lo que todavía no está en el índice: git no lo mostraría en el diff.
    untracked = _run(root, ["ls-files", "--others", "--exclude-standard", "-z", "--", "."])
    if untracked.returncode != 0:
        raise ScopeError(f"no se pudo listar lo no trackeado: {untracked.stderr.strip()}")
    changed.update(item for item in untracked.stdout.split("\0") if item)

    excluded = {_normalize(_relative_safe(root, item)) for item in excludes}
    return sorted(
        _normalize(item)
        for item in changed
        if not _is_evidence(_normalize(item))
        and not any(_normalize(item).startswith(prefix) for prefix in excluded if prefix)
    )


def _relative_safe(root: Path, path: Path) -> str:
    try:
        return (path if path.is_absolute() else root / path).resolve().relative_to(root).as_posix()
    except (OSError, ValueError):
        return str(path)


def stage_base(root: Path, stage: Path) -> str | None:
    """Commit en el que apareció la etapa; `None` si la etapa no está commiteada.

    La base no puede ser `HEAD`: quien commitea su trabajo deja el diff vacío y
    el gate aprobaría cualquier archivo. El commit que abrió la etapa se deriva
    de la historia (`--diff-filter=A` sobre el árbol de la etapa), así que no
    hace falta un campo nuevo ni migrar las etapas existentes.

    `git log` lista de más reciente a más antiguo: la última coincidencia es la
    primera vez que apareció la etapa.
    """
    relative = _relative_safe(root, stage)
    result = _run(root, ["log", "--diff-filter=A", "--format=%H", "--", relative])
    if result.returncode != 0:
        raise ScopeError(f"no se pudo leer la historia de {relative}: {result.stderr.strip()}")
    commits = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    return commits[-1] if commits else None


def scope_base(root: Path, stage: Path, explicit: str | None = None) -> str:
    """Base contra la que se mide el alcance.

    Orden: la que pase quien llama, el commit que abrió la etapa, y `HEAD`
    como último recurso si la etapa todavía no está commiteada. Es la única
    regla: `diff_scope.py` y el cierre la comparten.
    """
    if explicit is not None:
        return explicit
    return stage_base(root, stage) or "HEAD"


def compare(declared: dict[str, list[str]], touched: list[str]) -> dict[str, list[str]]:
    """Diferencias en las dos direcciones.

    - `undeclared`: se tocó y ninguna tarea lo declara (alcance nuevo, B-27).
    - `missing`: se declaró y no se tocó (la tarea no se hizo como decía).
    - `unmigrated`: tareas sin `**Archivos:**`; no se puede juzgar su parte.
    """
    known: dict[str, str] = {}
    for task_id, files in declared.items():
        for item in files:
            known.setdefault(_normalize(item), task_id)
    touched_set = {_normalize(item) for item in touched}
    undeclared = sorted(item for item in touched_set if item not in known)
    missing = sorted(item for item in known if item not in touched_set)
    unmigrated = sorted(task_id for task_id, files in declared.items() if not files)
    return {"undeclared": undeclared, "missing": missing, "unmigrated": unmigrated}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("stage", type=Path)
    parser.add_argument("--repo", type=Path, required=True, help="raíz del repositorio git")
    parser.add_argument(
        "--base",
        default=None,
        help=(
            "referencia contra la que comparar (por defecto, el commit que abrió la "
            "etapa; si la etapa no está commiteada, HEAD)"
        ),
    )
    parser.add_argument(
        "--exclude",
        type=Path,
        action="append",
        default=[],
        help="ruta excluida del diff; se añade el árbol de la etapa",
    )
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    stage = args.stage
    try:
        root = repo_root(args.repo.resolve())
    except SnapshotError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2

    # La etapa se interpreta desde la raíz del repo: un consumidor invoca desde
    # cualquier directorio y `features/01-export` debe resolver igual.
    if not stage.is_absolute():
        stage = root / stage
    stage = stage.resolve()

    tasks_path = stage / "TAREAS.md"
    if not tasks_path.exists():
        print(f"ERROR: no existe {tasks_path}", file=sys.stderr)
        return 2

    # El alcance de la etapa es el de todas sus listas: la principal y los
    # deltas que la auditoría escribió para cerrar una brecha. La unión es
    # por ID de tarea (`D0N-TN` no choca con `TN`) y la primera
    # declaración de una ruta gana, como en `compare`.
    declared = declared_in(stage)
    if not declared_files(tasks_path.read_text(encoding="utf-8")):
        print("ERROR: TAREAS.md no contiene tareas", file=sys.stderr)
        return 2

    try:
        # La base se elige una sola vez, aquí: el cierre llama al mismo contrato
        # y no puede inventarse otra.
        base = scope_base(root, stage, args.base)
        touched = touched_files(root, base, (stage, *(root / item if not item.is_absolute() else item for item in args.exclude)))
    except ScopeError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2

    result = compare(declared, touched)
    if args.json:
        print(json.dumps({**result, "touched": touched, "base": base}, ensure_ascii=False, indent=2))
    else:
        print(f"Base: {base}")
        for path in result["undeclared"]:
            print(f"ERROR: {path} cambió y ninguna tarea lo declara (alcance nuevo, B-27)")
        for path in result["missing"]:
            print(f"ADVERTENCIA: {path} se declara pero no cambió")
        for task_id in result["unmigrated"]:
            print(f"ADVERTENCIA: {task_id} no declara **Archivos:** (etapa sin migrar)")
        if not result["undeclared"] and not result["missing"]:
            print(f"OK: {len(touched)} archivo(s) tocados, todos dentro del alcance declarado")

    # Solo el alcance nuevo bloquea. Una ruta declarada que no cambió es una
    # tarea incompleta, no un cambio de alcance: avisarla es todo lo que un
    # script puede decir sin juzgar el cierre (B-29).
    return 1 if result["undeclared"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
