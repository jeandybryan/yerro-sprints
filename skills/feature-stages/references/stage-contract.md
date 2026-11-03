# Contrato de etapas

Este contrato define los artefactos y transiciones compartidos por las skills del ciclo. Las plantillas modulares de `feature-stages/templates/` son la forma canónica de producirlos; `templates.md` conserva solo el índice compatible.

## Transición única

El estado no se recuerda ni se negocia: se lee de los artefactos.

```bash
python3 <skills-root>/feature-stages/scripts/next_step.py <feature-root> [--stage NN-slug] [--json]
python3 <skills-root>/feature-stages/scripts/next_step.py <feature-root> --reconcile
python3 <skills-root>/feature-stages/scripts/doctor.py <feature-root>
python3 <skills-root>/feature-stages/scripts/snapshot.py <repo> --exclude <feature-root> --exclude .yerro/approvals.yml
python3 <skills-root>/feature-stages/scripts/expres.py <repo> [--base REF]
python3 <skills-root>/feature-stages/scripts/evidence.py run -- <comando...>
python3 <skills-root>/feature-stages/scripts/evidence.py verify <stage>/AUDIT.md
python3 <skills-root>/feature-stages/scripts/approvals.py <repo> --stage NN-slug
python3 <skills-root>/feature-stages/scripts/diff_scope.py <stage> --repo <repo> [--base REF]
```

Estados públicos: `trabajando`, `verificando`, `declarada-cerrada`, `necesita-decision`. `next_step.py` devuelve uno y la skill siguiente; `doctor.py` informa incoherencias entre el índice y los artefactos. Ambos son de solo lectura y no rebajan ningún gate: ante una discrepancia gana el gate más estricto y la discrepancia se registra como bloqueo. `necesita-decision` detiene el ciclo; no se sustituye por un valor por defecto.

`declarada-cerrada` dice lo que verifica el router: el índice marca la etapa `cerrada` y su auditoría declara `coincide`. No dice que los artefactos cumplan el contrato —`S-NN`, `Origen:`, `Interfaces:`, `Test-first:`, `**Snapshot:**`—, que es lo que juzga `validate_stage.py`. Antes se llamaba `listo`, y el nombre prometía más de lo comprobado: once etapas reales lo mostraban mientras el validador las rechazaba en todas sus tareas. La diferencia no se cierra en el router: un estado que declara cierre y un contrato que lo verifica son dos preguntas distintas, y el cierre cruzado las une con `validate_stage.py <stage> --repo <repo>` en la auditoría.

El contexto no sobrevive a la compactación (P21). Un agente que retoma una etapa relee `README.md`, `TAREAS.md` y `git log`, y ejecuta `next_step.py <feature-root> --reconcile` antes de actuar: imprime la transición del router, los IDs de tarea pendientes —proyectados por `tasks.py`, no un segundo veredicto del estado— y los últimos commits que tocan la etapa. Fuera de un repositorio git lo dice en vez de fallar. El modo imprime texto y no combina con `--json` ni `--all`: existe para releer el estado, no para alimentar un esquema nuevo. Re-ejecutar tareas que ya estaban hechas es el fallo más caro observado al usar el paquete contra trabajo real.

## Estados y baseline

- Conciliación: `borrador-corte` → `abierta` → `cerrada`. Una etapa ya cerrada puede volver a `abierta` por **reapertura** (ver abajo).
- Etapa: `borrador` → `conciliando` → `lista` → `implementando` → `auditando` → `cerrada`; `bloqueada` requiere causa, desbloqueador, evidencia y próxima revisión.
- `TAREAS.md` es la única lista principal. Un delta solo cierra una brecha contra el mismo baseline; un cambio de intención, alcance o CA reabre la conciliación y actualiza la lista principal.

## Reapertura

