#!/usr/bin/env python3
"""Prueba la identidad de auditoría (`snapshot.py`) y su verificación.

Uso: test_snapshot.py

Construye repositorios git temporales y comprueba que la identidad es estable,
cambia cuando cambia el código, ignora las rutas excluidas (la evidencia) y que
`validate_stage.py --repo` rechaza una pasada cuyo snapshot ya no coincide con
el árbol actual. Solo stdlib y el binario `git`; no consume tokens.
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

APPROVALS = Path(".yerro") / "approvals.yml"

from snapshot import SnapshotError, code_identity, identity # noqa: E402
import validate_stage # noqa: E402

same_identity = validate_stage.same_identity
snapshot_mismatch = validate_stage.snapshot_mismatch

errors: list[str] = []
checked = 0


def fail(message: str) -> None:
    errors.append(message)


def git(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True,
        text=True,
    )


def init_repo(repo: Path) -> None:
    created = git(repo, "init", "-q")
    if created.returncode != 0:
        raise RuntimeError(f"git init falló en {repo}: {created.stderr.strip()}")
    git(repo, "config", "user.email", "fixture@example.com")
    git(repo, "config", "user.name", "Fixture")
    git(repo, "config", "commit.gpgsign", "false")
    (repo / "src.txt").write_text("uno\n", encoding="utf-8")
    git(repo, "add", "src.txt")
    git(repo, "commit", "-qm", "inicial")


def check_stability(repo: Path) -> None:
    global checked
    first = identity(repo)
    second = identity(repo)
    checked += 1
    if first != second:
        fail(f"snapshot: dos lecturas del mismo árbol difieren: {first!r} vs {second!r}")
    if "dirty=no" not in first:
        fail(f"snapshot: árbol limpio marcado como sucio: {first!r}")
    if "head=sin-head" in first:
        fail(f"snapshot: repo con commit sin head: {first!r}")

    (repo / "src.txt").write_text("dos\n", encoding="utf-8")
    changed = identity(repo)
    checked += 1
    if changed == first:
        fail("snapshot: un cambio en el código no cambió la identidad")
    if "dirty=si" not in changed:
        fail(f"snapshot: cambio sin commitear no marca dirty=si: {changed!r}")

    git(repo, "add", "src.txt")
    git(repo, "commit", "-qm", "cambio")
    committed = identity(repo)
    checked += 1
    if committed == changed:
        fail("snapshot: commitear no cambió la identidad")
    if "dirty=no" not in committed:
        fail(f"snapshot: árbol commiteado sigue sucio: {committed!r}")


def check_exclude(repo: Path, bare: Path) -> None:
    global checked
    feature = repo / "feature"
    feature.mkdir()
    notes = feature / "AUDIT.md"
    notes.write_text("pasada 1\n", encoding="utf-8")
    before = identity(repo, (Path("feature"),))
    if "exclude=feature" not in before:
        fail(f"snapshot: no registra la exclusión: {before!r}")
    notes.write_text("pasada 1\npasada 2\n", encoding="utf-8")
    after = identity(repo, (Path("feature"),))
    checked += 1
    if before != after:
        fail("snapshot: escribir en la ruta excluida invalidó la identidad")
    without = identity(repo)
    checked += 1
    if without == before:
        fail("snapshot: sin exclusión la identidad no distingue el cambio")

    try:
        identity(bare / "no-existe")
    except SnapshotError:
        pass
    else:
        fail("snapshot: una ruta inexistente no produce SnapshotError")


def check_panel_index_excluded(repo: Path) -> None:
    """El índice del panel no forma parte del árbol auditado.

    Escribir la fila de estado de una etapa en el índice es el último paso del
    cierre; si el índice cuenta en el snapshot, esa celda obliga a una pasada
    nueva de auditoría (`tree=` cambia). Se excluye por forma —un `README.md`
    con carpetas de etapa hermanas— y no por nombre: el paquete no conoce las
    etapas de ningún consumidor.
    """
    global checked
    panel = repo / "docs" / "ai-review-console"
    (panel / "01-export").mkdir(parents=True)
    (panel / "01-export" / "AUDIT.md").write_text("pasada 1\n", encoding="utf-8")
    (panel / "README.md").write_text("| etapa | estado |\n| 01-export | activa |\n", encoding="utf-8")
    git(repo, "add", "-A")
    git(repo, "commit", "-qm", "panel")

    before = identity(panel / "01-export")
    checked += 1
    if "README.md" not in before:
        fail(f"snapshot: el índice del panel no viaja en exclude=: {before!r}")

    (panel / "README.md").write_text(
        "| etapa | estado |\n| 01-export | cerrada |\n", encoding="utf-8"
    )
    after = identity(panel / "01-export")
    checked += 1
    if before != after:
        fail(
            "snapshot: editar el índice del panel cambió la identidad del árbol "
            f"auditado ({before!r} → {after!r})"
        )

    # S61: la carpeta de la etapa es documentación (registro), así que
    # escribirla tampoco cambia el árbol. El código que no es de etapa, sí.
    (panel / "01-export" / "AUDIT.md").write_text("pasada 1\npasada 2\n", encoding="utf-8")
    changed_stage = identity(panel / "01-export")
    checked += 1
    if changed_stage != before:
        fail("snapshot: escribir en la carpeta de la etapa cambió el árbol auditado")
    (panel / "shared.yaml").write_text("k: v\n", encoding="utf-8")
    changed_code = identity(panel / "01-export")
    checked += 1
    if changed_code == before:
        fail("snapshot: excluir el índice cegó también el código del panel")

    # Un `README.md` suelto, sin carpetas de etapa hermanas, no es un panel:
    # sigue contando, y su cambio sí rompe la identidad.
    plain_root = repo / "lib"
    plain_root.mkdir()
    (plain_root / "README.md").write_text("docs\n", encoding="utf-8")
    git(repo, "add", "-A")
    git(repo, "commit", "-qm", "modulo")
    plain = identity(repo / "lib")
    (plain_root / "README.md").write_text("docs v2\n", encoding="utf-8")
    checked += 1
    if identity(repo / "lib") == plain:
        fail("snapshot: un README.md que no es índice de panel se excluyó por error")


STAGE = """# Etapa 01 — snapshot

