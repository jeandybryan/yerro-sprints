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
    ("coincide-sin-snapshot", "sin **Snapshot:**"),
    ("snapshot-de-pasada-anterior", "sin **Snapshot:**"),
    ("riesgo-rebajado", "rebaja el riesgo"),
]

VALIDATE_ACCEPTED = ["valid-stage", "index-estado/05-hecha"]


def check_validate_contract() -> None:
    """Cada regla nueva de validate_stage.py debe tener una fixture que la viole."""
    global checked
    for fixture in VALIDATE_ACCEPTED:
        result = run("validate_stage.py", str(FIXTURES / fixture), "--strict")
        checked += 1
        if result.returncode != 0:
            fail(f"validate/{fixture}: rechazó una etapa válida: {result.stdout}{result.stderr}")

    for fixture, expected in VALIDATE_REJECTED:
        result = run("validate_stage.py", str(FIXTURES / fixture), "--strict")
        checked += 1
        if result.returncode != 1:
            fail(f"validate/{fixture}: salida {result.returncode}, se esperaba 1")
        elif expected not in result.stdout:
            fail(f"validate/{fixture}: no reporta {expected!r} (obtenidos {result.stdout})")

    relaxed = run("validate_stage.py", str(FIXTURES / "riesgo-ausente"))
    checked += 1
    if relaxed.returncode != 0 or "WARN:" not in relaxed.stdout:
        fail(f"validate/riesgo-ausente: sin --strict debía avisar, no fallar: {relaxed.stdout}")
    strict = run("validate_stage.py", str(FIXTURES / "riesgo-ausente"), "--strict")
    checked += 1
    if strict.returncode != 1:
        fail("validate/riesgo-ausente: con --strict debía fallar por el riesgo ausente")

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

def main() -> int:
    check_transitions()
    check_doctor()
    check_doctor_structural()
    check_cli()
    check_validate_contract()
    check_expres_warning()
    for error in errors:
        print(f"ERROR: {error}")
    if not errors:
        print(f"OK: {checked} comprobaciones de transición y salud")
    return 1 if errors else 0

if __name__ == "__main__":
    raise SystemExit(main())
