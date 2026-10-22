# Evidencia, oráculo y sensibilidad

Este documento define **qué cuenta como prueba**. Sin él, `cumple` es una
palabra amable: `Test: true` termina en verde y la etapa cierra.

La cadena es:

```text
Test: <comando>  →  el comando debe poder fallar  →  se ve fallar  →  E-NN
```

---

## 1. Oráculo mínimo

Un `Test:` es válido solo si invoca un **runner** y su código de salida depende
del comportamiento.

### Lista negra: rechazo directo

Comandos que nunca prueban nada, aunque devuelvan `0`:

| Comando | Por qué no prueba |
| --- | --- |
| `true`, `:`, `false` | No ejecutan nada |
| `echo …`, `printf …` | Imprimen; el `0` es del `echo` |
| `sleep …` | Espera; no observa |
| `cat …`, `ls …`, `pwd`, `cd …` | Leen; no juzgan |
| `bash -c true`, `sh -c :`, `python -c pass` | El trivio disfrazado |
| `exit 0`, `:` | Verde incondicional |

El validador aplica la negra sobre el comando **completo**, no solo sobre la
primera palabra: `pytest -q && true` también se rechaza si todo el comando es
trivio. Y rechaza la forma encadenada cuando **todas** las partes están en la
negra.

### Lista blanca: runners declarados

La conciliación puede declarar los runners del proyecto:

```markdown
**Runners:** pytest | npm test | go test ./... | cargo test
```

Un comando que empieza por un runner declarado es aceptado sin más preguntas.
Si el proyecto no declara runners y el comando no está en la negra, el
validador **avisa** — no falla — porque el validador no puede adivinar todos los
runners del mundo.

La lista blanca reconoce el **instrumento**, no demuestra que el test pruebe
algo. `pytest -q` sobre un test vacío pasa la lista y falla la sensibilidad.

---

## 2. Sensibilidad: el test debe poder fallar

Un runner no basta: el test puede existir y no comprobar nada. La sensibilidad
se **demuestra**, no se declara. Tres métodos aceptados, en el ledger `E-NN`:

### a) Revertir → debe fallar → restaurar

```text
escribir el test  →  pasa
revertir el fix   →  DEBE FALLAR
restaurar el fix  →  pasa
```

Es el método más directo y el que usa superpowers: *"If you didn't watch the
test fail, you don't know if it tests the right thing."*

### b) Mutante

```text
mutante: <qué se cambió en el código>
resultado: rojo esperado | rojo obtenido
```

Cualquier método cuenta — herramienta de mutación, edición manual, fallo
inyectado. **No se exige herramienta** (B-35): lo que se exige es **ver el rojo**,
no instalar mutmut.

### c) Regresión funcional contra `HEAD`

```text
comando viejo contra HEAD  →  stdout/stderr/exit = X
comando nuevo contra el cambio  →  stdout/stderr/exit = Y
diferencia no pedida  →  regresión
```

Sirve para cambios sobre comandos ya existentes, donde no hay test unitario que
escribir.

### Qué no cuenta

- "Debería fallar si…": una predicción no es una observación.
- Un fallo por error de sintaxis o por un import roto: el test falla por la razón
  equivocada. Se corrige y se vuelve a ejecutar hasta que falle **por el
  comportamiento**.
- Un test que solo prueba mocks: se rompe el mock y el test sigue verde.

---

## 3. Cuándo se exige

La sensibilidad **no se negocia** por riesgo (B-23): siempre se exige en el
nivel que el CA declare. Lo que cambia con el riesgo es el **fondo**.

| Riesgo | Sensibilidad | Fondo adicional |
| --- | --- | --- |
| bajo | ≥1 test con fallo observado | — |
| medio | + un caso límite demostrado | — |
| alto | + un mutante o fallo inyectado **por CA crítico** | recuperación observable |

Un CA sin sensibilidad es `no verificado`, nunca `cumple`.

---

## 4. Dónde se registra

En el ledger de `AUDIT.md`, dos columnas nuevas:

| ID | CA | Procedimiento/comando | Sensibilidad | Esperado |
| --- | --- | --- | --- | --- |
| E-01 | CA-01 | `pytest -q tests/test_csv.py` | revertir → rojo → restaurar | verde/0 |

Si la sensibilidad no se pudo demostrar, la columna dice `no demostrada` y el
criterio es `no verificado`. No hay celda vacía que se pueda saltar.

---

## 5. Por qué el validador no lo hace solo

El validador **rechaza** la negra y exige la columna. No ejecuta los tests: eso
lo hace `implement-stage` y lo verifica `audit-stage` con snapshot. Un validador
que ejecutase tests propios sería un gate que miente cuando el entorno no está
preparado; la evidencia ya exige procedimiento reproducible.

Lo que sí puede ser ejecutable es la **captura**: `evidence.py run` deja la firma
del output para que nadie transcriba a mano un resultado que no ocurrió.
