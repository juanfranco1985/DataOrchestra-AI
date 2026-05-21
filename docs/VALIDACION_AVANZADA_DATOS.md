# Validacion avanzada de datos

## Objetivo

Agregar controles comerciales sobre los CSV ya validados por contrato.

La validacion base confirma estructura, columnas, fechas ISO y numeros no negativos. La validacion avanzada revisa consistencia entre archivos y condiciones comerciales que pueden volver riesgoso interpretar el diagnostico.

## Donde corre

La validacion avanzada corre dentro de:

```powershell
python -m dataorchestra.cli preflight --client-dir clients/cliente_001
```

Los hallazgos quedan en:

- `diagnostics/preflight/preflight_report.json`
- `validation.issues`

## Severidades

- `high`: bloquea el flujo y deja el estado en `data_fix_required`.
- `medium`: no bloquea automaticamente, pero debe revisarse antes de aprobar entrega.

## Reglas implementadas

### Fechas fuera de rango

Codigo:

- `date_out_of_supported_range`

Severidad: `high`

Detecta fechas fuera del rango soportado por el piloto:

- minimo: `2000-01-01`
- maximo: `2035-12-31`

Motivo: fechas demasiado antiguas o futuras pueden distorsionar periodos, tendencias y lectura comercial.

### Productos vendidos fuera del catalogo

Codigo:

- `sold_product_missing_from_catalog`

Severidad: `high`

Detecta productos presentes en `ventas.csv` que no existen en `productos.csv`.

Motivo: impide contrastar categoria, precio y costo de referencia.

### Precio menor al costo

Codigos:

- `unit_price_below_cost`
- `catalog_price_below_cost`

Severidad: `medium`

Detecta productos donde el precio unitario queda por debajo del costo unitario.

Motivo: puede ser una liquidacion o promocion real, pero requiere confirmacion antes de interpretar margen.

### Margenes imposibles

Codigos:

- `impossible_margin_zero_price_with_cost`
- `catalog_impossible_margin_zero_price_with_cost`

Severidad: `high`

Detecta precio cero con costo positivo.

Motivo: el margen no puede interpretarse de forma confiable.

### Ventas duplicadas

Codigo:

- `duplicate_sales_row`

Severidad: `medium`

Detecta filas de venta exactamente repetidas.

Motivo: pueden duplicar facturacion, unidades y margen. Como no hay `transaction_id` en el contrato v1.0, se marca como advertencia y no como bloqueo automatico.

### Stock logicamente riesgoso

Codigos:

- `zero_stock_with_recent_sales`
- `stock_below_minimum`

Severidad: `medium`

Detecta:

- stock actual cero con ventas recientes;
- stock actual menor al stock minimo informado.

Motivo: puede ser una foto valida del negocio, pero debe revisarse antes de entregar recomendaciones de reposicion.

### Categorias inconsistentes

Codigos:

- `category_mismatch_with_catalog`
- `inconsistent_sales_category_for_product`
- `inconsistent_catalog_category_for_product`

Severidad: `medium`

Detecta diferencias de categoria para el mismo producto entre ventas y catalogo, o multiples categorias para el mismo producto.

Motivo: afecta lectura por categoria y priorizacion comercial.

### Productos con nombres casi iguales

Codigo:

- `near_duplicate_product_name`

Severidad: `medium`

Detecta nombres normalizados muy parecidos entre catalogo y stock.

Ejemplos:

- `Producto A`
- `Producto AA`
- `Producto-A`

Motivo: puede indicar duplicacion o problemas de codificacion del catalogo.

## Relacion con score de calidad

La validacion avanzada ocurre antes o durante el `preflight`.

El score de calidad de datos (`data-quality`) evalua la calidad general y puede penalizar algunas condiciones similares, pero no reemplaza el `preflight`.

Resumen operativo:

- validacion avanzada `high`: corregir antes de analizar;
- validacion avanzada `medium`: revisar antes de aprobar entrega;
- score de calidad bajo: revisar o corregir antes de entregar.

## Limites actuales

- El contrato v1.0 no incluye `transaction_id`, por eso la deteccion de ventas duplicadas es conservadora.
- Las advertencias de margen negativo no bloquean automaticamente porque pueden existir promociones o liquidaciones reales.
- La deteccion de nombres parecidos usa heuristica local; debe revisarse manualmente antes de pedir correccion al cliente.

## Proximos ajustes posibles

- Agregar `transaction_id` opcional en contrato v1.1.
- Permitir rango de fechas configurable por cliente.
- Separar reglas bloqueantes y advertencias por rubro.
- Generar un resumen ejecutivo de validacion para enviar al cliente cuando hay correcciones pendientes.
