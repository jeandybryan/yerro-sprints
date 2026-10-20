# Checklist de release

No marques una release como lista mientras exista una decisión pendiente en
`GOVERNANCE.md`.

## Contrato y evidencia

- [ ] Las seis skills y sus límites siguen presentes.
- [ ] `validate_skill_evals.py` pasa.
- [ ] `test_next_step.py`, `test_snapshot.py`, `test_expres.py` y `test_skill_evals.py` pasan.
- [ ] `doctor.py` acepta la fixture sana y rechaza las fixtures negativas.
- [ ] Las fixtures negativas siguen fallando por su gate específico.
- [ ] La documentación describe los comandos realmente ejecutados.
- [ ] No hay cambios de dominio dentro de `skills/`.
- [ ] No hay un `coincide` reutilizado sobre otro snapshot.

## Revisión

- [ ] El diff tiene una intención única y un tamaño revisable.
- [ ] Cada cambio de comportamiento tiene fixture/caso y, cuando aplica,
      mutation check.
- [ ] Cada CA nuevo tiene `S-NN`; cada tarea tiene `Test-first:` y `Test:`;
      cada auditoría conserva `S → CA → T → test → E`.
- [ ] El riesgo, presupuesto de deltas y desviaciones están explícitos.
- [ ] No quedan preguntas abiertas ni bloqueos sin decisión.

## Publicación

- [ ] Licencia y titulares acordados.
- [ ] Canal de distribución canónico acordado.
- [ ] Política de tags/versionado acordada.
- [ ] Agentes/hosts soportados acordados.
- [ ] Owner y aprobadores de la release acordados.
- [ ] Changelog actualizado después de validar, no antes.
- [ ] El commit/árbol auditado está identificado y el árbol de trabajo está
      limpio.
