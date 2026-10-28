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

from snapshot import SnapshotError, identity  # noqa: E402

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
    # único distinto es la lista de exclusiones.
    snapshot = identity(repo, (Path("feature"),))
    audit.write_text(AUDIT.format(snapshot=snapshot), encoding="utf-8")
    checked += 1
    missing = validate(stage, repo)
    if missing.returncode == 0:
        fail("validate --repo: aceptó un snapshot sin excluir .yerro/approvals.yml")
    elif "no hace falta reauditar" not in missing.stdout:
        fail(f"validate --repo: no explicó que solo falta reexcluir: {missing.stdout}")

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
        check_validate(repo)
        check_delta_scope(repo)
        sin_exclusion = Path(raw) / "sin-exclusion"
        sin_exclusion.mkdir()
        init_repo(sin_exclusion)
        check_missing_approval_exclusion(sin_exclusion)
    for error in errors:
        print(f"ERROR: {error}")
    if not errors:
        print(f"OK: {checked} comprobaciones de snapshot")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
