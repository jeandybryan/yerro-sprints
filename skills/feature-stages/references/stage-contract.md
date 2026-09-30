# Contrato de etapas

Este contrato define los artefactos y transiciones compartidos por las skills del ciclo. Las plantillas de `sprints/feature-stages/templates.md` son la forma canónica de producirlos.

## Estados y baseline

- Conciliación: `borrador-corte` → `abierta` → `cerrada`.
- Etapa: `borrador` → `conciliando` → `lista` → `implementando` → `auditando` → `cerrada`; `bloqueada` requiere causa, desbloqueador, evidencia y próxima revisión.
- `TAREAS.md` es la única lista principal. Un delta solo cierra una brecha contra el mismo baseline; un cambio de intención, alcance o CA reabre la conciliación y actualiza la lista principal.

## Campos obligatorios

Una conciliación cerrada tiene resultado observable, `Entra`, `No entra`, dependencias cerradas o excepcionadas y justificadas, preguntas resueltas o diferidas a una etapa nombrada y CA estables.

Cada `CA-NN` declara: tipo (`salida` o `invariante`), estímulo/precondición, resultado observable, promesa negativa/límite relevante y nivel de evidencia. Un CA ambiental además declara host/perfil, ventana, umbral y artefacto esperado.

Cada tarea principal `Tn` enlaza al menos un CA y contiene `Verificar:` con nivel, procedimiento y oráculo observable. La cobertura es bidireccional: todo CA tiene tarea y toda tarea enlaza un CA.

Un `AUDIT.md` que cierre una etapa conserva cada pasada. El veredicto `coincide` requiere todos los CA principales `cumple`, verificaciones aplicables ejecutadas, controles globales correctos y ningún desvío bloqueante. La evidencia se registra como `E-NN` con procedimiento, esperado, observado/exit, entorno/timestamp, artefacto y limitación.

## Selección de trabajo

La prioridad es: (1) etapa nombrada por el usuario; (2) etapa comprometida en `Ciclo activo`; (3) delta que desbloquea ese objetivo; (4) etapa lista con mayor prioridad documentada; (5) primera elegible del índice. Registrar el motivo como `Por qué ahora`.

## Preguntas y evidencia

Antes de una pregunta bloqueante, la respuesta visible contiene `Contexto`, `Pregunta` y `Propuesta`. La selección en un formulario no reemplaza esos bloques.

`estructural` prueba forma; `conductual`, una rama y su oráculo; `sistema`, integración; `ambiental`, el host u operación acordados. No se puede sustituir un nivel requerido por uno inferior sin que el CA deje de cumplir.
