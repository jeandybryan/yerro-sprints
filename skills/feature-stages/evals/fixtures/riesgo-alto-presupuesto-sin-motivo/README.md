# Fixture — presupuesto sobrescrito sin motivo

Riesgo `alto`, cuya presupuesto derivado es `1`, con
`**Presupuesto de deltas:** 2` y sin `**Motivo del presupuesto:**`.

Debe **fallar**: escribir un número mayor no amplía el margen. En
`next_step.py` ocurre lo mismo: sin motivo rige el derivado. El positivo
equivalente es `presupuesto-amplio`, que sí escribe el motivo.

El ledger de aquí **sí** cumple el fondo de `alto` (mutante en rojo y caso
límite), para que el único error sea el presupuesto.
