# Auditoría — etapa 01

**Snapshot:** `head=abc123 dirty=no` (fixture)
**Trazabilidad:** CA-01 → T1 → test_parser → E-01
**Veredicto:** coincide
**Veredicto (calidad):** aceptable

## Ledger

| Evidencia | CA | Tarea | Test | Sensibilidad | Resultado |
| --- | --- | --- | --- | --- | --- |
| E-01 | CA-01 | T1 | `pytest tests/test_parser.py` | mutante que devuelve el mensaje anterior: rojo | exit 0 |
