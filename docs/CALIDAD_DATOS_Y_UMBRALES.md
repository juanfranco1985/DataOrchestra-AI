# Calidad de datos y umbrales por rubro

## Objetivo

Fortalecer el diagnostico comercial con dos controles adicionales:

- un score de calidad de datos de 0 a 100;
- umbrales analiticos ajustables por rubro o por configuracion del cliente.

Esto no convierte el sistema en una plataforma automatica. Sirve para que la revision humana tenga mejor contexto antes de interpretar alertas, margen, stock y concentracion.

## Score de calidad de datos

Comando:

```powershell
python -m dataorchestra.cli data-quality --client-dir clients/cliente_001
```

El comando genera:

- `diagnostics/data_quality/data_quality_report.json`
- copia historica en `runs/<run_id>/data_quality/`
- evento `data_quality` en `logs/audit.jsonl`

El analisis tambien genera:

- `diagnostics/analysis/data_quality.json`

`readiness` advierte si el score no fue calculado y bloquea si el score queda por debajo del objetivo configurado.

## Interpretacion del score

- `85-100`: calidad alta.
- `70-84`: calidad media, usable con observaciones visibles.
- `50-69`: calidad baja, revisar antes de aprobar entrega.
- `0-49`: calidad critica, no usar como base comercial sin correccion.

El objetivo minimo recomendado es `70`.

## Que controla

El score considera:

- cantidad minima de filas de ventas;
- duracion del periodo analizado;
- cobertura entre productos vendidos, catalogo y stock;
- costos o precios en cero;
- filas de ventas duplicadas;
- diferencias relevantes entre costos de venta y catalogo;
- disponibilidad de datos de rotacion en `stock.csv`.

El score no reemplaza `preflight`. Si hay datos sensibles, columnas faltantes, fechas invalidas o valores numericos invalidos, el flujo debe bloquearse antes.

## Umbrales por rubro

Comando:

```powershell
python -m dataorchestra.cli thresholds --client-dir clients/cliente_001
```

El analisis guarda:

- `diagnostics/analysis/threshold_config.json`
- copia historica en `runs/<run_id>/analysis/threshold_config.json`

## Perfiles disponibles

- `retail`
- `gastronomia`
- `distribucion`
- `ecommerce`
- `servicios`
- `default`

Si `client.yaml` tiene `client.business_type`, el sistema intenta inferir el perfil. Por ejemplo:

- `Comercio minorista` -> `retail`
- `Distribuidora` -> `distribucion`
- `Ecommerce` -> `ecommerce`

## Configuracion en client.yaml

Ejemplo:

```yaml
client:
  id: cliente_001
  business_type: Retail

analytics:
  threshold_profile: retail
  thresholds:
    low_margin: 0.18
    critical_margin: 0.10
    excess_stock_ratio: 2.5
    revenue_concentration_top_n: 5
    revenue_concentration_warning: 0.55

data_quality:
  target_score: 70
```

Si `threshold_profile` no esta definido, se usa el rubro del cliente. Si no se reconoce el rubro, se usa `default`.

## Umbrales disponibles

- `low_margin`: margen por debajo del cual un producto se marca como bajo margen.
- `critical_margin`: margen por debajo del cual la alerta de margen pasa a prioridad alta.
- `excess_stock_ratio`: multiplicador de ventas de 30 dias para detectar exceso de stock.
- `revenue_concentration_top_n`: cantidad de productos usados para medir concentracion.
- `revenue_concentration_warning`: ratio de concentracion que dispara alerta.

## Uso recomendado

1. Definir `business_type` al crear el cliente.
2. Ejecutar `thresholds` para verificar perfil aplicado.
3. Cargar CSV anonimizados.
4. Ejecutar `preflight`.
5. Ejecutar `data-quality`.
6. Ejecutar `analyze`.
7. Revisar en el informe las secciones `Calidad de datos` y `Umbrales aplicados`.

## Limites

- Los perfiles son criterios iniciales, no reglas absolutas.
- Los umbrales deben ajustarse con feedback de pilotos reales.
- El score de calidad no garantiza que el diagnostico sea correcto; mejora la trazabilidad de la interpretacion.
- La aprobacion humana sigue siendo obligatoria.