Una etapa cerrada reabre cuando el alcance que declaró se movió: otra etapa cambió un archivo que esta reclamaba, un cambio llegó al árbol después de la pasada que cerró, o la conciliación misma cambió de criterio. Un delta no cubre eso —corregiría contra un baseline que ya no es el vigente— y el presupuesto puede estar agotado.

La reapertura se registra en una **pasada nueva** del `AUDIT.md` que declara `**Reapertura:** <motivo>` y `**Veredicto:** no coincide`, porque la conformidad que registró otra pasada pertenecía a otro árbol. Esa pasada no lleva `**Veredicto (calidad):**` —no cierra— ni testigos de evidencia nuevos; no abre delta y no consume presupuesto. **La marca solo cuenta si la pasada no cierra:** una pasada `coincide` que nombra `**Reapertura:**` al citar la que resolvió es una pasada que cierra y no reabre nada.

Con la última pasada en `**Reapertura:**`, la etapa vuelve a `Conciliación: abierta` en `CONCILIACION.md` y en el índice, y su `Estado:` pasa a `implementando` (re-conciliando) conservando su `TAREAS.md`. `next_step.py` devuelve entonces `trabajando` con `conciliate-stage`, nunca `audit-stage`: lo siguiente es re-conciliar, no implementar. La etapa cierra cuando una pasada nueva vuelve a declarar `coincide` sobre el árbol resultante; el `no coincide` de la reapertura no se hereda como justificación de un delta.

## Campos obligatorios

Una conciliación cerrada tiene resultado observable, `Entra`, `No entra`, dependencias cerradas o excepcionadas y justificadas, preguntas resueltas o diferidas a una etapa nombrada y CA estables.

Cada `CA-NN` declara: tipo (`salida` o `invariante`), estímulo/precondición, resultado observable, promesa negativa/límite relevante y nivel de evidencia. Un CA ambiental además declara host/perfil, ventana, umbral y artefacto esperado.

Cada tarea principal `Tn` enlaza al menos un CA y contiene `Verificar:` con nivel, procedimiento y oráculo observable. La cobertura es bidireccional: todo CA tiene tarea y toda tarea enlaza un CA.

Un `AUDIT.md` que cierre una etapa conserva cada pasada. El veredicto `coincide` requiere todos los CA principales `cumple`, verificaciones aplicables ejecutadas, controles globales correctos y ningún desvío bloqueante. La evidencia se registra como `E-NN` con procedimiento, **sensibilidad demostrada**, esperado, observado/exit, entorno/timestamp, artefacto y limitación. Un `coincide` sin columna `Sensibilidad` no cierra: el ledger demuestra que el test pasó, no que pudiera fallar.

El cierre exige **dos veredictos** (P18, B-38). `**Veredicto:** coincide | no coincide` mide conformidad con la especificación. `**Veredicto (calidad):** aceptable | con hallazgos | bloqueante` responde solo por cuatro cosas del cambio: duplicación introducida, abstracción que nada pide (YAGNI), manejo de errores ausente en el camino nuevo y tests que prueban mocks en lugar del código. Solo `aceptable` cierra; `con hallazgos` se corrige con un delta dentro del presupuesto y se reaudita, y `bloqueante` no cabe en un delta: reabre la conciliación. El gate juzga la pasada que cierra, no las anteriores: una pasada `no coincide` no necesita veredicto de calidad.

## Riesgo, snapshot y presupuesto

