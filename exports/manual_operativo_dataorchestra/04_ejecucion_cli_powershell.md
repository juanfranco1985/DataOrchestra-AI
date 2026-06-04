# Ejecucion por CLI en PowerShell

Esta es la forma mas estable de operar el sistema.

## 1. Ir al proyecto

```powershell
cd "C:\Documentos\Aplicacion DATA ORCHESTRA\DataOrchestra_AI_v2_1_integrado"
$env:PYTHONPATH="src"
```

## 2. Preparar runtime

```powershell
python -m dataorchestra.cli prepare-runtime --runtime-dir "C:\Documentos\DataOrchestra_Runtime"
```

## 3. Crear cliente

```powershell
python -m dataorchestra.cli init-client `
  --clients-root "C:\Documentos\DataOrchestra_Runtime\clients" `
  --client-id cliente_001 `
  --display-name "Nombre del comercio" `
  --business-type "Retail"
```

## 4. Ver estado

```powershell
python -m dataorchestra.cli status --client-dir "C:\Documentos\DataOrchestra_Runtime\clients\cliente_001"
```

## 5. Ver umbrales activos

```powershell
python -m dataorchestra.cli thresholds --client-dir "C:\Documentos\DataOrchestra_Runtime\clients\cliente_001"
```

## 6. Ver contrato de datos

```powershell
python -m dataorchestra.cli data-contracts
python -m dataorchestra.cli data-contracts --dataset ventas
```

## 7. Ejecutar readiness

```powershell
python -m dataorchestra.cli readiness `
  --client-dir "C:\Documentos\DataOrchestra_Runtime\clients\cliente_001" `
  --repo-root .
```

Si `can_continue` es `false`, resolver antes de avanzar.

## 8. Ejecutar preflight

```powershell
python -m dataorchestra.cli preflight --client-dir "C:\Documentos\DataOrchestra_Runtime\clients\cliente_001"
```

Resultados posibles:

- `ready_for_analysis`: se puede analizar.
- `privacy_review_required`: detener por privacidad.
- `data_fix_required`: pedir correccion de datos.

## 9. Ejecutar calidad de datos

```powershell
python -m dataorchestra.cli data-quality --client-dir "C:\Documentos\DataOrchestra_Runtime\clients\cliente_001"
```

Interpretacion:

- `85-100`: alta.
- `70-84`: media usable.
- `50-69`: baja, revisar.
- `0-49`: critica, no entregar sin correccion.

## 10. Ejecutar analisis

```powershell
python -m dataorchestra.cli analyze --client-dir "C:\Documentos\DataOrchestra_Runtime\clients\cliente_001"
```

Alternativa para correr preflight y analisis juntos:

```powershell
python -m dataorchestra.cli full-run --client-dir "C:\Documentos\DataOrchestra_Runtime\clients\cliente_001"
```

`full-run` no aprueba ni entrega.

## 11. Revisar recomendaciones

```powershell
python -m dataorchestra.cli recommendations --client-dir "C:\Documentos\DataOrchestra_Runtime\clients\cliente_001"
```

Actualizar una recomendacion:

```powershell
python -m dataorchestra.cli update-recommendation `
  --client-dir "C:\Documentos\DataOrchestra_Runtime\clients\cliente_001" `
  --recommendation-id rec_bajo_margen `
  --status accepted `
  --reviewer "Juan" `
  --notes "Validada para devolucion controlada" `
  --confirm-no-sensitive-values
```

## 12. Aprobar informe

Solo despues de revision humana:

```powershell
python -m dataorchestra.cli approve `
  --client-dir "C:\Documentos\DataOrchestra_Runtime\clients\cliente_001" `
  --reviewer "Juan" `
  --notes "Revision humana completada" `
  --confirm-human-review
```

## 13. Exportar PDF

```powershell
python -m dataorchestra.cli export-pdf --client-dir "C:\Documentos\DataOrchestra_Runtime\clients\cliente_001"
```

Requiere Edge, Chrome o Chromium instalado.

## 14. Registrar entrega

```powershell
python -m dataorchestra.cli mark-delivered `
  --client-dir "C:\Documentos\DataOrchestra_Runtime\clients\cliente_001" `
  --recipient "Responsable cliente" `
  --method email `
  --notes "Informe aprobado enviado" `
  --confirm-delivery
```

## 15. Registrar incidente

Ejemplo:

```powershell
python -m dataorchestra.cli incident `
  --client-dir "C:\Documentos\DataOrchestra_Runtime\clients\cliente_001" `
  --type sensitive_data_detected `
  --severity alta `
  --responsible "Juan" `
  --action-taken "Proceso detenido y pedido de version anonimizada" `
  --confirm-no-sensitive-values
```

Resolver incidente:

```powershell
python -m dataorchestra.cli resolve-incident `
  --client-dir "C:\Documentos\DataOrchestra_Runtime\clients\cliente_001" `
  --incident-id incident_20260520T123456000000Z `
  --responsible "Juan" `
  --resolution "Incidente mitigado y verificado" `
  --confirm-no-sensitive-values
```

## 16. Cerrar piloto

```powershell
python -m dataorchestra.cli close-pilot `
  --client-dir "C:\Documentos\DataOrchestra_Runtime\clients\cliente_001" `
  --reviewer "Juan" `
  --notes "Cierre registrado" `
  --outcome completed `
  --confirm-close
```

## 17. Registrar retencion o borrado

```powershell
python -m dataorchestra.cli record-retention `
  --client-dir "C:\Documentos\DataOrchestra_Runtime\clients\cliente_001" `
  --responsible "Juan" `
  --action raw_deleted `
  --notes "Raw eliminado manualmente segun politica acordada" `
  --confirm-retention-review
```

