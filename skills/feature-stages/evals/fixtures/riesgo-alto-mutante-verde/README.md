# Fixture — mutante que sobrevive

Riesgo `alto` con presupuesto sancionado, caso límite y una prueba de mutación
que **sí** está declarada: `mutante: separador invertido → verde`.

Debe **fallar**. B-35 exige *ver el rojo*, no nombrar la palabra `mutante`; un
mutante que el test no detectó prueba lo contrario de lo que el ledger afirma:
que el oráculo no cubre ese comportamiento.

El único defecto es el resultado del mutante: presupuesto, caso límite y
sensibilidad están en orden, así que el error solo puede venir de ese gate.
