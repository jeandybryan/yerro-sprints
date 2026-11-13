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
  `snapshot.py`, para que el diff y el snapshot hablen del mismo árbol;
- los secretos locales (`.env`, `.env.demo.local`, `*.local`): nunca se
  versionan y declararlos en una tarea empujaría a escribir la credencial en
  el árbol de la etapa (B-46). Un `.env.example` sí cuenta: es contrato;
- el bytecode de Python (`__pycache__/`, `*.pyc`, `*.pyo`): lo escribe el
  intérprete al importar estos scripts. Contarlo pediría declararlo en una
  tarea y, en el snapshot, cambiaría el `tree=` de la pasada que acaba de
  correr el validador. Misma exclusión que `snapshot.py`, por forma.

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
from snapshot import SnapshotError, _is_bytecode, _run, repo_root, STAGE_DIR_RE # noqa: E402

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


def _is_local_secret(path: str) -> bool:
    """Credencial local sin versionar: no es código que se audite (B-46).

    Un `.env` (con cualquier sufijo) o un `*.local` guarda credenciales que la
    persona deja fuera de git. Pedirle a una tarea que lo declare empujaría a
    escribir la credencial en el árbol de la etapa. Un `.env.example` sí es
    contrato documentado y se declara.
    """
    name = path.rsplit("/", 1)[-1]
    if name == ".env.example" or name.endswith(".example"):
        return False
    return name == ".env" or name.startswith(".env.") or name.endswith(".local")


def _is_evidence(path: str) -> bool:
    name = path.rsplit("/", 1)[-1]
    return (
        name in EVIDENCE_NAMES
        or path.startswith(EVIDENCE_PREFIXES)
        or _is_local_secret(path)
    )


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
    kept: list[str] = []
    for item in changed:
        normalized = _normalize(item)
        if _is_evidence(normalized) or _is_bytecode(normalized):
            continue
        if any(normalized.startswith(prefix) for prefix in excluded if prefix):
            continue
        kept.append(normalized)
    return sorted(kept)


def _relative_safe(root: Path, path: Path) -> str:
    try:
        return (path if path.is_absolute() else root / path).resolve().relative_to(root).as_posix()
    except (OSError, ValueError):
        return str(path)


def stage_base(root: Path, stage: Path) -> str | None:
    """Commit en el que empezó la etapa; `None` si la etapa no está commiteada.

    La base no puede ser `HEAD`: quien commitea su trabajo deja el diff vacío y
    el gate aprobaría cualquier archivo. El commit de apertura se deriva de la
    historia, así que no hace falta un campo nuevo ni migrar las etapas
    existentes.

    B-45: la apertura es el commit que añade la **lista de tareas**
    (`TAREAS.md`), no la primera aparición de cualquier archivo de la carpeta.
    Una etapa puede dejar su `CONCILIACION.md` en un commit de hace semanas,
    junto a otras etapas, y empezar a implementarse mucho después: medir desde
    la conciliación mete en el diff todo lo que esas otras etapas commitearon
    entre medias, y el alcance se vuelve un falso positivo de cientos de
    archivos. La etapa empieza cuando nace su `TAREAS.md`, que es la lista que
    `declared_in()` necesita para juzgarla.

    Sin `TAREAS.md` se cae a la primera aparición de la carpeta, que es lo único
    que se puede atribuir a la etapa; sin nada, `None`.

    `git log` lista de más reciente a más antiguo: la última coincidencia es la
    primera vez que apareció el archivo.
    """
    relative = _relative_safe(root, stage)
    for candidate in (f"{relative}/TAREAS.md", relative):
        result = _run(root, ["log", "--diff-filter=A", "--format=%H", "--", candidate])
        if result.returncode != 0:
            raise ScopeError(
                f"no se pudo leer la historia de {candidate}: {result.stderr.strip()}"
            )
        commits = [line.strip() for line in result.stdout.splitlines() if line.strip()]
        if commits:
            return commits[-1]
    return None


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


def commit_touches(root: Path, base: str) -> dict[str, dict[str, object]]:
    """Commits entre `base` y `HEAD`, con sus rutas y su asunto.

    Un solo `git log` para todo el rango: pedir la historia ruta por ruta son
    cientos de procesos y el gate se vuelve inusable en una etapa grande.
    """
    result = _run(
        root,
        ["log", "--format=%x1e%H%x1f%s", "--name-only", "--no-renames", f"{base}..HEAD"],
    )
    if result.returncode != 0:
        raise ScopeError(
            f"no se pudo leer la historia desde {base!r}: {result.stderr.strip()}"
        )
    commits: dict[str, dict[str, object]] = {}
    for block in result.stdout.split("\x1e"):
        block = block.strip("\n")
        if not block:
            continue
        header, _, rest = block.partition("\n")
        sha, _, subject = header.partition("\x1f")
        if not sha:
            continue
        commits[sha] = {
            "subject": subject.strip(),
            "files": {line.strip() for line in rest.splitlines() if line.strip()},
        }
    return commits


