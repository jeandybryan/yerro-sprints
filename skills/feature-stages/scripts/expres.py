#!/usr/bin/env python3
"""Decide si un cambio cabe en la vía exprés, sin abrir etapa.

Uso: expres.py <repo> [--base REF] [--json]

Lee un diff de git y responde `cabe` o `no cabe` con el motivo concreto.
Comprueba lo mecánico: archivos de producción, líneas de producción, rutas
excluidas y manifiestos de dependencias. Incluye los archivos nuevos sin
trackear: si no se contaran, bastaría con no añadirlos para saltarse la
frontera. No puede leer del diff un criterio de aceptación nuevo ni un cambio
de interfaz pública: eso queda en la tabla de `EXPRES.md` y en las reglas de
la skill, y se reporta como pendiente de confirmar a mano.

Las pruebas no consumen presupuesto: un cambio con su test es un buen cambio,
no un cambio grande.

Salida: 0 si cabe; 1 si no cabe; 2 si el diff no se puede leer.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

MAX_FILES = 1
MAX_LINES = 20

TEST_RE = re.compile(
    r"(^|/)(tests?|specs?|__tests__)/"
    r"|(^|/)test_[^/]+$"
    r"|/test_[^/]*\.\w+$"
    r"|_test\.(go|py|rb)$"
    r"|\.(test|spec)\.[cm]?[jt]sx?$"
)

# Categorías que nunca caben en la vía exprés, por ruta. Un cambio que las
# toca abre etapa, sin importar cuántas líneas tenga. Las reglas de directorio
# van antes que las de extensión: `contracts/pedido.proto` es un contrato
# compartido, no un esquema suelto.
EXCLUDED = (
    ("migración", r"(^|/)migrations?/"),
    ("seguridad o auth", r"(^|/)(auth|security|crypto|secrets?)/"),
    ("contrato compartido", r"(^|/)(contracts?|openapi|idl)/|openapi\.(ya?ml|json)$"),
    (
        "manifiesto de dependencias",
        r"(^|/)(package\.json|requirements[^/]*\.txt|pyproject\.toml|setup\.(py|cfg)"
        r"|go\.mod|Cargo\.toml|Gemfile|pom\.xml|build\.gradle(\.kts)?)$",
    ),
    ("esquema", r"(^|/)(schemas?|proto)/|\.(sql|proto|avsc|graphql)$"),
)

HAND_CHECK = (
    "sin criterio de aceptación nuevo",
    "sin cambio de interfaz pública",
)


class ExpressError(Exception):
    """El diff no se puede leer."""


def production(path: str) -> bool:
    """Una ruta es de producción si no es una prueba."""
    candidate = path[2:] if path.startswith("b/") else path
    return not TEST_RE.search("/" + candidate)


def excluded_reason(path: str) -> str | None:
    candidate = "/" + (path[2:] if path.startswith("b/") else path)
    for label, pattern in EXCLUDED:
        if re.search(pattern, candidate, re.I):
            return label
    return None


def changed(repo: Path, base: str) -> list[tuple[str, int, int]]:
    """Rutas cambiadas con líneas añadidas y borradas, según `git diff --numstat`."""
    result = subprocess.run(
        ["git", "-C", str(repo), "diff", "--numstat", "--no-renames", base],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise ExpressError(
            f"no se puede leer el diff contra {base!r}: {result.stderr.strip() or 'base desconocida'}"
        )
    rows: list[tuple[str, int, int]] = []
    for line in result.stdout.splitlines():
        parts = line.split("\t")
        if len(parts) != 3:
            continue
        added, deleted, path = parts
        rows.append(
            (
                path,
                int(added) if added.isdigit() else 0,
                int(deleted) if deleted.isdigit() else 0,
            )
        )
    return rows + untracked(repo, {path for path, _, _ in rows})


def untracked(repo: Path, seen: set[str]) -> list[tuple[str, int, int]]:
    """Archivos nuevos que todavía no están en el índice de git.

    `git diff --numstat` los ignora. Se cuentan como líneas añadidas para que
    un archivo nuevo no esquive el límite por no haber sido añadido antes de
    ejecutar la comprobación.
    """
    result = subprocess.run(
        ["git", "-C", str(repo), "ls-files", "--others", "--exclude-standard", "-z"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise ExpressError(
            f"no se pueden listar los archivos nuevos: {result.stderr.strip() or 'git falló'}"
        )
    rows: list[tuple[str, int, int]] = []
    for path in result.stdout.split("\0"):
        if not path or path in seen:
            continue
        try:
            text = (repo / path).read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        rows.append((path, len(text.splitlines()), 0))
    return rows


def evaluate(rows: list[tuple[str, int, int]]) -> dict:
    """Veredicto de la frontera exprés sobre un conjunto de cambios."""
    production_rows = [row for row in rows if production(row[0])]
    test_rows = [row for row in rows if not production(row[0])]
    files = len(production_rows)
    lines = sum(added + deleted for _, added, deleted in production_rows)
    test_lines = sum(added + deleted for _, added, deleted in test_rows)

    motivos: list[dict[str, str]] = []
    if files > MAX_FILES:
        names = ", ".join(path for path, _, _ in production_rows)
        motivos.append(
            {
                "codigo": "ARCHIVOS",
                "mensaje": f"{files} archivos de producción (máximo {MAX_FILES}): {names}",
            }
        )
    if lines > MAX_LINES:
        motivos.append(
            {
                "codigo": "LINEAS",
                "mensaje": f"{lines} líneas de producción (máximo {MAX_LINES})",
            }
        )
    for path, _, _ in production_rows:
        label = excluded_reason(path)
        if label:
            motivos.append(
                {"codigo": "RUTA_EXCLUIDA", "mensaje": f"{path} toca {label}"}
            )

    return {
        "cabe": not motivos,
        "resultado": "no cabe" if motivos else "cabe",
        "archivos_produccion": files,
        "lineas_produccion": lines,
        "archivos_prueba": len(test_rows),
        "lineas_prueba": test_lines,
        "motivos": motivos,
        "limites": {"archivos": MAX_FILES, "lineas": MAX_LINES},
        "confirmar_a_mano": list(HAND_CHECK) if not motivos else [],
    }


def render(report: dict) -> str:
    lines = [f"Resultado: {report['resultado']}"]
    lines.append(
        f"Producción: {report['archivos_produccion']} archivo(s), "
        f"{report['lineas_produccion']} línea(s) "
        f"(máx. {report['limites']['archivos']} archivo / {report['limites']['lineas']} líneas)"
    )
    if report["archivos_prueba"]:
        lines.append(
            f"Pruebas: {report['archivos_prueba']} archivo(s), "
            f"{report['lineas_prueba']} línea(s) (no cuentan)"
        )
    for motivo in report["motivos"]:
        lines.append(f" - [{motivo['codigo']}] {motivo['mensaje']}")
    if report["cabe"]:
        lines.append(
            "Confirmar a mano: " + "; ".join(report["confirmar_a_mano"])
        )
        lines.append("Decisión: registrar la línea en EXPRES.md; no abre etapa")
    else:
        lines.append("Decisión: abre etapa; registrar el motivo en la conciliación")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("repo", type=Path, nargs="?", default=Path("."))
    parser.add_argument("--base", default="HEAD", help="referencia contra la que comparar (por defecto HEAD)")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    try:
        report = evaluate(changed(args.repo.resolve(), args.base))
    except ExpressError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(render(report))
    return 0 if report["cabe"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
