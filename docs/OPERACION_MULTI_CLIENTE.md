# Operacion multi-cliente

Esta unidad permite operar varios clientes piloto sin reutilizar carpetas ni mezclar datos.

## Crear un cliente nuevo

Desde la raiz de `DataOrchestra_AI_v2_1_integrado/`:

```powershell
$env:PYTHONPATH="src"
python -m dataorchestra.cli init-client --client-id cliente_002 --display-name "Cliente piloto 002" --business-type "Retail" --currency ARS
```

El comando crea:

```text
clients/cliente_002/
  raw/
  processed/
  diagnostics/
  reports/
  logs/
  runs/
  client.yaml
```

## Cargar datos

Colocar solo estos archivos en `clients/<cliente>/raw/`:

- `ventas.csv`
- `productos.csv`
- `stock.csv`

No editar los archivos dentro de `raw/` despues del preflight. Si hay correcciones, reemplazar los CSV y ejecutar preflight nuevamente.

## Ejecutar flujo

```powershell
python -m dataorchestra.cli preflight --client-dir clients/cliente_002
python -m dataorchestra.cli analyze --client-dir clients/cliente_002
python -m dataorchestra.cli approve --client-dir clients/cliente_002 --reviewer "Responsable" --notes "Revision humana completada" --confirm-human-review
```

## Historial de corridas

Los archivos vigentes se mantienen en `diagnostics/` y `reports/`. Ademas, cada corrida guarda una copia historica en:

```text
clients/<cliente>/runs/<run_id>/
  preflight/
  analysis/
  approval/
```

Esto permite reconstruir que se proceso, que se reviso y que se aprobo sin depender solo de los archivos actuales.

