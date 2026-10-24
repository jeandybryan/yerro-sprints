#!/usr/bin/env python3
"""Prueba el contrato ejecutable: transición única y salud del árbol.

Uso: test_next_step.py

Recorre las fixtures de `evals/fixtures/` y afirma, para cada estado de los
artefactos, el estado público, la skill siguiente y los códigos de bloqueo.
También ejecuta `doctor.py` como subproceso: debe aceptar el árbol sano y
reportar cada regla estructural violada en `doctor-estructural/`, `huerfana/`
e `indice-sin-tabla/`. Solo stdlib; no consume tokens.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
FIXTURES = HERE.parent / "evals" / "fixtures"
sys.path.insert(0, str(HERE))

from next_step import DECISION, LISTO, TRABAJANDO, VERIFICANDO, FeatureError, analyze  # noqa: E402
import validate_stage  # noqa: E402

errors: list[str] = []
checked = 0

CASES = [
    # fixture, etapa, estado esperado, skill esperada, códigos de bloqueo esperados
    ("transiciones", "01-corte", TRABAJANDO, "conciliate-stage", []),
    ("transiciones", "04-lista", TRABAJANDO, "implement-stage", []),
    ("transiciones", "05-auditando", VERIFICANDO, "audit-stage", []),
    ("transiciones", "06-cerrada", LISTO, None, []),
    ("transiciones", "07-delta", TRABAJANDO, "implement-stage", []),
    ("transiciones", None, VERIFICANDO, "audit-stage", []),
    ("sin-tareas", None, TRABAJANDO, "generate-stage-tasks", []),
    ("abierta", None, DECISION, None, ["PREGUNTAS_ABIERTAS"]),
    ("inconsistente", None, DECISION, None, ["INDICE_CERRADO_SIN_COINCIDE"]),
    ("dependencia", "02-dependiente", DECISION, None, ["DEPENDENCIA_ABIERTA"]),
    ("bloqueada", None, DECISION, None, ["ETAPA_BLOQUEADA"]),
    ("ambiguo", None, DECISION, None, ["VARIAS_ETAPAS_ACTIVAS"]),
    ("ambiguo", "01-una", VERIFICANDO, "audit-stage", []),
    ("cierre-pendiente", None, DECISION, None, ["COINCIDE_SIN_CIERRE"]),
    ("delta-huerfano", "01-sin-audit", DECISION, None, ["DELTA_SIN_AUDIT"]),
    ("delta-huerfano", "02-con-coincide", DECISION, None, ["DELTA_SIN_AUDIT", "COINCIDE_SIN_CIERRE"]),
    ("sin-conciliacion", None, DECISION, None, ["CONCILIACION_AUSENTE"]),
    ("conciliacion-invalida", None, DECISION, None, ["CONCILIACION_INVALIDA"]),
    ("sin-principal", None, DECISION, None, ["TAREA_NO_PRINCIPAL"]),
    ("presupuesto-agotado", None, DECISION, None, ["PRESUPUESTO_DE_DELTAS_AGOTADO"]),
    ("presupuesto-excedido", None, DECISION, None, ["PRESUPUESTO_DE_DELTAS_AGOTADO"]),
    ("presupuesto-excedido-coincide", None, DECISION, None, ["PRESUPUESTO_DE_DELTAS_AGOTADO"]),
    ("presupuesto-amplio", None, VERIFICANDO, "audit-stage", []),
]

def fail(message: str) -> None:
    errors.append(message)

def check_transitions() -> None:
    global checked
    for fixture, stage, state, skill, codes in CASES:
        root = FIXTURES / fixture
        label = f"{fixture}/{stage or 'auto'}"
        try:
            result = analyze(root, stage)
        except FeatureError as error:
            fail(f"{label}: no se pudo analizar: {error}")
            continue
        checked += 1
        if result["state"] != state:
            fail(f"{label}: estado {result['state']!r}, se esperaba {state!r}")
        if result["siguiente"] != skill:
            fail(f"{label}: siguiente {result['siguiente']!r}, se esperaba {skill!r}")
        got = {item["codigo"] for item in result["blockers"]}
        missing = set(codes) - got
        if missing:
            fail(f"{label}: faltan bloqueos {sorted(missing)} (obtenidos {sorted(got)})")
        if not codes and got:
            fail(f"{label}: bloqueos inesperados {sorted(got)}")
        if state == DECISION and result["siguiente"] is not None:
            fail(f"{label}: necesita-decision no puede proponer una skill")

def run(script: str, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(HERE / script), *args],
        capture_output=True,
        text=True,
    )

def check_doctor() -> None:
    global checked
    healthy = run("doctor.py", str(FIXTURES / "transiciones"), "--json")
    checked += 1
    if healthy.returncode != 0:
        fail(f"doctor/transiciones: salida {healthy.returncode}, se esperaba 0: {healthy.stdout}{healthy.stderr}")
    else:
        report = json.loads(healthy.stdout)
        if not report["ok"] or report["errores"]:
            fail(f"doctor/transiciones: errores inesperados {report['errores']}")
        if report["siguiente"]["state"] != VERIFICANDO:
            fail("doctor/transiciones: la transición reportada no coincide con next_step")

    broken = run("doctor.py", str(FIXTURES / "inconsistente"), "--json")
    checked += 1
    if broken.returncode != 1:
        fail(f"doctor/inconsistente: salida {broken.returncode}, se esperaba 1")
    else:
        codes = " ".join(json.loads(broken.stdout)["errores"])
        if "INDICE_CERRADO_SIN_COINCIDE" not in codes:
            fail("doctor/inconsistente: no reporta el cierre sin veredicto")


STRUCTURAL_CASES = [
    "01-sin-tareas: etapa lista sin TAREAS.md",
    "02-sin-audit: etapa auditando sin AUDIT.md",
    "03-sin-conciliacion: falta CONCILIACION.md",
    "TAREAS-delta-1.md: nombre de delta fuera de NN",
    "TAREAS-delta-02.md: no declara **Cierra:**",
]

# Fixtures cuyo rechazo entero es la aserción: el mensaje debe aparecer.
REJECTED_FIXTURES = [
    ("huerfana", "02-huerfana sin fila en el índice"),
    ("indice-sin-tabla", "el índice no tiene una tabla"),
]

HANDOFF_CASES = [
    "01-prematuro: TAREAS.md prematuro para etapa borrador",
    "02-sin-test: TAREAS.md sin Test-first",
    "02-sin-test: TAREAS.md sin Test",
    "03-audit-incompleta: AUDIT.md sin Snapshot",
    "03-audit-incompleta: AUDIT.md sin Trazabilidad",
    "03-audit-incompleta: AUDIT.md sin E-NN",
    "03-audit-incompleta: AUDIT.md sin Veredicto",
    "04-cierre-sin-coincide: cierre sin veredicto coincide",
    "05-estado-incompatible: estado lista incompatible con conciliación abierta",
]


def check_doctor_structural() -> None:
    """Cada regla de doctor.py debe tener una etapa que la viole."""
    global checked
    result = run("doctor.py", str(FIXTURES / "doctor-estructural"), "--json")
    checked += 1
    if result.returncode != 1:
        fail(f"doctor/doctor-estructural: salida {result.returncode}, se esperaba 1")
        return
    reported = json.loads(result.stdout)["errores"]
    for expected in STRUCTURAL_CASES:
        if expected not in reported:
            fail(f"doctor/doctor-estructural: no reporta {expected!r} (obtenidos {reported})")

    for fixture, expected in REJECTED_FIXTURES:
        rejected = run("doctor.py", str(FIXTURES / fixture), "--json")
        if rejected.returncode != 1:
            fail(f"doctor/{fixture}: salida {rejected.returncode}, se esperaba 1")
            continue
        errors_text = " ".join(json.loads(rejected.stdout)["errores"])
        if expected not in errors_text:
            fail(f"doctor/{fixture}: no reporta {expected!r} (obtenidos {errors_text})")

    handoff = run("doctor.py", str(FIXTURES / "handoff-invalido"), "--json")
    checked += 1
    if handoff.returncode != 1:
        fail(f"doctor/handoff-invalido: salida {handoff.returncode}, se esperaba 1")
        return
    reported = json.loads(handoff.stdout)["errores"]
    for expected in HANDOFF_CASES:
        if expected not in reported:
            fail(f"doctor/handoff-invalido: no reporta {expected!r} (obtenidos {reported})")

def check_cli() -> None:
    global checked
    ok = run("next_step.py", str(FIXTURES / "transiciones"), "--json", "--check")
    checked += 1
    if ok.returncode != 0:
        fail(f"next_step --check: salida {ok.returncode} sobre un árbol sano")
    try:
        json.loads(ok.stdout)
    except json.JSONDecodeError:
        fail("next_step --json: la salida no es JSON")

    blocked = run("next_step.py", str(FIXTURES / "abierta"), "--check")
    checked += 1
    if blocked.returncode != 1:
        fail(f"next_step --check: salida {blocked.returncode} con necesita-decision")
    if "necesita-decision" not in blocked.stdout:
        fail("next_step --check: la salida legible no reporta necesita-decision")


VALIDATE_REJECTED = [
    ("cierre-sin-aprobacion", "sin **Motivo del presupuesto:**"),
    ("riesgo-alto-sin-mutacion", "ningún CA crítico registra `mutante:`"),
    # B-35 exige ver el rojo, no nombrar el mutante: un mutante que el test
    # no detectó (`→ verde`) no prueba sensibilidad.
    ("riesgo-alto-mutante-verde", "declara el resultado `verde`"),
    ("riesgo-alto-mutante-esperado", "rojo esperado` es una predicción"),
    ("riesgo-alto-presupuesto-sin-motivo", "supera el derivado"),
    ("test-decorativo", "Test: decorativo"),
    ("sin-sensibilidad", "sensibilidad no demostrada"),
    ("coincide-sin-snapshot", "sin **Snapshot:**"),
    ("snapshot-de-pasada-anterior", "sin **Snapshot:**"),
    ("trazabilidad-invalida", "no hay decisiones S-NN"),
    ("test-first-invalido", "no declara Test-first"),
    ("audit-trazabilidad-invalida", "sin **Trazabilidad:**"),
    ("riesgo-rebajado", "rebaja el riesgo"),
    # B-25: un ruling sin coste oculta la decisión.
    ("ruling-sin-coste", "sin las tres partes"),
    # B-26: un ruling de categoría 2 sin revisar impide el cierre.
    ("ruling-categoria-2-sin-revision", "Rulings revisados"),
 # B-26 por identificador: una marca sin ID no se puede resolver.
 ("ruling-sujeto-sin-id", "necesita un identificador"),
 ("ruling-sujeto-id-cruzado", "no resuelve R1"),
 # P17: la etapa multi-tarea exige interfaces.
 ("interfaces-ausentes", "no declara `Consume:`"),
 # P22: test-first no se proporcionaliza por riesgo.
 ("riesgo-bajo-sin-test-first", "no declara Test-first"),
]

VALIDATE_ACCEPTED = [
    "valid-stage",
    "index-estado/05-hecha",
    "riesgo-cruzado-con-motivo",
    "ruling-categoria-1",
    "ruling-categoria-2-revisado",
    "interfaces-presentes",
    "riesgo-bajo-con-test-first-sin-revision-independiente",
]


def check_validate_contract() -> None:
    """Cada regla nueva de validate_stage.py debe tener una fixture que la viole."""
    global checked
    for fixture in VALIDATE_ACCEPTED:
        result = run("validate_stage.py", str(FIXTURES / fixture))
        checked += 1
        if result.returncode != 0:
            fail(f"validate/{fixture}: rechazó una etapa válida: {result.stdout}{result.stderr}")

    for fixture, expected in VALIDATE_REJECTED:
        result = run("validate_stage.py", str(FIXTURES / fixture))
        checked += 1
        if result.returncode != 1:
            fail(f"validate/{fixture}: salida {result.returncode}, se esperaba 1")
        elif expected not in result.stdout:
            fail(f"validate/{fixture}: no reporta {expected!r} (obtenidos {result.stdout})")

    # B-28: hay un solo contrato. Las fixtures que vivían de la dualidad
    # `--strict` / aviso ahora describen estados que el contrato rechaza.
    for fixture in ("riesgo-ausente", "ca-tipo"):
        result = run("validate_stage.py", str(FIXTURES / fixture))
        checked += 1
        if result.returncode != 1:
            fail(f"validate/{fixture}: salida {result.returncode}, se esperaba 1 sin modo legado")

    # El presupuesto derivado del riesgo: escribir un número mayor en la
    # conciliación no amplía el margen mientras falte `**Motivo del presupuesto:**`.
    amplio = run("next_step.py", str(FIXTURES / "presupuesto-amplio"), "--json")
    checked += 1
    payload = json.loads(amplio.stdout) if amplio.stdout.strip() else {}
    if payload.get("presupuesto_deltas") != 3:
        fail(
            "next_step/presupuesto-amplio: el motivo escrito no habilitó el presupuesto "
            f"(obtenido {payload.get('presupuesto_deltas')}, esperado 3)"
        )

    # Sin motivo, el mismo 3 no amplía nada: rige el derivado del riesgo.
    sin_motivo = run("validate_stage.py", str(FIXTURES / "riesgo-alto-presupuesto-sin-motivo"))
    checked += 1
    if sin_motivo.returncode != 1 or "supera el derivado" not in sin_motivo.stdout:
        fail(f"validate/riesgo-alto-presupuesto-sin-motivo: {sin_motivo.stdout}")

# B-35 se cumple por el resultado observado, no por la palabra. Se prueban los
# cuatro veredictos del parser directamente: una fixture sola no distingue un
# mutante rojo de uno verde cuando ambos son texto válido.
for mut_detalle, expected in (
    ("mutante: invertir separador → rojo", ["rojo"]),
    ("mutante: invertir separador → verde", ["verde"]),
    ("mutante: invertir separador → rojo esperado", ["esperado"]),
    ("mutante: invertir separador", ["sin resultado"]),
):
    checked += 1
    got = validate_stage.mutation_verdicts(mut_detalle)
    if got != expected:
        fail(f"mutation_verdicts: {mut_ledger!r} dio {got}, se esperaba {expected}")

# B-25 se cumple por estructura, no por longitud. Los tres separadores que un
# agente puede escribir cuentan; dos partes nunca.
for ruling, valido in (
    ("separador `;` — locales europeos — una línea y su test", True),
    ("separador `;` -- locales europeos -- una línea y su test", True),
    ("separador `;` – locales europeos – una línea y su test", True),
    ("separador `;` — locales europeos", False),
    ("separador `;` — locales europeos — ", False),
    ("separador `;`", False),
):
    checked += 1
    partes = [x for x in validate_stage.RULING_SEPARATOR_RE.split(ruling) if x.strip()]
    if (len(partes) >= 3) != valido:
        fail(f"ruling {ruling!r}: tres partes = {len(partes) >= 3}, se esperaba {valido}")

# B-26 se cruza por identificador: la marca y su resolución comparten `R-NN`.
# El parser acepta `R1` (y `r1`), y no confunde una marca sin ID.
for marca, esperado in (
    ("**Sujeto a revisión R1:** límite 50", "R1"),
    ("**Sujeto a revisión r2:** texto de error", "r2"),
    ("**Sujeto a revisión:** límite 50", ""),
    ("**Sujeto a revisión R1 R2:** límite 50", "R1 R2"),
):
    checked += 1
    encontrado = validate_stage.SUBJECT_RE.search(marca)
    if encontrado is None:
        fail(f"sujeto a revisión {marca!r}: el parser no lo reconoce")
        continue
    if encontrado.group(1).strip() != esperado:
        fail(
            f"sujeto a revisión {marca!r}: id "
            f"{encontrado.group(1).strip()!r}, se esperaba {esperado!r}"
        )

for resolucion, esperado in (
    ("- aceptado R1 — límite 50", ("aceptado", "R1")),
    ("- hallazgo R2 — contradice el CA", ("hallazgo", "R2")),
    ("- aceptado — límite 50", None),
    ("- R1 aceptado — límite 50", None),
):
    checked += 1
    encontrado = validate_stage.SUBJECT_RESOLVED_RE.search(resolucion)
    obtenido = (encontrado.group(1), encontrado.group(2)) if encontrado else None
    if obtenido != esperado:
        fail(f"resolución {resolucion!r}: {obtenido}, se esperaba {esperado}")

# P17: `Consume:`/`Produce:` se leen dentro de la tarea; `ninguna` es válido.
for cuerpo, consume, produce in (
    ("  Interfaces:\n    Consume: ninguna\n    Produce: `f() -> int`\n", True, True),
    ("  Interfaces:\n    Consume: `f() -> int` de T1\n    Produce: README\n", True, True),
    ("  Consume:\n    Produce: nada\n", False, True),
    ("  Consume: ninguna\n", True, False),
):
    checked += 1
    if bool(validate_stage.CONSUME_RE.search(cuerpo)) != consume:
        fail(f"Interfaces: Consume mal detectado en {cuerpo!r}")
    if bool(validate_stage.PRODUCE_RE.search(cuerpo)) != produce:
        fail(f"Interfaces: Produce mal detectado en {cuerpo!r}")

# Un mutante rojo en un CA y otro verde en otro no se compensan: basta uno que
# sobreviva para que el ledger no demuestre sensibilidad.
mixto = (
    "| E-01 | CA-01 | pytest | mutante: A → rojo |\n"
    "| E-02 | CA-02 | pytest | mutante: B → verde |\n"
    "| E-03 | CA-01 | pytest | caso límite: entrada vacía |"
)
checked += 1
gaps = validate_stage.risk_evidence_gaps("alto", mixto)
if not any("verde" in gap.lower() for gap in gaps):
    fail(f"risk_evidence_gaps: un mutante verde pasó desapercibido (obtenido {gaps})")

# `rojo esperado` es una predicción, no una observación (evidence.md §2).
checked += 1
prediccion = (
    "| E-01 | CA-01 | pytest | mutante: A → rojo esperado |\n"
    "| E-02 | CA-01 | pytest | caso límite: entrada vacía |"
)
if not validate_stage.risk_evidence_gaps("alto", prediccion):
    fail("risk_evidence_gaps: aceptó `rojo esperado` como observación")

# El mismo ledger sin mutante rojo sigue cerrando: el gate no veta el caso sano.
checked += 1
sano = (
    "| E-01 | CA-01 | pytest | mutante: A → rojo |\n"
    "| E-02 | CA-01 | pytest | caso límite: entrada vacía |"
)
if validate_stage.risk_evidence_gaps("alto", sano):
    fail(f"risk_evidence_gaps: rechazó un ledger alto correcto ({validate_stage.risk_evidence_gaps('alto', sano)})")

    open_pass = run(
        "validate_stage.py",
        str(FIXTURES / "transiciones" / "07-delta"),
        "--repo",
        str(HERE.parents[2]),
    )
    checked += 1
    if open_pass.returncode != 0:
        fail(f"validate --repo: una última pasada en no coincide no debe fallar: {open_pass.stdout}")
    elif "no hay snapshot que verificar" not in open_pass.stdout:
        fail("validate --repo: no avisa que la última pasada no tiene snapshot que verificar")

def check_rulings_warning() -> None:
    """B-33: más de tres rulings por tarea avisa y apunta a generate-stage-tasks."""
    global checked
    excesivo = run("doctor.py", str(FIXTURES / "rulings-excesivos"), "--json")
    checked += 1
    if excesivo.returncode != 0:
        fail("doctor/rulings-excesivos: el aviso de rulings no debe bloquear")
        return
    warnings = " ".join(json.loads(excesivo.stdout)["advertencias"])
    for expected in ("4 rulings en una tarea", "generate-stage-tasks"):
        if expected not in warnings:
            fail(f"doctor/rulings-excesivos: no reporta {expected!r} (obtenidos {warnings})")

    aceptado = run("doctor.py", str(FIXTURES / "rulings-aceptados"), "--json")
    checked += 1
    warnings = " ".join(json.loads(aceptado.stdout)["advertencias"])
    if "rulings en una tarea" in warnings:
        fail(f"doctor/rulings-aceptados: avisó con tres rulings (obtenidos {warnings})")


EXPRES_EXPECTED = (
    "3 cambios sobre el mismo CA 'CA-02'",
    "3 cambios sobre el mismo archivo 'parser.py'",
)


def check_expres_warning() -> None:
    """El registro exprés avisa por acumulación, pero nunca bloquea."""
    global checked
    acumulado = run("doctor.py", str(FIXTURES / "expres-acumulado"), "--json")
    checked += 1
    if acumulado.returncode != 0:
        fail(f"doctor/expres-acumulado: salida {acumulado.returncode}, no debe bloquear")
        return
    report = json.loads(acumulado.stdout)
    warnings = " ".join(report["advertencias"])
    for expected in EXPRES_EXPECTED:
        if expected not in warnings:
            fail(f"doctor/expres-acumulado: no reporta {expected!r} (obtenidos {warnings})")
    checked += 1
    if report["errores"]:
        fail(f"doctor/expres-acumulado: el registro no puede producir errores: {report['errores']}")

    sano = run("doctor.py", str(FIXTURES / "expres-sano"), "--json")
    checked += 1
    if sano.returncode != 0:
        fail(f"doctor/expres-sano: salida {sano.returncode}, se esperaba 0")
        return
    if json.loads(sano.stdout)["advertencias"]:
        fail("doctor/expres-sano: avisó por debajo del umbral")

    for fixture in ("expres-acumulado", "expres-sano"):
        result = run("next_step.py", str(FIXTURES / fixture), "--json")
        checked += 1
        if result.returncode != 0:
            fail(f"next_step/{fixture}: el registro exprés no debe cambiar la transición")
            continue
        data = json.loads(result.stdout)
        if data["state"] != TRABAJANDO or data["siguiente"] != "implement-stage":
            fail(f"next_step/{fixture}: transición {data['state']}/{data['siguiente']} alterada por EXPRES.md")

def check_validate_no_crash() -> None:
    """Ninguna fixture puede hacer que el validador se caiga en vez de juzgar."""
    global checked
    for fixture in sorted(FIXTURES.iterdir()):
        if not fixture.is_dir():
            continue
        targets = [fixture] if (fixture / "CONCILIACION.md").exists() else []
        targets += [item for item in fixture.iterdir() if item.is_dir()]
        for target in targets:
            if not (target / "CONCILIACION.md").exists() and not any(
                (target / name).exists() for name in ("CONCILIACION.md", "AUDIT.md")
            ):
                continue
            result = run("validate_stage.py", str(target))
            checked += 1
            crashed = result.returncode not in (0, 1) or "Traceback" in result.stdout + result.stderr
            if crashed:
                fail(
                    f"validate/{target.name}: se cayó en vez de juzgar "
                    f"(salida {result.returncode}): {(result.stdout + result.stderr).strip()[:200]}"
                )


def main() -> int:
    check_transitions()
    check_doctor()
    check_doctor_structural()
    check_cli()
    check_validate_contract()
    check_validate_no_crash()
    check_expres_warning()
    check_rulings_warning()
    for error in errors:
        print(f"ERROR: {error}")
    if not errors:
        print(f"OK: {checked} comprobaciones de transición y salud")
    return 1 if errors else 0

if __name__ == "__main__":
    raise SystemExit(main())