def _stage_prefixes(root: Path, stage: Path) -> tuple[str, list[str]]:
    """Prefijo de la etapa auditada y de **todas** las demás etapas del repo.

    Las etapas se reconocen por forma (`NN-nombre`) y por tener un artefacto
    de etapa (`CONCILIACION.md`, `TAREAS.md` o `AUDIT.md`), no por una ruta
    de un consumidor ni por la vecindad de un panel: un repositorio puede
    repartir sus etapas en varias carpetas, y mirar solo las hermanas del
    mismo panel dejaba como propias las rutas de todas las demás.
    """
    mine = _relative_safe(root, stage).rstrip("/") + "/"
    others: list[str] = []
    listed = _run(
        root,
        ["ls-files", "-z", "--", "*CONCILIACION.md", "*TAREAS.md", "*AUDIT.md"],
    )
    if listed.returncode == 0:
        directories = {
            str(Path(item).parent)
            for item in listed.stdout.split("\0")
            if item
        }
        for directory in sorted(directories):
            parts = Path(directory).parts
            if not parts or not STAGE_DIR_RE.match(parts[-1]):
                continue
            prefix = directory.rstrip("/") + "/"
            if prefix != mine:
                others.append(prefix)
    return mine, others


def attribute(root: Path, base: str, stage: Path, paths: list[str]) -> dict[str, dict[str, str]]:
    """B-50: qué rutas sin declarar vienen de commits de **otra** etapa.

    Un commit es ajeno cuando toca la carpeta de otra etapa del repositorio y
    no toca la auditada. Ese archivo lo produjo otra etapa y pedirle a esta
    que lo declare sería pedirle que se apropie de trabajo ajeno: en un
    repositorio con ramas por etapa, el cruce marca cientos de rutas que
    ningún agente de esta etapa escribió.

    Un commit que no toca ninguna etapa es ambiguo y se cuenta como propio:
    puede ser la implementación de esta etapa. Lo mismo una ruta sin commit
    (el árbol de trabajo): eso es lo que el agente acaba de escribir. El gate
    no se rebaja; se atribuye.
    """
    try:
        commits = commit_touches(root, base)
    except ScopeError:
        return {}
    mine, others = _stage_prefixes(root, stage)

    def touches(files: set[str], prefix: str) -> bool:
        return any(item.startswith(prefix) for item in files)

    own_commits = {
        sha for sha, data in commits.items() if touches(data["files"], mine)
    }
    foreign_commits = {
        sha
        for sha, data in commits.items()
        if any(touches(data["files"], prefix) for prefix in others)
    }

    foreign: dict[str, dict[str, str]] = {}
    for path in paths:
        # Dentro del árbol de otra etapa: es de esa etapa aunque el commit que
        # lo tocó sea mixto. Su código, sus deltas y sus notas no son alcance
        # de esta, igual que el árbol de esta no lo es de la otra.
        if any(path.startswith(prefix) for prefix in others):
            owners = [sha for sha, data in commits.items() if path in data["files"]]
            sha = owners[0] if owners else ""
            foreign[path] = {
                "commit": sha[:8] or "sin commit",
                "subject": str(commits[sha]["subject"]) if sha else "árbol de otra etapa",
            }
            continue
        owners = [
            sha for sha, data in commits.items() if path in data["files"]
        ]
        if not owners:
            continue
        if all(sha in foreign_commits and sha not in own_commits for sha in owners):
            sha = owners[0]
            foreign[path] = {
                "commit": sha[:8],
                "subject": str(commits[sha]["subject"]),
            }
    return foreign


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
    try:
        foreign = attribute(root, base, stage, result["undeclared"])
    except ScopeError as error:
        foreign = {}
        print(f"ADVERTENCIA: no se pudo atribuir el alcance nuevo: {error}", file=sys.stderr)
    own = [path for path in result["undeclared"] if path not in foreign]
    if args.json:
        print(json.dumps({**result, "undeclared": own, "foreign": foreign, "touched": touched, "base": base}, ensure_ascii=False, indent=2))
    else:
        print(f"Base: {base}")
        for path in own:
            print(f"ERROR: {path} cambió y ninguna tarea lo declara (alcance nuevo, B-27)")
        for path, source in foreign.items():
            print(
                f"ADVERTENCIA: {path} lo cambió {source['commit']} «{source['subject']}», "
                "otra etapa; no es alcance de esta"
            )
        for path in result["missing"]:
            print(f"ADVERTENCIA: {path} se declara pero no cambió")
        for task_id in result["unmigrated"]:
            print(f"ADVERTENCIA: {task_id} no declara **Archivos:** (etapa sin migrar)")
        if not own and not result["missing"]:
            print(f"OK: {len(touched)} archivo(s) tocados, todos dentro del alcance declarado")

    # Solo el alcance propio bloquea. Una ruta declarada que no cambió es una
    # tarea incompleta, no un cambio de alcance: avisarla es todo lo que un
    # script puede decir sin juzgar el cierre (B-29). Una ruta atribuida a otra
    # etapa se informa con su commit, no se calla.
    return 1 if own else 0


if __name__ == "__main__":
    raise SystemExit(main())
