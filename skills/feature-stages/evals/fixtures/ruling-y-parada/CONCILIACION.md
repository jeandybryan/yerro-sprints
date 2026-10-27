# Etapa 03 — exportar las solicitudes cerradas

**Estado:** cerrada
**Suites de referencia:** `pytest tests/test_export.py`
**Riesgo:** medio

## Resultado observable

Las solicitudes cerradas se pueden exportar desde la pantalla de listado.

## Dependencias

- `Ninguna`

## Entra

- Exportar las solicitudes cerradas, en el formato que ya usa la pantalla.
- El nombre visible de la columna que muestra el total.

## No entra

- Cambiar el esquema de la base de datos.
- Añadir columnas que nadie pidió.

## Aclaraciones

- **S-01 — Decisión de baseline:** el export respeta la paginación actual de la
  lista y no la amplía.
**Riesgo:** medio

## Criterios de aceptación

- **CA-01 — [condición de salida]:** exportar las solicitudes cerradas produce un archivo descargable; sin solicitudes, solo la cabecera; evidencia `conductual`. Origen: S-01

## Riesgos y compatibilidad

- `Ninguno identificado`

## Bloqueos

- `Ninguno`