- `**Riesgo:** bajo | medio | alto` se congela al cerrar la conciliación. `alto` nombra los ítems concretos: datos, seguridad, contratos compartidos, concurrencia, entrega o huecos de prueba. El auditor puede subirlo en `AUDIT.md`; bajarlo reabre la conciliación.
- Cada pasada registra `**Snapshot:**` con la salida exacta de `snapshot.py`. La identidad auditada es **el árbol**: `tree=`, con el `dirty=` que se deriva de él. `head=` es el commit desde el que se partió y `exclude=` la lista con la que se calculó el árbol; ninguno de los dos entra en la comparación, porque un commit de documentos mueve `head` y el alta de otra etapa del panel alarga `exclude=` sin cambiar una línea del código auditado. Un `tree=` distinto sí es otro árbol y hay que reauditar. El validador excluye siempre `.yerro/approvals.yml`: si la pasada no lo declara, lo avisa —el árbol es el mismo y la exclusión se aplica igual—; si su árbol lo incluye, no coincide y la pasada se vuelve a tomar. `snapshot.py` excluye también, por contrato, **todas las carpetas de etapa del panel** (las hermanas `NN-nombre` y su `README.md`, B-49/S61): la fila de estado del índice se escribe al cerrar y, dentro del snapshot, obligaría a una pasada nueva para cambiar una celda; y los documentos de una etapa dentro del snapshot de otra harían que escribir en la vecina invalidara una pasada que auditó el mismo código. Lo que se audita es el código; el panel es registro, y un archivo del panel que no es de etapa sigue contando.
- Un `coincide` solo vale para el snapshot que auditó. Si el árbol cambió, la pasada está obsoleta y se reaudita; no se reutiliza el veredicto para cerrar. `validate_stage.py <etapa> --repo <repo>` verifica esa coincidencia.
- Una **reapertura** no se cuenta contra el presupuesto de deltas aunque la última pasada sea `no coincide`: no corrige un hueco del baseline, lo reemplaza. La excepción no alcanza a una pasada `no coincide` sin `**Reapertura:**`, que sigue bloqueando con el presupuesto agotado.
- Un **delta** lo justifica una pasada que lo abre con `no coincide` **o** la pasada que lo cierra declarándolo en `**Deltas:**` con su ID (`D1`, `D2`): esa pasada dice a qué archivos aplica su conformidad y su ledger los mide. Un delta que ninguna pasada nombra no tiene origen (`DELTA_SIN_AUDIT`), y nombrarlo en prosa no lo declara. Un delta de verificación —sin hueco de código— existe precisamente por la declaración de cierre.
- `**Presupuesto de deltas:**` se **deriva del riesgo**: `bajo → 2`, `medio → 1`, `alto → 1`. Un valor escrito distinto solo vale con `**Motivo del presupuesto:**`; sin motivo gana el derivado, tanto en `validate_stage.py` como en `next_step.py`. Agotado el presupuesto, si la auditoría sigue en `no coincide`, `next_step.py` devuelve `necesita-decision` con `PRESUPUESTO_DE_DELTAS_AGOTADO`: reabrir la conciliación, aceptar el riesgo residual con owner o detener la etapa. Escribir otro delta no es una salida.
- **El presupuesto no funcional es un campo del corte (P7).** `**Presupuesto no funcional:**` declara, en cinco líneas, latencia, memoria, tamaño de artefacto, dependencias nuevas y rendimiento de la operación crítica. Cada línea se rellena o se marca `no aplica (motivo)`; `no aplica` sin razón es una línea vacía con más palabras, y conservar el `…` de la plantilla no responde. `validate_stage.py` exige las cinco respuestas y **no juzga el número**: el umbral lo acuerda el humano en la conciliación, `Verificar:` de cada tarea lo hereda y la auditoría lo mide contra el ledger. Una etapa que no puede responder una línea lo escribe con su motivo, no la omite.
- **Prueba y revisión son dos ejes (P22).** Test-first, sensibilidad demostrada y suite de referencia se exigen siempre; el riesgo solo cambia la profundidad de la revisión. «Revisión independiente» es un auditor distinto del implementador cuando el host lo permite; si no, la aprobación humana en `.yerro/approvals.yml`. Riesgo `bajo` no compra menos prueba.
- **La suite de referencia la declara el humano y la ejecuta el cierre (B-11).** `**Suites de referencia:**` en `CONCILIACION.md` nombra los comandos que deben pasar, en la forma en que se invocan. `ninguna` solo vale con `**Motivo de la suite:**` escrito: es la misma forma que el contrato usa para un presupuesto ampliado, y evita que «no ejecuté nada» pase en silencio. No la elige el agente: un repo grande no puede exigir «toda la suite» en cada etapa, y «nada» no protege. Al cerrar, cada comando declarado debe tener su fila `E-NN` en el ledger con el `Procedimiento/comando` que lo contiene, así que la verificación global deja de ser narrativa. Una suite declarada y no ejecutada es un comando prometido que nadie corrió.
- El riesgo decide el **fondo** de la evidencia, no si hay que demostrarla. La sensibilidad se exige siempre; por encima de `bajo` el ledger declara un caso límite o un negativo demostrado; en `alto`, cada CA crítico registra `mutante:` (o fallo inyectado) con resultado rojo (B-35: se exige ver el rojo, no una herramienta). El resultado se comprueba: `→ verde` (el mutante sobrevivió), `→ rojo esperado` (una predicción) o sin resultado no cumplen, y un rojo en un CA no compensa un verde en otro.

