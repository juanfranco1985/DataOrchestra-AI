# Estado actual - DataOrchestra AI v2.0

Fecha de corte: 2026-05-20

## Veredicto

DataOrchestra AI v2.0 esta operativo como primer piloto comercial controlado.

No debe presentarse aun como SaaS, plataforma autoservicio ni producto final escalable. El estado correcto es: servicio inicial supervisado para diagnostico de datos de PyMEs con datos anonimizados, revision humana y entrega controlada.

## Estructura actual

```text
v2_0_primer_piloto_real_controlado/
  src/dataorchestra/
    analytics/              Motor deterministico de diagnostico
    approval.py             Aprobacion humana auditable
    audit.py                Eventos JSONL de auditoria
    cli.py                  Comandos operativos del piloto controlado
    confidence.py           Score de confianza operativa por hallazgo
    contracts.py            Contratos versionados de datos CSV
    data_quality.py         Score de calidad de datos
    incidents.py            Registro y resolucion auditable de incidentes
    integrity.py            Fingerprints SHA-256 de archivos raw
    periods.py              Comparacion de ventas y margen por periodos
    readiness.py            Checklist tecnico-operativo automatizado
    privacy.py              Escaneo de columnas y valores sensibles
    reporting.py            Render de borrador ejecutivo Markdown
    status.py               Estado operativo y proxima accion
    thresholds.py           Umbrales analiticos por rubro
    clients.py              Creacion de espacios operativos por cliente
    runs.py                 Historial de artefactos por run_id
    states.py               Estados permitidos del diagnostico
    validation.py           Validacion de esquemas CSV
  tests/                    Tests automatizados
  contracts/                Contratos JSON versionados para archivos CSV
  clients/cliente_001/      Estructura del primer piloto
    raw/                    Entrada original, no editable
    processed/              Reservado para transformaciones futuras
    diagnostics/            Reportes tecnicos y auditoria de corrida
    reports/                Borradores y entregables aprobados
    logs/                   Auditoria JSONL
    client.yaml             Estado y metadata del cliente piloto
  templates/                CSV esperados para ventas, productos y stock
  checklists/               Controles operativos obligatorios
  docs/                     Runbook, privacidad, readiness y estado
  dataorchestra-web/        Landing institucional profesional
```

## Flujo operativo implementado

1. Admision del cliente y confirmacion de alcance.
2. Recepcion de CSV anonimizados en `clients/cliente_001/raw/`.
3. Crear carpeta del cliente si corresponde:

```powershell
dataorchestra init-client --client-id cliente_002 --display-name "Cliente piloto 002"
```

4. Preflight:

```powershell
dataorchestra preflight --client-dir clients/cliente_001
```

5. Analisis:

```powershell
dataorchestra analyze --client-dir clients/cliente_001
```

6. Revision humana del borrador.
7. Aprobacion controlada:

```powershell
dataorchestra approve --client-dir clients/cliente_001 --reviewer "Nombre responsable" --notes "Revision humana completada" --confirm-human-review
```

8. Entrega operativa solo del informe aprobado.

## Capacidades ya logradas

- Validacion de archivos obligatorios: `ventas.csv`, `productos.csv`, `stock.csv`.
- Contrato de datos versionado `1.0` para archivos CSV de entrada.
- Validacion de columnas requeridas, fechas ISO y valores numericos no negativos.
- Validacion avanzada de consistencia comercial entre ventas, productos y stock.
- Deteccion bloqueante de datos sensibles por nombres de columnas y patrones de valores.
- Fingerprints SHA-256 de archivos `raw/`.
- Bloqueo del analisis si los CSV cambian despues del preflight aprobado.
- Motor analitico basico para ventas, costos, margen, ticket promedio, stock, concentracion, top productos, ventas por categoria y ventas por mes.
- Comparacion por periodos: ultimo mes observado vs mes anterior y ultimos 30 dias vs 30 dias previos.
- Alertas de bajo margen, stock bajo, exceso de stock y concentracion de facturacion.
- Nivel de confianza por alerta, con score, motivos y limitaciones.
- Score de calidad de datos con observaciones trazables.
- Umbrales analiticos por rubro y overrides por cliente.
- Recomendaciones asociadas a alertas/evidencia.
- Borrador tecnico JSON y borrador ejecutivo Markdown.
- Borrador ejecutivo HTML preparado para imprimir o guardar como PDF.
- Estado `pending_human_review` por defecto.
- Aprobacion humana auditable con revisor, notas y confirmacion explicita.
- Artefactos aprobados separados de los borradores.
- Informe aprobado HTML para entrega ejecutiva.
- Auditoria de preflight, analisis y aprobacion.
- Creacion de carpetas de cliente desde CLI con estructura operativa completa.
- Historial de corridas por `run_id` en `clients/<cliente>/runs/<run_id>/`.
- `.gitignore` preparado para evitar versionar datos reales, logs y entregables generados.
- Workflow CI preparado para GitHub Actions.
- Paquete comercial y aceptacion de piloto documentados.
- Caso demo ficticio reproducible.
- Web institucional integrada en el repositorio.
- Deploy estatico de la web preparado para GitHub Pages.
- Formulario de contacto controlado por email, sin backend ni carga de archivos.
- FAQ publica e interna para preguntas comerciales, privacidad y limites del piloto.
- Base publica de terminos y privacidad para la web institucional.
- Repositorio remoto GitHub integrado: `juanfranco1985/DataOrchestra-AI`.
- Panel interno local para operar pilotos controlados.
- Runtime externo para datos reales.
- Cierre auditable de pilotos.
- Tests automatizados de privacidad, validacion, integridad, analisis, reporte y aprobacion.
- Readiness tecnico automatizado para bloquear o advertir antes de avanzar.
- Procedimiento documentado de incidentes operativos.
- Registro y resolucion auditable de incidentes operativos desde CLI.
- Bloqueo de readiness si existen incidentes abiertos de severidad `alta` o `media`.

