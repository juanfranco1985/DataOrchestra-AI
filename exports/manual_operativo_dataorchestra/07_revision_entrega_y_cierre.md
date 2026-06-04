# Revision, entrega y cierre

## Archivos generados por el analisis

Despues de `analyze`, revisar:

```text
diagnostics/analysis/metrics_summary.json
diagnostics/analysis/alerts.json
diagnostics/analysis/recommendations.json
diagnostics/analysis/data_quality.json
diagnostics/analysis/period_comparison.json
reports/diagnostico_borrador.md
reports/diagnostico_borrador.html
```

## Regla de revision humana

No entregar:

- `diagnostico_borrador.md`;
- `diagnostico_borrador.html`;
- archivos JSON tecnicos;
- archivos `raw/`;
- logs internos.

Primero revisar:

- si los hallazgos tienen sentido;
- si la calidad de datos es suficiente;
- si hay alertas con baja confianza;
- si las recomendaciones son prudentes;
- si falta contexto del cliente;
- si hay informacion sensible.

## Aprobar entrega

```powershell
python -m dataorchestra.cli approve `
  --client-dir "C:\Documentos\DataOrchestra_Runtime\clients\cliente_001" `
  --reviewer "Juan" `
  --notes "Revision humana completada" `
  --confirm-human-review
```

Esto genera:

```text
diagnostics/review/approval_record.json
reports/diagnostico_aprobado.json
reports/diagnostico_aprobado.md
reports/diagnostico_aprobado.html
```

## Exportar PDF

```powershell
python -m dataorchestra.cli export-pdf --client-dir "C:\Documentos\DataOrchestra_Runtime\clients\cliente_001"
```

## Registrar entrega

```powershell
python -m dataorchestra.cli mark-delivered `
  --client-dir "C:\Documentos\DataOrchestra_Runtime\clients\cliente_001" `
  --recipient "Responsable cliente" `
  --method email `
  --notes "Informe aprobado enviado" `
  --confirm-delivery
```

## Como hacer la devolucion

No mandar solo el archivo. Explicar:

1. Que datos se usaron.
2. Que limitaciones hay.
3. Tres hallazgos principales.
4. Riesgos o advertencias.
5. Recomendaciones concretas.
6. Proximo paso.

## Preguntas de feedback

- El informe se entiende?
- Que hallazgo te sorprendio?
- Que decision podrias tomar con esto?
- Que dato faltaria para mejorar el analisis?
- Te serviria repetirlo mensualmente?
- El precio te parece razonable para el valor recibido?

## Cierre de piloto

```powershell
python -m dataorchestra.cli close-pilot `
  --client-dir "C:\Documentos\DataOrchestra_Runtime\clients\cliente_001" `
  --reviewer "Juan" `
  --notes "Cierre registrado" `
  --outcome completed `
  --confirm-close
```

## Despues del cierre

Revisar:

- si se conserva el informe aprobado;
- si se borran datos raw;
- si hay continuidad mensual;
- si se documentan aprendizajes;
- si hubo objeciones comerciales;
- si conviene ajustar precio.

Registrar la decision:

```powershell
python -m dataorchestra.cli record-retention `
  --client-dir "C:\Documentos\DataOrchestra_Runtime\clients\cliente_001" `
  --responsible "Juan" `
  --action raw_deleted `
  --notes "Raw eliminado manualmente segun politica acordada" `
  --confirm-retention-review
```