## Aprobación humana

- La firma vive en **`.yerro/approvals.yml`**, un archivo versionado del repositorio consumidor que **edita la persona**. `AUDIT.md` no lleva `**Aprobado por:**`: una marca que el agente puede escribir no distingue una firma de una invención.
- Cada entrada declara `etapa`, `aprobado-por`, `fecha` y, opcionalmente, `alcance`: el árbol aprobado, `tree=<sha>`, completo o en forma corta (`tree=152c3474`, el prefijo que muestra `git rev-parse --short` y que una persona copia de la pasada). Se compara con el `tree=` del snapshot, así que la firma sigue valiendo mientras el código no cambie, aunque un commit de documentos mueva `head=`. Un árbol que no es prefijo del auditado no cubre. Un prefijo literal del snapshot grabado (`head=<sha>`) se sigue aceptando para las firmas anteriores.
- Sin entrada para la etapa, el cierre no se sostiene: `validate_stage.py <etapa> --repo <repo>` lo comprueba y falla. La aprobación se escribe **antes** de auditar; el validador excluye `.yerro/` del snapshot para que firmar no invalide la pasada.
- Riesgo explícito y aceptado: un archivo del repositorio lo puede editar cualquier proceso con acceso, agente incluido, salvo que el host lo impida. La garantía es social —se revisa el diff—, no criptográfica. Un commit firmado es una extensión opcional.

## Cierre cruzado

Un `coincide` que baja el criterio más exigente declara `**Cruza riesgo:** sí — <qué se bajó>` y `**Motivo del presupuesto:** <por qué>` en la pasada, o el motivo en la conciliación. Sin motivo, la etapa no cierra. Los deltas declarados (`**Deltas:** D1, D2`) sobre el presupuesto vigente también cuentan como criterio rebajado.

## Rulings en ejecución (B-21, B-25, B-26)

- Una ambigüedad **dentro** del plan aprobado no detiene la implementación: se decide y se registra. Solo la categoría 3 (intención, alcance o criterio) y las paradas incondicionales (operación irreversible, seguridad, efecto fuera del worktree, dependencia externa nueva, plan roto) reabren `conciliate-stage`.
- El registro vive junto a la tarea que lo produjo, en `TAREAS.md`, con formato cerrado: `Ruling: <qué decidí> — <por qué> — <qué cuesta si me equivoco>`. Las tres partes son obligatorias; un ruling sin coste oculta la decisión y `validate_stage.py` lo rechaza.
- Un ruling de categoría 2 (efecto observable y reversible, sin cambio de alcance) añade `**Sujeto a revisión R1:**` en la tarea, numerado. `AUDIT.md` lo resuelve en `### Rulings revisados` como `- aceptado R1` o `- hallazgo R1`: el cruce es por identificador, así que una marca sin resolución o una resolución de otro ID impide el cierre.
- La revisión se hace contra artefactos y diff, nunca contra la conversación de implementación: «lo decidí porque…» no es un argumento (B-32).
- La categoría 3 no tiene gate propio porque el diff la cubre: lo que ningún CA ni tarea declara abre `necesita-decision` (B-27).

