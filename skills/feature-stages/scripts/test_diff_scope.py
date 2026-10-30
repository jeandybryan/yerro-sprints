#!/usr/bin/env python3
"""Prueba la comparación diff ↔ alcance declarado (`diff_scope.py`, B-27).

Uso: test_diff_scope.py

Construye repositorios git temporales y comprueba que el script distingue lo que
se tocó de lo que `**Archivos:**` declara: una ruta no declarada es alcance
nuevo (error), una declarada que no cambió es una tarea incompleta (advertencia,
no error), y la evidencia de la propia etapa nunca cuenta como código. Solo
stdlib y el binario `git`; no consume tokens.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from diff_scope import _normalize, compare, declared_files, declared_in, stage_base # noqa: E402

SCRIPT = HERE / "diff_scope.py"
errors: list[str] = []
checked = 0

TASKS = """# Tareas — etapa 01

**Principal:** sí

## Listado

- [ ] T1 — exportar (CA-01)
  **Archivos:** `src/export.csv`, `tests/test_export_csv.py`
  Test-first: sí; Test: pytest -q tests/test_export_csv.py;

- [ ] T2 — documentar
  **Archivos:** `docs/export.md`
  Test-first: sí; Test: pytest -q tests/test_export_csv.py;
"""


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
    (repo / "src").mkdir()
    (repo / "tests").mkdir()
    (repo / "docs").mkdir()
    (repo / "src" / "utilidades.py").write_text("base\n", encoding="utf-8")
    (repo / "src" / "export.csv").write_text("base\n", encoding="utf-8")
    (repo / "tests" / "test_export_csv.py").write_text("base\n", encoding="utf-8")
    (repo / "docs" / "export.md").write_text("base\n", encoding="utf-8")
    git(repo, "add", "-A")
    git(repo, "commit", "-qm", "inicial")
    stage = repo / "features" / "01-export"
    stage.mkdir(parents=True)
    (stage / "TAREAS.md").write_text(TASKS, encoding="utf-8")
    (stage / "CONCILIACION.md").write_text("# Conciliación\n", encoding="utf-8")


def run(repo: Path, stage: str = "features/01-export", *extra: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), stage, "--repo", str(repo), "--json", *extra],
        capture_output=True,
        text=True,
    )


def check_parser() -> None:
    """`**Archivos:**` se lee por tarea, con acentos o desnudo."""
    global checked
    parsed = declared_files(TASKS)
    checked += 1
    if parsed != {
        "T1": ["src/export.csv", "tests/test_export_csv.py"],
        "T2": ["docs/export.md"],
    }:
        fail(f"declared_files: obtuvo {parsed}")

    # Sin acentos y con separadores distintos: mismas rutas.
    desnudo = declared_files("- [ ] T1 — x\n  Archivos: a.py, b.py\n")
    checked += 1
    if desnudo != {"T1": ["a.py", "b.py"]}:
        fail(f"declared_files (desnudo): obtuvo {desnudo}")

    # Una tarea sin el campo no se confunde con una que declara vacío.
    checked += 1
    if declared_files("- [ ] T1 — x\n  Test-first: sí;\n") != {"T1": []}:
        fail("declared_files: una tarea sin **Archivos:** debe dar lista vacía")

    # `lstrip("./")` convertiría `.yerro/x` en `yerro/x` y la evidencia dejaría
    # de excluirse. La normalización borra el prefijo, no los caracteres.
    checked += 1
    if _normalize(".yerro/approvals.yml") != ".yerro/approvals.yml":
        fail(f"_normalize: rompió la ruta oculta ({_normalize('.yerro/approvals.yml')})")
    checked += 1
    if _normalize("./src/a.py") != "src/a.py":
        fail(f"_normalize: no quitó el prefijo ./ ({_normalize('./src/a.py')})")


def check_compare() -> None:
    """Las dos direcciones de la diferencia, sin git."""
    global checked
    declared = {"T1": ["src/a.py", "tests/t.py"], "T2": []}
    result = compare(declared, ["src/a.py", "./tests/t.py", "src/sorpresa.py"])
    checked += 1
    if result["undeclared"] != ["src/sorpresa.py"]:
        fail(f"compare: undeclared = {result['undeclared']}")
    if result["missing"]:
        fail(f"compare: missing inesperado = {result['missing']}")
    if result["unmigrated"] != ["T2"]:
        fail(f"compare: unmigrated = {result['unmigrated']}")


def check_clean(repo: Path) -> None:
    """Tocar exactamente lo declarado pasa."""
    global checked
    (repo / "src" / "export.csv").write_text("nuevo\n", encoding="utf-8")
    (repo / "tests" / "test_export_csv.py").write_text("test\n", encoding="utf-8")
    (repo / "docs" / "export.md").write_text("doc\n", encoding="utf-8")
    result = run(repo)
    checked += 1
    if result.returncode != 0:
        fail(f"diff_scope limpio: salida {result.returncode}: {result.stdout}{result.stderr}")


def check_local_secrets_ignored(repo: Path) -> None:
    """B-46: un secreto local sin versionar no es alcance nuevo.

    El operador deja sus credenciales de demo en un `.env` local que nunca se
    versiona. El gate no puede confundirlo con código: pedirle a una tarea que
    declare una credencial empuja a escribirla en el árbol de la etapa. Se
    excluye por **forma** (`*.env*`, `*.local`), nunca por el nombre de un
    archivo del consumidor.
    """
    global checked
    (repo / "console").mkdir(exist_ok=True)
    secret = repo / "console" / ".env.demo.local"
    secret.write_text("TOKEN=secreto\n", encoding="utf-8")

    checked += 1
    result = run(repo)
    payload = json.loads(result.stdout) if result.stdout.strip() else {}
    if result.returncode != 0 or payload.get("undeclared"):
        fail(
            "diff_scope: un .env local sin versionar no es alcance nuevo "
            f"({result.returncode}, {payload.get('undeclared')})"
        )

    # Un `.env.example` versionado sí es contrato: se documenta en una tarea.
    (repo / "console" / ".env.example").write_text("TOKEN=\n", encoding="utf-8")
    checked += 1
    result = run(repo)
    payload = json.loads(result.stdout) if result.stdout.strip() else {}
    if payload.get("undeclared") != ["console/.env.example"]:
        fail(
            "diff_scope: .env.example es contrato y debe bloquear si no se "
            f"declara (obtuvo {payload.get('undeclared')})"
        )

    (repo / "console" / ".env.example").unlink()
    secret.unlink()


def check_undeclared(repo: Path) -> None:
    """Un archivo que ninguna tarea declara es alcance nuevo: exit 1."""
    global checked
    (repo / "src" / "utilidades.py").write_text("refactor de paso\n", encoding="utf-8")
    result = run(repo)
    checked += 1
    if result.returncode != 1:
        fail(f"diff_scope undeclared: salida {result.returncode}, se esperaba 1")
    payload = json.loads(result.stdout) if result.stdout.strip() else {}
    if payload.get("undeclared") != ["src/utilidades.py"]:
        fail(f"diff_scope undeclared: obtuvo {payload.get('undeclared')}")


def check_untracked(repo: Path) -> None:
    """Un archivo nuevo sin `git add` también cuenta: git no lo vería en el diff."""
    global checked
    (repo / "src" / "otro.py").write_text("nuevo\n", encoding="utf-8")
    result = run(repo)
    checked += 1
    payload = json.loads(result.stdout) if result.stdout.strip() else {}
    if "src/otro.py" not in payload.get("undeclared", []):
        fail(f"diff_scope untracked: no detectó src/otro.py ({payload.get('undeclared')})")


def check_committed_change_is_seen() -> None:
    """`--base` ve el trabajo commiteado; contra `HEAD` desaparece.

    Con `--base HEAD`, quien commitea su trabajo deja el diff vacío. El script
    sí ve lo commiteado cuando la base es un commit anterior, así que medir el
    alcance depende de elegir bien la base. Repo propio: este caso commitea y no
    debe dejar el árbol de los demás casos a medias.
    """
    global checked
    repo = Path(tempfile.mkdtemp(prefix="yerro-diffscope-commit-"))
    try:
        init_repo(repo)
        git(repo, "add", "-A")
        git(repo, "commit", "-qm", "etapa en su linea base")
        base = git(repo, "rev-parse", "HEAD").stdout.strip()

        # La etapa se implementa y se commitea, como haría un agente ordenado.
        (repo / "src" / "export.csv").write_text("nuevo\n", encoding="utf-8")
        (repo / "src" / "intruso.py").write_text("alcance nuevo\n", encoding="utf-8")
        git(repo, "add", "-A")
        git(repo, "commit", "-qm", "implementar la etapa")

        # Desde la base el intruso se ve y bloquea.
        result = run(repo, "features/01-export", "--base", base)
        checked += 1
        payload = json.loads(result.stdout) if result.stdout.strip() else {}
        if result.returncode != 1 or payload.get("undeclared") != ["src/intruso.py"]:
            fail(f"diff_scope committed: desde la base obtuvo {result.returncode} {payload.get('undeclared')}")

        # Contra HEAD el mismo trabajo es invisible: el caso de por qué el
        # cierre no puede usar HEAD como base.
        result = run(repo, "features/01-export", "--base", "HEAD")
        checked += 1
        payload = json.loads(result.stdout) if result.stdout.strip() else {}
        if result.returncode != 0 or payload.get("undeclared"):
            fail(f"diff_scope committed: HEAD debería no ver nada, obtuvo {payload.get('undeclared')}")
    finally:
        shutil.rmtree(repo, ignore_errors=True)


def check_default_base_is_stage_start() -> None:
    """Sin `--base`, el alcance se mide desde que la etapa apareció.

    Con `HEAD` como base, quien commitea su trabajo deja el diff vacío y el
    gate aprueba cualquier archivo. La base es el commit que abrió la etapa:
    se deriva de la historia, sin campo nuevo ni migración.
    """
    global checked
    repo = Path(tempfile.mkdtemp(prefix="yerro-diffscope-base-"))
    try:
        init_repo(repo)
        git(repo, "add", "-A")
        git(repo, "commit", "-qm", "abrir la etapa")
        opened = git(repo, "rev-parse", "HEAD").stdout.strip()

        checked += 1
        derived = stage_base(repo, repo / "features" / "01-export")
        if derived != opened:
            fail(f"stage_base: obtuvo {derived!r}, se esperaba el commit {opened[:8]}")

        (repo / "src" / "export.csv").write_text("nuevo\n", encoding="utf-8")
        (repo / "src" / "colado.py").write_text("alcance nuevo\n", encoding="utf-8")
        git(repo, "add", "-A")
        git(repo, "commit", "-qm", "implementar la etapa")

        # Sin `--base` el intruso commiteado se ve y bloquea.
        result = run(repo)
        checked += 1
        payload = json.loads(result.stdout) if result.stdout.strip() else {}
        if result.returncode != 1 or payload.get("undeclared") != ["src/colado.py"]:
            fail(
                "diff_scope base por defecto: no bloqueó lo commiteado "
                f"({result.returncode}, {payload.get('undeclared')})"
            )

        # Con `--base HEAD` el mismo trabajo es invisible: por eso la base no
        # puede ser HEAD.
        result = run(repo, "features/01-export", "--base", "HEAD")
        checked += 1
        payload = json.loads(result.stdout) if result.stdout.strip() else {}
        if payload.get("undeclared"):
            fail(f"diff_scope base por defecto: HEAD debería no ver nada, vio {payload.get('undeclared')}")

        # Una etapa que todavía no está commiteada no tiene commit de apertura:
        # se cae a HEAD, que es lo que sí puede verse.
        (repo / "features" / "02-nueva").mkdir()
        (repo / "features" / "02-nueva" / "TAREAS.md").write_text(TASKS, encoding="utf-8")
        checked += 1
        if stage_base(repo, repo / "features" / "02-nueva") is not None:
            fail("stage_base: una etapa sin commitear no debe tener base")
    finally:
        shutil.rmtree(repo, ignore_errors=True)


def check_base_is_task_list_start() -> None:
    """B-45: la base es el commit que abre la etapa, no la primera ruta.

    Una etapa puede dejar su `CONCILIACION.md` en un commit de hace semanas,
    junto a otras etapas, y empezar a implementarse mucho después. Si la base
    es esa primera aparición, el diff arrastra todo lo que las otras etapas
    commitearon entre medias y el gate se vuelve un falso positivo de cientos
    de archivos. La etapa abre cuando nace su `TAREAS.md`.
    """
    global checked
    repo = Path(tempfile.mkdtemp(prefix="yerro-diffscope-apertura-"))
    try:
        init_repo(repo)
        git(repo, "add", "-A")
        git(repo, "commit", "-qm", "inicial")

        stage = repo / "features" / "03-tarde"
        stage.mkdir(parents=True)
        (stage / "CONCILIACION.md").write_text("# Conciliación\n", encoding="utf-8")
        (repo / "src" / "otra-a.py").write_text("a\n", encoding="utf-8")
        git(repo, "add", "-A")
        git(repo, "commit", "-qm", "conciliación de pasada, con otras etapas")

        # Otras etapas commitean entre medias: no es de esta etapa.
        for index in range(2):
            (repo / "src" / f"otra-{index}.py").write_text(f"{index}\n", encoding="utf-8")
            git(repo, "add", "-A")
            git(repo, "commit", "-qm", f"otra etapa {index}")

        (stage / "TAREAS.md").write_text(TASKS, encoding="utf-8")
        (stage / "delta-choca.md").write_text("no\n", encoding="utf-8")
        git(repo, "add", "-A")
        git(repo, "commit", "-qm", "cerrar conciliación y abrir la etapa")
        apertura = git(repo, "rev-parse", "HEAD").stdout.strip()

        checked += 1
        derived = stage_base(repo, stage)
        if derived != apertura:
            fail(
                "stage_base: debe ser el commit que añade TAREAS.md, obtuvo "
                f"{str(derived)[:8]} y se esperaba {apertura[:8]}"
            )
    finally:
        shutil.rmtree(repo, ignore_errors=True)

DELTA = """# Delta 01 — etapa 01

