# Mantenimiento de skills del ciclo

Cambiar cualquiera de las seis skills (`identify-feature-stages`, `feature-stages`,
`conciliate-stage`, `generate-stage-tasks`, `implement-stage`, `audit-stage`)
exige conservar este contrato y ejecutar los casos retenidos definidos en
`../EVALUATION.md`. Mantener los procedimientos en cada skill; las reglas transversales viven en `stage-contract.md` para evitar divergencia.

No añadir una skill nueva si extiende de forma natural una de las existentes. Una nueva skill necesita una petición distinta, pasos verificables y casos de activación positivos y negativos.

Las skills deben mantenerse cortas y operativas; las reglas normativas detalladas viven en referencias enlazadas y no se duplican en cada `SKILL.md`.

## Una regla nueva trae su fixture

Toda regla de gate entra con una fixture que **falle con el contrato anterior** y
un caso en el test correspondiente. Si la fixture pasa antes del cambio, la regla
no comprueba nada: se revisa el diseño, no se rebaja la fixture.

Una regla nueva o que cambia comportamiento trae además su **baseline**: qué hizo
el agente sin ella, en una frase, con la cita del comportamiento observado. Sin
baseline y sin fixture, la regla solo ocupa contexto.

```text
Regla: <texto que se añade>
Baseline: <qué hizo el agente sin la regla; cita verbatim>
Reps: <n ≥ 5 por variante>
Control: <qué falló sin la guía>
```

Si el control no exhibe el fallo, **no hay nada que corregir**: la regla no se
escribe. Cinco repeticiones que producen cinco interpretaciones dicen que la
redacción no obliga, aunque cada una parezca razonable: la varianza se reporta,
no se promedia (P23). Las correcciones factuales, de enlace y de formato quedan
exentas (B-24); sin esa acotación el proceso de mantenimiento se vuelve
inoperable.

## La forma de la regla depende del fallo

La misma frase no corrige todos los fallos. Antes de escribir una regla,
clasifica qué falla y usa la forma que ese fallo pide (P24):

| Fallo | Forma correcta |
| --- | --- |
| Salta la regla bajo presión | prohibición + tabla de racionalizaciones + red flags |
| Output con forma equivocada | receta positiva: el output **es** esto, en orden |
| Omite un elemento | campo obligatorio en la plantilla |
| Depende de condición | condicional con predicado observable |

Dos prohibiciones de redacción:

1. **Sin cláusulas de matiz.** «No hagas X salvo que importe» reabre la
   negociación, y bajo presión siempre se encuentra que importa.
2. **Las excepciones no se escriben como cláusulas**, sino como otro
   condicional con predicado observable: «salvo que el riesgo lo justifique»
   no se comprueba; «si `**Motivo del presupuesto:**` está escrito» sí.

La forma se juzga en la revisión del PR, no con un linter: el catálogo no
puede saber si una regla responde a un fallo de forma o de disciplina sin
metadata por regla, y añadirla obligaría a declarar `Fallo:` y `Forma:` en
cada regla de las seis skills. La revisión comprueba dos cosas: que una
regla de forma no esté escrita como prohibición, y que toda excepción nombre
su predicado.

## Evidencia antes que transcripción

Lo que cierra una etapa es una observación, no un relato. `Test:` se rechaza si
no invoca un runner, y el ledger `E-NN` exige la columna `Sensibilidad`. La
evidencia citada para cerrar sale de `evidence.py run`, no de la memoria: una
firma que no se reproduce con `evidence.py verify` es evidencia inventada.
