#!/usr/bin/env python3
"""Prepara la corrida de nivel 4 de `EVALUATION.md`.

Uso:
    prepare.py --out <dir> [--only S52,S55] [--check] [--force]

Para cada caso de `cases.json` materializa un snapshot aislado:

    <out>/<ID>/snapshot/        repositorio git con las seis skills y la fixture
    <out>/<ID>/PROMPT.md        la petición que recibe el agente
    <out>/<ID>/_rubrica/        EXPECTATIONS.md, META.json, RESULTADO.json
    <out>/<ID>/_rubrica/esperado.json   valores que el `--check` verifica

La rúbrica vive **fuera** del snapshot: el agente no la ve antes de responder.
`--check` comprueba que cada snapshot arranca en el estado que el caso necesita
(por ejemplo, que `validate_stage.py` falla por el gate que el caso mide). No
consume tokens y no ejecuta ningún agente.

Solo stdlib y el binario `git`.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
FEATURE = HERE.parents[1]          # skills/feature-stages
SKILLS_ROOT = HERE.parents[2]      # skills
REPO = HERE.parents[3]             # raíz del paquete
FIXTURES = FEATURE / "evals" / "fixtures"
SCRIPTS = FEATURE / "scripts"

SKILL_NAMES = (
    "identify-feature-stages",
    "feature-stages",
    "conciliate-stage",
    "generate-stage-tasks",
    "implement-stage",
    "audit-stage",
)

CASES = json.loads((HERE / "cases.json").read_text(encoding="utf-8"))["cases"]


# --- utilidades -----------------------------------------------------------

def run(cmd: list[str], cwd: Path, check: bool = False) -> subprocess.CompletedProcess[str]:
    done = subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True)
    if check and done.returncode != 0:
        raise RuntimeError(f"falló {' '.join(cmd)} en {cwd}:\n{done.stdout}{done.stderr}")
    return done


def git(repo: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return run(["git", "-C", str(repo), *args], repo, check=check)


def write(repo: Path, rel: str, text: str) -> Path:
    path = repo / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def commit(repo: Path, message: str) -> str:
    git(repo, "add", "-A")
    git(repo, "commit", "-qm", message)
    return git(repo, "rev-parse", "HEAD").stdout.strip()


def init_repo(repo: Path) -> None:
    repo.mkdir(parents=True, exist_ok=True)
    git(repo, "init", "-q")
    git(repo, "config", "user.email", "fixture@example.com")
    git(repo, "config", "user.name", "Fixture")
    git(repo, "config", "commit.gpgsign", "false")
    write(repo, "src.txt", "uno\n")
    commit(repo, "inicial")


def copy_skills(snapshot: Path) -> None:
    """Copia las seis skills sin `evals/`: el agente necesita el contrato y los
    scripts, no el catálogo de fixtures."""
    for name in SKILL_NAMES:
        shutil.copytree(
            SKILLS_ROOT / name,
            snapshot / "skills" / name,
            ignore=shutil.ignore_patterns("evals", "__pycache__"),
        )


def script(snapshot: Path, name: str, *args: str) -> subprocess.CompletedProcess[str]:
    return run(
        [sys.executable, str(snapshot / "skills" / "feature-stages" / "scripts" / name), *args],
        snapshot,
    )


def snapshot_of(snapshot: Path, stage: str, *extra: str) -> str:
    done = script(snapshot, "snapshot.py", stage, *extra)
    if done.returncode != 0:
        raise RuntimeError(f"snapshot.py falló en {stage}: {done.stderr}")
    return done.stdout.strip()


def tree_of(identity: str) -> str:
    match = re.search(r"tree=([0-9a-f]+)", identity)
    if not match:
        raise RuntimeError(f"identidad sin tree=: {identity}")
    return match.group(1)


def code_id(identity: str) -> str:
    """La parte que el validador compara: `tree=` y `dirty=`, sin `head=`."""
    match = re.search(r"tree=(\S+)\s+dirty=(\S+)", identity)
    if not match:
        raise RuntimeError(f"identidad sin tree=/dirty=: {identity}")
    return f"tree={match.group(1)} dirty={match.group(2)}"


def valid_stage(snapshot: Path, rel: str, snapshot_line: str | None = None) -> None:
    """Copia la fixture `valid-stage` y, si se pide, fija su `**Snapshot:**`."""
    for name in ("CONCILIACION.md", "TAREAS.md", "AUDIT.md"):
        text = (FIXTURES / "valid-stage" / name).read_text(encoding="utf-8")
        if name == "AUDIT.md" and snapshot_line:
            text = re.sub(
                r"^\*\*Snapshot:\*\*.*$",
                f"**Snapshot:** {snapshot_line}",
                text,
                flags=re.M,
            )
        write(snapshot, f"{rel}/{name}", text)


def baseline_of(snapshot: Path, stage: str) -> str:
    """El `base=` que pide el cierre: sha256 de la conciliación sin `**Estado:**`."""
    script = (
        "import sys; from pathlib import Path\n"
        "sys.path.insert(0, sys.argv[1])\n"
        "from approvals import baseline_of\n"
        "print(baseline_of(Path(sys.argv[2])))"
    )
    result = run(
        [
            sys.executable,
            "-c",
            script,
            str(snapshot / "skills" / "feature-stages" / "scripts"),
            stage,
        ],
        cwd=snapshot,
    )
    line = result.stdout.strip().splitlines()[-1] if result.stdout.strip() else ""
    if result.returncode != 0 or len(line) != 64:
        raise RuntimeError(f"no se pudo calcular el baseline de {stage}: {result.stderr}")
    return line

def approve(snapshot: Path, stage: str, scope: str = "") -> None:
    """Firma como lo haría la persona: el plan siempre, el árbol si se pide.

    S66/B2: el cierre exige `base=` en todas las etapas; en riesgo bajo esa
    firma basta. `scope` añade `alcance:` a la misma entrada, que es lo que
    pide riesgo medio o alto.
    """
    entry = (
        f"- etapa: {stage}\n"
        " aprobado-por: Fixture\n"
        " fecha: 2026-11-06\n"
        f" base: {baseline_of(snapshot, f'features/{stage}')}\n"
    )
    if scope:
        entry += f" alcance: {scope}\n"
    write(snapshot, ".yerro/approvals.yml", entry)


CONCILIACION = """# Etapa {name} — fixture

