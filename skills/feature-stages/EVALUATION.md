# Evaluación de skills de etapas

Mide si las skills del ciclo conservan el contrato, se activan para la petición correcta y cambian decisiones con evidencia. No mide longitud, cobertura global ni benchmarks generales.

## Niveles

1. **Estructural — CI/local, sin tokens.** Ejecutar `scripts/validate_stage.py` sobre fixtures y etapas reales. Verifica el contrato de artefactos.
2. **Activación y separación — CI/local, sin tokens.** Los casos `evals/cases/*.json` contienen peticiones positivas y negativas escritas como usuarios reales. Un cambio de descripción no puede hacer que otra skill sea la respuesta esperada.
3. **Comportamiento — bajo demanda, consume tokens.** Ejecutar cada caso en un snapshot aislado y puntuar el transcript/diff contra `expectations`. Mantener casos retenidos que la skill no vea antes de la evaluación.

Al informar resultados, fijar modelo, versión de Cursor/agente, fecha, configuración y commit de las skills. Una regresión en un caso retenido bloquea adoptar una redacción hasta explicar y corregir la causa.

## Casos retenidos

| ID | Fallo sembrado | Skill esperada | Resultado exigido |
|----|----------------|----------------|-------------------|
| S01 | CA compuesto | `conciliate-stage` | Lo descompone o enumera afirmaciones/evidencia atómicas. |
| S02 | Prueba decorativa sin assertion | `implement-stage`, `audit-stage` | Exige oráculo o fallo inyectado; no marca cumple. |
| S03 | Dependencia abierta | `generate-stage-tasks`, `implement-stage` | Bloquea salvo excepción escrita y justificada. |
| S04 | Cambio disfrazado como delta | `audit-stage` | Confirma y reabre conciliación; no genera delta. |
| S05 | Evidencia ambiental ausente | `audit-stage` | `no verificado`/`bloqueada`, nunca cierre. |
| S06 | Fuga de alcance hacia una integración no aprobada | `audit-stage` | Desviación con impacto y propietario. |
| S07 | Proceso externo adverso | `implement-stage`, `audit-stage` | Fallo inyectado y recuperación observable. |
| S08 | Almacenamiento persistente adverso | `implement-stage`, `audit-stage` | Consistencia fs↔DB y reintento/estado observable. |
| S09 | Pregunta asumida | `conciliate-stage` | `Contexto`, `Pregunta`, `Propuesta` visibles; no cierra con default. |
| S10 | Oráculo unidireccional | `audit-stage` | Pide afirmación negativa/inversa o reabre. |
| S11 | Índice cerrado con audit fallido | validador | Falla el contrato, no acepta el cierre. |
| I01 | Corte ambiguo o por encabezados | `identify-feature-stages` | Pide aclaración o corta por resultados; asigna requisitos; no crea tareas/auditoría. |

## Rúbrica conductual

Puntuar 0/1 por: riesgo identificado; baseline preservado; evidencia correcta; ausencia de falso cierre; siguiente artefacto mínimo; paths/comandos reproducibles; ausencia de scope extra. Registrar puntos, falsos positivos, falsos cierres, rework y tiempo hasta evidencia suficiente.

## Ejecución

```bash
# Desde la raíz del paquete: <skills-root>/feature-stages
python3 scripts/validate_stage.py evals/fixtures/valid-stage --strict
python3 scripts/validate_stage.py evals/fixtures/closed-without-task --strict
```

Para comportamiento, materializar la fixture indicada en un repositorio temporal, dar el `prompt` a un agente con la skill objetivo y aplicar la rúbrica a la conversación y artefactos. Los casos de activación se revisan al editar `description` de cualquier skill: al menos tres positivos, dos negativos con propietario y una evaluación conductual por skill modificada.
