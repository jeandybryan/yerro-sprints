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

import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from evidence import ( # noqa: E402
    EvidenceError,
    ledger_row,
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


def audit_with(command: list[str], digest: str, exit_code: int) -> str:
    row = ledger_row("E-01", command, exit_code, digest)
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
    check_cli()
    for error in errors:
        print(f"ERROR: {error}")
    if not errors:
        print(f"OK: {checked} comprobaciones de evidencia")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
