# Caso demo ficticio - Retail Santa Clara

Este caso permite ejecutar el flujo completo sin usar datos reales.

## Ubicacion

```text
demos/retail_santa_clara/
```

## Archivos incluidos

- `raw/ventas.csv`
- `raw/productos.csv`
- `raw/stock.csv`
- `client.yaml`

## Ejecutar demo

Desde la raiz de `DataOrchestra_AI_v2_1_integrado/`:

```powershell
$env:PYTHONPATH="src"
python -m dataorchestra.cli preflight --client-dir demos/retail_santa_clara
python -m dataorchestra.cli analyze --client-dir demos/retail_santa_clara
python -m dataorchestra.cli approve --client-dir demos/retail_santa_clara --reviewer "Demo interna" --notes "Caso ficticio revisado para presentacion" --confirm-human-review
```

## Salidas esperadas

El flujo genera:

- `reports/diagnostico_borrador.md`
- `reports/diagnostico_borrador.html`
- `reports/diagnostico_aprobado.md`
- `reports/diagnostico_aprobado.html`
- `diagnostics/`
- `runs/<run_id>/`

## Uso recomendado

Usar este caso para:

- demostrar el flujo sin datos reales;
- mostrar el informe HTML imprimible;
- explicar alertas de margen, stock y concentracion;
- entrenar la operacion interna antes del primer cliente.

No usar este caso como evidencia de resultados reales.

