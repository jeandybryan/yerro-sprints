#!/usr/bin/env python3
"""Prueba la evidencia ejecutable (`evidence.py`).

Uso: test_evidence.py

Comprueba que la firma depende de lo observado y no del formato: misma salida,
misma firma; salida distinta o exit distinto, firma distinta; y que lo volátil
(timestamps, puertos, rutas temporales) no rompe la firma. Después verifica que
`verify` acepta una auditoría real y rechaza una transcripción inventada.

Solo stdlib; no consume tokens.
"""
from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from evidence import ( # noqa: E402
    EvidenceError,
    ledger_row,
    parse_ledger,
    truncated_rows,
    normalize,
    run_command,
    signature,
    verify,
)

errors: list[str] = []
checked = 0


def fail(message: str) -> None:
    errors.append(message)


def check(condition: bool, message: str) -> None:
    global checked
    checked += 1
    if not condition:
        fail(message)


def check_signature() -> None:
    same = signature(0, "verde\n", "")
    check(same == signature(0, "verde\n", ""), "la firma no es estable")
    check(signature(0, "verde\n", "") != signature(1, "verde\n", ""), "la firma ignora el exit")
    check(signature(0, "verde\n", "") != signature(0, "rojo\n", ""), "la firma ignora el output")
    check(signature(0, "verde\n", "") != signature(0, "verde\n", "warn"), "la firma ignora stderr")
    # Formato: espacios finales y líneas vacías no son observación.
    check(
        signature(0, "a\nb\n", "") == signature(0, "a  \n\nb\n\n", ""),
        "la firma distingue ruido de formato",
    )
    # Volátil: lo que cambia en cada ejecución no debe romper la firma.
    first = "ok 2026-10-22T10:00:00Z pid=1001 en /tmp/tmpabc123"
    second = "ok 2026-10-22T10:00:05Z pid=2002 en /tmp/tmpzzz999"
    check(
        signature(0, first, "") == signature(0, second, ""),
        "la firma incluye lo volátil (timestamp, pid, ruta temporal)",
    )
    check("2026-10-22" not in normalize(first), "normalize no sustituye el timestamp")
# Tiempos de `node --test`: cambian en cada corrida correcta y no son
# observación. Sin normalizarlos, la firma de un test verde nunca reproduce.
slow = "ok caso (12.345678ms)\nℹ duration_ms 95288.974833"
fast = "ok caso (0.128ms)\nℹ duration_ms 120.5"
check(signature(0, slow, "") == signature(0, fast, ""), "la firma incluye el tiempo de cada caso")
check("ms)" not in normalize(slow), "normalize no sustituye el tiempo por caso")


def check_run() -> None:
    exit_code, stdout, _ = run_command([sys.executable, "-c", "print('verde'); raise SystemExit(3)"])
    check(exit_code == 3, f"exit no capturado: {exit_code}")
    check(stdout.strip() == "verde", f"stdout no capturado: {stdout!r}")
    try:
        run_command(["__no_existe_este_comando__"])
        fail("un comando inexistente no falló")
    except EvidenceError:
        pass
    try:
        run_command([])
        fail("un comando vacío no falló")
    except EvidenceError:
        pass


def audit_with(
    command: list[str] | str, digest: str, exit_code: int, ca: str = "CA-…"
) -> str:
    row = ledger_row("E-01", command, exit_code, digest).replace("| CA-… |", f"| {ca} |", 1)
    return (
        "# Auditoría\n\n### Ledger de evidencia\n\n"
        "| ID | CA | Procedimiento/comando | Sensibilidad | Esperado | Observado/exit | Entorno y timestamp | Artefacto/log | Limitación |\n"
        "|----|----|------------------------|--------------|----------|----------------|---------------------|---------------|------------|\n"
        f"{row}\n"
    )


