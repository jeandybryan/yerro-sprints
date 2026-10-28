# Registro de cambios exprés

Registro de cambios que no abren etapa. Una línea por cambio, en orden
cronológico. Si un cambio deja de cumplir la frontera, se promueve a etapa y
esta línea se marca `→ NN-slug`.

| # | Fecha | Cambio | Archivos | CA | Frontera | Comando | Resultado | Confirmado por |
|---|-------|--------|----------|----|----------|---------|-----------|----------------|
| E-01 | 2026-10-19 | Corregir el mensaje de error | `parser.py` | CA-02 | 1 archivo, 6 líneas | `python3 -m pytest tests/test_parser.py` | exit 0 · el mensaje conserva el formato previo | Ana Ruiz · 2026-10-19 |
| E-02 | 2026-10-19 | Ajustar el valor por defecto | `parser.py` | CA-02 | 1 archivo, 2 líneas | `python3 -m pytest tests/test_parser.py` | exit 0 · el valor por defecto sigue el del constructor | Ana Ruiz · 2026-10-19 |
| E-03 | 2026-10-19 | Normalizar el separador | `parser.py` | CA-02 | 1 archivo, 4 líneas | `python3 -m pytest tests/test_parser.py` | exit 0 · el separador se lee con comas | Ana Ruiz · 2026-10-19 |
