# Registro de cambios exprés

Dos cambios sobre el mismo archivo y ningún CA repetido tres veces: el registro
es válido y no debe producir ninguna advertencia de acumulación.

| # | Fecha | Cambio | Archivos | CA | Frontera | Comando | Resultado | Confirmado por |
|---|-------|--------|----------|----|----------|---------|-----------|----------------|
| E-01 | 2026-10-19 | Corregir el mensaje de error | `parser.py` | — | 1 archivo, 6 líneas | `python3 -m pytest tests/test_parser.py` | exit 0 · el mensaje conserva el formato previo | Ana Ruiz · 2026-10-19 |
| E-02 | 2026-10-19 | Ajustar el valor por defecto | `parser.py` | — | 1 archivo, 2 líneas | `python3 -m pytest tests/test_parser.py` | exit 0 · el valor por defecto sigue el del constructor | Ana Ruiz · 2026-10-19 |
