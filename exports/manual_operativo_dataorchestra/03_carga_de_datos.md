# Carga de datos

## Regla principal

Los datos reales nunca van dentro del repositorio Git. Usar runtime externo.

Ruta recomendada:

```text
C:\Documentos\DataOrchestra_Runtime
```

## Crear runtime externo

Desde la raiz del proyecto:

```powershell
$env:PYTHONPATH="src"
python -m dataorchestra.cli prepare-runtime --runtime-dir "C:\Documentos\DataOrchestra_Runtime"
```

El runtime crea:

```text
C:\Documentos\DataOrchestra_Runtime\
  clients\
  intake\
  exports\
  archive\
  logs\
  policies\
  deletion_requests\
```

## Crear cliente

Ejemplo:

```powershell
$env:PYTHONPATH="src"
python -m dataorchestra.cli init-client `
  --clients-root "C:\Documentos\DataOrchestra_Runtime\clients" `
  --client-id cliente_001 `
  --display-name "Comercio de prueba" `
  --business-type "Retail"
```

Esto crea:

```text
C:\Documentos\DataOrchestra_Runtime\clients\cliente_001\
  raw\
  processed\
  diagnostics\
  reports\
  logs\
  runs\
  client.yaml
```

## Donde poner los CSV

Copiar:

```text
ventas.csv
productos.csv
stock.csv
```

en:

```text
C:\Documentos\DataOrchestra_Runtime\clients\cliente_001\raw\
```

## Que no hacer

- No editar archivos dentro de `raw/` despues del preflight.
- No reemplazar archivos despues de analizar sin repetir preflight.
- No poner datos reales en `clients/` dentro del repo.
- No mezclar clientes.
- No guardar datos sensibles.

## Si hay que corregir datos

Pedir al cliente una nueva version anonimizada y volver a ejecutar:

```powershell
python -m dataorchestra.cli preflight --client-dir "C:\Documentos\DataOrchestra_Runtime\clients\cliente_001"
```
