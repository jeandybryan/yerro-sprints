#!/usr/bin/env python3
"""Ejecuta un comando y deja una firma estable de lo observado.

Uso: evidence.py run -- <comando...> [--label E-NN] [--json]
     evidence.py verify <audit.md> --repo <repo> [--json]

`run` ejecuta el comando y emite una línea de ledger con `exit`, la firma del
output normalizado y el timestamp. `verify` re-ejecuta lo que la auditoría
declaró y comprueba que la firma registrada corresponde a lo que el comando
produce ahora.

Por qué existe: un ledger escrito a mano dice lo que el agente recuerda. La
firma dice lo que el comando produjo. Si no coinciden, la evidencia es
`no verificado`, no `cumple`.

Salida de `run`: la línea del ledger, lista para pegar en `AUDIT.md`.
Salida de `verify`: 0 si toda evidencia citada se reproduce; 1 si alguna no.

Solo stdlib. No consume tokens.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path

# Las líneas volátiles rompen la firma sin dejar de ser observaciones válidas:
# timestamps, puertos, rutas temporales. Se normalizan antes de firmar.
VOLATILE = (
    (re.compile(r"\b\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z?\b"), "<ts>"),
    (re.compile(r"\b\d{2}:\d{2}:\d{2}(?:\.\d+)?\b"), "<hora>"),
    (re.compile(r"/private/var/folders/\S+|/tmp/\S+|/var/folders/\S+"), "<tmp>"),
    (re.compile(r"\b0x[0-9a-f]{6,}\b", re.I), "<addr>"),
    (re.compile(r"\b(?:pid|PID)[:= ]\d+\b"), "<pid>"),
    (re.compile(r"\b\d+\.\d+s\b"), "<dur>"),
)

LEDGER_ROW_RE = re.compile(r"^\s*\|\s*(E-\d+)\s*\|(.*)$")


class EvidenceError(Exception):
    """El comando no se pudo ejecutar o la auditoría no se pudo leer."""


def normalize(text: str) -> str:
    """Quita lo volátil y colapsa el ruido de formato."""
    for pattern, replacement in VOLATILE:
        text = pattern.sub(replacement, text)
    lines = [line.rstrip() for line in text.replace("\r\n", "\n").split("\n")]
    return "\n".join(line for line in lines if line.strip())


def signature(exit_code: int, stdout: str, stderr: str) -> str:
    """Firma de lo observado: mismo exit, mismo output normalizado, misma firma."""
    payload = f"{exit_code}\n{normalize(stdout)}\n{normalize(stderr)}"
    return sha256(payload.encode("utf-8")).hexdigest()[:12]


def run_command(command: list[str]) -> tuple[int, str, str]:
    if not command:
        raise EvidenceError("falta el comando después de --")
    try:
        done = subprocess.run(
            command, capture_output=True, text=True, timeout=900
        )
    except FileNotFoundError:
        raise EvidenceError(f"comando no encontrado: {command[0]}") from None
    except subprocess.TimeoutExpired:
        raise EvidenceError(f"el comando superó el tiempo máximo: {' '.join(command)}") from None
    return done.returncode, done.stdout, done.stderr


def ledger_row(label: str, command: list[str], exit_code: int, digest: str) -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M")
    text = " ".join(command)
    return (
        f"| {label} | CA-… | `{text}` | revertir → rojo → restaurar "
        f"| verde | exit={exit_code} firma={digest} | local; {stamp} | ninguno | ninguna |"
    )


def parse_ledger(audit: str) -> list[tuple[str, str, str, str | None]]:
    """(id, comando, exit, firma) de cada fila E-NN con firma registrada."""
    entries: list[tuple[str, str, str, str | None]] = []
    for line in audit.splitlines():
        match = LEDGER_ROW_RE.match(line)
        if not match:
            continue
        label, rest = match.group(1), match.group(2)
        cells = [cell.strip() for cell in rest.split("|")]
        command = ""
        for cell in cells:
            candidate = cell.strip("`").strip()
            if candidate and (
                " " in candidate
                or candidate.startswith(("pytest", "npm", "go", "cargo", "make"))
            ):
                command = candidate
                break
        exit_match = re.search(r"exit=(-?\d+)", rest)
        signature_match = re.search(r"firma=([0-9a-f]{6,64})", rest, re.I)
        entries.append(
            (
                label,
                command,
                exit_match.group(1) if exit_match else "",
                signature_match.group(1) if signature_match else None,
            )
        )
    return entries


def verify(audit_text: str) -> list[str]:
    """Reejecuta cada evidencia firmada; devuelve las discrepancias."""
    problems: list[str] = []
    entries = parse_ledger(audit_text)
    if not entries:
        raise EvidenceError("la auditoría no tiene filas E-NN con evidencia")
    for label, command, declared_exit, declared_signature in entries:
        if not command:
            problems.append(f"{label}: no declara comando")
            continue
        try:
            exit_code, stdout, stderr = run_command(command.split())
        except EvidenceError as error:
            problems.append(f"{label}: {error}")
            continue
        if declared_exit and str(exit_code) != declared_exit:
            problems.append(
                f"{label}: exit {exit_code}, la auditoría registró {declared_exit}"
            )
        if declared_signature:
            current = signature(exit_code, stdout, stderr)
            if current != declared_signature:
                problems.append(
                    f"{label}: firma {current}, la auditoría registró {declared_signature}"
                )
    return problems


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="action", required=True)

    run_parser = sub.add_parser("run", help="ejecuta y firma")
    run_parser.add_argument("--label", default="E-NN")
    run_parser.add_argument("--json", action="store_true")
    run_parser.add_argument("command", nargs=argparse.REMAINDER)

    verify_parser = sub.add_parser("verify", help="reejecuta lo declarado")
    verify_parser.add_argument("audit", type=Path)
    verify_parser.add_argument("--json", action="store_true")

    args = parser.parse_args(argv)

    if args.action == "run":
        command = args.command[1:] if args.command and args.command[0] == "--" else args.command
        try:
            exit_code, stdout, stderr = run_command(command)
        except EvidenceError as error:
            print(f"ERROR: {error}", file=sys.stderr)
            return 2
        digest = signature(exit_code, stdout, stderr)
        row = ledger_row(args.label, command, exit_code, digest)
        if args.json:
            print(json.dumps({"exit": exit_code, "firma": digest, "fila": row}, ensure_ascii=False))
        else:
            print(row)
        return 0

    audit_path = args.audit
    if not audit_path.exists():
        print(f"ERROR: no existe {audit_path}", file=sys.stderr)
        return 2
    try:
        problems = verify(audit_path.read_text(encoding="utf-8"))
    except EvidenceError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps({"fallos": problems, "ok": not problems}, ensure_ascii=False))
    elif problems:
        for problem in problems:
            print(f"ERROR: {problem}")
        print("Veredicto: no verificado (la evidencia no se reproduce)")
    else:
        print("OK: toda la evidencia citada se reproduce")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
