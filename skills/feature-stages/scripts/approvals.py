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
  alcance: tree=<sha>   # completo o en forma corta
```

`fecha` es la fecha de la aprobación; `alcance` es, opcionalmente, el árbol
que se aprueba (`tree=<sha>`, completo o en forma corta). Se compara con el
`tree=` del snapshot, así que la firma sigue valiendo mientras el código no
cambie, aunque un commit de documentos mueva `head=`. Un árbol que no es
prefijo del auditado no cubre. Un prefijo literal del snapshot se sigue
aceptando para las firmas anteriores. Sin `alcance`, la aprobación cubre la
etapa entera.

Formato: lista de bloques `clave: valor`. Se lee sin PyYAML para no añadir una
dependencia al paquete.

`--suggest <etapa>` imprime el bloque listo para pegar, con el `tree=` del
snapshot actual ya resuelto. **No escribe el archivo**: la firma la pega la
persona. El helper quita el trabajo de copiar el sha a mano y el error de
formato, no la decisión.

Salida: 0 con la aprobación encontrada, 1 sin aprobación, 2 error de lectura.
Solo stdlib. No consume tokens.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from snapshot import SnapshotError, identity, tree_of

DEFAULT_PATH = Path(".yerro") / "approvals.yml"
ENTRY_RE = re.compile(r"^\s*-\s*(\w[\w-]*)\s*:\s*(.*)$")
FIELD_RE = re.compile(r"^\s*(\w[\w-]*)\s*:\s*(.*)$")
STAGE_NAME_RE = re.compile(r"^\d{2}-[^\s/]+$")


class ApprovalError(Exception):
    """El archivo de aprobaciones no se puede leer."""


@dataclass(frozen=True)
class Approval:
    stage: str
    approved_by: str
    date: str
    scope: str = ""
    base: str = ""

    def covers(self, snapshot: str) -> bool:
        """¿La aprobación cubre este snapshot? Sin alcance, cubre la etapa.

        El alcance se compara con el **árbol auditado**, no con la línea
        literal: `alcance: tree=<sha>` cubre toda pasada de ese árbol, aunque
        un commit de documentos haya movido `head=` (que no forma parte de la
        identidad). El árbol se admite completo o en forma corta —`tree=152c3474`
        es prefijo del sha—. Un prefijo literal del snapshot se sigue aceptando
        para las firmas anteriores a S62, que anclaban el `head=`.
        """
        if not self.scope:
            # Una entrada con `base=` es firma de plan: cubre el baseline, no
            # un árbol. Sin `alcance` ni `base` se mantiene la firma anterior,
            # que cubría la etapa entera.
            return not self.base
        if snapshot.lower().startswith(self.scope.lower()):
            return True
        wanted = tree_of(self.scope)
        audited = tree_of(snapshot)
        if wanted is None or audited is None:
            return False
        # El árbol se firma completo o en forma corta, como `git rev-parse
        # --short`: es lo que una persona escribe al copiar `tree=152c3474` de
        # la pasada. Un alcance que no es prefijo del árbol no cubre.
        return audited.startswith(wanted)

    def covers_plan(self, baseline: str) -> bool:
        """¿La firma cubre este baseline de la conciliación?

        `base=` es el sha256 completo de `CONCILIACION.md` sin su línea
        `**Estado:**`, que es ciclo de vida y no baseline. Se exige completo:
        a diferencia del árbol, no hay un comando que muestre la forma corta,
        así que un prefijo solo puede venir de un copiado a medias.
        """
        if not self.base:
            return False
        return self.base.strip().lower() == baseline.strip().lower()

def baseline_of(stage: Path) -> str:
    """sha256 del baseline firmable de una etapa.

    Es la conciliación sin `**Estado:**`: cerrar la etapa escribe esa línea y
    reabrirla la cambia, así que incluirla haría que la firma de plan dejara de
    cubrir el baseline en el mismo acto de cerrar la conciliación. Todo lo
    demás —riesgo, alcance, criterios, decisiones, presupuesto— sí es baseline:
    editarlo invalida la firma y obliga a volver a firmar.
    """
    text = (stage / "CONCILIACION.md").read_text(encoding="utf-8")
    lines = [
        line for line in text.splitlines()
        if not re.match(r"^\s*\*\*Estado:\*\*", line, re.I)
    ]
    return hashlib.sha256("\n".join(lines).encode("utf-8")).hexdigest()


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
            hints = [hint for key in missing if (hint := _typo_hint(entry, key))]
            detail = f"; {'; '.join(hints)}" if hints else ""
            raise ApprovalError(
                f"aprobación incompleta en {entry.get('etapa') or '<sin etapa>'}: "
                f"falta {', '.join(missing)}{detail}"
            )
        approvals.append(
            Approval(
                stage=entry["etapa"],
                approved_by=entry["aprobado-por"],
                date=entry["fecha"],
                scope=entry.get("alcance", ""),
                base=entry.get("base", ""),
            )
        )
    return approvals


