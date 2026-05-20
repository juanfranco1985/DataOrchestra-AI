# Runtime seguro para datos reales

El repositorio contiene codigo, documentacion, plantillas y datos demo ficticios. Los datos reales de clientes no deben guardarse dentro del repositorio.

## Crear runtime local

Desde la raiz del proyecto:

```powershell
$env:PYTHONPATH="src"
python -m dataorchestra.cli prepare-runtime --runtime-dir "C:\Documentos\DataOrchestra_Runtime"
```

El comando crea:

```text
C:\Documentos\DataOrchestra_Runtime\
  clients\
  intake\
  exports\
  archive\
  logs\
  policies\
  deletion_requests\
  README_RUNTIME.md
  runtime_policy.yaml
  .gitignore
```

## Crear cliente dentro del runtime

```powershell
python -m dataorchestra.cli init-client --clients-root "C:\Documentos\DataOrchestra_Runtime\clients" --client-id cliente_002 --display-name "Cliente piloto 002"
```

Luego usar:

```powershell
python -m dataorchestra.cli status --client-dir "C:\Documentos\DataOrchestra_Runtime\clients\cliente_002"
python -m dataorchestra.cli readiness --client-dir "C:\Documentos\DataOrchestra_Runtime\clients\cliente_002" --repo-root .
python -m dataorchestra.cli full-run --client-dir "C:\Documentos\DataOrchestra_Runtime\clients\cliente_002"
```

## Variables de entorno recomendadas

```powershell
$env:DATAORCHESTRA_RUNTIME_DIR="C:\Documentos\DataOrchestra_Runtime"
$env:DATAORCHESTRA_CLIENTS_ROOT="C:\Documentos\DataOrchestra_Runtime\clients"
```

El panel interno puede usar `DATAORCHESTRA_CLIENTS_ROOT` para operar sobre el runtime externo.

## Reglas

- No guardar datos reales dentro del repo Git.
- No subir runtime a GitHub.
- Usar una carpeta por cliente.
- No mezclar archivos de clientes.
- No editar `raw/` despues del preflight sin repetir preflight.
- Cerrar cada piloto con `close-pilot`.
- Revisar retencion o borrado al cerrar.