**Principal:** no
**Cierra:** AUDIT.md pasada 1; CA-01; E-01
**Hueco:** falta el caso negativo.
**Estado:** pendiente

## Listado

- [ ] D01-T1 — añadir el caso negativo (CA-01)
**Archivos:** `tests/test_negativo.py`
Test-first: sí; Test: pytest -q tests/test_negativo.py;
Verificar: nivel `conductual`; ejecutar el test; oráculo: falla inyectada → rojo.
"""


def check_delta_scope() -> None:
    """El archivo que produce un delta está dentro del alcance de la etapa.

    La auditoría escribe `TAREAS-delta-NN.md` para cerrar un hueco, y esa
    tarea puede crear un archivo que la lista principal no nombra. Leer solo
    `TAREAS.md` reportaba ese archivo como alcance nuevo: una etapa con delta
    nunca cerraba, aunque el delta declarara exactamente lo que tocó.
    """
    global checked
    repo = Path(tempfile.mkdtemp(prefix="yerro-diffscope-delta-"))
    try:
        init_repo(repo)
        git(repo, "add", "-A")
        git(repo, "commit", "-qm", "abrir la etapa")
        stage = repo / "features" / "01-export"

        # La base es el commit que abrió la etapa: un delta escrito después
        # del archivo quedaría en el mismo diff y taparía el defecto. El
        # ciclo real escribe el delta en la auditoría y lo implementa después.
        (repo / "tests" / "test_negativo.py").write_text("negativo\n", encoding="utf-8")
        git(repo, "add", "-A")
        git(repo, "commit", "-qm", "colar el archivo sin delta")
        result = run(repo)
        checked += 1
        payload = json.loads(result.stdout) if result.stdout.strip() else {}
        if payload.get("undeclared") != ["tests/test_negativo.py"]:
            fail(
                "diff_scope delta: sin delta, tests/test_negativo.py debería ser "
                f"alcance nuevo ({payload.get('undeclared')})"
            )

        (stage / "TAREAS-delta-01.md").write_text(DELTA, encoding="utf-8")
        merged = declared_in(stage)
        checked += 1
        if merged != {
            "T1": ["src/export.csv", "tests/test_export_csv.py"],
            "T2": ["docs/export.md"],
            "D01-T1": ["tests/test_negativo.py"],
        }:
            fail(f"declared_in: obtuvo {merged}")

        # Con el delta escrito, el mismo archivo está declarado y la etapa
        # puede cerrar.
        result = run(repo)
        checked += 1
        payload = json.loads(result.stdout) if result.stdout.strip() else {}
        if payload.get("undeclared"):
            fail(
                "diff_scope delta: el delta declaró el archivo y se reportó "
                f"({payload.get('undeclared')})"
            )
    finally:
        shutil.rmtree(repo, ignore_errors=True)


def check_missing_is_warning(repo: Path) -> None:
    """Declarado y no tocado: advertencia, no bloqueo (B-27 solo veta lo nuevo)."""
    global checked
    (repo / "src" / "otro.py").unlink()
    (repo / "src" / "utilidades.py").write_text("base\n", encoding="utf-8")
    (repo / "docs" / "export.md").write_text("base\n", encoding="utf-8")
    result = run(repo)
    checked += 1
    if result.returncode != 0:
        fail(f"diff_scope missing: salida {result.returncode}, una ruta sin tocar no bloquea")
    payload = json.loads(result.stdout) if result.stdout.strip() else {}
    if payload.get("missing") != ["docs/export.md"]:
        fail(f"diff_scope missing: obtuvo {payload.get('missing')}")


def check_evidence_ignored(repo: Path) -> None:
    """Escribir en el árbol de la etapa no es código: no aparece en el diff."""
    global checked
    stage = repo / "features" / "01-export"
    (stage / "AUDIT.md").write_text("# Auditoría\n", encoding="utf-8")
    (repo / ".yerro").mkdir(exist_ok=True)
    (repo / ".yerro" / "approvals.yml").write_text("", encoding="utf-8")
    result = run(repo)
    checked += 1
    payload = json.loads(result.stdout) if result.stdout.strip() else {}
    tocados = payload.get("undeclared", []) + payload.get("touched", [])
    if any("AUDIT.md" in item or ".yerro" in item for item in tocados):
        fail(f"diff_scope evidence: la evidencia contó como código ({tocados})")


def check_foreign_attribution() -> None:
    """B-50: una ruta de otra etapa se atribuye, no se cuenta como propia.

    En un repositorio con una rama por etapa, medir el alcance desde la
    apertura de esta etapa arrastra todo lo que las otras commitearon. Sin
    atribución, el cierre se vuelve rojo con cientos de rutas que ningún
    agente de esta etapa escribió, y el auditor no sabe de dónde vienen.
    Una ruta de un commit que toca una etapa hermana se informa con su
    commit; una que viene de un commit sin etapa (esta implementación) sigue
    bloqueando, y un commit mixto también: la ambigüedad no absuelve (B-27).
    """
    global checked
    repo = Path(tempfile.mkdtemp(prefix="yerro-diffscope-ajenas-"))
    try:
        init_repo(repo)
        mine = repo / "features" / "01-mia"
        other = repo / "features" / "02-ajena"
        mine.mkdir(parents=True)
        other.mkdir(parents=True)
        (mine / "TAREAS.md").write_text(TASKS, encoding="utf-8")
        (other / "CONCILIACION.md").write_text("# Otra etapa\n", encoding="utf-8")
        git(repo, "add", "-A")
        git(repo, "commit", "-qm", "abrir las dos etapas")

        # Otra etapa produce un archivo de código y su propia evidencia.
        (other / "AUDIT.md").write_text("# Auditoría ajena\n", encoding="utf-8")
        (repo / "src" / "ajena.py").write_text("otra etapa\n", encoding="utf-8")
        git(repo, "add", "-A")
        git(repo, "commit", "-qm", "avanzar la etapa ajena")

        result = run(repo, "features/01-mia")
        checked += 1
        payload = json.loads(result.stdout) if result.stdout.strip() else {}
        if result.returncode != 0:
            fail(
                "atribución: una ruta de otra etapa bloqueó el cierre "
                f"({result.returncode}, {payload.get('undeclared')})"
            )
        if payload.get("undeclared"):
            fail(f"atribución: undeclared debía quedar vacío ({payload.get('undeclared')})")
        foreign = payload.get("foreign") or {}
        if "src/ajena.py" not in foreign:
            fail(f"atribución: no atribuyó src/ajena.py a otra etapa ({foreign})")
        elif foreign["src/ajena.py"].get("subject") != "avanzar la etapa ajena":
            fail(f"atribución: no nombró el commit de origen ({foreign.get('src/ajena.py')})")

        # Un commit que no toca ninguna etapa es esta implementación: bloquea.
        (repo / "src" / "mia.py").write_text("mi etapa\n", encoding="utf-8")
        git(repo, "add", "-A")
        git(repo, "commit", "-qm", "implementar la etapa propia")
        result = run(repo, "features/01-mia")
        checked += 1
        payload = json.loads(result.stdout) if result.stdout.strip() else {}
        if result.returncode != 1 or payload.get("undeclared") != ["src/mia.py"]:
            fail(
                "atribución: un commit sin etapa no bloqueó como propio "
                f"({result.returncode}, {payload.get('undeclared')})"
            )

        # Un commit mixto toca las dos etapas: su ruta de código es ambigua y
        # cuenta como propia; lo que vive en el árbol ajeno sigue siendo ajeno.
        (mine / "AUDIT.md").write_text("# Auditoría mía\n", encoding="utf-8")
        (other / "NOTA.md").write_text("nota\n", encoding="utf-8")
        (repo / "src" / "compartido.py").write_text("mixto\n", encoding="utf-8")
        git(repo, "add", "-A")
        git(repo, "commit", "-qm", "commit que toca las dos etapas")
        result = run(repo, "features/01-mia")
        checked += 1
        payload = json.loads(result.stdout) if result.stdout.strip() else {}
        if payload.get("undeclared") != ["src/compartido.py", "src/mia.py"]:
            fail(
                "atribución: un commit mixto absolvió una ruta "
                f"({result.returncode}, {payload.get('undeclared')})"
            )
    finally:
        shutil.rmtree(repo, ignore_errors=True)


def check_bad_base(repo: Path) -> None:
    """Una base inexistente es error de lectura (2), no un falso limpio."""
    global checked
    result = run(repo, "features/01-export", "--base", "no-existe")
    checked += 1
    if result.returncode != 2:
        fail(f"diff_scope bad base: salida {result.returncode}, se esperaba 2")


def check_unmigrated(repo: Path) -> None:
    """Una tarea sin `**Archivos:**` se informa; no bloquea sola."""
    global checked
    stage = repo / "features" / "02-sin-migrar"
    stage.mkdir(parents=True)
    (stage / "TAREAS.md").write_text(
        "- [ ] T1 — x\n  Test-first: sí; Test: pytest -q;\n", encoding="utf-8"
    )
    result = subprocess.run(
        [sys.executable, str(SCRIPT), str(stage), "--repo", str(repo), "--json"],
        capture_output=True,
        text=True,
    )
    checked += 1
    payload = json.loads(result.stdout) if result.stdout.strip() else {}
    if payload.get("unmigrated") != ["T1"]:
        fail(f"diff_scope unmigrado: obtuvo {payload.get('unmigrated')}")


def check_fixture() -> None:
    """La fixture retenida existe y declara un alcance que el diff puede violar."""
    global checked
    fixture = HERE.parent / "evals" / "fixtures" / "cambio-fuera-de-alcance"
    checked += 1
    if not (fixture / "TAREAS.md").exists():
        fail("fixture cambio-fuera-de-alcance: falta TAREAS.md")
        return
    parsed = declared_files((fixture / "TAREAS.md").read_text(encoding="utf-8"))
    checked += 1
    if parsed.get("T1") != ["src/export.csv", "tests/test_export_csv.py"]:
        fail(f"fixture cambio-fuera-de-alcance: declaró {parsed.get('T1')}")


def main() -> int:
    check_parser()
    check_compare()
    check_fixture()

    work = Path(tempfile.mkdtemp(prefix="yerro-diffscope-"))
    try:
        init_repo(work)
        # El orden importa: cada caso parte del estado que dejó el anterior.
        # `check_clean` necesita el repo recién inicializado; los siguientes
        # añaden una ruta no declarada y luego la retiran.
        check_clean(work)
        check_evidence_ignored(work)
        check_local_secrets_ignored(work)
        check_undeclared(work)
        check_untracked(work)
        check_committed_change_is_seen()
        check_missing_is_warning(work)
        check_default_base_is_stage_start()
        check_base_is_task_list_start()
        check_foreign_attribution()
        check_bad_base(work)
        check_unmigrated(work)
        check_delta_scope()
    finally:
        shutil.rmtree(work, ignore_errors=True)

    if errors:
        for message in errors:
            print(f"ERROR: {message}")
        return 1
    print(f"OK: {checked} comprobaciones de alcance")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
