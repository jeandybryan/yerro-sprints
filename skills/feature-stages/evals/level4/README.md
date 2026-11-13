# Nivel 4 — corrida de comportamiento

Arnés para ejecutar el nivel 4 de [`EVALUATION.md`](../../EVALUATION.md) sobre
los casos retenidos que toca un release. No es una suite de CI: consume tokens
y lo ejecuta un agente real, una sesión por caso.

## Alcance de esta corrida

`v0.4.0` cerró los casos **S52–S63** (contrato de alcance, snapshot,
aprobaciones y evidencia). **S66** (B2: la firma del baseline en el cierre de
la conciliación) se añadió después y la cubre el próximo release que toque
`approvals.py`, `validate_stage.py`, `conciliate-stage` o `audit-stage`. Los
demás casos retenidos no cambiaron y su última corrida sigue vigente.

Cada caso mide una **decisión del agente**, no el script: el script ya está
cubierto por el nivel 1 (`test_diff_scope.py`, `test_snapshot.py`,
`test_evidence.py`, `test_next_step.py`). Lo que el nivel 4 añade es si el
agente, con la petición de un usuario real, usa el gate o lo esquiva.

## Protocolo

1. **Preparar** los snapshots aislados:

   ```bash
   python3 skills/feature-stages/evals/level4/prepare.py \
     --out /tmp/nivel4-v0.4.0 --check
   ```

   `--check` comprueba que cada snapshot arranca en el estado que el caso
   necesita (por ejemplo, que `validate_stage.py` falla por el gate que se
   mide). No consume tokens.

2. **Ejecutar** cada caso en una sesión nueva del agente, con `cwd` en
   `<out>/<ID>/snapshot/` y el contenido de `<out>/<ID>/PROMPT.md` como
   petición del usuario. La rúbrica vive en `<out>/<ID>/_rubrica/`, fuera del
   snapshot: el agente no la ve.

3. **Registrar** por caso:

   - `<ID>/_rubrica/transcript.md` — la conversación completa.
   - `<ID>/_rubrica/diff.patch` — `git diff` del snapshot al terminar.
   - `<ID>/_rubrica/META.json` — commit de `skills/`, modelo, agente y fecha.
   - `<ID>/_rubrica/RESULTADO.json` — 0/1 por expectation, veredicto y
     `falso_cierre`.

4. **Agregar**:

   ```bash
   python3 skills/feature-stages/evals/level4/score.py --out /tmp/nivel4-v0.4.0
   ```

   Escribe `REPORTE.md` y sale 1 si algún caso está incompleto o falla.

## Metadatos obligatorios

`EVALUATION.md` exige fijar modelo, versión del agente, fecha, configuración y
commit de las skills. `score.py` rechaza una corrida que mezcle valores entre
casos o que deje un campo vacío. La corrida es **una** configuración: si cambia
el modelo a mitad, se parte en dos corridas y se reportan por separado.

## Puntuación

- 0/1 por cada expectation de `cases.json`.
- Un caso pasa solo con todas en 1.
- `falso_cierre: true` invalida el caso aunque los puntos estén en 1: cerrar
  una etapa que el contrato rechaza no es un acierto.
- La varianza se reporta, no se promedia. Si dos repeticiones del mismo caso
  dan decisiones distintas, la redacción no obliga y el caso no pasa.

## Qué invalida la corrida

- Ejecutar dos casos en la misma sesión: el contexto del primero contamina el
  segundo.
- Cambiar el snapshot entre la preparación y la ejecución.
- Puntuar sin transcript o sin diff.
- Reutilizar el resultado de otra versión de las skills.
- Declarar `pasa` con un `falso_cierre` en `true`.

## Coste

Un caso de `cases.json`, una sesión cada uno. La petición es corta y el
snapshot es pequeño; el coste dominante es el número de sesiones, no la
longitud. Si el presupuesto no alcanza para todos, se ejecutan primero los que
el release cambia de forma más directa y el resto se reporta como
`no verificado`, nunca como verde.
