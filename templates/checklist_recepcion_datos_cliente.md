# Checklist de recepcion de datos del cliente

## Antes de recibir archivos

- [ ] Cliente aceptado como caso de bajo riesgo.
- [ ] Alcance del piloto explicado y aceptado.
- [ ] Aceptacion de piloto controlado completada.
- [ ] Cliente instruido para no enviar datos personales.
- [ ] Plantillas CSV enviadas.

## Al recibir archivos

- [ ] Se recibio `ventas.csv`.
- [ ] Se recibio `productos.csv`.
- [ ] Se recibio `stock.csv`.
- [ ] Los archivos se guardaron en la carpeta `raw/` del cliente correcto.
- [ ] No se mezclaron archivos de clientes distintos.
- [ ] No se editaron archivos dentro de `raw/`.

## Antes del preflight

- [ ] Se creo cliente con `init-client`.
- [ ] `client.yaml` contiene identificador correcto.
- [ ] No hay archivos adicionales innecesarios en `raw/`.
- [ ] El responsable operativo sabe que debe detenerse ante hallazgos de privacidad.

## Despues del preflight

- [ ] Estado `ready_for_analysis` verificado, o se detuvo el proceso.
- [ ] Fingerprints SHA-256 registrados.
- [ ] Reporte de preflight archivado por `run_id`.
- [ ] Si hubo error, se pidio correccion al cliente sin modificar `raw/` manualmente.
