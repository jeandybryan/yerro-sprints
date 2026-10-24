# Fixture — ruling de categoría 2 marcado y sin revisar

`T1` cambia el límite por defecto de una paginación (observable, reversible, sin
cambio de alcance) y lo marca con `**Sujeto a revisión:**`. El `AUDIT.md` cierra
con `coincide` y **no** tiene la sección `### Rulings revisados`.

Debe **fallar** (B-26): un ruling de categoría 2 sin resolver —ni aceptado ni
convertido en hallazgo— impide el cierre. La marca mantiene la decisión visible
sin detener el trabajo; la revisión es lo que la vuelve auditable.

Riesgo `bajo` para que el gate del fondo no se mezcle con este: el único defecto
es la revisión ausente.