def _typo_hint(entry: dict[str, str], key: str) -> str:
    """Nombra el campo si la persona escribió la variante con guion bajo.

    El parser no conoce claves: `aprobado_por` se lee como otra clave y la que
    falta es `aprobado-por`. Sin la pista, el error dice «falta aprobado-por» y
    la línea que la persona acaba de escribir tiene exactamente esas palabras.
    """
    alt = key.replace("-", "_")
    if alt != key and entry.get(alt):
        return f"escribiste `{alt}`, el campo va `{key}`"
    return ""

def suggest(
    repo: Path,
    stage_dir: Path,
    *,
    path: Path = DEFAULT_PATH,
    approved_by: str = "<tu nombre>",
    on_date: str | None = None,
    plan: bool = False,
) -> tuple[str, str]:
    """Bloque listo para pegar, con el árbol del snapshot actual.

    Devuelve `(bloque, aviso)`. El `tree=` se calcula con las mismas
    exclusiones que la auditoría (`<feature-root>` y el archivo de
    aprobaciones), así que el bloque cubre la pasada que se grabe a
    continuación mientras no cambie el código. **No escribe nada**: quien
    firma pega el bloque en `.yerro/approvals.yml`.

    Con `plan=True` imprime la firma del baseline (`base=`) en vez de la del
    árbol: es la que se pide al cerrar la conciliación, antes de que exista
    código que auditar.
    """
    stage_dir = stage_dir if stage_dir.is_absolute() else (repo / stage_dir)
    stage_dir = stage_dir.resolve()
    if not stage_dir.is_dir():
        raise ApprovalError(f"la etapa {stage_dir} no existe")
    # La etapa se reconoce por forma (`NN-nombre`), como en el resto del
    # paquete. Sin esta guarda, pasar la raíz de la feature excluye el árbol
    # entero y el bloque se imprime con el árbol vacío: una firma que no cubre
    # nada y un error que aparecería recién al cerrar.
    if not STAGE_NAME_RE.match(stage_dir.name):
        raise ApprovalError(
            f"{stage_dir.name} no parece una etapa: se espera una carpeta `NN-nombre`"
        )
    panel = stage_dir.parent
    try:
        snapshot = identity(repo.resolve(), (panel, path))
    except SnapshotError as error:
        raise ApprovalError(f"no se pudo tomar el snapshot: {error}") from None
    tree = tree_of(snapshot) or ""
    warning = ""
    if not tree:
        raise ApprovalError(f"el snapshot no trae un tree= reconocible: {snapshot}")
    try:
        existing = load(repo.resolve(), path)
    except ApprovalError:
        existing = []
    if plan:
        baseline = baseline_of(stage_dir)
        covering = next(
            (
                item for item in existing
                if item.stage == stage_dir.name and item.covers_plan(baseline)
            ),
            None,
        )
        if covering is not None:
            warning = (
                f"{stage_dir.name} ya tiene la firma de plan de {covering.approved_by} "
                f"({covering.date}) para este baseline: no hace falta otra entrada"
            )
        block = (
            f"- etapa: {stage_dir.name}\n"
            f" aprobado-por: {approved_by}\n"
            f" fecha: {on_date or date.today().isoformat()}\n"
            f" base: {baseline}\n"
        )
        return block, warning
    covering = find(existing, stage_dir.name, snapshot)
    if covering is not None:
        warning = (
            f"{stage_dir.name} ya está aprobada por {covering.approved_by} "
            f"({covering.date}) para este árbol: no hace falta otra entrada"
        )
    block = (
        f"- etapa: {stage_dir.name}\n"
        " aprobado-por: {by}\n"
        " fecha: {when}\n"
        " alcance: tree={tree}\n"
    ).format(by=approved_by, when=on_date or date.today().isoformat(), tree=tree)
    return block, warning

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
    parser.add_argument(
        "--suggest",
        type=Path,
        metavar="ETAPA",
        help="imprime el bloque de firma con el tree= del snapshot actual (no escribe nada)",
    )
    parser.add_argument("--by", default="<tu nombre>", help="nombre para --suggest")
    parser.add_argument(
        "--plan",
        action="store_true",
        help="con --suggest, imprime la firma del baseline (base=) en vez de la del árbol",
    )
    parser.add_argument("--date", dest="on_date", help="fecha ISO para --suggest (por defecto, hoy)")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    if args.suggest is not None:
        try:
            block, warning = suggest(
                args.repo,
                args.suggest,
                path=args.path,
                approved_by=args.by,
                on_date=args.on_date,
                plan=args.plan,
            )
        except ApprovalError as error:
            print(f"ERROR: {error}", file=sys.stderr)
            return 2
        if warning:
            print(f"AVISO: {warning}", file=sys.stderr)
        print(block, end="")
        return 0

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
