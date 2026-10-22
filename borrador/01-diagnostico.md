# 01 — Diagnóstico

> Estado: en discusión. Cada hueco cita el artefacto actual del repo que lo
> demuestra, para que la crítica sea verificable y no una opinión.

## Cómo se midió

Lectura del estado publicado (`skills/`) y de su validador estructural.
No se ejecutó una evaluación conductual (requiere tokens y un modelo fijo);
los huecos S02/S13/S18 ya están descritos en `skills/feature-stages/EVALUATION.md`
y aquí se señalan como riesgos de proceso, no como resultados medidos.

---

## D1 — El test-first es estructural, no demostrable

**Dónde:** `references/decision-traceability.md` (línea 12-13) y
`templates/AUDIT.md` (línea 59).

> "Cada tarea incluye `Test-first: sí` y `Test: <comando reproducible>`."

El validador comprueba que **exista el texto** `Test: <algo>`. No comprueba:

- que el comando ejecute algo;
- que tenga un oráculo (assertion, exit code distinto de 0, comparación);
- que **haya fallado antes** de la implementación.

Un agente puede escribir `Test: true`, `Test: echo hecho` y la etapa cierra.
La propia `EVALUATION.md` lo reconoce como caso S18 ("test decorativo o sin
test-first"), pero solo en el nivel 3 — evaluación conductual bajo demanda, que
no es un gate.

**Consecuencia:** el criterio de "un `coincide` vale" depende de la buena fe del
agente.

---

## D2 — La auditoría no exige ver el oráculo fallar

**Dónde:** `skills/audit-stage/SKILL.md` (líneas 37-58) y
`references/...` (no existe aún un `audit-procedure.md` propio; las reglas viven
en `templates/AUDIT.md` y en `stage-contract.md`).

La auditoría re-ejecuta tests y busca negativos "proporcionales al riesgo".
Pero no distingue entre:

- un test que **puede** detectar el defecto;
- un test que solo **pasa** con el código actual.

Ambos se ven igual en un ledger de evidencia: `exit 0`, todos verdes.

La literatura de mutación (mutation testing) y de revisión adversarial converge
en la misma regla: **un oráculo que nunca falló no es evidencia**. Sin un
mutante, un fallo inyectado o un valor esperado alterado a mano, la columna
"Observado" del ledger no demuestra sensibilidad.

**Consecuencia:** la auditoría puede ser formalmente correcta y materialmente
vacía.

---

## D3 — No hay gate humano ni separación de roles

**Dónde:** todo el contrato (`references/stage-contract.md`, tabla de ownership).

La tabla de ownership dice **qué escribe cada fase**, no **quién** la ejecuta.
En la práctica, un agente puede encadenar conciliar → generar → implementar →
auditar sin que una persona apruebe nada. El único punto con confirmación
humana explícita es la vía exprés (dos condiciones manuales).

Los únicos invariantes que protegen contra el auto-cierre son formales
(snapshot, riesgo rebajado, presupuesto de deltas). Ninguno impide que el mismo
agente que implementó escriba el `coincide`.

**Consecuencia:** un revisor humano no tiene un punto de entrada obligatorio;
el proceso es auditable en el papel y opaco en la práctica.

---

## D4 — El riesgo no define obligaciones y el presupuesto de deltas es arbitrario

**Dónde:** `references/stage-contract.md` (líneas 36-39) y
`templates/AUDIT.md` (líneas 63-65).

`**Riesgo:** bajo | medio | alto` se congela y no puede bajarse. Es un buen
invariante. Pero:

- "alto" no obliga a nada concreto más allá de "nombra los ítems";
- "bajo" no exige menos evidencia que "alto";
- `**Presupuesto de deltas:**` tiene default 2 sin relación con el riesgo.

Un cambio de 3 líneas en auth (riesgo alto) y un cambio de 300 líneas en una
página de marketing (riesgo bajo) tienen el mismo presupuesto y la misma
exigencia de evidencia.

**Consecuencia:** el riesgo se etiqueta bien y se usa poco.

---

## D5 — El cierre no exige suite completa ni diff completo

**Dónde:** `templates/AUDIT.md` ("Verificación global") y
`skills/implement-stage/SKILL.md` (línea 53: "Run proportional tests/lints").

"Proporcional" es la palabra clave: la implementación corre lo que la tarea
dice. El cierre no exige:

- la suite completa del repo en verde;
- lint/tipado en verde;
- el **diff completo** contra el baseline, para detectar cambios fuera de
  `Entra`.

Un cambio que cumple los CAs nuevos y rompe tres tests viejos puede cerrar si
esos tests no están en el `Test:` de ninguna tarea.

**Consecuencia:** el hueco de regresión clásico queda abierto.

---

## D6 — La trazabilidad no se comprueba de punta a punta

**Dónde:** `references/decision-traceability.md` (línea 14-15).

La cadena es `S-NN → CA-NN → T-NN → test → E-NN`. El validador comprueba:

- que los CA tengan `Origen: S-NN` (con fixture `trazabilidad-invalida`);
- que las tareas tengan `Test-first:` y `Test:`.

No comprueba mecánicamente:

- que todo `CA` citado en `AUDIT.md` exista en `CONCILIACION.md`;
- que toda `E-NN` referenciada tenga fila en el ledger;
- que toda `S` citada exista;
- que no haya IDs duplicados o huérfanos.

**Consecuencia:** la cadena se puede "dibujar" con IDs que no existen.

---

## D7 — Falta el no-funcional

**Dónde:** `references/stage-contract.md` (línea 36: los ítems de riesgo).

Rendimiento, memoria, tamaño, accesibilidad, compatibilidad y número de
dependencias viven dentro de "riesgo alto" como texto libre. No hay un
**presupuesto numérico** obligatorio ni una declaración explícita de que no
aplica.

**Consecuencia:** el rendimiento se descubre en producción, y "no aplica" no
queda escrito, así que no se puede auditar.

---

## D8 — La vía exprés queda fuera de todo gate

**Dónde:** `references/express-lane.md` (líneas 24-32).

`EXPRES.md` "es registral: `next_step.py` no lo lee, no cambia una transición y
no bloquea una etapa". `doctor.py` solo emite `WARN` a los tres cambios.

Dos problemas:

1. Un cambio exprés no exige **comando de verificación** ni resultado, así que
   no hay evidencia de que se probó.
2. El `WARN` por acumulación nunca bloquea: tres cambios en el mismo archivo
   son, por definición, una feature sin etapa.

**Consecuencia:** el modo de trabajo más común es el único sin trazabilidad
verificable.

---

## D9 — No hay nivel intermedio

**Dónde:** `references/express-lane.md` (frontera: 1 archivo, ≤20 líneas) frente
a seis fases completas.

Entre "1 archivo/20 líneas" y "seis fases" no hay nada. Una feature de tres
archivos con riesgo bajo paga el coste completo.

**Consecuencia:** la fricción empuja a usar la vía exprés por encima de su
frontera, o a omitir el ciclo.

---

## D10 — El validador es sintáctico; la evidencia es prosa

**Dónde:** `templates/AUDIT.md` (ledger `E-NN`, líneas 20-22).

El ledger registra "Observado/exit" como **texto que el agente escribe**. Nada
verifica que ese `exit 0` ocurrió. Un agente que quiere cerrar puede escribir
un ledger plausible.

Esto es el hueco raíz: **todas las demás defensas (snapshot, riesgo congelado,
presupuesto) se apoyan en que el ledger dice la verdad.**

**Consecuencia:** el proceso es tan riguroso como la honestidad del agente.
