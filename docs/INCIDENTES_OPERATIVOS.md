# Incidentes operativos

## Objetivo

Definir como actuar ante errores, datos sensibles, archivos corruptos o fallas de proceso durante un piloto controlado de DataOrchestra AI.

## Principio general

Si hay duda sobre privacidad, integridad o autorizacion de datos, detener el flujo antes de analizar o entregar resultados.

## Tipos de incidente

### Datos sensibles detectados

Ejemplos:

- nombres de personas;
- emails;
- telefonos;
- DNI, CUIT/CUIL personales;
- datos bancarios;
- datos medicos, legales, fiscales o laborales personales.

Accion:

1. Detener el proceso.
2. No ejecutar `analyze`.
3. Registrar el hallazgo operativo sin copiar valores sensibles.
4. Pedir al cliente una version corregida y anonimizada.
5. Ejecutar nuevamente `preflight`.

### Archivos incompletos o invalidos

Ejemplos:

- falta `ventas.csv`, `productos.csv` o `stock.csv`;
- faltan columnas requeridas;
- fechas invalidas;
- valores numericos negativos;
- campos obligatorios vacios.

Accion:

1. Marcar el caso como `data_fix_required`.
2. Comunicar al cliente que los archivos no son procesables todavia.
3. Pedir correccion con referencia a las plantillas.
4. Repetir `preflight`.

### Cambios despues del preflight

Si los fingerprints cambian despues de un preflight aprobado, el analisis debe bloquearse.

Accion:

1. No reutilizar el preflight anterior.
2. Ejecutar un nuevo `preflight`.
3. Confirmar que los nuevos fingerprints queden registrados.

### Error durante analisis o exportacion

Accion:

1. Conservar el mensaje de error tecnico.
2. No entregar borradores incompletos.
3. Revisar logs y artefactos generados.
4. Corregir causa y repetir el paso.
5. Si el error afecta evidencia o conclusiones, regenerar el informe.

### Envio accidental de datos sensibles por formulario o email

Accion:

1. No copiar el dato sensible a tickets, documentos o respuestas.
2. Responder solicitando reenvio anonimizado por el canal acordado.
3. Borrar el mensaje o adjunto segun politica aplicable.
4. Registrar solo tipo de incidente, fecha y decision tomada.

## Severidades

- `alta`: riesgo de privacidad, integridad o entrega incorrecta.
- `media`: bloqueo operativo corregible antes de analizar.
- `baja`: inconsistencia documental o mejora de proceso.

## Registro minimo

Registrar:

- fecha;
- cliente;
- tipo de incidente;
- severidad;
- estado del flujo;
- responsable;
- accion tomada;
- si requiere borrado o retencion especial.

No registrar valores sensibles textuales.

## Comando para registrar un incidente

```powershell
python -m dataorchestra.cli incident --client-dir clients/cliente_001 --type sensitive_data_detected --severity alta --responsible "Nombre responsable" --action-taken "Proceso detenido y pedido de version anonimizada" --requires-data-deletion --confirm-no-sensitive-values
```

Tipos permitidos:

- `sensitive_data_detected`
- `invalid_files`
- `post_preflight_change`
- `analysis_export_error`
- `accidental_sensitive_submission`
- `process_deviation`
- `other`

El comando genera:

- `diagnostics/incidents/incident_<id>.json`
- `diagnostics/incidents/incidents_index.json`
- evento `incident_registered` en `logs/audit.jsonl`

Los incidentes abiertos con severidad `alta` o `media` bloquean `readiness` hasta su resolucion.

## Comando para resolver un incidente

Usar el `incident_id` devuelto por el comando `incident`.

```powershell
python -m dataorchestra.cli resolve-incident --client-dir clients/cliente_001 --incident-id incident_20260520T123456000000Z --responsible "Nombre responsable" --resolution "Incidente mitigado y verificado" --confirm-no-sensitive-values
```

La resolucion no debe incluir emails, telefonos, documentos, cuentas, nombres personales ni valores sensibles. Registrar solo la decision operativa y la accion tomada.

## Comando recomendado antes de continuar

```powershell
python -m dataorchestra.cli readiness --client-dir clients/cliente_001
```

Si `can_continue` es `false`, resolver los bloqueos antes de avanzar.
