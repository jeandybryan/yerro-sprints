# Vía exprés

La vía exprés decide si una corrección pequeña puede quedar fuera del árbol de
etapas. No es una etapa ni una séptima skill.

```bash
python3 <skills-root>/feature-stages/scripts/expres.py <repo> [--base REF]
```

## Frontera

Cabe fuera del ciclo solo si cumple todo:

- un archivo de producción;
- como máximo 20 líneas de producción; las pruebas no cuentan;
- ninguna migración, esquema, seguridad/auth, contrato compartido o manifiesto
  de dependencias;
- no introduce un CA nuevo;
- no cambia una interfaz pública.

Las dos últimas condiciones requieren confirmación humana. Si el script dice
`no cabe`, o no se pueden confirmar, se abre etapa sin override.

## Registro y promoción

Si cabe, registra en `EXPRES.md` el cambio con cuatro cosas: la **Frontera**
—por qué cabía—, el **Comando** que lo comprobó, el **Resultado** con su exit
y la **Confirmación** humana de las dos condiciones que el diff no puede
mostrar. Una fila sin ellas no es un registro: `doctor.py` la rechaza como
error (P8). El exit es lo que distingue «pasó» de «no se ejecutó»; `ok` no lo
distingue.

`EXPRES.md` sigue siendo registral para la transición: `next_step.py` no lo
lee y no cambia ninguna etapa. Lo que no es registral es su contenido.

## Promoción: de aviso a error

`doctor.py` rechaza, como error:

- tres o más cambios sobre el mismo CA o el mismo archivo;
- un cambio exprés sobre un archivo que declara una tarea de una etapa en
  `lista`, `implementando` o `auditando` —esa etapa está abierta y el cambio es
  trabajo suyo—;
- una línea marcada `→ NN-slug` cuyo destino no existe en el índice.

Las tres significan lo mismo: el corte estaba mal y el trabajo pertenece a una
etapa. Promover no impide mergear; impide seguir sin abrir etapa. Una etapa
cerrada no cuenta nunca: sus archivos son histórico, no trabajo en curso.
