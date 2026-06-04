# Checklist de seguridad antes del primer cliente real

## Preparacion

- [ ] Runtime externo creado con `prepare-runtime`.
- [ ] Cliente creado dentro del runtime externo, no dentro del repo.
- [ ] Aceptacion de piloto controlado completada.
- [ ] Politica de datos reales explicada al cliente.
- [ ] Cliente instruido para entregar datos anonimizados.
- [ ] Canal de recepcion acordado.

## Antes de cargar archivos

- [ ] Confirmar que no hay nombres, emails, telefonos, direcciones ni identificadores personales.
- [ ] Confirmar que los archivos son `ventas.csv`, `productos.csv` y `stock.csv`.
- [ ] Confirmar que los datos corresponden al cliente correcto.
- [ ] Confirmar que no se mezclaron demos con datos reales.

## Durante el proceso

- [ ] Ejecutar `status`.
- [ ] Ejecutar `preflight`.
- [ ] Detener si aparece `privacy_review_required`.
- [ ] Ejecutar `analyze` solo si el preflight esta listo.
- [ ] Revisar borrador manualmente.
- [ ] Aprobar solo con revisor, notas y confirmacion humana.
- [ ] Exportar PDF solo desde informe aprobado.
- [ ] Registrar la entrega con `mark-delivered`.

## Cierre

- [ ] Registrar feedback.
- [ ] Registrar decision de continuidad.
- [ ] Ejecutar `close-pilot`.
- [ ] Revisar retencion o borrado de datos y registrarlo con `record-retention`.
- [ ] No subir runtime, raw ni informes reales a GitHub.
