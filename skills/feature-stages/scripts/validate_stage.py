#!/usr/bin/env python3
"""Valida de forma estática artefactos de una etapa de implementación.

Uso: validate_stage.py <stage-directory>

Hay **un** contrato y **un** modo: cualquier incumplimiento es un error. No hay
modo de advertencias: convivir con dos formatos obliga a probar cada fixture dos
veces y deja vivo un formato que el contrato ya no sostiene.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from approvals import (  # noqa: E402
    DEFAULT_PATH as DEFAULT_APPROVALS,
    ApprovalError,
    load as load_approvals,
)
from snapshot import SnapshotError, identity, repo_root  # noqa: E402
from diff_scope import ( # noqa: E402
    ScopeError,
    compare,
    declared_files,
    scope_base,
    stage_base,
    touched_files,
)

CA_RE = re.compile(r"^\s*-\s*\*\*(CA-\d+)\b", re.M)
DECISION_RE = re.compile(r"^\s*-\s*\*\*(S-\d+)\s+—", re.M)
CA_ORIGIN_RE = re.compile(r"\bOrigen:\s*(S-\d+)", re.I)
TEST_FIRST_RE = re.compile(r"^\s*Test-first:\s*(.+)$", re.I | re.M)
TEST_COMMAND_RE = re.compile(r"(?:^|;\s*)Test:\s*([^;\n]+)", re.I | re.M)
TRACE_RE = re.compile(r"^\s*\*\*Trazabilidad:\*\*\s*(.+)$", re.I | re.M)
E_COMMAND_RE = re.compile(r"\|\s*E-\d+\s*\|.*?\|\s*([^|]+?)\s*\|.*?\|")
TASK_RE = re.compile(
    r"^\s*-\s*\[[ xX]\]\s*((?:D\d+-)?T\d+)\b(.*?)(?=^\s*-\s*\[[ xX]\]|\Z)",
    re.M | re.S,
)
STATE_RE = re.compile(r"\*\*Estado:\*\*\s*([^\n]+)")
# Misma línea del CA: placeholder, una opción entre corchetes, o prosa.
# No basta la palabra suelta «salida» o «invariante» en el cuerpo.
CA_TYPE_RE = re.compile(
    "|".join(
        (
            r"\[condición de salida(?:\s*\|\s*invariante acumulado)?\]",
            r"\[invariante acumulado(?:\s*\|\s*condición de salida)?\]",
            r"\bsalida de etapa\b",
            r"\binvariante acumulada\b",
        )
    ),
    re.I,
)
EVIDENCE_RE = re.compile(r"estructural|conductual|sistema|ambiental", re.I)
SNAPSHOT_RE = re.compile(r"^\s*\*\*Snapshot:\*\*\s*(.+?)\s*$", re.M | re.I)
SNAPSHOT_VALUE_RE = re.compile(
    r"^head=(?:[0-9a-f]{7,40}|sin-head)\s+tree=[0-9a-f]{7,40}\s+dirty=(?:si|no)\s+exclude=\S+$",
    re.I,
)
RISK_RE = re.compile(r"^\s*\*\*Riesgo:\*\*\s*(bajo|medio|alto)\b", re.M | re.I)
AUDITED_RISK_RE = re.compile(r"^\s*\*\*Riesgo auditado:\*\*\s*(bajo|medio|alto)\b", re.M | re.I)
RISK_RANK = {"bajo": 0, "medio": 1, "alto": 2}
VERDICT_RE = re.compile(r"^\s*\*\*Veredicto:\*\*\s*(.+?)\s*$", re.I | re.M)
AUDIT_PASS_RE = re.compile(r"^##\s+Pasada\b.*?$(.*?)(?=^##\s+Pasada\b|\Z)", re.M | re.S | re.I)
RUNNERS_RE = re.compile(r"^\s*\*\*Runners:\*\*\s*(.+?)\s*$", re.M | re.I)
SENSITIVITY_RE = re.compile(r"(?:\||^)\s*Sensibilidad\s*(?:\||$)", re.I | re.M)
# B-25: `Ruling: <qué> — <por qué> — <qué cuesta>`. Las tres partes son
# obligatorias; dos guiones largos separan tres tramos no vacíos. Se acepta
# también `--` porque un agente puede escribir ASCII en un archivo markdown.
RULING_RE = re.compile(r"^\s*Ruling:\s*(.+?)\s*$", re.I | re.M)
RULING_SEPARATOR_RE = re.compile(r"\s+(?:—|--|–)\s+")
# B-26: la marca de categoría 2 lleva identificador (R1, R2…) para que su
# resolución en la auditoría se cruce por ID y no por conteo.
SUBJECT_RE = re.compile(r"\*\*Sujeto a revisión([^*]*):\*\*[ \t]*(.*?)[ \t]*$", re.I | re.M)
SUBJECT_ID_RE = re.compile(r"R\d+", re.I)
SUBJECT_REVIEW_SECTION = "### Rulings revisados"
SUBJECT_RESOLVED_RE = re.compile(r"^\s*-\s*(aceptado|hallazgo)\s+(R\d+)\b", re.I | re.M)
# P17: interfaces entre tareas. Solo se exigen cuando la etapa tiene más de una
# tarea; un `Consume: ninguna` explícito es una respuesta válida.
# `[ \t]`, no `\s`: un `Consume:` vacío no debe "leerse" en la línea siguiente.
CONSUME_RE = re.compile(r"^[ \t]*Consume:[ \t]*(\S.*?)[ \t]*$", re.I | re.M)
PRODUCE_RE = re.compile(r"^[ \t]*Produce:[ \t]*(\S.*?)[ \t]*$", re.I | re.M)
NO_DEMOSTRADA_RE = re.compile(r"no demostrada", re.I)

# Presupuesto de deltas por riesgo. El default no se inventa: está calibrado
# con lo medido hasta hoy y **solo** se sobrescribe con motivo escrito.
DELTA_BUDGET_BY_RISK = {"bajo": 2, "medio": 1, "alto": 1}
BUDGET_RE = re.compile(r"^\s*\*\*Presupuesto de deltas:\*\*\s*(\d+)", re.M | re.I)
BUDGET_REASON_RE = re.compile(
    r"^\s*\*\*Motivo del presupuesto:\*\*\s*(\S.*)$", re.M | re.I
)
CROSSES_RE = re.compile(
    r"^\s*\*\*Cruza riesgo:\*\*\s*(s[íi]|no)\b(?:\s*[—-]\s*(.*))?$", re.M | re.I
)
# B-35 exige **ver el rojo**, no nombrar la palabra «mutante». Por eso se lee
# el resultado declarado: `mutante: X → verde` es un mutante que el test no
# detectó, y es exactamente el falso cierre que este gate persigue.
MUTANT_RE = re.compile(r"\bmutante\s*:([^;|]*)", re.I)
INJECTED_RE = re.compile(
 r"\b(?:fallo inyectado|oráculo alterado|inyectar(?:lo)?)\s*:?([^;|]*)", re.I
)
MUTATION_OBSERVED_RE = re.compile(r"\brojo\b", re.I)
MUTATION_SURVIVED_RE = re.compile(r"\b(?:verde|verdes)\b", re.I)
DELTA_IDS_RE = re.compile(r"^\s*\*\*Deltas:\*\*\s*(.+?)\s*$", re.M | re.I)

# Comandos que devuelven 0 sin observar comportamiento alguno. Se comparan por
# palabra inicial y se exige que *todas* las partes encadenadas estén aquí:
# `pytest -q && true` no es decorativo, `true && :` sí.
DECORATIVE = {
    "true", "false", ":", "exit", "echo", "printf", "sleep", "cat", "ls",
    "pwd", "cd", "test",
}
CHAIN_RE = re.compile(r"\s*(?:&&|\|\||;)\s*")
WRAPPER_RE = re.compile(r"^(?:bash|sh|zsh)\s+-c\s+(.*)$", re.I | re.S)
TRIVIAL_PY_RE = re.compile(r"^python[0-9.]*\s+-c\s+['\"]?(?:pass|exit\s*\(?\s*0?\s*\)?)['\"]?$", re.I)


class Result:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def require(self, ok: bool, text: str) -> None:
        if not ok:
            self.errors.append(text)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def split_row(line: str) -> list[str]:
    return [cell.strip() for cell in line.split("|")]

def parse_excludes(snapshot: str) -> tuple[Path, ...]:
    """Rutas excluidas declaradas en el snapshot canónico."""
    match = re.search(r"\bexclude=(\S+)", snapshot, re.I)
    if not match or match.group(1).lower() == "ninguno":
        return ()
    return tuple(Path(item) for item in match.group(1).split(",") if item)


def declarative_command(command: str) -> bool:
    """¿El comando es trivio disfrazado? Se mira cada parte encadenada."""
    for part in CHAIN_RE.split(command.strip()):
        part = part.strip()
        if not part:
            continue
        wrapped = WRAPPER_RE.match(part)
        if wrapped:
            part = wrapped.group(1).strip()
        if TRIVIAL_PY_RE.match(part):
            continue
        head = re.split(r"\s+", part, maxsplit=1)[0]
        # `exit 0` devuelve verde incondicional y no observa nada. La sufijación
        # con `test` no salva: `npm test` no está en DECORATIVE, así que nunca
        # llega a esta rama.
        if head in DECORATIVE:
            continue
        return False
    return True


def declared_runners(conciliation: str) -> list[str]:
    """Runners que la conciliación declara, separados por `|` o comas."""
    match = RUNNERS_RE.search(conciliation)
    if not match:
        return []
    return [item.strip() for item in re.split(r"[|,]", match.group(1)) if item.strip()]


def is_runner(command: str, runners: list[str]) -> bool:
    command = command.strip()
    return any(command.startswith(runner) for runner in runners)


def checkpoint_approval(repo: Path, stage: Path, snapshot: str) -> bool:
    """¿Hay una aprobación humana de esta etapa para este snapshot?

    Se lee del archivo versionado, nunca de `AUDIT.md`: una marca que el agente
    puede escribir no distingue una firma de una invención.
    """
    try:
        approvals = load_approvals(repo)
    except ApprovalError as error:
        raise SystemExit(f"ERROR: {error}") from None
    return any(
        item.stage == stage.name and item.covers(snapshot) for item in approvals
    )


def delta_ids(audit: str) -> list[str]:
    """IDs de delta declarados por la pasada (`**Deltas:** D1, D2`).

    No se cuentan las apariciones de la palabra en prosa: un texto puede
    explicar la diferencia entre un delta y una reapertura sin declarar deltas.
    """
    match = DELTA_IDS_RE.search(audit)
    if not match:
        return []
    return [item for item in re.split(r"[,\s]+", match.group(1)) if item]


def mutation_verdicts(ledger: str) -> list[str]:
    """Qué declaró cada prueba de mutación del ledger: `rojo` o `verde`.

    Una prueba de mutación sirve si el código mutado **rompió** el test. Se
    devuelve el veredicto por prueba, no un booleano, para que el mensaje diga
    cuál sobrevivió.
    """
    declared = [
        MUTANT_RE.findall(ledger),
        INJECTED_RE.findall(ledger),
    ]
    verdicts: list[str] = []
    for matches in declared:
        for text in matches:
            # `mutante: X → rojo esperado` no es una observación.
            if re.search(r"\besperad[oa]\b", text, re.I):
                verdicts.append("esperado")
            elif MUTATION_OBSERVED_RE.search(text):
                verdicts.append("rojo")
            elif MUTATION_SURVIVED_RE.search(text):
                verdicts.append("verde")
            else:
                verdicts.append("sin resultado")
    return verdicts


def risk_evidence_gaps(risk: str, audit: str) -> list[str]:
    """Lo que el nivel de riesgo exige en el ledger y todavía no está.

    La sensibilidad se exige siempre (B-23); el riesgo solo añade fondo:
    un caso límite declarado por encima de `bajo` y una prueba de mutación
    observada en rojo por encima de `alto` (B-35, sin herramienta obligatoria).
    """
    if not risk:
        return []
    gaps: list[str] = []
    ledger = "\n".join(ledger_rows(audit))
    text = ledger.lower()
    if risk in ("medio", "alto") and not (
        "límite" in text or "limite" in text or "negativo" in text
    ):
        gaps.append(
            f"riesgo {risk}: el ledger no declara un caso límite ni un negativo demostrado"
        )
    if risk == "alto":
        verdicts = mutation_verdicts(ledger)
        # Un mutante verde en cualquier CA crítico invalida el fondo aunque otro
        # CA tenga mutante rojo: los rojos no compensan los supervivientes.
        if not verdicts:
            gaps.append(
                "riesgo alto: ningún CA crítico registra `mutante:` (o fallo inyectado) con resultado rojo"
            )
        elif "verde" in verdicts:
            gaps.append(
                "riesgo alto: una prueba de mutación declara el resultado `verde` "
                "(el mutante sobrevivió); cada CA crítico exige ver el rojo"
            )
        elif "esperado" in verdicts or "sin resultado" in verdicts:
            gaps.append(
                "riesgo alto: una prueba de mutación no declara el resultado observado; "
                "`rojo esperado` es una predicción, no una observación (B-35)"
            )
        elif "rojo" not in verdicts:
            detalle = ", ".join(sorted(set(verdicts)))
            gaps.append(
                f"riesgo alto: la prueba de mutación no observó el rojo ({detalle}); "
                "un mutante que sobrevive dice que el test no prueba el comportamiento"
            )
    return gaps


def crosses_risk_gate(audit: str, deltas: int, budget: int) -> bool:
    """¿La pasada declaró explícitamente que baja el criterio más exigente?"""
    match = CROSSES_RE.search(audit)
    if match and match.group(1).lower().startswith("s"):
        return True
    # Sin la marca, un delta por encima del presupuesto es una bajada implícita:
    # el delta es la corrección acotada, no un permiso para ignorar el nivel.
    return deltas > budget


def ledger_rows(audit: str) -> list[str]:
    """Filas de datos del ledger de evidencia (las que empiezan por `| E-NN`)."""
    return [
        line for line in audit.splitlines()
        if re.match(r"^\s*\|\s*E-\d+\s*\|", line)
    ]


def sensitivity_cell(row: str, audit: str) -> str:
    """Valor de la celda `Sensibilidad` de una fila del ledger, o "" si no hay."""
    header = next(
        (line for line in audit.splitlines() if SENSITIVITY_RE.search(line) and "|" in line),
        "",
    )
    if not header:
        return ""
    names = [cell.strip().lower() for cell in split_row(header)]
    if "sensibilidad" not in names:
        return ""
    cells = split_row(row)
    at = names.index("sensibilidad")
    return cells[at] if at < len(cells) else ""


def stage_index_estado(index: str, stage_name: str) -> str | None:
    """Celda Estado de la etapa en el índice, identificada por el enlace de Carpeta."""
    header: list[str] | None = None
    for line in index.splitlines():
        if not line.strip().startswith("|"):
            continue
        cells = split_row(line)
        if "Conciliación" in cells and "Estado" in cells and "Carpeta" in cells:
            header = cells
            break
    if header is None:
        return None
    folder_at = header.index("Carpeta")
    state_at = header.index("Estado")
    link = f"]({stage_name}/"
    for line in index.splitlines():
        if not line.strip().startswith("|"):
            continue
        cells = split_row(line)
        if folder_at >= len(cells) or state_at >= len(cells):
            continue
        if link in cells[folder_at]:
            return cells[state_at]
    return None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("stage", type=Path)
    parser.add_argument(
        "--repo",
        type=Path,
        help="verifica que el snapshot de la última pasada coincide con el árbol actual",
    )
    args = parser.parse_args()

    stage = args.stage.resolve()
    result = Result()
    conciliation, tasks, audit = (
        read(stage / name) for name in ("CONCILIACION.md", "TAREAS.md", "AUDIT.md")
    )
    result.require(bool(conciliation), "falta CONCILIACION.md")
    if not conciliation:
        return finish(result)

    state = STATE_RE.search(conciliation)
    closed = bool(state and "cerrada" in state.group(1).lower())
    ca_ids = CA_RE.findall(conciliation)
    result.require(bool(ca_ids), "no hay CA-NN en CONCILIACION.md")
    decision_ids = DECISION_RE.findall(conciliation)
    result.require(bool(decision_ids), "no hay decisiones S-NN en CONCILIACION.md")
    result.require(len(decision_ids) == len(set(decision_ids)), "hay IDs S-NN duplicados")
    result.require(len(ca_ids) == len(set(ca_ids)), "hay IDs CA duplicados")

    declared_risk = RISK_RE.search(conciliation)
    if closed:
        result.require(
            bool(declared_risk),
            "conciliación cerrada sin **Riesgo:** bajo|medio|alto congelado",
        )

    for ca in ca_ids:
        line = next((item for item in conciliation.splitlines() if f"**{ca}" in item), "")
        result.require(
            bool(CA_TYPE_RE.search(line)),
            f"{ca} no declara tipo condición de salida/invariante acumulado",
        )
        result.require(
            bool(CA_ORIGIN_RE.search(line)),
            f"{ca} no enlaza una decisión S-NN mediante Origen:",
        )
        result.require(bool(EVIDENCE_RE.search(line)), f"{ca} no declara nivel de evidencia")

    task_bodies: dict[str, str] = {}
    declared = declared_runners(conciliation)
    if closed:
        result.require(bool(tasks), "conciliación cerrada sin TAREAS.md")
    if tasks:
        principal = re.search(r"\*\*Principal:\*\*\s*sí", tasks, re.I)
        result.require(bool(principal), "TAREAS.md no declara Principal: sí")
        for task_id, body in TASK_RE.findall(tasks):
            task_bodies[task_id] = body
            result.require(bool(re.search(r"CA-\d+", body)), f"{task_id} no enlaza CA-NN")
            # B-25: un ruling sin coste oculta la decisión. Las tres partes se
            # exigen por separado para que el error diga cuál falta.
            for ruling in RULING_RE.findall(body):
                parts = [item for item in RULING_SEPARATOR_RE.split(ruling) if item.strip()]
                result.require(
                    len(parts) >= 3,
                    f"{task_id} tiene un `Ruling:` sin las tres partes "
                    "(<qué> — <por qué> — <qué cuesta>); un ruling sin coste es una decisión oculta",
                )
            result.require(bool(TEST_FIRST_RE.search(body)), f"{task_id} no declara Test-first:")
            result.require(bool(TEST_COMMAND_RE.search(body)), f"{task_id} no declara Test:")
            for command in TEST_COMMAND_RE.findall(body):
                result.require(
                    not declarative_command(command),
                    f"{task_id} declara un Test: decorativo ({command.strip()}): no observa comportamiento",
                )
                if declared and not is_runner(command, declared):
                    result.warnings.append(
                        f"{task_id}: Test: no empieza por un runner declarado en **Runners:**"
                    )
            verification = re.search(r"Verificar:\s*(.*)", body, re.I)
            result.require(bool(verification), f"{task_id} no contiene Verificar:")
            if verification:
                value = verification.group(1)
                result.require(bool(EVIDENCE_RE.search(value)), f"{task_id} no declara nivel")
                result.require(
                    ";" in value or "oráculo" in value.lower(),
                    f"{task_id} no separa procedimiento y oráculo",
                )
        # P17: una etapa con varias tareas necesita decir qué firma recibe cada
        # una de las anteriores. Un subagente no debe adivinar nombres.
        if len(task_bodies) > 1:
            for task_id, body in task_bodies.items():
                result.require(
                    bool(CONSUME_RE.search(body)),
                    f"{task_id} no declara `Consume:` en Interfaces: una etapa con "
                    "varias tareas exige qué firma recibe (`ninguna` si no consume)",
                )
                result.require(
                    bool(PRODUCE_RE.search(body)),
                    f"{task_id} no declara `Produce:` en Interfaces: las tareas "
                    "posteriores necesitan nombres y tipos exactos",
                )

        # B-26: un ruling de categoría 2 cambia algo observable. El auditor lo
        # revisa con artefactos, no con memoria (B-32), y mientras no lo acepte
        # o lo convierta en hallazgo, el cierre no pasa. El cruce es por ID:
        # contar resoluciones dejaría dos `aceptado` tapando una marca sin leer.
        marks: list[tuple[str, str]] = []
        for task_id, body in task_bodies.items():
            for match in SUBJECT_RE.finditer(body):
                raw = match.group(1).strip()
                text = match.group(2).strip()
                found = SUBJECT_ID_RE.findall(raw)
                valid_id = len(found) == 1 and raw == found[0]
                marks.append((task_id, found[0].upper() if valid_id else ""))
                if not valid_id:
                    result.require(
                        False,
                        f"{task_id}: `**Sujeto a revisión{raw}:**` necesita un "
                        "identificador (`**Sujeto a revisión R1:**`) para que la "
                        "auditoría pueda resolverlo",
                    )
                result.require(
                    bool(text),
                    f"{task_id}: `**Sujeto a revisión{raw}:**` no describe qué "
                    "cambió ni qué cuesta; no hay nada que revisar",
                )
        mark_ids = [rid for _, rid in marks if rid]
        repeated = sorted({rid for rid in mark_ids if mark_ids.count(rid) > 1})
        result.require(
            not repeated,
            f"identificadores de sujeto a revisión duplicados: {', '.join(repeated)}; "
            "cada marca necesita el suyo",
        )
        if marks:
            reviewed = audit.split(SUBJECT_REVIEW_SECTION, 1)
            result.require(
                len(reviewed) > 1,
                f"AUDIT.md no tiene «{SUBJECT_REVIEW_SECTION}» y hay {len(marks)} "
                "ruling(s) de categoría 2 (`**Sujeto a revisión R1:**`) sin revisar",
            )
            if len(reviewed) > 1:
                resolved = [rid.upper() for _, rid in SUBJECT_RESOLVED_RE.findall(reviewed[1])]
                twice = sorted({rid for rid in resolved if resolved.count(rid) > 1})
                result.require(
                    not twice,
                    f"«{SUBJECT_REVIEW_SECTION}» resuelve dos veces {', '.join(twice)}",
                )
                missing = sorted(set(mark_ids) - set(resolved))
                result.require(
                    not missing,
                    f"«{SUBJECT_REVIEW_SECTION}» no resuelve {', '.join(missing)}: "
                    "cada marca se acepta o se convierte en hallazgo",
                )
                unknown = sorted(set(resolved) - set(mark_ids))
                result.require(
                    not unknown,
                    f"«{SUBJECT_REVIEW_SECTION}» resuelve {', '.join(unknown)}, que "
                    "ninguna tarea marca como sujeto a revisión",
                )
        result.require(bool(task_bodies), "TAREAS.md no contiene tareas implementables")
        result.require(
            len(task_bodies) == len(set(task_bodies)), "hay IDs de tarea duplicados"
        )
        for ca in ca_ids:
            result.require(
                any(re.search(rf"\b{re.escape(ca)}\b", body) for body in task_bodies.values()),
                f"{ca} no tiene tarea trazable",
            )

    verdicts = VERDICT_RE.findall(audit)
    has_coincide = any(item.strip().lower() == "coincide" for item in verdicts)
    passes = AUDIT_PASS_RE.findall(audit) or ([audit] if audit else [])
    coincide_passes: list[str] = []
    last_verdict = ""
    for body in passes:
        found = [item.strip().lower() for item in VERDICT_RE.findall(body)]
        last_verdict = found[-1] if found else ""
        if last_verdict == "coincide":
            coincide_passes.append(body)
    if audit and has_coincide:
        result.require(bool(tasks), "AUDIT coincide sin lista principal")
        for ca in ca_ids:
            result.require(
                bool(re.search(rf"\|\s*{re.escape(ca)}\s*\|.*?\|\s*cumple\s*\|", audit, re.I)),
                f"AUDIT coincide no demuestra {ca}=cumple",
            )
        result.require("### Ledger de evidencia" in audit, "AUDIT coincide sin ledger de evidencia")
        result.require(
            bool(SENSITIVITY_RE.search(audit)),
            "AUDIT coincide sin columna Sensibilidad en el ledger: no demuestra que el test pueda fallar",
        )
        if SENSITIVITY_RE.search(audit):
            for row in ledger_rows(audit):
                result.require(
                    bool(sensitivity_cell(row, audit)),
                    f"ledger con sensibilidad vacía: {row.strip()[:80]}",
                )
                result.require(
                    not NO_DEMOSTRADA_RE.search(row),
                    f"ledger declara sensibilidad no demostrada: {row.strip()[:80]}",
                )
        result.require(bool(TRACE_RE.search(audit)), "AUDIT coincide sin **Trazabilidad:** CA → T → E")
        result.require(bool(re.search(r"\bE-\d+\b", audit)), "AUDIT coincide sin evidencia E-NN")

    # Riesgo → evidencia y presupuesto → deltas. Son gates cruzados: el riesgo
    # declarado en la conciliación decide qué fondo exige el ledger, y el delta
    # permitido decide cuándo el cierre está bajando el criterio.
    budget_match = BUDGET_RE.search(conciliation)
    measured_budget = (
        int(budget_match.group(1)) if budget_match
        else DELTA_BUDGET_BY_RISK[declared_risk.group(1).lower()]
        if declared_risk
        else 2
    )
    deltas = len(delta_ids(audit))
    risk = declared_risk.group(1).lower() if declared_risk else ""
    if budget_match and risk:
        derived = DELTA_BUDGET_BY_RISK[risk]
        result.require(
            int(budget_match.group(1)) <= derived
            or BUDGET_REASON_RE.search(conciliation) is not None,
            f"**Presupuesto de deltas:** {budget_match.group(1)} con riesgo {risk} "
            f"supera el derivado ({derived}) sin **Motivo del presupuesto:**",
        )
    for gap in risk_evidence_gaps(risk, audit):
        result.require(False, gap)
    if crosses_risk_gate(audit, deltas, measured_budget):
        result.require(
            (BUDGET_REASON_RE.search(conciliation) or BUDGET_REASON_RE.search(audit))
            is not None,
            f"cierre con el criterio rebajado (Cruza riesgo / {deltas} delta(s) "
            f"con presupuesto {measured_budget}) sin **Motivo del presupuesto:** escrito "
            "en la conciliación o la pasada",
        )

    for body in coincide_passes:
        valid_snapshots = [
            item.strip() for item in SNAPSHOT_RE.findall(body)
            if SNAPSHOT_VALUE_RE.match(item.strip())
        ]
        result.require(
            bool(valid_snapshots),
            "AUDIT coincide sin **Snapshot:** head=… tree=… dirty=… exclude=…",
        )
        audited_risk = AUDITED_RISK_RE.findall(body)
        result.require(bool(audited_risk), "AUDIT coincide sin **Riesgo auditado:**")
        if declared_risk and audited_risk:
            declared = declared_risk.group(1).lower()
            audited = audited_risk[-1].lower()
            result.require(
                RISK_RANK[audited] >= RISK_RANK[declared],
                f"AUDIT rebaja el riesgo: declarado {declared}, auditado {audited}",
            )
        if args.repo is not None and valid_snapshots and body is coincide_passes[-1]:
            recorded = valid_snapshots[-1]
            # La aprobación es un archivo humano del repositorio, no código: se
            # excluye del snapshot para que firmar no invalide la pasada que firma.
            excludes = parse_excludes(recorded) + (DEFAULT_APPROVALS,)
            try:
                current = identity(args.repo, excludes)
            except SnapshotError as error:
                result.warnings.append(f"no se pudo verificar el snapshot: {error}")
            else:
                result.require(
                    recorded.lower() == current.lower(),
                    f"la pasada auditó {recorded} y el árbol actual es {current}; reauditar",
                )
                result.require(
                    checkpoint_approval(args.repo, stage, recorded),
                    f"ninguna aprobación humana en {DEFAULT_APPROVALS} cubre la etapa "
                    f"{stage.name} en el snapshot auditado: una firma textual la escribe "
                    "el agente; ese archivo lo edita la persona",
                )
            # B-27: el alcance se comprueba en el diff. Un archivo que ninguna tarea
            # declara es superficie nueva y abre necesita-decision.
            try:
                declared = declared_files(tasks)
                # La base es el commit que abrió la etapa, no `HEAD`: quien
                # commitea su trabajo deja `git diff HEAD` vacío y el gate
                # aprobaría cualquier archivo (B-27).
                root = repo_root(args.repo.resolve())
                if stage_base(root, stage) is None:
                    result.warnings.append(
                        "la etapa no está commiteada: el alcance solo ve lo que "
                        "sigue sin commitear, no lo que ya se commiteó"
                    )
                touched = touched_files(
                    root, scope_base(root, stage), (stage, DEFAULT_APPROVALS)
                )
            except (ScopeError, SnapshotError) as error:
                result.warnings.append(f"no se pudo comprobar el alcance del diff: {error}")
            else:
                for path in compare(declared, touched)["undeclared"]:
                    result.require(
                        False,
                        f"{path} cambió y ninguna tarea declara `**Archivos:**` con esa ruta: "
                        "es alcance nuevo, reabre la conciliación (B-27)",
                    )
    if args.repo is not None and last_verdict and last_verdict != "coincide":
        result.warnings.append(
            "la última pasada no coincide: no hay snapshot que verificar contra el árbol actual"
        )

    index = read(stage.parent / "README.md")
    if index:
        estado = stage_index_estado(index, stage.name)
        if estado is not None:
            result.require(
                "cerrada" not in estado.lower() or has_coincide,
                "índice marca etapa cerrada sin AUDIT.md con veredicto coincide",
            )
    return finish(result)


def finish(result: Result) -> int:
    for text in result.warnings:
        print(f"WARN: {text}")
    for text in result.errors:
        print(f"ERROR: {text}")
    if not result.errors:
        print("OK: contrato estructural válido")
    return 1 if result.errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
