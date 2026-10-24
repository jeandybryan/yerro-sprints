# Borrador — endurecimiento del ciclo YerroSprints

> **Estado:** propuesta en discusión. Nada de esta carpeta es normativo ni está
> implementado. El ciclo publicado sigue siendo el de `skills/`.
>
> Esta carpeta recoge el diseño del *endurecimiento de calidad* del ciclo:
> las mejoras discutidas, sus supuestos, su alcance y las decisiones que aún
> no están tomadas. No contiene fixtures, scripts ni cambios en las skills:
> cuando una idea madure, se propondrá como cambio de contrato con su fixture.

## Por qué existe

El ciclo actual impone **conformidad estructural**: `validate_stage.py` comprueba
que los artefactos tienen la forma acordada. Eso no garantiza que el software
producido sea correcto. Los huecos identificados:

1. `Test-first: sí` y `Test: <comando>` se validan como texto; un comando
   decorativo satisface el gate.
2. La auditoría pide "intentar refutar", pero no exige ver el oráculo fallar.
3. No hay gate humano ni separación de roles entre quien implementa y quien
   audita.
4. El riesgo es una etiqueta, no un mínimo de evidencia; el presupuesto de
   deltas es una constante mágica.
5. El cierre no exige suite completa ni diff completo contra el baseline.
6. La trazabilidad `S → CA → T → test → E` no se comprueba de punta a punta.
7. No hay presupuesto no funcional (latencia, memoria, tamaño, dependencias).
8. La vía exprés queda fuera de todo gate verificable.
9. No hay nivel intermedio entre "1 archivo/20 líneas" y "seis fases completas".
10. El validador es sintáctico: un agente puede escribir un `coincide` falso.

La tesis del borrador:

> **Un `coincide` debe significar que el test vio fallar al código.**
> Todo lo demás es burocracia bien escrita.

A la tesis se le suma **una restricción, no una meta opcional**:

> **Si una regla se puede ejecutar, no se le pide al LLM que la recuerde.**
> Pero ningún ahorro de tokens puede rebajar un gate de calidad.

## Documentos

| Documento | Contenido |
| --- | --- |
| [01-diagnostico.md](01-diagnostico.md) | Los huecos, con evidencia del estado actual del repo. |
| [02-propuestas.md](02-propuestas.md) | Las diez mejoras iniciales (P1–P10), cada una con diseño, gate y coste. |
| [03-decisiones.md](03-decisiones.md) | Decisiones tomadas, propuestas y **abiertas** (requieren acuerdo). |
| [04-plan-de-trabajo.md](04-plan-de-trabajo.md) | Orden de implementación, dependencias y criterio de salida. |
| [05-preguntas-abiertas.md](05-preguntas-abiertas.md) | Lo que falta acotar o agregar antes de congelar el diseño. |
| [06-economia-de-tokens.md](06-economia-de-tokens.md) | Eje transversal: coste de contexto, primacía determinista y la regla de que la calidad nunca se rebaja por ahorrar tokens. |
| [07-referencias-gentle-ai.md](07-referencias-gentle-ai.md) | Contraste con [gentle-ai](https://github.com/Gentleman-Programming/gentle-ai): qué confirma, qué nos corrige y qué nos falta. |
| [08-referencias-superpowers.md](08-referencias-superpowers.md) | Contraste con [superpowers](https://github.com/obra/superpowers): disciplina, evidencia y método para escribir skills. |
| [09-propuestas-superpowers.md](09-propuestas-superpowers.md) | Propuestas P17–P24 derivadas de superpowers. |
| [10-modelo-c-rulings.md](10-modelo-c-rulings.md) | **Diseño acordado**: cómo se decide en ejecución (Q15), formato del ruling, fixtures y cambios por archivo. |
| [11-resolucion-abiertas.md](11-resolucion-abiertas.md) | Qué se cerró de las 20 preguntas, con qué norma y qué queda esperando datos. |

## Primer acuerdo: Modelo C (Q15)

La primera decisión cerrada del borrador es **cómo actúa el agente cuando
encuentra algo que el plan no resolvió**. Se acordó el **Modelo C**: se decide
por *clase* de decisión, no por duda.

| Categoría | Qué hace el agente |
| --- | --- |
| Detalle de implementación | Decide y registra `Ruling:` con coste de equivocarse |
| Efecto observable y reversible | Decide, registra y marca `**Sujeto a revisión:**` |
| Cambio de intención, alcance o criterio | Para y reabre `conciliate-stage` |

Y una decisión de migración asociada (B-28): cuando entre, **no habrá modo
legado**. Un solo contrato, un solo modo de validación, y las etapas en curso se
migran re-conciliando el alcance, nunca derivando los archivos del diff.

Diseño completo en [10-modelo-c-rulings.md](10-modelo-c-rulings.md); normas en
B-21, B-25, B-26 y B-27; propuesta P19; Fase 5 del plan.

## Estado del borrador

Las 20 preguntas abiertas están resueltas salvo dos que **no se resuelven
escribiendo**: Q1 (presupuesto de deltas por riesgo) y Q9 (presupuesto de
contexto) se cierran con datos de uso real. Q2 y Q13 siguen diferidas (B-06).

Resumen y razonamiento en [11-resolucion-abiertas.md](11-resolucion-abiertas.md).
**Fase 1 implementada (2026-10-22):** oráculo mínimo, `Sensibilidad` obligatoria
en el ledger y evidencia firmada con `evidence.py`. Las fixtures
`test-decorativo` y `sin-sensibilidad` **pasaban** con el contrato viejo y hoy
fallan.

**Fase 2 implementada (2026-10-23):** aprobación humana en
`.yerro/approvals.yml`, riesgo que fija el fondo de la evidencia, presupuesto de
deltas derivado del riesgo y cierre bloqueado si el criterio se rebaja sin
motivo. El gate de mutación ahora juzga el **resultado observado**: un mutante
`→ verde` ya no cierra. Lo siguiente es la Fase 5 (Modelo C: rulings), que
además arrastra los campos de rol de P3.

## Reglas de esta carpeta

- Nada aquí entra en `skills/` sin: (a) decisión acordada, (b) fixture que
  falle con el contrato viejo, (c) caso en el test correspondiente, (d) fila en
  `EVALUATION.md` y (e) entrada en `CHANGELOG.md`. Es la regla de `AGENTS.md`.
- Una mejora que cambie una transición o un gate **no** se publica como
  "documentación": se publica como cambio de contrato con su evidencia.
- Este borrador no se cita desde `README.md` ni desde las skills hasta que se
  decida publicarlo.
- Las decisiones de licencia, distribución, tags, hosts y owner siguen
  pendientes según `GOVERNANCE.md`; este borrador no las toca.

## Convención de estados de cada propuesta

Cada propuesta de `02-propuestas.md` y `09-propuestas-superpowers.md` usa uno de
estos estados:

- `abierta`: se está discutiendo; puede cambiar de forma.
- `acordada`: el diseño está cerrado; falta implementar.
- `descartada`: se discutió y no va, con motivo.
- `diferida`: válida, pero fuera del alcance de esta iteración.
