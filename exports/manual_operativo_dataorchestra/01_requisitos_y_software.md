# Requisitos y software

## Software minimo

- Windows con PowerShell.
- Python 3.11 o superior.
- Git, si vas a versionar o publicar cambios.
- Navegador Microsoft Edge, Google Chrome o Chromium para exportar PDF automaticamente.

## Software opcional

- Node.js 20 o superior, solo para trabajar con la web.
- Streamlit, si queres usar el panel visual local.
- VS Code u otro editor para revisar archivos Markdown/JSON/CSV.

## Dependencias del proyecto

El paquete base requiere:

- `pyyaml`

Extras disponibles:

- `pytest` para tests;
- `streamlit` para panel local.

## Donde esta el proyecto

Ruta actual:

```powershell
cd "C:\Documentos\Aplicacion DATA ORCHESTRA\DataOrchestra_AI_v2_1_integrado"
```

## Instalacion recomendada

Desde la raiz del proyecto:

```powershell
python -m pip install -e .
```

Para instalar tambien herramientas de desarrollo:

```powershell
python -m pip install -e .[dev]
```

Para usar panel visual:

```powershell
python -m pip install -e .[panel]
```

Para instalar todo junto:

```powershell
python -m pip install -e .[dev,panel]
```

## Uso sin instalar

Si no queres instalar el paquete, podes ejecutar con:

```powershell
$env:PYTHONPATH="src"
python -m dataorchestra.cli --help
```

## Verificacion rapida

```powershell
$env:PYTHONPATH="src"
python -m dataorchestra.cli --help
python -m pytest -q
```

El comando de ayuda debe mostrar comandos como:

- `init-client`
- `prepare-runtime`
- `status`
- `readiness`
- `preflight`
- `analyze`
- `full-run`
- `approve`
- `export-pdf`
- `mark-delivered`
- `close-pilot`
- `record-retention`

