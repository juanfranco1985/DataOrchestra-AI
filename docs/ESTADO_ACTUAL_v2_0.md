# Estado actual - DataOrchestra AI v2.0

Fecha de corte: 2026-05-14

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
    cli.py                  Comandos preflight, analyze y approve
    integrity.py            Fingerprints SHA-256 de archivos raw
    privacy.py              Escaneo de columnas y valores sensibles
    reporting.py            Render de borrador ejecutivo Markdown
    clients.py              Creacion de espacios operativos por cliente
    runs.py                 Historial de artefactos por run_id
    states.py               Estados permitidos del diagnostico
    validation.py           Validacion de esquemas CSV
  tests/                    Tests automatizados
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
- Validacion de columnas requeridas, fechas ISO y valores numericos no negativos.
- Deteccion bloqueante de datos sensibles por nombres de columnas y patrones de valores.
- Fingerprints SHA-256 de archivos `raw/`.
- Bloqueo del analisis si los CSV cambian despues del preflight aprobado.
- Motor analitico basico para ventas, costos, margen, ticket promedio, stock, concentracion, top productos, ventas por categoria y ventas por mes.
- Alertas de bajo margen, stock bajo, exceso de stock y concentracion de facturacion.
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
- Tests automatizados de privacidad, validacion, integridad, analisis, reporte y aprobacion.

## Artefactos generados

Preflight:

- `diagnostics/preflight/preflight_report.json`
- `logs/audit.jsonl`

Analisis:

- `diagnostics/analysis/metrics_summary.json`
- `diagnostics/analysis/alerts.json`
- `diagnostics/analysis/recommendations.json`
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

## Validaciones tecnicas ejecutadas

Ultima verificacion realizada:

```text
python -m pytest -q            -> 21 passed
python -m compileall src tests -> OK
CLI disponible                -> init-client, preflight, analyze, approve
```

## Limites actuales

- No hay validacion con cliente real todavia.
- No hay repositorio Git formal inicializado/publicado; `.gitignore` y workflow CI ya estan preparados.
- No hay contrato/aceptacion comercial versionada dentro de esta unidad.
- No hay panel interno; la operacion sigue siendo por CLI.
- El motor analitico es deterministico y basico; no reemplaza analisis experto ni garantiza resultados.
- La exportacion PDF automatica no esta integrada; existe HTML aprobado imprimible/exportable a PDF desde navegador.
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

El siguiente paso es ejecutar el flujo completo con un cliente real de bajo riesgo:

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
