# Solucion de problemas

## El comando no reconoce `dataorchestra`

Usar modo sin instalar:

```powershell
$env:PYTHONPATH="src"
python -m dataorchestra.cli --help
```

O instalar:

```powershell
python -m pip install -e .
```

## Falta Python

Instalar Python 3.11 o superior. Verificar:

```powershell
python --version
```

## Faltan dependencias

Instalar:

```powershell
python -m pip install -e .[dev,panel]
```

## Preflight da `privacy_review_required`

No avanzar. Revisar si los archivos tienen datos sensibles. Pedir version anonimizada.

## Preflight da `data_fix_required`

No avanzar. Puede faltar:

- archivo requerido;
- columna obligatoria;
- fecha valida;
- numero valido;
- producto en catalogo;
- consistencia entre ventas, productos y stock.

## Analyze se bloquea

Posibles causas:

- no existe preflight;
- preflight no quedo en `ready_for_analysis`;
- los archivos `raw/` cambiaron despues del preflight;
- falta algun CSV.

Solucion:

```powershell
python -m dataorchestra.cli status --client-dir "C:\Documentos\DataOrchestra_Runtime\clients\cliente_001"
python -m dataorchestra.cli preflight --client-dir "C:\Documentos\DataOrchestra_Runtime\clients\cliente_001"
```

## PDF no exporta

Verificar que exista informe aprobado:

```text
reports/diagnostico_aprobado.html
```

Verificar que haya Edge, Chrome o Chromium instalado.

Si hace falta, definir navegador:

```powershell
$env:DATAORCHESTRA_BROWSER_PATH="C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
```

## El cliente cambio los archivos despues del preflight

Repetir preflight. No analizar con fingerprints viejos.

## Score de calidad bajo

No entregar como conclusion fuerte. Pedir:

- mas datos;
- mejor catalogo;
- stock actualizado;
- costos/precios completos;
- menos duplicados.

## Hay incidentes abiertos

Readiness puede bloquear si hay incidentes `alta` o `media`.

Resolver:

```powershell
python -m dataorchestra.cli resolve-incident `
  --client-dir "C:\Documentos\DataOrchestra_Runtime\clients\cliente_001" `
  --incident-id incident_ID `
  --responsible "Juan" `
  --resolution "Incidente mitigado" `
  --confirm-no-sensitive-values
```