def check_verify() -> None:
    command = [sys.executable, "-c", "print('estable')"]
    with tempfile.TemporaryDirectory() as tmp:
        target = Path(tmp) / "AUDIT.md"
        exit_code, stdout, stderr = run_command(command)
        digest = signature(exit_code, stdout, stderr)

        target.write_text(audit_with(command, digest, exit_code), encoding="utf-8")
        check(verify(target.read_text()) == [], "verify rechazó una evidencia que se reproduce")

        invented = audit_with(command, "000000000000", exit_code)
        check(bool(verify(invented)), "verify aceptó una firma inventada")

        wrong_exit = audit_with(command, digest, 9)
        check(bool(verify(wrong_exit)), "verify aceptó un exit que no ocurrió")

        other = audit_with([sys.executable, "-c", "print('otra cosa')"], digest, exit_code)
        check(bool(verify(other)), "verify aceptó un comando que no produce esa firma")

    try:
        verify("# Auditoría sin ledger\n")
        fail("verify aceptó una auditoría sin evidencia")
    except EvidenceError:
        pass


def check_pipe_in_command() -> None:
    """Una fila con `|` en el comando se parte al pegarla en el ledger.

    La celda de comando es una celda de tabla markdown: un `|` crudo la corta,
    `verify` lee un fragmento, lo ejecuta y reporta un `exit` que nadie corrió.
    `run` escapa el `|` como `\|` y el parser lo devuelve al ejecutar; una fila
    escrita a mano con el `|` crudo se detecta y se nombra, en vez de ejecutar
    basura.
    """
    command = "printf 'a|b\\n' | wc -l"
    row = ledger_row("E-42", command, 0, "abc123def456")
    check("\\|" in row, f"ledger_row no escapó el `|` del comando: {row}")

    audit = (
        "| ID | CA | Procedimiento/comando | Sensibilidad | Esperado | Observado/exit | "
        "Entorno | Artefacto | Limitación |\n"
        "|----|----|------------------------|--------------|----------|----------------|"
        "--------|-----------|------------|\n"
        + row
        + "\n"
    )
    entries = parse_ledger(audit)
    check(len(entries) == 1, f"parse_ledger no leyó la fila escapada: {entries}")
    if entries:
        check(
            entries[0][1] == command,
            f"parse_ledger no devolvió el comando original: {entries[0][1]!r}",
        )
    check(not truncated_rows(audit), f"una fila escapada se leyó como partida: {audit}")

    # La fila escapada se reejecuta de verdad.
    directory = Path(tempfile.mkdtemp(prefix="yerro-evidence-pipe-"))
    try:
        (directory / "AUDIT.md").write_text(audit.replace("abc123def456", ""), encoding="utf-8")
        problems = verify((directory / "AUDIT.md").read_text(encoding="utf-8"))
        check(not problems, f"verify no reejecutó una fila con `|`: {problems}")
    finally:
        shutil.rmtree(directory, ignore_errors=True)

    # Una fila con el `|` crudo declara más celdas que el encabezado: se nombra.
    cruda = row.replace("\\|", "|")
    check(
        bool(truncated_rows(audit.replace(row, cruda))),
        "una fila con `|` crudo no se detectó como partida",
    )