## Interfaces entre tareas (P17)

- En una etapa con más de una tarea, cada tarea declara `Interfaces:` con `Consume:` (la firma exacta que recibe de una tarea anterior, o `ninguna`) y `Produce:` (nombres y tipos que las posteriores dan por hechos). Sin eso, quien ejecuta la siguiente tarea inventa nombres.
- Una etapa de una sola tarea no necesita declararlo: no hay interfaz que cruzar.

## Alcance en el diff (B-27)

- Cada tarea declara `**Archivos:**` con las rutas que produce. Se derivan del CA, **nunca del diff** ya producido: tomarlas del diff blanquea justo el caso que el gate persigue (B-28).
- `scripts/diff_scope.py <etapa> --repo <repo> [--base REF]` compara lo que git ve cambiado contra lo declarado. Un archivo que ninguna tarea declara es **alcance nuevo** y abre `necesita-decision`; `validate_stage.py <etapa> --repo` lo comprueba en el cierre con la misma regla.
- El alcance son **todas** las listas de la etapa: `TAREAS.md` y cada `TAREAS-delta-NN.md`. Una tarea `D0N-TN` declara `**Archivos:**`, `Test-first:`, `Test:` y `Verificar:` igual que una principal, porque el delta es la corrección acotada de un hueco, no una lista de segunda. Leer solo la lista principal dejaba el archivo que produce un delta como alcance nuevo: esa etapa nunca podía cerrar.
- La base es **el commit que abrió la etapa**, derivado de la historia de su árbol: con `HEAD` como base, `git commit` dejaría el diff vacío y el gate aprobaría cualquier archivo (B-44). Si la etapa no está commiteada, se usa `HEAD` y el cierre avisa de que solo ve lo que sigue sin commitear.
- La apertura es el commit que añade su `TAREAS.md`, no la primera aparición de cualquier archivo de la carpeta (B-45). Una etapa puede dejar su `CONCILIACION.md` en un commit de hace semanas, junto a otras etapas, y empezar a implementarse mucho después: medir desde ahí arrastra todo lo que las otras etapas commitearon entre medias y el cruce se vuelve un falso positivo de cientos de archivos que ninguna tarea de esta etapa puede declarar. Sin `TAREAS.md` se cae a la primera aparición de la carpeta; sin nada, no hay base y el cierre avisa.
- El archivo que vive dentro de otra etapa del panel es de esa etapa, aunque el commit que lo tocó sea mixto: no es alcance de esta. Un commit que toca una carpeta de etapa del repositorio —forma `NN-nombre` con `CONCILIACION.md`, `TAREAS.md` o `AUDIT.md`, no solo las hermanas de su panel— y no esta atribuye sus rutas con hash y asunto; un commit sin etapa, el árbol de trabajo o un commit mixto siguen bloqueando (B-50). El gate no se rebaja: se atribuye.
- Una ruta declarada que no cambió **no bloquea**: es una tarea incompleta, y decidir si la tarea se cumplió es cierre, no alcance (B-29). Se informa.
- La evidencia de la etapa y `.yerro/` nunca cuentan como código: son el registro, no el cambio. La exclusión es la misma que la del snapshot, para que diff y snapshot hablen del mismo árbol.
- Los secretos locales tampoco cuentan: `.env`, `.env.*` y `*.local` nunca se versionan, y declararlos en una tarea empujaría a escribir la credencial en el árbol de la etapa (B-46). Se excluyen por forma, no por el nombre de un archivo de ningún consumidor. Un `.env.example` sí es contrato documentado y se declara como cualquier otra ruta.
- El cruce mira **todo el repo** desde la apertura de la etapa, no solo su carpeta. En un repo que mueve otras etapas en paralelo —o que hereda commits de ellas—, esas rutas aparecen como no declaradas y el cruce no puede estar verde aunque la etapa declare todo lo suyo; las rutas atribuidas a otra etapa se informan con su commit y no bloquean (B-50); las que vienen de esta etapa o de un commit sin etapa sí. Se declara la limitación con la medición y la atribución por commit, y no se sortea con `--base`. Si se quiere el cruce verde sin avisos, el trabajo de la etapa va en una rama donde solo esa etapa se mueve.

