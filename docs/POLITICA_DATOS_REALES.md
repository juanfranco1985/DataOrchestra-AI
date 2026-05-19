# Politica operativa de datos reales

Esta politica aplica a pilotos reales de DataOrchestra AI.

## Principios

- Procesar solo datos necesarios para el diagnostico comercial.
- Trabajar con datos anonimizados desde origen.
- Bloquear el proceso ante datos sensibles innecesarios.
- Mantener trazabilidad de archivos y acciones.
- Entregar solo informes aprobados.
- Revisar retencion o borrado al cerrar cada piloto.

## Datos aceptados

- Ventas anonimizadas.
- Productos.
- Categorias.
- Precios.
- Costos.
- Stock.
- Fechas de operaciones.
- Cantidades.

## Datos no aceptados

- Nombres de personas.
- Emails.
- Telefonos.
- Direcciones.
- DNI, CUIT/CUIL personales u otros identificadores personales.
- Datos bancarios.
- Datos medicos.
- Datos legales sensibles.
- Datos laborales personales.
- Datos fiscales personales.

## Recepcion

Los archivos deben recibirse con estos nombres:

- `ventas.csv`
- `productos.csv`
- `stock.csv`

No deben recibirse por canales informales si el cliente incluye informacion sensible. Si hay duda, detener el proceso.

## Retencion

La retencion debe definirse por piloto. Recomendacion inicial:

- Datos raw: conservar solo mientras dure el piloto y la revision.
- Informes aprobados: conservar segun acuerdo comercial.
- Logs y fingerprints: conservar para trazabilidad mientras exista relacion operativa.
- Datos no viables o sensibles: eliminar cuanto antes luego de registrar el incidente operativo.

## Borrado

El borrado debe ser manual, deliberado y registrado. Antes de borrar:

- confirmar que no hay entrega pendiente;
- confirmar que se guardo el informe aprobado si corresponde;
- registrar cierre del piloto;
- registrar responsable, fecha y motivo;
- eliminar archivos raw y derivados segun politica acordada.

## Cierre

Todo piloto debe cerrarse con:

```powershell
python -m dataorchestra.cli close-pilot --client-dir <cliente> --reviewer "Responsable" --notes "Cierre registrado" --outcome completed --confirm-close
```

Resultados permitidos:

- `completed`
- `not_viable`
- `needs_follow_up`
- `converted_to_service`

El cierre no borra datos automaticamente. Deja constancia y obliga a revisar retencion/borrado.