def check_reproducible_rows() -> None:
    """La fila que `run` emite tiene que poder reejecutarse tal cual."""
    # Un argumento con espacio no puede perder las comillas al escribirse en el
    # ledger: `--test-name-pattern "panel chat"` se leía como dos argumentos y
    # la fila dejaba de reproducirse.
    spaced = [sys.executable, "-c", "print('con espacio')"]
    exit_code, stdout, stderr = run_command(spaced)
    digest = signature(exit_code, stdout, stderr)
    text = audit_with(spaced, digest, exit_code)
    check(
        verify(text) == [],
        "verify rechazó una fila con un argumento citado (el ledger perdió las comillas): "
        f"{verify(text)}",
    )

    # Una línea de shell con `cd … && …`, la forma de `**Suites de referencia:**`.
    with tempfile.TemporaryDirectory() as tmp:
        (Path(tmp) / "marca.txt").write_text("dentro\n", encoding="utf-8")
        line = f"cd {tmp} && tail -n 1 marca.txt"
        try:
            exit_code, stdout, stderr = run_command(line)
        except EvidenceError as error:
            fail(f"la línea de shell no se pudo ejecutar: {error}")
            exit_code, stdout, stderr = 1, "", str(error)
        check(
            exit_code == 0 and stdout.strip() == "dentro",
            f"la línea de shell no se ejecutó en su directorio: {exit_code} {stdout!r} {stderr!r}",
        )
        digest = signature(exit_code, stdout, stderr)
        audit = audit_with(line, digest, exit_code)
        check(verify(audit) == [], f"verify rechazó una línea de shell: {verify(audit)}")

    # La celda `CA` escrita con coma no es el comando: manda el encabezado.
    command = [sys.executable, "-c", "print('otra')"]
    exit_code, stdout, stderr = run_command(command)
    digest = signature(exit_code, stdout, stderr)
    typed = audit_with(command, digest, exit_code, ca="CA-01, CA-03")
    check(verify(typed) == [], f"verify leyó la celda CA como comando: {verify(typed)}")


def check_last_pass() -> None:
    """`verify` reejecuta la pasada que decide, no el histórico."""
    command = [sys.executable, "-c", "print('cierre')"]
    exit_code, stdout, stderr = run_command(command)
    digest = signature(exit_code, stdout, stderr)
    current = audit_with(command, digest, exit_code)
    row = next(line for line in current.splitlines() if line.startswith("| E-01"))
    stale = (
        "| E-01 | CA-01 | `/herramienta/que/ya/no/existe --bandera` | "
        "revertir → rojo → restaurar | verde | exit=0 firma=000000000000 | local | ninguno | ninguna |"
    )
    history = (
        "# Auditoría\n\n## Pasada 1 — 2026-09-30\n\n"
        "| ID | CA | Procedimiento/comando | Sensibilidad | Esperado | Observado/exit | Entorno y timestamp | Artefacto/log | Limitación |\n"
        "|----|----|------------------------|--------------|----------|----------------|---------------------|---------------|------------|\n"
        f"{stale}\n\n## Pasada 2 — 2026-10-01\n\n"
        "| ID | CA | Procedimiento/comando | Sensibilidad | Esperado | Observado/exit | Entorno y timestamp | Artefacto/log | Limitación |\n"
        "|----|----|------------------------|--------------|----------|----------------|---------------------|---------------|------------|\n"
        f"{row}\n"
    )
    problems = verify(history)
    check(
        problems == [],
        "verify relanzó una pasada anterior (`/herramienta/que/ya/no/existe`): "
        f"{problems}",
    )
    broken = history.replace(f"firma={digest}", "firma=000000000000", 1)
    check(bool(verify(broken)), "verify no reporta una firma falsa de la última pasada")


def check_cli() -> None:
    run = subprocess.run(
        [sys.executable, str(HERE / "evidence.py"), "run", "--label", "E-02", "--json",
         "--", sys.executable, "-c", "print('cli')"],
        capture_output=True,
        text=True,
    )
    check(run.returncode == 0, f"evidence run: salida {run.returncode}: {run.stderr}")
    check('"firma"' in run.stdout and "E-02" in run.stdout, f"evidence run --json: {run.stdout}")

    missing = subprocess.run(
        [sys.executable, str(HERE / "evidence.py"), "run", "--", "__no_existe__"],
        capture_output=True,
        text=True,
    )
    check(missing.returncode == 2, f"evidence run con comando inexistente: salida {missing.returncode}")


def main() -> int:
    check_signature()
    check_run()
    check_verify()
    check_reproducible_rows()
    check_pipe_in_command()
    check_last_pass()
    check_cli()
    for error in errors:
        print(f"ERROR: {error}")
    if not errors:
        print(f"OK: {checked} comprobaciones de evidencia")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