## Vía exprés

- Un cambio fuera del ciclo solo puede ser una corrección pequeña: un archivo de producción y como máximo 20 líneas de producción; las pruebas no cuentan.
- Migraciones, esquemas, seguridad/auth, contratos compartidos, interfaces públicas, dependencias nuevas y CA nuevos siempre abren etapa.
- `expres.py` decide los límites mecánicos. La ausencia de CA nuevo y de cambio de interfaz pública se confirma en la fila correspondiente de `EXPRES.md`.
- `EXPRES.md` es opcional y registral para la transición: `next_step.py` no lo lee. Cada fila declara `Comando`, `Resultado` (con exit o recuento) y `Confirmado por`; una fila incompleta es error de `doctor.py`, porque un registro sin prueba no acredita nada (P8).
- `doctor.py` rechaza la acumulación de tres o más registros sobre el mismo CA o archivo, un cambio exprés sobre el archivo de una etapa en `lista`, `implementando` o `auditando`, y una promoción `→ NN-slug` a una etapa fuera del índice. Son promociones: el trabajo pertenece a una etapa (P8).
- Si la comprobación mecánica dice `no cabe`, o no se pueden confirmar las dos condiciones manuales, se abre etapa sin override.

## Selección de trabajo

La prioridad es: (1) etapa nombrada por el usuario; (2) etapa comprometida en `Ciclo activo`; (3) delta que desbloquea ese objetivo; (4) etapa lista con mayor prioridad documentada; (5) primera elegible del índice. Registrar el motivo como `Por qué ahora`.

## Preguntas y evidencia

Antes de una pregunta bloqueante, la respuesta visible contiene `Contexto`, `Pregunta` y `Propuesta`. La selección en un formulario no reemplaza esos bloques.

`estructural` prueba forma; `conductual`, una rama y su oráculo; `sistema`, integración; `ambiental`, el host u operación acordados. No se puede sustituir un nivel requerido por uno inferior sin que el CA deje de cumplir.

## Ownership y handoff

| Fase | Entrada mínima | Puede modificar | No modifica | Entrega | Siguiente |
|---|---|---|---|---|---|
| `identify-feature-stages` | spec y contexto de feature | `README.md`, borradores `CONCILIACION.md` | `TAREAS.md`, `AUDIT.md`, código | árbol de etapas propuesto | `conciliate-stage` |
| `conciliate-stage` | spec y etapa seleccionada | `CONCILIACION.md`, índice operativo | `TAREAS.md`, código, `AUDIT.md` | baseline cerrado | `generate-stage-tasks` |
| `generate-stage-tasks` | conciliación cerrada | `TAREAS.md`, índice operativo | conciliación, código, auditoría | lista principal trazada | `implement-stage` |
| `implement-stage` | tareas o delta aprobado | código, tests, estado operativo | baseline, criterios, auditoría | implementación verificable | `audit-stage` |
| `audit-stage` | código, tareas y evidencia | `AUDIT.md`, delta, cierre del índice | código, baseline, criterios | `coincide`, `no coincide` o bloqueo | `implement-stage` o cierre |
| `feature-stages` | árbol completo | nada | todos los artefactos | transición calculada | skill indicada |