## Artefactos generados

Preflight:

- `diagnostics/preflight/preflight_report.json`
- `logs/audit.jsonl`
- `validation.contract_version`
- `data_contract.version`

Analisis:

- `diagnostics/analysis/metrics_summary.json`
- `diagnostics/analysis/alerts.json`
- `diagnostics/analysis/recommendations.json`
- `diagnostics/analysis/data_quality.json`
- `diagnostics/analysis/period_comparison.json`
- `diagnostics/analysis/threshold_config.json`
- `diagnostics/analysis/analysis_summary.json`
- `reports/diagnostico_borrador.json`
- `reports/diagnostico_borrador.md`
- `reports/diagnostico_borrador.html`

Aprobacion:

- `diagnostics/review/approval_record.json`
- `reports/diagnostico_aprobado.json`
- `reports/diagnostico_aprobado.md`
- `reports/diagnostico_aprobado.html`

Historial por corrida:

- `runs/<run_id>/preflight/preflight_report.json`
- `runs/<run_id>/analysis/*`
- `runs/<run_id>/approval/*`

Incidentes:

- `diagnostics/incidents/incident_<id>.json`
- `diagnostics/incidents/incidents_index.json`
- eventos `incident_registered` e `incident_resolved` en `logs/audit.jsonl`

Confianza por hallazgo:

- incluida dentro de `diagnostics/analysis/alerts.json`
- incluida dentro de `reports/diagnostico_borrador.json`
- visible en `reports/diagnostico_borrador.md`
- visible en `reports/diagnostico_borrador.html`

Calidad de datos:

- `diagnostics/data_quality/data_quality_report.json`
- `runs/<run_id>/data_quality/data_quality_report.json`
- evento `data_quality` en `logs/audit.jsonl`

## Validaciones tecnicas ejecutadas

Ultima verificacion realizada:

```text
python -m pytest -q            -> 64 passed
python -m compileall src tests -> OK
CLI disponible                -> init-client, prepare-runtime, status, readiness, data-contracts, thresholds, data-quality, preflight, analyze, full-run, approve, export-pdf, incident, resolve-incident, close-pilot
Readiness tecnico             -> checks de workspace, raw, preflight, docs, revision, incidentes y runtime
Validacion avanzada           -> fechas fuera de rango, catalogo, margen, duplicados, stock, categorias y nombres similares
Comparacion por periodos      -> ultimo mes observado y ventana movil de 30 dias
Confianza por hallazgo        -> score, nivel, motivos y limitaciones por alerta
Web Next.js                   -> npm run build OK, export estatico preparado
Web GitHub Pages              -> build OK con basePath /DataOrchestra-AI
Web FAQ comercial             -> ruta /faq incluida en export estatico
Web terminos y privacidad     -> ruta /terminos-privacidad incluida en export estatico
Export PDF demo               -> OK con Microsoft Edge headless
Panel interno local           -> compileall OK, helpers testeados
```

## Limites actuales

- No hay validacion con cliente real todavia.
- GitHub Pages requiere activar `Settings -> Pages -> GitHub Actions` en el repositorio.
- El formulario de contacto requiere configurar `DATAORCHESTRA_CONTACT_EMAIL` para salir con destinatario.
- La pagina de terminos y privacidad es una base institucional; requiere revision legal antes de uso contractual definitivo.
- Hay aceptacion operativa de piloto, pero no contrato legal formal revisado.
- El panel interno es local y operativo; todavia no es multiusuario ni tiene autenticacion propia.
- El motor analitico es deterministico y basico; no reemplaza analisis experto ni garantiza resultados.
- La exportacion PDF automatica esta integrada mediante navegador Chromium/Edge/Chrome local.
- No hay mecanismo de entrega o marcado `delivered`; la entrega sigue siendo accion manual externa.
- No hay persistencia historica multi-periodo ni comparacion mensual en v2.0.

## Validaciones pendientes antes de llamarlo producto final

1. Ejecutar un piloto real con cliente de bajo riesgo.
2. Confirmar que el cliente puede entregar datos anonimizados y procesables.
3. Medir tiempo operativo real de admision, limpieza, analisis, revision y devolucion.
4. Validar si el cliente entiende al menos tres hallazgos accionables.
5. Registrar objeciones, dudas, utilidad percibida y disposicion a pagar o continuar.
6. Ajustar precio y alcance segun esfuerzo real.
7. Crear contrato o aceptacion escrita de alcance, privacidad, limitaciones y no garantia de resultados.
8. Repetir con un segundo cliente o rubro para probar repetibilidad.
9. Formalizar Git, CI, releases y versionado.
10. Definir si conviene panel interno, PDF comercial o seguimiento mensual.

## Siguiente paso recomendado

No sumar mas complejidad tecnica antes del primer piloto real.

El siguiente paso operativo es activar GitHub Pages para publicar la web institucional y ejecutar el flujo completo con un cliente real de bajo riesgo:

```text
admision -> datos anonimizados -> preflight -> analyze -> revision humana -> approve -> entrega controlada -> feedback
```

Despues de esa prueba, decidir una de estas opciones:

- Continuar con el mismo cliente.
- Ajustar oferta/precio y repetir.
- Cambiar cliente objetivo.
- Pausar desarrollo de producto y revisar propuesta de valor.

## Calificacion de madurez

- Piloto comercial controlado: 8/10.
- Servicio inicial supervisado: 7/10.
- Producto final escalable: 5/10.
- SaaS/autoservicio: no corresponde aun.
