# Fixture — cierre con el criterio rebajado sin motivo

La pasada declara `**Cruza riesgo:** sí` (baja el criterio más exigente) y no
escribe `**Motivo del presupuesto:**`.

Debe **fallar**: `validate_stage.py` exige el motivo o la etapa no cierra.

**Nota de nombre:** la aprobación humana ya no vive en el artefacto (B-37), así
que esta fixture no prueba "falta la firma": prueba el gate de criterio
rebajado. La firma se prueba en `test_snapshot.py`, con `.yerro/approvals.yml`
real. Se conserva el nombre histórico para no reciclar una fixture.
