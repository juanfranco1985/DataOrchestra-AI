# Modelos y tipos de analisis disponibles

En esta version, DataOrchestra AI usa modelos deterministas y reglas de negocio. No es un modelo predictivo ni una IA generativa que decide sola.

## 1. Modelo de validacion de privacidad

Objetivo:

- detectar nombres de columnas sensibles;
- detectar patrones sensibles en valores;
- bloquear si hay riesgo.

Sirve para:

- evitar datos personales;
- detener el flujo antes del analisis;
- pedir version anonimizada.

## 2. Modelo de contrato de datos

Objetivo:

- validar que existan `ventas.csv`, `productos.csv` y `stock.csv`;
- validar columnas obligatorias;
- validar tipos basicos;
- impedir interpretar archivos incompatibles.

Comando:

```powershell
python -m dataorchestra.cli data-contracts
```

## 3. Modelo de integridad raw

Objetivo:

- generar fingerprints SHA-256 de los archivos originales;
- bloquear analisis si los CSV cambian despues del preflight.

Sirve para trazabilidad y auditoria.

## 4. Modelo de calidad de datos

Objetivo:

- calcular un score de 0 a 100;
- marcar limitaciones antes de interpretar.

Evalua:

- cantidad minima de filas;
- duracion del periodo;
- cobertura entre ventas, catalogo y stock;
- costos/precios en cero;
- duplicados;
- diferencias de costos;
- rotacion disponible.

Comando:

```powershell
python -m dataorchestra.cli data-quality --client-dir "C:\Documentos\DataOrchestra_Runtime\clients\cliente_001"
```

Interpretacion:

- `85-100`: alta.
- `70-84`: media.
- `50-69`: baja.
- `0-49`: critica.

## 5. Modelo de umbrales por rubro

Objetivo:

- adaptar alertas a perfiles de negocio.

Perfiles disponibles:

- `retail`
- `gastronomia`
- `distribucion`
- `ecommerce`
- `servicios`
- `default`

Umbrales disponibles:

- `low_margin`
- `critical_margin`
- `excess_stock_ratio`
- `revenue_concentration_top_n`
- `revenue_concentration_warning`

Comando:

```powershell
python -m dataorchestra.cli thresholds --client-dir "C:\Documentos\DataOrchestra_Runtime\clients\cliente_001"
```

## 6. Modelo de analisis comercial base

Objetivo:

- calcular metricas comerciales principales.

Analiza:

- ventas totales;
- costos estimados;
- margen bruto;
- margen porcentual;
- ventas por producto;
- ventas por categoria;
- ticket o venta promedio;
- productos top;
- productos de bajo margen;
- stock bajo;
- exceso de stock;
- concentracion de facturacion.

Comando:

```powershell
python -m dataorchestra.cli analyze --client-dir "C:\Documentos\DataOrchestra_Runtime\clients\cliente_001"
```

## 7. Modelo de comparacion por periodos

Objetivo:

- comparar desempeño reciente contra periodo anterior.

Compara:

- ultimo mes observado vs mes anterior observado;
- ultimos 30 dias vs 30 dias previos.

Metricas:

- ventas;
- margen bruto;
- margen porcentual;
- unidades;
- cantidad de tickets;
- ticket promedio.

## 8. Modelo de alertas

Objetivo:

- convertir metricas en señales priorizadas.

Alertas actuales:

- bajo margen;
- stock bajo;
- exceso de stock;
- concentracion de facturacion.

## 9. Modelo de confianza por hallazgo

Objetivo:

- asignar confianza `alta`, `media` o `baja` a cada alerta.

Considera:

- calidad general de datos;
- evidencia disponible;
- cobertura de catalogo;
- datos de stock;
- cantidad de operaciones;
- limitaciones de muestra.

No mide impacto futuro ni garantiza resultados.

## 10. Modelo de recomendaciones

Objetivo:

- generar recomendaciones asociadas a alertas;
- permitir revision humana;
- registrar estado.

Estados:

- `pending_review`
- `accepted`
- `rejected`
- `needs_client_context`
- `converted_to_action`
- `completed`
- `superseded`

## Que modelo elegir segun caso

### Comercio minorista, almacen, autoservicio, ferreteria

Usar perfil:

```text
retail
```

Enfasis:

- margen;
- stock bajo;
- exceso de stock;
- top productos;
- concentracion.

### Gastronomia, bar, rotiseria

Usar perfil:

```text
gastronomia
```

Enfasis:

- margen;
- productos/categorias fuertes;
- cambios por periodo;
- insumos con costo alto.

### Distribuidora

Usar perfil:

```text
distribucion
```

Enfasis:

- volumen;
- stock;
- concentracion;
- margen bajo por producto.

### Ecommerce

Usar perfil:

```text
ecommerce
```

Enfasis:

- productos top;
- concentracion;
- variacion entre periodos;
- ticket promedio.

### Servicios

Usar perfil:

```text
servicios
```

Enfasis:

- facturacion por categoria;
- margen si hay costos;
- concentracion;
- comparacion temporal.

## Limites actuales

- No hay prediccion avanzada.
- No hay forecast de demanda.
- No hay estacionalidad corregida.
- No hay integracion directa con sistemas del cliente.
- No hay analisis financiero/contable legal.
- No hay segmentacion de clientes si no se provee dato anonimo adecuado.