**Estado:** cerrada
**Suites de referencia:** `pytest`
**Riesgo:** medio
**Presupuesto no funcional:**
- Latencia: no aplica (etapa de snapshot sin superficie de servicio)
- Memoria: no aplica (sin proceso residente)
- Tamaño/artefacto: no aplica (sin artefacto entregable)
- Dependencias nuevas: 0
- Rendimiento de operación crítica: no aplica (sin operación crítica)

## Aclaraciones

- **S-01 — Decisión:** se valida el snapshot antes del cierre.

## Criterios de aceptación

- **CA-01 — [condición de salida]:** estímulo → resultado; límite; evidencia `conductual`. Origen: S-01
"""

TASKS = """# Tareas

**Principal:** sí

## Listado

- [ ] T1 — implementar salida (CA-01)
  **Archivos:** `src.txt`
  Test-first: sí; Test: pytest -q test_focal.py;
  Verificar: nivel `conductual`; ejecutar test focalizado; oráculo observable: exit 0.
"""

AUDIT = """# Auditoría

## Pasada 1

**Snapshot:** {snapshot}
**Riesgo auditado:** medio
**Trazabilidad:** S-01 → CA-01 → T1 → test_focal.py → E-01

| Criterio | Afirmaciones auditadas | Tareas | Resultado | Evidencia reproducible | Limitaciones |
|----------|-------------------------|--------|-----------|-------------------------|--------------|
| CA-01 | salida y negativo | T1 | cumple | E-01 | ninguna |

### Ledger de evidencia

| ID | CA | Procedimiento/comando | Sensibilidad | Esperado | Observado/exit | Entorno y timestamp | Artefacto/log | Limitación |
|----|----|------------------------|--------------|----------|----------------|---------------------|---------------|------------|
| E-01 | CA-01 | pytest | revertir → rojo → restaurar; caso límite: entrada vacía → rechazo | verde | verde/0 | local; 2026-10-19 | log | ninguna |

**Veredicto:** coincide
**Veredicto (calidad):** aceptable
"""


DELTA = """# Delta 01 — etapa 02

**Principal:** no
**Cierra:** AUDIT.md pasada 1; CA-01; E-01
**Hueco:** falta el caso negativo.
**Estado:** implementada

## Listado

- [x] D01-T1 — añadir el caso negativo (CA-01)
  **Archivos:** `negativo.py`
  Test-first: sí; Test: pytest -q test_focal.py;
  Verificar: nivel `conductual`; ejecutar test focalizado; oráculo observable: exit 0.