`README.md` puede actualizarse por la fase que cambia el estado operativo, pero
la fase no puede usar ese índice para ocultar un artefacto inválido. El handoff
se acepta solo cuando la entrada mínima y los gates del artefacto de salida
están satisfechos. `next_step.py` es la autoridad de transición; ninguna skill
inventa una siguiente fase.

## Política de contexto

Lee primero el `SKILL.md` activo, el contrato y los artefactos de entrada. Lee
una referencia temática o la plantilla específica solo cuando vayas a escribir
ese artefacto o resolver el caso que cubre. Por defecto **no** se cargan:

| Ruta | Motivo |
|---|---|
| `references/express-lane.md` | solo aplica a la vía exprés; esa vía tiene su propio procedimiento |
| `GOVERNANCE.md` | mantenimiento del paquete, no del trabajo de una etapa |
| `RELEASE_CHECKLIST.md` | publicación del paquete, no del trabajo de una etapa |
| `templates.md` | se lee la plantilla concreta que se va a escribir, no el índice de plantillas |

Esta tabla es la fuente: `preflight.py` emite la misma lista y `test_preflight.py`
falla si divergen. Añadir una fila cambia lo que el script omite; no hay dos
políticas.

| Fase | Lee primero | Carga bajo demanda |
|---|---|---|
| Identify | su skill y este contrato | plantilla de índice/conciliación |
| Conciliate | su skill, contrato y conciliación | decisiones/preguntas y plantilla de conciliación |
| Generate | contrato y conciliación cerrada | plantilla de tareas |
| Implement | contrato y `TAREAS.md` | delta, código y tests afectados |
| Audit | contrato y procedimiento de auditoría | scoring, evidencia y deltas |
| Router | routing y estado calculado | referencia solicitada explícitamente |

El plan de lectura no se adivina: `python3 scripts/preflight.py <feature-root>
[--etapa NN-slug] [--fase <skill>]` devuelve los archivos de la etapa en orden
con sus líneas, lo que **no** hay que leer con su motivo, y una estimación de
tokens con margen declarado (P11, B-15).

Tres reglas lo gobiernan (P14):

- si la fase no se reconoce, se prepara la etapa completa en vez de recortar;
- cada archivo omitido aparece con su motivo: un recorte silencioso es un
  defecto;
- las **líneas** son la medida reproducible; los tokens son información.

Sin `**Presupuesto de contexto:**` en la conciliación, `preflight.py` solo
informa. Con él, `--check` devuelve error al excederse (P12).

Presupuesto recomendado, calibrado el 2026-10-27 sobre seis features reales (47
etapas, todas implementadas y cerradas con el proceso): se mide la etapa activa
de cada árbol fase por fase y se toma el máximo observado, redondeado a la
centena para dejar margen.

| Fase | Máximo observado | Recomendado |
|---|---|---|
| identify / audit | 824 | 900 |
| conciliate / generate | 268 | 300 |
| implement | 380 | 400 |

`identify` y `audit` comparten número porque leen los mismos tres artefactos de
la etapa: dos presupuestos distintos para la misma lectura solo pueden
contradecirse, y con la propuesta anterior —400 y 1000— cualquier etapa entre
ambos demostraba que uno de los dos no significaba nada.

Son una **recomendación**, no un valor por defecto: ninguna etapa está obligada
a declararlos y `--check` solo mira las que lo hacen. Calibrar sobre el máximo
de trabajo aceptado evita el otro extremo: un presupuesto por debajo de 824
habría rechazado etapas que el equipo dio por buenas, y un gate que rechaza
trabajo aceptado se aprende a saltar.

## Glosario

