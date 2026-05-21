# Comparacion por periodos

## Objetivo

Agregar contexto temporal al diagnostico comercial.

Hasta ahora el analisis describia el estado agregado de ventas, margen, stock y concentracion. Con esta mejora, DataOrchestra AI tambien compara periodos para detectar cambios relevantes antes de la revision humana.

## Donde se ejecuta

La comparacion corre dentro de:

```powershell
python -m dataorchestra.cli analyze --client-dir clients/cliente_001
```

Tambien queda incluida cuando se ejecuta:

```powershell
python -m dataorchestra.cli full-run --client-dir clients/cliente_001
```

## Artefactos generados

El analisis genera:

- `diagnostics/analysis/period_comparison.json`
- copia historica en `runs/<run_id>/analysis/period_comparison.json`
- resumen dentro de `reports/diagnostico_borrador.md`
- seccion visual dentro de `reports/diagnostico_borrador.html`

## Comparaciones implementadas

### Ultimo mes observado vs mes anterior observado

Compara el ultimo mes con ventas contra el mes observado inmediatamente anterior.

Ejemplo:

```text
2026-02 vs 2026-01
```

Metricas comparadas:

- ventas totales;
- margen bruto;
- margen porcentual;
- unidades vendidas;
- cantidad de tickets;
- ticket promedio.

### Ultimos 30 dias vs 30 dias previos

Usa la fecha maxima de `ventas.csv` como cierre de la ventana reciente.

Ejemplo:

```text
ventana actual: 2026-02-01 a 2026-03-02
ventana previa: 2026-01-02 a 2026-01-31
```

Si no hay datos en ambas ventanas, la comparacion queda marcada como `insufficient_data`.

## Resultado tecnico

El archivo `period_comparison.json` contiene:

- `available`: indica si hay al menos una comparacion disponible;
- `comparison_count`: cantidad de comparaciones calculadas;
- `comparisons`: detalle de cada comparacion;
- `highlights`: senales relevantes detectadas.

Cada metrica incluye:

- valor actual;
- valor previo;
- cambio absoluto;
- cambio porcentual;
- direccion: `up`, `down` o `flat`.

## Senales destacadas

El sistema crea highlights cuando detecta:

- cambio de ventas igual o superior al 10%;
- cambio absoluto de margen porcentual igual o superior a 5 puntos.

Estas senales no reemplazan la revision humana. Sirven para orientar la lectura del informe.

## Interpretacion comercial

La comparacion ayuda a responder:

- si las ventas crecieron o cayeron;
- si el margen mejoro o empeoro;
- si el ticket promedio cambio;
- si el volumen acompana la facturacion;
- si el diagnostico refleja un problema puntual o una tendencia reciente.

## Limites actuales

- No corrige estacionalidad.
- No compara trimestres todavia.
- No separa efectos de precio, volumen y mix de productos.
- Si el dataset tiene pocas fechas, puede no haber base comparable.
- La comparacion usa datos provistos por el cliente y debe interpretarse junto al score de calidad.

## Proximos ajustes posibles

- Comparacion trimestre actual vs trimestre anterior.
- Evolucion por categoria.
- Productos que mas suben y mas caen.
- Separacion de crecimiento por precio vs unidades.
- Configuracion de ventanas por cliente.
