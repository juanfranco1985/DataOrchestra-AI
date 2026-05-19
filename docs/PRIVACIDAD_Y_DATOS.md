# Privacidad y datos

El piloto opera con datos anonimizados. No se necesitan nombres de personas, emails, telefonos, direcciones, DNI, CUIT/CUIL, tarjetas, cuentas bancarias ni datos personales sensibles.

## Regla de bloqueo

Si el preflight detecta columnas o valores sensibles, el estado debe pasar a `privacy_review_required` y no se debe ejecutar analisis.

## Archivos raw

Los archivos en `raw/` son evidencia de entrada. No se editan, no se corrigen y no se sobrescriben. Cualquier limpieza o transformacion se guarda en `processed/`.

## Evidencia

Los reportes de privacidad no deben copiar valores sensibles detectados. Solo deben indicar tipo de hallazgo, columna, archivo y severidad.
