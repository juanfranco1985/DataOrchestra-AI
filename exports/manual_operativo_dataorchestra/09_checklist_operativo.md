# Checklist operativo por cliente

## Antes de vender

- [ ] Cliente entiende que es diagnostico, no garantia.
- [ ] Cliente tiene ventas registradas.
- [ ] Cliente tiene productos identificables.
- [ ] Cliente tiene stock o inventario.
- [ ] Cliente acepta trabajar con datos anonimizados.
- [ ] Precio y alcance explicados.

## Antes de recibir datos

- [ ] Aceptacion de piloto completada.
- [ ] Se explico que no debe enviar datos sensibles.
- [ ] Se enviaron plantillas o columnas requeridas.
- [ ] Se definio canal seguro de entrega.

## Preparacion tecnica

- [ ] Runtime externo creado.
- [ ] Cliente creado con `init-client`.
- [ ] Archivos cargados en `raw/`.
- [ ] `status` revisado.
- [ ] `readiness` ejecutado.

## Validacion

- [ ] `preflight` ejecutado.
- [ ] Estado `ready_for_analysis`.
- [ ] No hay datos sensibles.
- [ ] Fingerprints registrados.
- [ ] `data-quality` ejecutado.
- [ ] Score revisado.

## Analisis

- [ ] `thresholds` revisado.
- [ ] `analyze` o `full-run` ejecutado.
- [ ] Borrador Markdown revisado.
- [ ] HTML revisado.
- [ ] Alertas revisadas.
- [ ] Recomendaciones revisadas.
- [ ] Confianza por hallazgo revisada.

## Aprobacion

- [ ] No hay recomendaciones riesgosas sin revisar.
- [ ] Limitaciones explicadas.
- [ ] `approve` ejecutado con revisor y notas.
- [ ] Informe aprobado generado.
- [ ] PDF exportado si corresponde.

## Devolucion

- [ ] Se explicaron datos usados.
- [ ] Se explicaron limitaciones.
- [ ] Se presentaron tres hallazgos principales.
- [ ] Se presentaron recomendaciones.
- [ ] Se pidio feedback.
- [ ] `mark-delivered` ejecutado con destinatario, canal y notas.

## Cierre

- [ ] Feedback registrado.
- [ ] Decision de continuidad registrada.
- [ ] `close-pilot` ejecutado.
- [ ] Retencion o borrado revisado.
- [ ] `record-retention` ejecutado.
