#!/usr/bin/env python3
"""Lee las aprobaciones humanas del repositorio consumidor.

Uso: approvals.py <repo> [--path RUTA] [--stage NN] [--json]

La aprobación **no** vive en el artefacto de la etapa: un `**Aprobado por:**`
que el agente puede escribir no protege de nada. Vive en un archivo versionado
del repositorio consumidor, fuera del árbol de la etapa y fuera de lo que el
agente edita:

```yaml
# .yerro/approvals.yml
- etapa: 01-export
  aprobado-por: Ana Ruiz
  fecha: 2026-10-22
  alcance: 3f9c1e2
```

`fecha` es la fecha de la aprobación; `alcance` es, opcionalmente, el prefijo
del snapshot que se aprueba. Sin `alcance`, la aprobación cubre la etapa entera.

Formato: lista de bloques `clave: valor`. Se lee sin PyYAML para no añadir una
dependencia al paquete.

Salida: 0 con la aprobación encontrada, 1 sin aprobación, 2 error de lectura.
Solo stdlib. No consume tokens.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

DEFAULT_PATH = Path(".yerro") / "approvals.yml"
ENTRY_RE = re.compile(r"^\s*-\s*(\w[\w-]*)\s*:\s*(.*)$")
FIELD_RE = re.compile(r"^\s*(\w[\w-]*)\s*:\s*(.*)$")


class ApprovalError(Exception):
    """El archivo de aprobaciones no se puede leer."""


@dataclass(frozen=True)
class Approval:
    stage: str
    approved_by: str
    date: str
    scope: str = ""

    def covers(self, snapshot: str) -> bool:
        """¿La aprobación cubre este snapshot? Sin alcance, cubre la etapa."""
        if not self.scope:
            return True
        return snapshot.lower().startswith(self.scope.lower())


def parse(text: str) -> list[Approval]:
    """Lista de aprobaciones. Ignora comentarios y líneas vacías."""
    entries: list[dict[str, str]] = []
    current: dict[str, str] | None = None
    for raw in text.splitlines():
        line = raw.split("#", 1)[0].rstrip() if not raw.lstrip().startswith("#") else ""
        if not line.strip():
            continue
        start = ENTRY_RE.match(line)
        if start:
            if current:
                entries.append(current)
            current = {start.group(1).lower(): start.group(2).strip()}
            continue
        field = FIELD_RE.match(line)
        if field and current is not None:
            current[field.group(1).lower()] = field.group(2).strip()
    if current:
        entries.append(current)

    approvals: list[Approval] = []
    for entry in entries:
        missing = [key for key in ("etapa", "aprobado-por", "fecha") if not entry.get(key)]
        if missing:
            raise ApprovalError(
                f"aprobación incompleta en {entry.get('etapa') or '<sin etapa>'}: "
                f"falta {', '.join(missing)}"
            )
        approvals.append(
            Approval(
                stage=entry["etapa"],
                approved_by=entry["aprobado-por"],
                date=entry["fecha"],
                scope=entry.get("alcance", ""),
            )
        )
    return approvals


def load(repo: Path, relative: Path = DEFAULT_PATH) -> list[Approval]:
    path = repo / relative
    if not path.exists():
        return []
    try:
        return parse(path.read_text(encoding="utf-8"))
    except OSError as error:
        raise ApprovalError(f"no se pudo leer {path}: {error}") from None


def find(approvals: list[Approval], stage: str, snapshot: str = "") -> Approval | None:
    """La aprobación de la etapa, priorizando la que cubre el snapshot dado."""
    candidates = [item for item in approvals if item.stage == stage]
    if snapshot:
        covering = [item for item in candidates if item.covers(snapshot)]
        if covering:
            return covering[-1]
    return candidates[-1] if candidates else None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("repo", type=Path)
    parser.add_argument("--path", type=Path, default=DEFAULT_PATH)
    parser.add_argument("--stage", help="etapa a consultar, p. ej. 01-export")
    parser.add_argument("--snapshot", default="", help="snapshot que debe cubrir")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    try:
        approvals = load(args.repo, args.path)
    except ApprovalError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2

    if args.stage:
        found = find(approvals, args.stage, args.snapshot)
        if args.json:
            payload = {"ok": found is not None}
            if found:
                payload.update(
                    {
                        "aprobado_por": found.approved_by,
                        "fecha": found.date,
                        "alcance": found.scope,
                    }
                )
            print(json.dumps(payload, ensure_ascii=False))
        elif found:
            print(f"Aprobada por {found.approved_by} el {found.date}")
        else:
            print(f"Sin aprobación para {args.stage} en {args.path}")
        return 0 if found else 1

    if args.json:
        print(json.dumps([item.__dict__ for item in approvals], ensure_ascii=False))
    else:
        for item in approvals:
            print(f"{item.stage}: {item.approved_by} · {item.date}" + (f" · {item.scope}" if item.scope else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
