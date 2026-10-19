# Gobernanza de YerroSprints

Este documento define cómo se mantiene el paquete sin mezclar reglas de
consumidores dentro de las seis skills. Una decisión marcada como pendiente no
se puede resolver por defecto ni publicar como si estuviera acordada.

## Límites de responsabilidad

- `identify-feature-stages` corta la especificación en resultados observables;
  no crea tareas ni audita.
- `feature-stages` define el contrato, los estados, los gates y la evaluación;
  no ejecuta una fase.
- `conciliate-stage` cierra intención, alcance, decisiones, criterios, riesgo
  y evidencia esperada; no implementa.
- `generate-stage-tasks` produce la única lista principal trazada a los CA;
  no cambia el baseline.
- `implement-stage` ejecuta solo una lista aprobada; no audita su propio
  resultado.
- `audit-stage` intenta refutar el cumplimiento y conserva la evidencia; no
  reescribe el baseline para hacer pasar el código.

Una modificación que afecte más de una frontera debe explicar la separación o
partirse en cambios revisables.

## Presupuesto de revisión

- Un cambio debe tener una intención revisable y una prueba de regresión cuando
  cambie comportamiento.
- Si el diff mezcla contrato, scripts, fixtures y documentación de varias fases,
  se divide en commits o PRs que puedan validarse por separado.
- El tamaño no se usa para rebajar un gate. Un cambio pequeño que altera una
  transición sigue necesitando fixture negativa y mutation check.
- La vía exprés solo aplica a cambios fuera del árbol de etapas y respeta su
  frontera mecánica y su registro `EXPRES.md`.

## Uso de IA

- La IA puede explorar, proponer, editar y ejecutar validaciones dentro del
  alcance autorizado, pero no decide silenciosamente intención de producto,
  alcance, riesgo aceptado, owner, licencia, distribución ni política de tags.
- Toda decisión de producto acordada por una persona queda en
  `CONCILIACION.md` como `S-NN`, con cita textual cuando sea relevante.
- La IA no puede convertir una pregunta abierta en una decisión, rebajar un
  riesgo, reutilizar un `coincide` obsoleto ni escribir otro delta después de
  agotar el presupuesto.
- No se introducen secretos, datos de consumidores ni contenido propietario en
  fixtures, prompts, logs o documentación del paquete.
- La revisión humana conserva la responsabilidad de aceptar el baseline, el
  riesgo, la evidencia y el release.

## Cambios de baseline

Un cambio de intención, alcance o criterio reabre conciliación. No se maquilla
como delta, no se resuelve con una excepción en tareas y no se cierra con una
pasada de auditoría antigua.

## Decisiones pendientes antes de publicar

Estas decisiones no están acordadas en el repositorio y deben resolverse antes
de crear una release o promesa de compatibilidad:

- licencia y titulares de derechos;
- canales de distribución y repositorios canónicos;
- política de tags y versionado publicado;
- agentes/hosts oficialmente soportados;
- owner de mantenimiento y mecanismo de aprobación.

Hasta que cada punto tenga una decisión registrada, el paquete puede validarse
localmente, pero no debe presentarse como release gobernada.

## Contexto progresivo

Cada skill carga primero su contrato y los artefactos de entrada. Las plantillas
modulares y referencias temáticas se leen bajo demanda, solo al escribir o
resolver el artefacto correspondiente. Esta política reduce contexto repetido
sin omitir gates: no se cargan todas las plantillas ni todo `GOVERNANCE.md` por
defecto.