"""


def validate(stage: Path, repo: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(HERE / "validate_stage.py"), str(stage), "--repo", str(repo)],
        capture_output=True,
        text=True,
    )


def check_whole_panel_excluded(repo: Path) -> None:
    """Los documentos de las demás etapas no son código auditado.

    El snapshot de una etapa excluía su propia carpeta y el índice del panel,
    pero no las carpetas de las etapas vecinas: escribir el `AUDIT.md` de la
    etapa 02 cambiaba el árbol que la etapa 01 había auditado, y cada pasada
    de una etapa obligaba a repetir la de al lado. Se excluye el panel entero
    por forma —todas las carpetas `NN-nombre` y su `README.md`— y el código
    que viva en el mismo panel sigue contando.
    """
    global checked
    panel = repo / "docs" / "panel"
    for name in ("01-uno", "02-dos"):
        (panel / name).mkdir(parents=True)
        (panel / name / "AUDIT.md").write_text("pasada 1\n", encoding="utf-8")
    (panel / "README.md").write_text("| etapa | estado |\n", encoding="utf-8")
    git(repo, "add", "-A")
    git(repo, "commit", "-qm", "panel de dos etapas")

    before = identity(panel / "01-uno")
    checked += 1
    if "exclude=" not in before or f"exclude=" not in before:
        fail(f"snapshot: sin exclude= en la identidad: {before!r}")
    # Todas las etapas del panel, no solo la auditada.
    declared = before.split("exclude=", 1)[1]
    checked += 1
    if not {"01-uno", "02-dos", "README.md"} <= set(declared.replace("/", ",").split(",")):
        fail(f"snapshot: el panel entero no viaja en exclude=: {before!r}")

    (panel / "02-dos" / "AUDIT.md").write_text("pasada 2\n", encoding="utf-8")
    after_neighbour = identity(panel / "01-uno")
    checked += 1
    if before != after_neighbour:
        fail(
            "snapshot: escribir en la etapa vecina cambió el árbol auditado "
            f"({before!r} → {after_neighbour!r})"
        )

    (panel / "README.md").write_text("| etapa | estado |\n| 01-uno | cerrada |\n", encoding="utf-8")
    after_index = identity(panel / "01-uno")
    checked += 1
    if before != after_index:
        fail("snapshot: editar el índice del panel cambió el árbol auditado")

    (panel / "01-uno" / "AUDIT.md").write_text("pasada 1\npasada 2\n", encoding="utf-8")
    after_own = identity(panel / "01-uno")
    checked += 1
    if before != after_own:
        fail("snapshot: escribir en la propia etapa cambió el árbol auditado")

    # El código dentro del panel sigue contando: la exclusión es de documentos.
    code = repo / "docs" / "panel" / "src.py"
    code.write_text("uno\n", encoding="utf-8")
    with_code = identity(panel / "01-uno")
    checked += 1
    if code_identity(with_code) == code_identity(after_own):
        fail("snapshot: excluir el panel cegó también el código que contiene")

    # Dos etapas del mismo panel ven el mismo árbol: no se condicionan entre sí.
    checked += 1
    if code_identity(identity(panel / "01-uno")) != code_identity(identity(panel / "02-dos")):
        fail("snapshot: dos etapas del mismo panel no ven el mismo árbol de código")


def check_new_stage_does_not_invalidate(repo: Path) -> None:
    """Una etapa nueva en el panel no invalida la pasada de las anteriores.

    El snapshot enumera las carpetas de etapa que excluye, así que crear la
    etapa 02 alarga la línea `exclude=` sin cambiar el árbol auditado.
    Comparar la línea literal convertía ese alta en una reauditoría de todas
    las etapas: la 01 y la 02 quedaban mirando el mismo árbol de código con
    dos `exclude=` distintos, y ninguna de las dos había perdido una línea
    de código. La lista de exclusión dice lo mismo con una carpeta más.
    """
    global checked
    panel = repo / "docs" / "otro-panel"
    (panel / "01-uno").mkdir(parents=True)
    (panel / "01-uno" / "AUDIT.md").write_text("pasada 1\n", encoding="utf-8")
    (panel / "README.md").write_text("| etapa | estado |\n", encoding="utf-8")
    git(repo, "add", "-A")
    git(repo, "commit", "-qm", "panel de una etapa")
    before = identity(panel / "01-uno")

    (panel / "02-dos").mkdir()
    (panel / "02-dos" / "CONCILIACION.md").write_text("nueva etapa\n", encoding="utf-8")
    git(repo, "add", "-A")
    git(repo, "commit", "-qm", "alta de la etapa 02")
    after = identity(panel / "01-uno")

    # La fixture tiene que mover la lista de exclusión, o no prueba lo que dice.
    checked += 1
    if "02-dos" not in after.split("exclude=", 1)[1]:
        fail("snapshot: la etapa nueva no aparece en exclude=; la fixture no prueba nada")
    checked += 1
    if before.split("exclude=", 1)[1] == after.split("exclude=", 1)[1]:
        fail("snapshot: la lista de exclusiones no cambió al crear una etapa")
    checked += 1
    if not same_identity(before, after):
        fail(
            "validate: crear una etapa invalidó la pasada de la vecina "
            f"({before!r} → {after!r})"
        )
    # El árbol no cambió: es la misma pasada, no otra.
    checked += 1
    if code_identity(before) != code_identity(after):
        fail("snapshot: la etapa nueva cambió la identidad del árbol auditado")


def check_validate(repo: Path) -> None:
    global checked
    stage = repo / "feature" / "01-snapshot"
    stage.mkdir(parents=True)
    (stage / "CONCILIACION.md").write_text(STAGE, encoding="utf-8")
    (stage / "TAREAS.md").write_text(TASKS, encoding="utf-8")
    audit = stage / "AUDIT.md"
    audit.write_text(AUDIT.format(snapshot="pendiente"), encoding="utf-8")

    # La aprobación existe antes de auditar y queda fuera del snapshot.
    approvals = repo / APPROVALS
    approvals.parent.mkdir(parents=True, exist_ok=True)
    approvals.write_text(
        f"- etapa: 01-snapshot\n  aprobado-por: Ana\n  fecha: 2026-10-23\n", encoding="utf-8"
    )
    snapshot = identity(repo, (Path("feature"), APPROVALS))
    audit.write_text(AUDIT.format(snapshot=snapshot), encoding="utf-8")

    checked += 1
    fresh = validate(stage, repo)
    if fresh.returncode != 0:
        fail(f"validate --repo: rechazó una pasada fresca: {fresh.stdout}{fresh.stderr}")

    # Sin aprobación humana la etapa no cierra, aunque el snapshot sea correcto.
    approvals.write_text("", encoding="utf-8")
    checked += 1
    unsigned = validate(stage, repo)
    if unsigned.returncode == 0:
        fail("validate --repo: aceptó el cierre sin aprobación humana")
    elif "ninguna aprobación humana" not in unsigned.stdout:
        fail(f"validate --repo: rechazó por otro motivo: {unsigned.stdout}")
    approvals.write_text(
        f"- etapa: 01-snapshot\n  aprobado-por: Ana\n  fecha: 2026-10-23\n", encoding="utf-8"
    )

    # Una aprobación con alcance que no cubre el snapshot no sirve.
    approvals.write_text(
        f"- etapa: 01-snapshot\n  aprobado-por: Ana\n  fecha: 2026-10-23\n  alcance: ffff\n",
        encoding="utf-8",
    )
    checked += 1
    out_of_scope = validate(stage, repo)
    if out_of_scope.returncode == 0:
        fail("validate --repo: una aprobación fuera de alcance cerró la etapa")
    approvals.write_text(
        f"- etapa: 01-snapshot\n  aprobado-por: Ana\n  fecha: 2026-10-23\n", encoding="utf-8"
    )

    # Una aprobación se ancla al árbol auditado, no al commit desde el que se
    # partió: firma con `alcance: tree=<sha>` y cubre la pasada aunque un commit
    # de documentos haya movido `head=`.
    tree = snapshot.split("tree=", 1)[1].split(" ", 1)[0]
    approvals.write_text(
        f"- etapa: 01-snapshot\n aprobado-por: Ana\n fecha: 2026-11-03\n alcance: tree={tree}\n",
        encoding="utf-8",
    )
    (stage / "AUDIT.md").write_text(
        AUDIT.format(snapshot=snapshot) + "\n## Pasada 2 — nota\n", encoding="utf-8"
    )
    git(repo, "add", "--", "feature/01-snapshot/AUDIT.md")
    git(repo, "commit", "-qm", "nota de la etapa")
    checked += 1
    signed_tree = validate(stage, repo)
    if signed_tree.returncode != 0:
        fail(
            "validate --repo: una firma por árbol no cubrió la pasada tras un "
            f"commit de documentos: {signed_tree.stdout}"
        )
    # El árbol se puede firmar en forma corta, como `git rev-parse --short`:
    # es lo que una persona escribe al leer `tree=152c3474` en la pasada.
    approvals.write_text(
        f"- etapa: 01-snapshot\n aprobado-por: Ana\n fecha: 2026-11-03\n alcance: tree={tree[:8]}\n",
        encoding="utf-8",
    )
    checked += 1
    short_tree = validate(stage, repo)
    if short_tree.returncode != 0:
        fail(
            "validate --repo: una firma con el árbol en forma corta no cubrió la pasada: "
            f"{short_tree.stdout}"
        )
    # Y un alcance con otro árbol no cubre.
    approvals.write_text(
        f"- etapa: 01-snapshot\n aprobado-por: Ana\n fecha: 2026-11-03\n alcance: tree={'0' * 40}\n",
        encoding="utf-8",
    )
    checked += 1
    wrong_tree = validate(stage, repo)
    if wrong_tree.returncode == 0:
        fail("validate --repo: una firma con otro árbol cerró la etapa")
    approvals.write_text(
        "- etapa: 01-snapshot\n aprobado-por: Ana\n fecha: 2026-10-23\n",
        encoding="utf-8",
    )
    # La pasada se vuelve a grabar sobre el árbol actual: la nota de la etapa
    # está excluida del árbol y el head ya no es el de la firma.
    snapshot = identity(repo, (Path("feature"), APPROVALS))
    audit.write_text(AUDIT.format(snapshot=snapshot), encoding="utf-8")

    (repo / "src.txt").write_text("tres\n", encoding="utf-8")
    checked += 1
    stale = validate(stage, repo)
    if stale.returncode == 0:
        fail("validate --repo: aceptó una pasada cuyo snapshot ya no coincide")
    elif "la pasada auditó" not in stale.stdout or "reauditar" not in stale.stdout:
        fail(f"validate --repo: falló por otro motivo: {stale.stdout}{stale.stderr}")

    current = identity(repo, (Path("feature"), APPROVALS))
    audit.write_text(AUDIT.format(snapshot=current), encoding="utf-8")
    checked += 1
    refreshed = validate(stage, repo)
    if refreshed.returncode != 0:
        fail(f"validate --repo: rechazó la pasada reauditada: {refreshed.stdout}{refreshed.stderr}")

    # B-27: un archivo que ninguna tarea declara es alcance nuevo, y el gate
    # vive en el validador, no solo en `diff_scope.py`.
    (repo / "colado.py").write_text("alcance nuevo\n", encoding="utf-8")
    current = identity(repo, (Path("feature"), APPROVALS))
    audit.write_text(AUDIT.format(snapshot=current), encoding="utf-8")
    checked += 1
    out_of_scope = validate(stage, repo)
    if out_of_scope.returncode == 0:
        fail("validate --repo: aceptó un archivo que ninguna tarea declara")
    elif "alcance nuevo" not in out_of_scope.stdout:
        fail(f"validate --repo: rechazó por otro motivo: {out_of_scope.stdout}")
    (repo / "colado.py").unlink()

    # B-27 con el trabajo commiteado: quien commitea antes de auditar deja
    # `git diff HEAD` vacío. El alcance se mide desde el commit que abrió la
    # etapa, así que lo commiteado sigue contando.
    git(repo, "add", "-A")
    git(repo, "commit", "-qm", "abrir la etapa")
    (repo / "src.txt").write_text("tres\n", encoding="utf-8")
    git(repo, "add", "-A")
    git(repo, "commit", "-qm", "cumplir la tarea")
    (repo / "commitado.py").write_text("alcance nuevo\n", encoding="utf-8")
    git(repo, "add", "-A")
    git(repo, "commit", "-qm", "colar un archivo")
    current = identity(repo, (Path("feature"), APPROVALS))
    audit.write_text(AUDIT.format(snapshot=current), encoding="utf-8")
    checked += 1
    committed_scope = validate(stage, repo)
    if committed_scope.returncode == 0:
        fail("validate --repo: aceptó trabajo commiteado que ninguna tarea declara")
    elif "commitado.py" not in committed_scope.stdout or "alcance nuevo" not in committed_scope.stdout:
        fail(f"validate --repo: rechazó por otro motivo: {committed_scope.stdout}")


def _plant_bytecode(repo: Path) -> None:
    cache = repo / "skills" / "feature-stages" / "scripts" / "__pycache__"
    cache.mkdir(parents=True)
    (cache / "snapshot.cpython-311.pyc").write_bytes(b"\x00bytecode")
    (cache / "diff_scope.cpython-311.pyc").write_bytes(b"\x00bytecode-2")
    (cache / "approvals.cpython-311.pyc").write_bytes(b"\x00bytecode-3")
    (repo / "legacy.pyc").write_bytes(b"\x00legacy")


def check_bytecode_ignored() -> None:
    """El bytecode no cambia el árbol auditado ni bloquea el cierre.

    Correr `validate_stage.py --repo` importa módulos hermanos y, si las
    skills viven dentro del repositorio y este no ignora `__pycache__`,
    escribe `*.pyc` antes de calcular la identidad. Sin excluirlos, la pasada
    que acaba de medirse queda obsoleta y el cruce pide declarar el artefacto.
    Un cambio en `src.txt` sigue invalidando la pasada: el gate no se apaga.
    """
    global checked
    repo = Path(tempfile.mkdtemp(prefix=".tmp-snapshot-pyc-"))
    try:
        init_repo(repo)
        stage = repo / "feature" / "01-snapshot"
        stage.mkdir(parents=True)
        (stage / "CONCILIACION.md").write_text(STAGE, encoding="utf-8")
        (stage / "TAREAS.md").write_text(TASKS, encoding="utf-8")
        (stage / "AUDIT.md").write_text(AUDIT.format(snapshot="pendiente"), encoding="utf-8")
        approvals = repo / APPROVALS
        approvals.parent.mkdir(parents=True)
        approvals.write_text(
            "- etapa: 01-snapshot\n  aprobado-por: Ana\n  fecha: 2026-11-13\n",
            encoding="utf-8",
        )
        git(repo, "add", "-A")
        git(repo, "commit", "-qm", "abre la etapa")
        before = identity(repo, (Path("feature"), APPROVALS))
        (stage / "AUDIT.md").write_text(AUDIT.format(snapshot=before), encoding="utf-8")

        _plant_bytecode(repo)
        checked += 1
        after = identity(repo, (Path("feature"), APPROVALS))
        if after != before:
            fail(
                "snapshot: un .pyc sin commitear cambió la identidad del árbol "
                f"auditado ({before!r} → {after!r})"
            )
        checked += 1
        fresh = validate(stage, repo)
        if fresh.returncode != 0:
            fail(
                "validate --repo: un .pyc sin commitear rechazó la pasada: "
                f"{fresh.stdout}{fresh.stderr}"
            )

        git(repo, "add", "-A")
        git(repo, "commit", "-qm", "bytecode colado")
        checked += 1
        committed = identity(repo, (Path("feature"), APPROVALS))
        if code_identity(committed) != code_identity(before):
            fail(
                "snapshot: commitear bytecode cambió la identidad del árbol "
                f"({code_identity(before)!r} → {code_identity(committed)!r})"
            )
        checked += 1
        still = validate(stage, repo)
        if still.returncode != 0:
            fail(
                "validate --repo: bytecode commiteado rechazó la pasada: "
                f"{still.stdout}{still.stderr}"
            )

        (repo / "src.txt").write_text("tres\n", encoding="utf-8")
        checked += 1
        changed = identity(repo, (Path("feature"), APPROVALS))
        if code_identity(changed) == code_identity(before):
            fail("snapshot: excluir el bytecode cegó un cambio de código")
        checked += 1
        stale = validate(stage, repo)
        text = stale.stdout + stale.stderr
        if stale.returncode == 0:
            fail("validate --repo: aceptó una pasada cuyo código cambió junto a un .pyc")
        elif ".pyc" in text or "__pycache__" in text:
            fail(f"validate --repo: el bytecode siguió contando al cambiar el código: {text}")
        elif "la pasada auditó" not in text:
            fail(f"validate --repo: falló por otro motivo: {text}")
    finally:
        shutil.rmtree(repo, ignore_errors=True)


def check_document_commit(repo: Path) -> None:
    """Commitea un documento de la etapa sin tocar el árbol auditado.

    Un commit que solo escribe dentro de las rutas excluidas —la etapa, el
    índice del panel, la aprobación— deja el mismo árbol de código en otro
    `head`. La identidad tiene que seguir siendo la misma: si el `head` entra
    en la comparación, cada corrección de documento invalida la pasada y pide
    reauditar un árbol que no cambió, que es lo que pasó en la etapa 07 del
    consumidor.
    """
    global checked
    stage = repo / "feature" / "01-snapshot"
    audit = stage / "AUDIT.md"
    audit.write_text("# Auditoría\n\nanotación\n", encoding="utf-8")
    (repo / ".yerro" / "approvals.yml").write_text(
        "- etapa: 01-snapshot\n aprobado-por: Ana\n fecha: 2026-11-03\n", encoding="utf-8"
    )
    git(repo, "add", "-A")
    git(repo, "commit", "-qm", "documento")
    document = identity(repo, (Path("feature"), APPROVALS))
    head_only = identity(repo, ())
    # Commit solo dentro de las excluidas: otra nota de la etapa.
    audit.write_text("# Auditoría\n\nanotación\nmás\n", encoding="utf-8")
    git(repo, "add", "-A")
    git(repo, "commit", "-qm", "otra anotación")
    same_tree = identity(repo, (Path("feature"), APPROVALS))
    checked += 1
    if head_only[:head_only.index(" tree=")] == same_tree[:same_tree.index(" tree=")]:
        fail("snapshot: la fixture no movió HEAD; no prueba lo que dice probar")
    checked += 1
    if code_identity(document) != code_identity(same_tree):
        fail(
            "snapshot: un commit que solo toca rutas excluidas cambió la identidad "
            f"({document!r} → {same_tree!r})"
        )
    # El `head=` grabado sigue describiendo de dónde se partió, pero no es la
    # identidad: el validador no rechaza el mismo árbol por otro commit.
    checked += 1
    if not same_identity(document, same_tree):
        fail(
            "validate: el mismo árbol en otro commit cuenta como pasada obsoleta "
            f"({document!r} → {same_tree!r})"
        )
    checked += 1
    if "solo cambió el commit de partida" not in snapshot_mismatch(document, same_tree):
        fail("validate: el mismo árbol en otro commit no se explica por el commit de partida")

    # Un commit que sí toca el código sigue invalidando la pasada.
    (repo / "src.txt").write_text("cuatro\n", encoding="utf-8")
    git(repo, "add", "-A")
    git(repo, "commit", "-qm", "código")
    code = identity(repo, (Path("feature"), APPROVALS))
    checked += 1
    if code_identity(code) == code_identity(same_tree):
        fail("snapshot: un commit de código dejó la identidad igual")
    checked += 1
    if same_identity(same_tree, code):
        fail("validate: un cambio de código no invalidó la pasada")
    checked += 1
    if "reauditar" not in snapshot_mismatch(document, code):
        fail("validate: un cambio de código no pide reauditar")


def check_delta_scope(repo: Path) -> None:
    """El archivo que produce un delta pertenece al alcance de la etapa.

    Un delta es la corrección que la auditoría escribió; si su tarea añade un
    archivo que la lista principal no nombra, ese archivo sigue estando dentro
    del alcance. Comprobar el cierre solo contra `TAREAS.md` impedía cerrar
    cualquier etapa corregida con un delta que añade archivo.
    """
    global checked
    stage = repo / "feature" / "02-delta"
    stage.mkdir(parents=True)
    (stage / "CONCILIACION.md").write_text(STAGE, encoding="utf-8")
    (stage / "TAREAS.md").write_text(TASKS, encoding="utf-8")
    audit = stage / "AUDIT.md"
    approvals = repo / APPROVALS
    approvals.parent.mkdir(parents=True, exist_ok=True)
    approvals.write_text(
        f"- etapa: 02-delta\n aprobado-por: Ana\n fecha: 2026-10-23\n", encoding="utf-8"
    )
    # La etapa se abre y se implementa, como haría un agente ordenado...
    git(repo, "add", "-A")
    git(repo, "commit", "-qm", "abrir la etapa 02")
    (repo / "src.txt").write_text("cuatro\n", encoding="utf-8")
    git(repo, "add", "-A")
    git(repo, "commit", "-qm", "implementar la etapa 02")
    # ...y el delta escribe un archivo que la lista principal no declara.
    (repo / "negativo.py").write_text("negativo\n", encoding="utf-8")
    (stage / "TAREAS-delta-01.md").write_text(DELTA, encoding="utf-8")
    audit.write_text(
        AUDIT.format(snapshot=identity(repo, (Path("feature"), APPROVALS))),
        encoding="utf-8",
    )
    checked += 1
    closed = validate(stage, repo)
    if closed.returncode != 0:
        fail(
            "validate --repo: el archivo declarado por un delta bloqueó el cierre "
            f"como alcance nuevo: {closed.stdout}"
        )
    # Un archivo que ningún delta declara sigue siendo alcance nuevo.
    (repo / "sobrante.py").write_text("de más\n", encoding="utf-8")
    audit.write_text(
        AUDIT.format(snapshot=identity(repo, (Path("feature"), APPROVALS))),
        encoding="utf-8",
    )
    checked += 1
    out_of_scope = validate(stage, repo)
    if out_of_scope.returncode == 0:
        fail("validate --repo: un delta absolvió un archivo que ninguna lista declara")
    elif "sobrante.py" not in out_of_scope.stdout:
        fail(f"validate --repo: rechazó por otro motivo: {out_of_scope.stdout}")
    (repo / "sobrante.py").unlink()


def check_missing_approval_exclusion(repo: Path) -> None:
    """Un snapshot sin la exclusión de `.yerro/approvals.yml` no coincide.

    El validador excluye siempre el archivo de aprobación. Si la pasada no lo
    excluyó, la identidad no coincide aunque el árbol sea el mismo, y reauditar
    no arregla nada: falta volver a tomar el snapshot. El mensaje debe decir eso
    y nombrar la exclusión, en los dos casos —con y sin el archivo ya escrito.
    """
    global checked
    stage = repo / "feature" / "01-snapshot"
    stage.mkdir(parents=True)
    (stage / "CONCILIACION.md").write_text(STAGE, encoding="utf-8")
    (stage / "TAREAS.md").write_text(TASKS, encoding="utf-8")
    audit = stage / "AUDIT.md"

    # Sin `.yerro/approvals.yml` en el repositorio: el árbol es el mismo y lo
    # único distinto es la lista de exclusiones. S62: la identidad es el árbol,
    # así que la pasada vale; la línea que no nombra la exclusión se avisa,
    # porque miente sobre cómo se calculó el árbol, pero no bloquea.
    snapshot = identity(repo, (Path("feature"),))
    audit.write_text(AUDIT.format(snapshot=snapshot), encoding="utf-8")
    checked += 1
    missing = validate(stage, repo)
    if "no excluye .yerro/approvals.yml" not in missing.stdout:
        fail(f"validate --repo: no avisó que la pasada no declara la exclusión: {missing.stdout}")
    # Y no bloquea por eso: el único error que queda es la firma que falta.
    blockers = [line for line in missing.stdout.splitlines() if line.startswith("ERROR:")]
    checked += 1
    if len(blockers) != 1 or "ninguna aprobación humana" not in blockers[0]:
        fail(
            "validate --repo: la lista de exclusiones sigue bloqueando un árbol idéntico: "
            f"{missing.stdout}"
        )

    # El flujo real escribe la aprobación antes de auditar. Si la pasada no
    # excluye el archivo, su árbol lo incluye y el actual no: el mensaje debe
    # nombrar la exclusión, porque reauditar con el mismo comando vuelve a
    # fallar.
    approvals = repo / APPROVALS
    approvals.parent.mkdir(parents=True, exist_ok=True)
    approvals.write_text(
        f"- etapa: 01-snapshot\n aprobado-por: Ana\n fecha: 2026-10-23\n", encoding="utf-8"
    )
    snapshot = identity(repo, (Path("feature"),))
    audit.write_text(AUDIT.format(snapshot=snapshot), encoding="utf-8")
    checked += 1
    signed = validate(stage, repo)
    if signed.returncode == 0:
        fail("validate --repo: aceptó un snapshot que no excluye la aprobación")
    elif "--exclude .yerro/approvals.yml" not in signed.stdout:
        fail(f"validate --repo: no nombró la exclusión que falta: {signed.stdout}")

    # Y con la exclusión el mismo árbol cierra: no es un gate más estricto, es
    # el mismo árbol con la lista correcta.
    audit.write_text(
        AUDIT.format(snapshot=identity(repo, (Path("feature"), APPROVALS))),
        encoding="utf-8",
    )
    checked += 1
    closed = validate(stage, repo)
    if closed.returncode != 0:
        fail(f"validate --repo: rechazó el snapshot con la exclusión correcta: {closed.stdout}")

def main() -> int:
    if shutil.which("git") is None:
        print("SKIP: git no está disponible")
        return 0
    with tempfile.TemporaryDirectory(prefix=".tmp-snapshot-", dir=REPO_ROOT) as raw:
        repo = Path(raw) / "repo"
        repo.mkdir()
        bare = Path(raw) / "no-git"
        bare.mkdir()
        init_repo(repo)
        check_stability(repo)
        check_exclude(repo, bare)
        check_panel_index_excluded(repo)
        check_validate(repo)
        check_document_commit(repo)
        check_whole_panel_excluded(repo)
        check_new_stage_does_not_invalidate(repo)
        check_delta_scope(repo)
        sin_exclusion = Path(raw) / "sin-exclusion"
        sin_exclusion.mkdir()
        init_repo(sin_exclusion)
        check_missing_approval_exclusion(sin_exclusion)
        check_bytecode_ignored()
    for error in errors:
        print(f"ERROR: {error}")
    if not errors:
        print(f"OK: {checked} comprobaciones de snapshot")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