- **Estado:** valor público del índice o del artefacto. Etapa: `borrador`, `conciliando`, `lista`, `implementando`, `auditando`, `cerrada`, `bloqueada`. Conciliación: `borrador-corte`, `abierta`, `cerrada`. Lista de tareas: `pendiente`, `en curso`, `implementando`, `implementada`, `auditada`. El vocabulario es cerrado y `next_step.py` bloquea con `TAREAS_ESTADO_DESCONOCIDO` ante cualquier otro valor —de ahí no se deduce «quizá pendiente»—, porque un valor inventado caía antes en la ruta por defecto y mandaba la etapa a `audit-stage` con trabajo pendiente y `exit 0`.
- **Origen:** decisión `S-NN` que justifica un `CA-NN`.
- **Riesgo:** nivel congelado al cerrar la conciliación: `bajo`, `medio` o `alto`.
- **Test-first:** si la tarea nace de una prueba que falla antes del cambio (`sí` o `no`).
- **Test:** comando reproducible que verifica la tarea. Si filtra por nombre (`--test-name-pattern`), el patrón tiene que casar al menos un caso del archivo que apunta: un patrón sin coincidencias sale 0 sin ejecutar nada y `validate_stage.py` lo rechaza.
- **Verificar:** nivel, procedimiento y oráculo observable de una tarea.
- **Ruling:** decisión tomada durante la implementación, con qué se decidió, por qué y qué cuesta equivocarse. Se escribe en `TAREAS.md`, junto a la tarea.
- **Sujeto a revisión R-NN:** marca numerada de un ruling de categoría 2; exige una resolución con el mismo ID en `### Rulings revisados` del `AUDIT.md`.
- **Snapshot:** identidad del árbol auditado: `head`, `tree`, `dirty` y `exclude`. La identidad es **el árbol**: `tree=`, con el `dirty=` que se deriva de él. Ni `head=` ni `exclude=` entran en la comparación: `head=` es el commit desde el que se partió —un commit que solo escribe rutas excluidas lo mueve sin tocar el árbol— y `exclude=` es la lista con la que se calculó, que crece al dar de alta otra etapa del panel sin cambiar el contenido auditado. Un `tree=` distinto sí es otro árbol y hay que reauditar.
- **Trazabilidad:** cadena `S-NN → CA-NN → T-NN → test → E-NN`.
- **Veredicto:** resultado de una pasada: `coincide` o `no coincide`. Manda la última pasada: una reapertura declara `no coincide` aunque una pasada anterior dijera `coincide`, y ese `coincide` no se reutiliza.
- **Reapertura:** `**Reapertura:** <motivo>` en la última pasada del `AUDIT.md`: el alcance se movió después del árbol auditado y la etapa re-concilia. No es un delta ni consume presupuesto, y nunca lleva a `audit-stage`.
- **Veredicto (calidad):** resultado de la pasada que cierra sobre las cuatro comprobaciones de calidad: `aceptable`, `con hallazgos` o `bloqueante`.
- **E-NN:** evidencia reproducible registrada en el ledger de la pasada.

## Evidencia, oráculo y sensibilidad

Una afirmación de cumplimiento no se sostiene con una transcripción. Ver [evidence.md](evidence.md) para el detalle; en resumen:

- `Test:` debe invocar un runner. El validador rechaza el trivio (`true`, `echo`, `sleep`, `:`, `bash -c true`, `python -c pass`) y acepta los runners que la conciliación declare en `**Runners:**`. Si no hay `**Runners:**`, un comando fuera de la lista negra solo avisa: el validador no adivina runners.
- La sensibilidad se demuestra con `revertir → rojo → restaurar`, con un mutante que produce rojo, o con una regresión funcional contra `HEAD`. No se exige herramienta de mutación: se exige **ver el rojo**.
- Una sensibilidad `no demostrada` deja el criterio en `no verificado`; nunca en `cumple`.
- `evidence.py run` ejecuta y deja `exit=` y `firma=` en la fila del ledger. `evidence.py verify` reejecuta lo declarado y compara: una firma que no se reproduce es evidencia inventada.
- La sensibilidad no se negocia por riesgo; lo que escala con el riesgo es el fondo (caso límite, mutante por CA crítico, recuperación observable).
