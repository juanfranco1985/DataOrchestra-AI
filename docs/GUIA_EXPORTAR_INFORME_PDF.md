# Guia para exportar informe a PDF

DataOrchestra AI genera informes HTML aprobados y puede exportarlos automaticamente a PDF usando Microsoft Edge, Google Chrome u otro navegador basado en Chromium.

## Archivo de entrada

Despues de aprobar un diagnostico, abrir:

```text
clients/<cliente>/reports/diagnostico_aprobado.html
```

## Exportar automaticamente desde CLI

Desde la raiz del proyecto:

```powershell
$env:PYTHONPATH="src"
python -m dataorchestra.cli export-pdf --client-dir clients/cliente_001
```

Salida esperada:

```text
clients/cliente_001/reports/diagnostico_aprobado.pdf
```

El comando usa el informe aprobado. Si no existe `diagnostico_aprobado.html` o la metadata no confirma `approved_for_delivery`, la exportacion se bloquea.

Para exportar a una ruta especifica:

```powershell
python -m dataorchestra.cli export-pdf --client-dir clients/cliente_001 --output reports_finales/diagnostico_cliente_001.pdf
```

Si el navegador no se detecta automaticamente:

```powershell
python -m dataorchestra.cli export-pdf --client-dir clients/cliente_001 --browser-path "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
```

Tambien se puede definir:

```powershell
$env:DATAORCHESTRA_BROWSER_PATH="C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
```

## Exportar manualmente desde navegador

1. Abrir el archivo HTML en el navegador.
2. Presionar `Ctrl + P`.
3. Elegir destino `Guardar como PDF`.
4. Activar fondos o graficos de fondo si el navegador lo permite.
5. Guardar el archivo con nombre:

```text
DataOrchestra_AI_Diagnostico_<cliente>_<fecha>.pdf
```

## Reglas de entrega

- Entregar solo informes aprobados.
- No entregar `diagnostico_borrador.*`.
- No entregar archivos `raw/`.
- No entregar logs internos salvo acuerdo especifico.
- No entregar diagnosticos con dudas de privacidad o calidad de datos.

## Nota

La exportacion automatica evita librerias externas de PDF y usa el motor de impresion del navegador instalado. Si el entorno no tiene navegador compatible, usar la exportacion manual desde navegador.
