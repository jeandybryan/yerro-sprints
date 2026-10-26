# Etapa 04 — exportar con separador configurable

**Estado:** cerrada
**Riesgo:** medio

## Resultado observable

El usuario exporta la lista con el separador que elige, y el README explica cómo
usar la función con y sin argumentos.

## Dependencias

- `Ninguna`

## Entra

- Elegir `,` o `;` como separador del export.
- Documentar la función de export para quien consuma la librería.

## No entra

- Nuevos formatos de archivo.

## Aclaraciones

- **S-01 — Decisión de baseline:** el separador es un parámetro con `,` por
  defecto, para no romper a quien ya llama a la función.
**Riesgo:** medio

## Criterios de aceptación

- **CA-01 — [condición de salida]:** exportar con separador `;` produce un archivo separado por punto y coma; sin elegir, se usa `,`; evidencia `conductual`. Origen: S-01

## Riesgos y compatibilidad

- Cambiar la firma rompería a los consumidores; por eso el parámetro tiene
  default.

## Bloqueos

- `Ninguno`
