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

Si cabe, registra en `EXPRES.md` el cambio, por qué respeta la frontera y cómo
se verificó. `EXPRES.md` es registral: `next_step.py` no lo lee, no cambia una
transición y no bloquea una etapa.

`doctor.py` emite `WARN` al acumular tres o más cambios sobre el mismo CA o
archivo. Es señal de que el corte estaba mal hecho y el trabajo debe promoverse
a una etapa; nunca es un error estructural.
