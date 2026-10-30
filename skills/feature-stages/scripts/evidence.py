#!/usr/bin/env python3
"""Ejecuta un comando y deja una firma estable de lo observado.

Uso: evidence.py run -- <comando...> [--label E-NN] [--json]
     evidence.py verify <audit.md> --repo <repo> [--json]

`run` ejecuta el comando y emite una línea de ledger con `exit`, la firma del
output normalizado y el timestamp. `verify` re-ejecuta lo que la última pasada
del `AUDIT.md` declaró y comprueba que la firma registrada corresponde a lo que
el comando produce ahora; las pasadas anteriores son historia y no se relanzan.
Los comandos son líneas de shell y se ejecutan con `/bin/sh -c`:
`cd console && npm test` y un argumento citado se reejecutan tal cual.
Un `|` dentro del comando se escribe `\|` en la fila (`run` lo hace) y se
deshace al reejecutar; una fila con el `|` crudo se nombra en vez de ejecutarse.

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
import shlex
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
    # `node --test` imprime el tiempo de cada caso y el total: cambian en cada
    # corrida correcta y, sin normalizarlos, la firma de un test verde nunca
    # reproduce (`firma=609cb154…` y `firma=b0d2e450…` del mismo comando).
    (re.compile(r"\(\d+(?:\.\d+)?\s?m?s\)"), "(<dur>)"),
    (re.compile(r"\bduration_ms[: ]\s*\d+(?:\.\d+)?\b"), "duration_ms <dur>"),
)

LEDGER_ROW_RE = re.compile(r"^\s*\|\s*(E-\d+)\s*\|(.*)$")
PASS_RE = re.compile(r"^##\s+Pasada\b.*$", re.M | re.I)


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


def command_text(command: list[str] | str) -> str:
    """Línea de shell que se ejecuta y que viaja al ledger.

    Una cadena es una línea de shell y se usa tal cual —`cd console && npm test`
    o un argumento ya citado—. Una lista es un argv y se vuelve a citar: sin
    eso, `--test-name-pattern "panel chat"` perdía las comillas y la fila del
    ledger ya no se podía reejecutar.
    """
    if isinstance(command, str):
        return command.strip()
    parts = [str(part) for part in command]
    if len(parts) == 1:
        return parts[0].strip()
    return shlex.join(parts)

def run_command(command: list[str] | str) -> tuple[int, str, str]:
    text = command_text(command)
    if not text:
        raise EvidenceError("falta el comando después de --")
    try:
        # Las filas del ledger son líneas de shell: `cd console && npm test` y
        # los argumentos citados tienen que reejecutarse como se escribieron.
        done = subprocess.run(
            ["/bin/sh", "-c", text], capture_output=True, text=True, timeout=900
        )
    except FileNotFoundError:
        raise EvidenceError(f"comando no encontrado: {text}") from None
    except subprocess.TimeoutExpired:
        raise EvidenceError(f"el comando superó el tiempo máximo: {text}") from None
    if done.returncode == 127 and "not found" in done.stderr:
        raise EvidenceError(f"comando no encontrado: {text}")
    return done.returncode, done.stdout, done.stderr


def ledger_row(label: str, command: list[str], exit_code: int, digest: str) -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M")
    text = command_text(command)
    return (
        f"| {label} | CA-… | `{escape_cell(text)}` | revertir → rojo → restaurar "
        f"| verde | exit={exit_code} firma={digest} | local; {stamp} | ninguno | ninguna |"
    )


COMMAND_HEADER_RE = re.compile(r"procedimiento|comando", re.I)

# B-47: la celda del ledger es una celda de tabla markdown: un `|` crudo la corta y
# `verify` acaba ejecutando un fragmento, con un exit que nadie corrió. Se
# escribe `\|` y se deshace al reejecutar.
CELL_SPLIT_RE = re.compile(r"(?<!\\)\|")


def escape_cell(text: str) -> str:
    """Texto seguro dentro de una celda de tabla."""
    return text.replace("|", "\\|")


def unescape_cell(text: str) -> str:
    """Deshace `escape_cell`: devuelve el comando que se escribió."""
    return text.replace("\\|", "|")


def split_cells(line: str) -> list[str]:
    """Celdas de una fila, sin romper por un `|` escapado."""
    return [cell.strip() for cell in CELL_SPLIT_RE.split(line.strip().strip("|"))]


def header_cells(audit: str) -> int:
    """Número de celdas del encabezado del ledger, o 0 si no hay encabezado."""
    for line in audit.splitlines():
        if line.strip().startswith("|") and COMMAND_HEADER_RE.search(line):
            return len(split_cells(line))
    return 0


def truncated_rows(audit: str) -> list[str]:
    """Filas `E-NN` que no tienen las celdas del encabezado.

    Es la firma de un `|` sin escapar en una celda: la fila se parte, `verify`
    leería un fragmento de comando y el `exit` registrado no se reproduciría.
    """
    expected = header_cells(audit)
    if not expected:
        return []
    rotas: list[str] = []
    for line in audit.splitlines():
        match = LEDGER_ROW_RE.match(line)
        if not match:
            continue
        if len(split_cells(line)) != expected:
            rotas.append(match.group(1))
    return rotas

def command_column(audit: str) -> int | None:
    """Índice de la columna `Procedimiento/comando`, leído del encabezado.

    Sin el encabezado, la heurística de «la primera celda con un espacio»
    adivinaba: una celda `CA-01, CA-03` escrita con coma se leía como comando.
    """
    for line in audit.splitlines():
        if "|" not in line:
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        for index, cell in enumerate(cells):
            if COMMAND_HEADER_RE.search(cell):
                return index
    return None

def parse_ledger(audit: str) -> list[tuple[str, str, str, str | None]]:
    """(id, comando, exit, firma) de cada fila E-NN con firma registrada."""
    entries: list[tuple[str, str, str, str | None]] = []
    column = command_column(audit)
    for line in audit.splitlines():
        match = LEDGER_ROW_RE.match(line)
        if not match:
            continue
        label = match.group(1)
        cells = split_cells(line)
        command = ""
        if column is not None and column < len(cells) and column >= 2:
            command = unescape_cell(cells[column].strip("`").strip())
        else:
            for cell in cells[2:]:
                candidate = cell.strip("`").strip()
                if candidate and (
                    " " in candidate
                    or candidate.startswith(("pytest", "npm", "go", "cargo", "make"))
                ):
                    command = candidate
                    break
        exit_match = re.search(r"exit=(-?\d+)", line)
        signature_match = re.search(r"firma=([0-9a-f]{6,64})", line, re.I)
        entries.append(
            (
                label,
                command,
                exit_match.group(1) if exit_match else "",
                signature_match.group(1) if signature_match else None,
            )
        )
    return entries


def last_pass(audit: str) -> str:
    """Texto de la última pasada del `AUDIT.md`.

    Las pasadas anteriores son historia: reejecutarlas vuelve a lanzar
    procedimientos que ya ocurrieron —un `kill -9` al runtime, por ejemplo— y
    una pasada superada no decide el cierre. Sin encabezado `## Pasada`, el
    archivo entero es una sola pasada.
    """
    matches = list(PASS_RE.finditer(audit))
    if not matches:
        return audit
    return audit[matches[-1].start():]

def verify(audit_text: str) -> list[str]:
    """Reejecuta cada evidencia firmada de la pasada que cierra."""
    problems: list[str] = []
    pass_text = last_pass(audit_text)
    for label in truncated_rows(pass_text):
        problems.append(
            f"{label}: la fila se partió; un `|` sin escapar en una celda la corta: "
            "escríbelo `\\|` (lo hace `evidence.py run`)"
        )
    entries = parse_ledger(pass_text)
    if not entries:
        raise EvidenceError("la pasada no tiene filas E-NN con evidencia")
    for label, command, declared_exit, declared_signature in entries:
        if not command:
            problems.append(f"{label}: no declara comando")
            continue
        try:
            exit_code, stdout, stderr = run_command(command)
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