**Estado:** cerrada
**Presupuesto no funcional:**
- Latencia: no aplica (la etapa no expone una ruta con presupuesto de latencia)
- Memoria: no aplica (no hay proceso residente en la etapa)
- Tamaño/artefacto: no aplica (la etapa no entrega un artefacto con tamaño propio)
- Dependencias nuevas: 0
- Rendimiento de operación crítica: no aplica (no hay operación crítica en la etapa)

## Aclaraciones

- **S-01 — Decisión de baseline:** se acepta el resultado observable del criterio y su verificación focalizada.
**Suites de referencia:** `pytest`
**Riesgo:** medio

## Criterios de aceptación

- **CA-01 — [condición de salida | invariante acumulado]:** estímulo → resultado observable; no falla; evidencia `conductual`. Origen: S-01
"""

TAREAS = """# Tareas — {name}

**Principal:** sí

## Listado

- [x] T1 — implementar salida (CA-01)
  **Archivos:** `{source}`
  Test-first: sí; Test: pytest -q test_focal.py;
  Verificar: nivel `conductual`; ejecutar test focalizado; oráculo observable: exit 0 y assertion verde.
"""


# --- constructores --------------------------------------------------------

def build_s52(snapshot: Path) -> dict:
    init_repo(snapshot)
    write(snapshot, "features/07-x/CONCILIACION.md", CONCILIACION.format(name="07-x"))
    write(snapshot, "features/08-y/CONCILIACION.md", CONCILIACION.format(name="08-y"))
    old_base = commit(snapshot, "corte: etapas 07 y 08")
    # La etapa 08 trabaja entre el corte y la apertura de la 07: con la base
    # vieja (primera aparición de la carpeta) todo esto cae dentro del diff.
    for index in range(20):
        write(snapshot, f"features/08-y/src/otra_{index:02d}.py", f"otra = {index}\n")
    commit(snapshot, "etapa 08: implementa")
    write(snapshot, "features/07-x/TAREAS.md", TAREAS.format(name="07-x", source="src/07.py"))
    base = commit(snapshot, "etapa 07: abre la lista")
    write(snapshot, "src/07.py", "salida = 1\n")
    commit(snapshot, "etapa 07: implementa")
    return {"base": base, "old_base": old_base}


def build_s53(snapshot: Path) -> dict:
    init_repo(snapshot)
    write(snapshot, "features/01-x/CONCILIACION.md", CONCILIACION.format(name="01-x"))
    write(snapshot, "features/01-x/TAREAS.md", TAREAS.format(name="01-x", source="src/a.py"))
    commit(snapshot, "abre etapa 01")
    write(snapshot, "src/a.py", "a = 1\n")
    commit(snapshot, "etapa 01: implementa")
    write(snapshot, "console/.env.demo.local", "TOKEN=secreto\n")
    return {}


def build_s54(snapshot: Path) -> dict:
    init_repo(snapshot)
    write(snapshot, "features/01-x/CONCILIACION.md", CONCILIACION.format(name="01-x"))
    write(snapshot, "features/01-x/TAREAS.md", TAREAS.format(name="01-x", source="src/a.py"))
    write(snapshot, "src/a.py", "a = 1\n")
    commit(snapshot, "abre etapa 01")
    row = script(
        snapshot,
        "evidence.py",
        "run",
        "--label",
        "E-01",
        "--",
        "sh",
        "-c",
        "printf 'hola\n' | wc -l",
    )
    if row.returncode != 0:
        raise RuntimeError(f"evidence.py run falló: {row.stderr}")
    # La fila que escribe `run` trae el `|` escapado. El caso mide el ledger
    # escrito a mano por el agente, donde un `|` crudo parte la fila: se
    # des-escapa solo la fila E-01, que es la que el contrato debe rechazar.
    # Si no hubiera nada que partir, el caso no mediría y la preparación
    # falla en vez de dejar pasar un verde vacío.
    raw = r"\|"
    broken = row.stdout.strip().replace(raw, "|")
    if broken == row.stdout.strip():
        raise RuntimeError("la fila E-01 no trae un `|` que el caso pueda partir")
    audit = (
        "# Auditoría — etapa 01\n\n"
        "## Pasada 1\n\n"
        "**Snapshot:** head=0000000000000000000000000000000000000000 "
        "tree=1111111111111111111111111111111111111111 dirty=no exclude=ninguno\n"
        "**Riesgo auditado:** medio\n"
        "**Trazabilidad:** CA-01 → T1 → test_focal.py → E-01\n\n"
        "| Criterio | Afirmaciones auditadas | Tareas | Resultado | Evidencia reproducible | Limitaciones |\n"
        "|----------|-------------------------|--------|-----------|-------------------------|--------------|\n"
        "| CA-01 | salida y negativo | T1 | cumple | E-01 | ninguna |\n\n"
        "### Ledger de evidencia\n\n"
        "| ID | CA | Procedimiento/comando | Sensibilidad | Esperado | Observado/exit | Entorno y timestamp | Artefacto/log | Limitación |\n"
        "|----|----|------------------------|--------------|----------|----------------|---------------------|---------------|------------|\n"
        f"{broken}\n\n"
        "**Veredicto:** coincide\n"
        "**Veredicto (calidad):** aceptable\n"
    )
    write(snapshot, "features/01-x/AUDIT.md", audit)
    commit(snapshot, "etapa 01: audita")
    return {}


def build_s55(snapshot: Path) -> dict:
    init_repo(snapshot)
    shutil.copytree(FIXTURES / "tarea-sin-archivos", snapshot / "features" / "01-x")
    commit(snapshot, "etapa 01 sin Archivos")
    return {}


def build_s56(snapshot: Path) -> dict:
    init_repo(snapshot)
    write(
        snapshot,
        "features/README.md",
        "# Panel\n\n| # | Carpeta | Estado |\n|---|---------|--------|\n"
        "| 01 | [01-x](01-x/CONCILIACION.md) | cerrada |\n",
    )
    valid_stage(snapshot, "features/01-x")
    write(snapshot, "src/salida.py", "salida = 1\n")
    write(snapshot, "tests/test_salida.py", "def test_salida():\n    assert True\n")
    commit(snapshot, "etapa 01 auditada")
    before = snapshot_of(snapshot, "features/01-x")
    write(
        snapshot,
        "features/README.md",
        "# Panel\n\n| # | Carpeta | Estado |\n|---|---------|--------|\n"
        "| 01 | [01-x](01-x/CONCILIACION.md) | cerrada (índice actualizado) |\n",
    )
    return {"snapshot": before}


def build_s57(snapshot: Path) -> dict:
    init_repo(snapshot)
    write(snapshot, "features/07-x/CONCILIACION.md", CONCILIACION.format(name="07-x"))
    write(snapshot, "features/07-x/TAREAS.md", TAREAS.format(name="07-x", source="src/07.py"))
    write(snapshot, "features/08-y/CONCILIACION.md", CONCILIACION.format(name="08-y"))
    commit(snapshot, "abre etapa 07")
    write(snapshot, "features/08-y/src/otra.py", "otra = 1\n")
    commit(snapshot, "etapa 08: implementa")
    write(snapshot, "src/07.py", "salida = 1\n")
    commit(snapshot, "etapa 07: implementa")
    return {}


def build_s58(snapshot: Path) -> dict:
    init_repo(snapshot)
    shutil.copytree(FIXTURES / "reapertura-auditoria", snapshot / "features")
    commit(snapshot, "etapa reabierta")
    return {}


def build_s59(snapshot: Path) -> dict:
    init_repo(snapshot)
    shutil.copytree(FIXTURES / "transiciones", snapshot / "features")
    commit(snapshot, "panel de transiciones")
    return {}


def build_s66(snapshot: Path) -> dict:
    init_repo(snapshot)
    valid_stage(snapshot, "features/02-x")
    write(snapshot, "src/salida.py", "salida = 1\n")
    write(snapshot, "tests/test_salida.py", "def test_salida():\n assert True\n")
    commit(snapshot, "etapa 02 implementada")
    before = snapshot_of(snapshot, "features/02-x", "--exclude", ".yerro/approvals.yml")
    valid_stage(snapshot, "features/02-x", before)
    tasks = snapshot / "features/02-x" / "TAREAS.md"
    tasks.write_text(
        tasks.read_text(encoding="utf-8").replace("- [ ] T1", "- [x] T1"),
        encoding="utf-8",
    )
    # `valid_stage` copia la plantilla de `medio`, y es la última escritura
    # del documento: el riesgo se baja después de grabar la pasada.
    conciliation = snapshot / "features/02-x" / "CONCILIACION.md"
    conciliation.write_text(
        re.sub(
            r"^\*\*Riesgo:\*\*\s*\w+$",
            "**Riesgo:** bajo",
            conciliation.read_text(encoding="utf-8"),
            flags=re.M,
        ),
        encoding="utf-8",
    )
    # Se comprueba antes de la pasada final: si `**Riesgo:**` vuelve a `medio`,
    # el snapshot no arranca en el estado que S66 mide y el caso no demuestra
    # nada (el control sigue fallando, así que el arnés no lo notaría).
    if "**Riesgo:** bajo" not in conciliation.read_text(encoding="utf-8"):
        raise RuntimeError("S66: no se pudo bajar el riesgo de la etapa 02-x a bajo")
    commit(snapshot, "etapa 02 auditada")
    approve(snapshot, "02-x")
    commit(snapshot, "firma de plan")
    return {"snapshot": before}

def build_s60(snapshot: Path) -> dict:
    init_repo(snapshot)
    valid_stage(snapshot, "features/01-x")
    write(snapshot, "src/salida.py", "salida = 1\n")
    write(snapshot, "tests/test_salida.py", "def test_salida():\n    assert True\n")
    commit(snapshot, "etapa 01 implementada")
    before = snapshot_of(snapshot, "features/01-x", "--exclude", ".yerro/approvals.yml")
    valid_stage(snapshot, "features/01-x", before)
    commit(snapshot, "etapa 01 auditada")
    approve(snapshot, "01-x", f"tree={tree_of(before)}")
    commit(snapshot, "firma")
    write(snapshot, "features/01-x/AUDIT.md", (snapshot / "features/01-x/AUDIT.md").read_text() + "\nNota de cierre.\n")
    commit(snapshot, "documento de la etapa")
    return {"snapshot": before}


def build_s61(snapshot: Path) -> dict:
    init_repo(snapshot)
    write(
        snapshot,
        "features/README.md",
        "# Panel\n\n| # | Carpeta | Estado |\n|---|---------|--------|\n"
        "| 01 | [01-x](01-x/CONCILIACION.md) | cerrada |\n"
        "| 02 | [02-y](02-y/CONCILIACION.md) | cerrada |\n",
    )
    valid_stage(snapshot, "features/01-x")
    valid_stage(snapshot, "features/02-y")
    write(snapshot, "src/salida.py", "salida = 1\n")
    write(snapshot, "tests/test_salida.py", "def test_salida():\n    assert True\n")
    commit(snapshot, "panel con dos etapas")
    before = snapshot_of(snapshot, "features/01-x")
    valid_stage(snapshot, "features/01-x", before)
    commit(snapshot, "audita 01")
    write(snapshot, "features/02-y/AUDIT.md", (snapshot / "features/02-y/AUDIT.md").read_text() + "\nNota de la 02.\n")
    commit(snapshot, "audita 02")
    return {"snapshot": before}


def build_s62(snapshot: Path) -> dict:
    init_repo(snapshot)
    write(
        snapshot,
        "features/README.md",
        "# Panel\n\n| # | Carpeta | Estado |\n|---|---------|--------|\n"
        "| 07 | [07-x](07-x/CONCILIACION.md) | cerrada |\n",
    )
    valid_stage(snapshot, "features/07-x")
    write(snapshot, "src/salida.py", "salida = 1\n")
    write(snapshot, "tests/test_salida.py", "def test_salida():\n    assert True\n")
    commit(snapshot, "etapa 07 implementada")
    before = snapshot_of(snapshot, "features/07-x", "--exclude", ".yerro/approvals.yml")
    valid_stage(snapshot, "features/07-x", before)
    commit(snapshot, "etapa 07 auditada")
    approve(snapshot, "07-x", f"tree={tree_of(before)}")
    commit(snapshot, "firma por árbol")
    write(snapshot, "features/10-z/CONCILIACION.md", CONCILIACION.format(name="10-z"))
    commit(snapshot, "alta de la etapa 10")
    return {"snapshot": before}


def build_s63(snapshot: Path) -> dict:
    init_repo(snapshot)
    write(
        snapshot,
        "features/README.md",
        "# Panel\n\n| # | Carpeta | Estado |\n|---|---------|--------|\n"
        "| 08 | [08-x](08-x/CONCILIACION.md) | cerrada |\n",
    )
    valid_stage(snapshot, "features/08-x")
    write(snapshot, "src/salida.py", "salida = 1\n")
    write(snapshot, "tests/test_salida.py", "def test_salida():\n    assert True\n")
    commit(snapshot, "etapa 08 implementada")
    before = snapshot_of(snapshot, "features/08-x", "--exclude", ".yerro/approvals.yml")
    valid_stage(snapshot, "features/08-x", before)
    commit(snapshot, "etapa 08 auditada")
    approve(snapshot, "08-x", f"tree={tree_of(before)[:8]}")
    commit(snapshot, "firma corta")
    return {"snapshot": before}


BUILDERS = {
    "s52": build_s52,
    "s53": build_s53,
    "s54": build_s54,
    "s55": build_s55,
    "s56": build_s56,
    "s57": build_s57,
    "s58": build_s58,
    "s59": build_s59,
    "s60": build_s60,
    "s61": build_s61,
    "s62": build_s62,
    "s63": build_s63,
    "s66": build_s66,
}


# --- comprobaciones de estado inicial ------------------------------------

def check_s52(snapshot: Path, esperado: dict) -> list[str]:
    done = script(snapshot, "diff_scope.py", "features/07-x", "--repo", ".", "--json")
    if done.returncode != 0:
        return [f"diff_scope.py salió {done.returncode}: {done.stderr.strip()}"]
    data = json.loads(done.stdout)
    problems = []
    if data.get("base") != esperado["base"]:
        problems.append(f"la base es {data.get('base')}, se esperaba {esperado['base']}")
    if data.get("undeclared"):
        problems.append(f"hay alcance propio sin declarar: {data['undeclared']}")
    # La fixture reproduce el fallo viejo: con la base anterior, las rutas de
    # la etapa 08 entran en el diff. Si no entran, el caso no mide nada.
    old = script(
        snapshot, "diff_scope.py", "features/07-x", "--repo", ".",
        "--base", esperado["old_base"], "--json",
    )
    if old.returncode != 0:
        problems.append(f"con la base vieja el cruce falló: {old.stderr.strip()}")
    else:
        old_data = json.loads(old.stdout)
        if not old_data.get("foreign"):
            problems.append("con la base vieja las rutas de la etapa 08 no entran en el diff")
    return problems


def check_s53(snapshot: Path, esperado: dict) -> list[str]:
    done = script(snapshot, "diff_scope.py", "features/01-x", "--repo", ".")
    problems = []
    if done.returncode != 0:
        problems.append(f"el .env local bloquea: {done.stdout.strip()}{done.stderr.strip()}")
    with tempfile.TemporaryDirectory(prefix="n4-s53-") as raw:
        copy = Path(raw) / "repo"
        shutil.copytree(snapshot, copy)
        write(copy, "console/.env.example", "TOKEN=\n")
        other = script(copy, "diff_scope.py", "features/01-x", "--repo", ".")
        if other.returncode == 0:
            problems.append("un .env.example sin declarar no bloquea")
    return problems


def check_s54(snapshot: Path, esperado: dict) -> list[str]:
    done = script(snapshot, "evidence.py", "verify", "features/01-x/AUDIT.md")
    problems = []
    # El caso mide el rechazo: si `verify` acepta la fila rota, el agente
    # nunca ve el fallo y el caso se ejecutaría sin poder fallar.
    if done.returncode == 0:
        problems.append(f"verify acepta la fila partida: {done.stdout.strip()}")
    if "la fila se partió" not in (done.stdout + done.stderr):
        problems.append(
            f"verify no nombra la fila partida: {done.stdout.strip()}{done.stderr.strip()}"
        )
    return problems


def check_s55(snapshot: Path, esperado: dict) -> list[str]:
    done = script(snapshot, "validate_stage.py", "features/01-x")
    problems = []
    if done.returncode == 0:
        problems.append("validate_stage.py acepta una tarea sin **Archivos:**")
    if "no declara" not in (done.stdout + done.stderr):
        problems.append(f"el error no nombra el campo ausente: {done.stdout}{done.stderr}")
    return problems


def check_s56(snapshot: Path, esperado: dict) -> list[str]:
    after = snapshot_of(snapshot, "features/01-x")
    problems = []
    if after != esperado["snapshot"]:
        problems.append(f"editar el índice cambió la identidad: {after}")
    with tempfile.TemporaryDirectory(prefix="n4-s56-") as raw:
        copy = Path(raw) / "repo"
        shutil.copytree(snapshot, copy)
        write(copy, "src/salida.py", "salida = 2\n")
        changed = snapshot_of(copy, "features/01-x")
        if changed == esperado["snapshot"]:
            problems.append("un cambio de código no cambió la identidad")
    return problems


def check_s57(snapshot: Path, esperado: dict) -> list[str]:
    done = script(snapshot, "diff_scope.py", "features/07-x", "--repo", ".", "--json")
    if done.returncode != 0:
        return [f"diff_scope.py salió {done.returncode}: {done.stderr.strip()}"]
    data = json.loads(done.stdout)
    problems = []
    if data.get("undeclared"):
        problems.append(f"hay alcance propio sin declarar: {data['undeclared']}")
    if "features/08-y/src/otra.py" not in data.get("foreign", {}):
        problems.append("la ruta de la etapa 08 no se atribuye como ajena")
    return problems


def check_s58(snapshot: Path, esperado: dict) -> list[str]:
    done = script(snapshot, "next_step.py", "features")
    text = done.stdout + done.stderr
    problems = []
    if "trabajando" not in text:
        problems.append(f"el estado no es trabajando: {text.strip()}")
    if "conciliate-stage" not in text:
        problems.append(f"la skill siguiente no es conciliate-stage: {text.strip()}")
    return problems


def check_s59(snapshot: Path, esperado: dict) -> list[str]:
    done = script(snapshot, "next_step.py", "features", "--stage", "08-cerrada-con-delta")
    text = done.stdout + done.stderr
    problems = []
    if "declarada-cerrada" not in text:
        problems.append(f"el estado no es declarada-cerrada: {text.strip()}")
    if "audit-stage" in text:
        problems.append(f"el router manda a reauditar: {text.strip()}")
    return problems


def check_s60(snapshot: Path, esperado: dict) -> list[str]:
    after = snapshot_of(snapshot, "features/01-x", "--exclude", ".yerro/approvals.yml")
    problems = []
    if code_id(after) != code_id(esperado["snapshot"]):
        problems.append(f"el commit de documento cambió la identidad: {after}")
    done = script(snapshot, "validate_stage.py", "features/01-x", "--repo", ".")
    if done.returncode != 0:
        problems.append(f"validate_stage --repo rechaza: {done.stdout.strip()}{done.stderr.strip()}")
    return problems


def check_s61(snapshot: Path, esperado: dict) -> list[str]:
    after = snapshot_of(snapshot, "features/01-x")
    problems = []
    if code_id(after) != code_id(esperado["snapshot"]):
        problems.append(f"el AUDIT de la vecina cambió la identidad: {after}")
    with tempfile.TemporaryDirectory(prefix="n4-s61-") as raw:
        copy = Path(raw) / "repo"
        shutil.copytree(snapshot, copy)
        write(copy, "src/salida.py", "salida = 2\n")
        changed = snapshot_of(copy, "features/01-x")
        if changed == esperado["snapshot"]:
            problems.append("un cambio de código no cambió la identidad")
    return problems


def check_s62(snapshot: Path, esperado: dict) -> list[str]:
    after = snapshot_of(snapshot, "features/07-x", "--exclude", ".yerro/approvals.yml")
    problems = []
    if code_id(after) != code_id(esperado["snapshot"]):
        problems.append(f"el alta de la etapa 10 cambió la identidad: {after}")
    done = script(snapshot, "validate_stage.py", "features/07-x", "--repo", ".")
    if done.returncode != 0:
        problems.append(f"la firma por árbol no cubre: {done.stdout.strip()}{done.stderr.strip()}")
    return problems


def check_s66(snapshot: Path, esperado: dict) -> list[str]:
    problems = []
    done = script(snapshot, "validate_stage.py", "features/02-x", "--repo", ".")
    if done.returncode != 0:
        problems.append(f"la firma de plan no cerró: {done.stdout.strip()}{done.stderr.strip()}")
    with tempfile.TemporaryDirectory(prefix="n4-s66-") as raw:
        copy = Path(raw) / "repo"
        shutil.copytree(snapshot, copy)
        approvals = copy / ".yerro" / "approvals.yml"
        plan_only = approvals.read_text(encoding="utf-8")
        # Control: la etapa es de riesgo bajo, así que no firmó árbol. Sin la
        # firma de plan no queda nada que cubra el cierre.
        if "alcance:" in plan_only:
            problems.append("la etapa de riesgo bajo firmó el árbol; el control no mide lo que dice")
        tree_only = "\n".join(
            line for line in plan_only.splitlines() if not line.startswith(" base:")
        ) + "\n"
        approvals.write_text(tree_only, encoding="utf-8")
        other = script(copy, "validate_stage.py", "features/02-x", "--repo", ".")
        if other.returncode == 0:
            problems.append("la firma del árbol cerró sin la firma de plan")
        elif "falta la firma de plan" not in other.stdout:
            problems.append(f"falló por otro motivo: {other.stdout.strip()}")
    return problems

def check_s63(snapshot: Path, esperado: dict) -> list[str]:
    done = script(snapshot, "validate_stage.py", "features/08-x", "--repo", ".")
    problems = []
    if done.returncode != 0:
        problems.append(f"la firma corta no cubre: {done.stdout.strip()}{done.stderr.strip()}")
    with tempfile.TemporaryDirectory(prefix="n4-s63-") as raw:
        copy = Path(raw) / "repo"
        shutil.copytree(snapshot, copy)
        approve(copy, "08-x", "tree=deadbeef")
        other = script(copy, "validate_stage.py", "features/08-x", "--repo", ".")
        if other.returncode == 0:
            problems.append("un árbol que no es prefijo cubre la pasada")
    return problems


CHECKS = {
    "s52": check_s52,
    "s53": check_s53,
    "s54": check_s54,
    "s55": check_s55,
    "s56": check_s56,
    "s57": check_s57,
    "s58": check_s58,
    "s59": check_s59,
    "s60": check_s60,
    "s61": check_s61,
    "s62": check_s62,
    "s63": check_s63,
    "s66": check_s66,
}


# --- materialización ------------------------------------------------------

def rubric(case: dict) -> str:
    lines = [
        f"# Rúbrica — {case['id']}",
        "",
        f"**Skill esperada:** `{case['skill']}`",
        "",
        "## Petición",
        "",
        case["prompt"],
        "",
        "## Resultado exigido",
        "",
    ]
    lines += [f"- {item}" for item in case["expectations"]]
    lines += [
        "",
        "## Control (contrato anterior)",
        "",
        case["control"],
        "",
        "## Puntuación",
        "",
        "0/1 por cada expectation. Un caso pasa solo con todas en 1 y sin falso",
        "cierre. Registra el transcript y el diff; una respuesta sin artefacto no",
        "cuenta como evidencia.",
        "",
    ]
    return "\n".join(lines)


def prepare_case(case: dict, out: Path) -> dict:
    case_dir = out / case["id"]
    snapshot = case_dir / "snapshot"
    if case_dir.exists():
        shutil.rmtree(case_dir)
    snapshot.mkdir(parents=True)
    copy_skills(snapshot)
    esperado = BUILDERS[case["setup"]](snapshot)
    (case_dir / "PROMPT.md").write_text(case["prompt"] + "\n", encoding="utf-8")
    rubrica = case_dir / "_rubrica"
    rubrica.mkdir()
    (rubrica / "EXPECTATIONS.md").write_text(rubric(case), encoding="utf-8")
    (rubrica / "esperado.json").write_text(
        json.dumps(esperado, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (rubrica / "META.json").write_text(
        json.dumps(
            {
                "id": case["id"],
                "skill": case["skill"],
                "commit": "",
                "model": "",
                "agent": "",
                "date": "",
                "transcript": "",
                "diff": "",
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (rubrica / "RESULTADO.json").write_text(
        json.dumps(
            {
                "id": case["id"],
                "pasa": None,
                "puntos": {str(index + 1): None for index in range(len(case["expectations"]))},
                "falso_cierre": None,
                "notas": "",
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return esperado


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--only", default="", help="IDs separados por coma")
    parser.add_argument("--check", action="store_true", help="verifica el estado inicial")
    parser.add_argument("--force", action="store_true", help="borra la salida existente")
    args = parser.parse_args(argv)

    out = args.out.resolve()
    if out.exists() and args.force:
        shutil.rmtree(out)
    out.mkdir(parents=True, exist_ok=True)

    wanted = {item.strip().upper() for item in args.only.split(",") if item.strip()}
    selected = [case for case in CASES if not wanted or case["id"] in wanted]
    if wanted and len(selected) != len(wanted):
        missing = wanted - {case["id"] for case in selected}
        print(f"ERROR: casos desconocidos: {', '.join(sorted(missing))}", file=sys.stderr)
        return 2

    failures: list[str] = []
    for case in selected:
        try:
            esperado = prepare_case(case, out)
        except Exception as error:  # noqa: BLE001 - se informa y se sigue
            failures.append(f"{case['id']}: no se pudo materializar: {error}")
            continue
        if args.check:
            problems = CHECKS[case["setup"]](out / case["id"] / "snapshot", esperado)
            if problems:
                failures.extend(f"{case['id']}: {problem}" for problem in problems)
                print(f"FALLA {case['id']}")
            else:
                print(f"OK    {case['id']}  {case['title']}")

    index = [
        "# Corrida de nivel 4 — índice",
        "",
        f"Casos preparados: {len(selected)}",
        "",
        "| ID | Skill | Título | Snapshot |",
        "|----|-------|--------|----------|",
    ]
    for case in selected:
        # El `|` de un título parte la fila de la tabla igual que parte una
        # celda del ledger: se escapa, no se deja romper.
        title = case["title"].replace("|", "\\|")
        index.append(
            f"| {case['id']} | `{case['skill']}` | {title} | "
            f"`{case['id']}/snapshot/` |"
        )
    index += [
        "",
        "## Cómo se ejecuta",
        "",
        "1. Abre una sesión nueva del agente con `cwd` en `<ID>/snapshot/`.",
        "2. Pega el contenido de `<ID>/PROMPT.md` como petición del usuario.",
        "3. Guarda el transcript en `<ID>/_rubrica/transcript.md` y el diff en",
        "   `<ID>/_rubrica/diff.patch`.",
        "4. Rellena `<ID>/_rubrica/META.json` (commit, modelo, agente, fecha) y",
        "   `<ID>/_rubrica/RESULTADO.json` (puntos por expectation).",
        "5. Ejecuta `score.py --out <dir>` para agregar el reporte.",
        "",
        "La rúbrica no está dentro del snapshot: el agente no la ve antes de",
        "responder.",
        "",
    ]
    (out / "INDICE.md").write_text("\n".join(index), encoding="utf-8")

    if failures:
        print("\nFallos de preparación:", file=sys.stderr)
        for failure in failures:
            print(f"  {failure}", file=sys.stderr)
        return 1
    print(f"\nPreparados {len(selected)} casos en {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
