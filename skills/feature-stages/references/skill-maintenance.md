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

## Evidencia antes que transcripción

Lo que cierra una etapa es una observación, no un relato. `Test:` se rechaza si
no invoca un runner, y el ledger `E-NN` exige la columna `Sensibilidad`. La
evidencia citada para cerrar sale de `evidence.py run`, no de la memoria: una
firma que no se reproduce con `evidence.py verify` es evidencia inventada.
