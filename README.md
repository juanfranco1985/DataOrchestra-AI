# DataOrchestra AI v2.0 - Primer Piloto Real Controlado

Esta unidad convierte el proyecto consolidado v1.95 en una base operativa para ejecutar un primer piloto real de bajo riesgo.

No es una plataforma comercial final. Es un entorno controlado para recibir datos anonimizados, validar calidad, bloquear riesgos de privacidad, generar diagnosticos internos y mantener el informe en revision humana hasta aprobacion explicita.

## Principios

- No usar datos personales reales.
- No mezclar demo, piloto y plataforma futura.
- No modificar archivos `raw/`.
- No entregar ningun informe sin revision humana.
- Toda recomendacion debe estar respaldada por una metrica, alerta o evidencia registrada.
- Si hay duda de privacidad, el flujo se bloquea.

## Estructura

```text
v2_0_primer_piloto_real_controlado/
  src/dataorchestra/        Codigo base profesional
  tests/                    Tests automatizados minimos
  clients/cliente_001/      Estructura vacia del primer piloto
  templates/                Plantillas CSV para datos anonimizados
  checklists/               Controles operativos obligatorios
  docs/                     Runbook, privacidad, admision y criterios
  dataorchestra-web/        Landing institucional Next.js
```

## Comandos sugeridos

Desde esta carpeta:

```bash
python -m pip install -e .
dataorchestra init-client --client-id cliente_002 --display-name "Cliente piloto 002"
dataorchestra status --client-dir clients/cliente_001
dataorchestra preflight --client-dir clients/cliente_001
dataorchestra analyze --client-dir clients/cliente_001
dataorchestra full-run --client-dir clients/cliente_001
dataorchestra approve --client-dir clients/cliente_001 --reviewer "Nombre responsable" --notes "Revision humana completada" --confirm-human-review
dataorchestra export-pdf --client-dir clients/cliente_001
```

Para ejecutar sin instalar el paquete:

```bash
python -m compileall src tests
set PYTHONPATH=src
python -m pytest -q
python -m dataorchestra.cli init-client --client-id cliente_002 --display-name "Cliente piloto 002"
python -m dataorchestra.cli status --client-dir clients/cliente_001
python -m dataorchestra.cli preflight --client-dir clients/cliente_001
python -m dataorchestra.cli analyze --client-dir clients/cliente_001
python -m dataorchestra.cli full-run --client-dir clients/cliente_001
python -m dataorchestra.cli approve --client-dir clients/cliente_001 --reviewer "Nombre responsable" --notes "Revision humana completada" --confirm-human-review
python -m dataorchestra.cli export-pdf --client-dir clients/cliente_001
```

En PowerShell:

```powershell
$env:PYTHONPATH="src"
python -m pytest -q
python -m dataorchestra.cli preflight --client-dir clients/cliente_001
```

El preflight guarda `diagnostics/preflight/preflight_report.json` con el resultado de privacidad, validacion y fingerprints SHA-256 de los CSV recibidos en `raw/`. Tambien registra un evento en `logs/audit.jsonl`.

Para operar mas de un cliente, crear una carpeta separada con `init-client`. No reutilizar `cliente_001` para clientes distintos. Ver `docs/OPERACION_MULTI_CLIENTE.md`.

El comando `status` muestra el estado operativo del cliente, archivos faltantes, preflight, analisis, aprobacion y proxima accion recomendada.

El comando `full-run` ejecuta `preflight` y, solo si esta listo, ejecuta `analyze`. No aprueba ni entrega informes; la aprobacion humana sigue siendo separada y obligatoria.

El analisis solo corre si el preflight quedo en `ready_for_analysis` y si los fingerprints actuales de `raw/` coinciden con los aprobados. Genera metricas, alertas, recomendaciones y borradores en:

- `reports/diagnostico_borrador.json`
- `reports/diagnostico_borrador.md`

El borrador Markdown es interno, incluye evidencia y conserva `report_status: pending_human_review`. No habilita entrega automatica.

La aprobacion humana se registra con `approve`. Solo crea artefactos aprobados si existen borradores de analisis, si se informa un revisor, si hay notas y si se usa `--confirm-human-review`. Las salidas aprobadas son:

- `reports/diagnostico_aprobado.json`
- `reports/diagnostico_aprobado.md`
- `reports/diagnostico_aprobado.html`
- `diagnostics/review/approval_record.json`

El HTML aprobado esta preparado para abrir en navegador e imprimir o guardar como PDF. Ver `docs/GUIA_EXPORTAR_INFORME_PDF.md`.

Tambien se puede generar PDF automaticamente con `export-pdf`, usando Microsoft Edge, Google Chrome o un navegador Chromium compatible instalado localmente.

El estado aprobado es `approved_for_delivery`. La entrega al cliente sigue siendo una accion operativa separada.

Cada preflight, analisis y aprobacion genera un `run_id` y conserva copias historicas en `clients/<cliente>/runs/<run_id>/`. Los archivos actuales siguen quedando en `diagnostics/` y `reports/`.

## Web institucional

La landing institucional esta integrada en `dataorchestra-web/`.

```powershell
cd dataorchestra-web
cmd /c npm.cmd install
cmd /c npm.cmd run dev
```

Build de produccion:

```powershell
cmd /c npm.cmd run build
```

La web comunica el estado real del proyecto: servicio supervisado para diagnostico comercial de PyMEs, no SaaS ni plataforma autoservicio.

Paginas incluidas:

- `/` landing institucional.
- `/servicio` alcance del diagnostico.
- `/privacidad` criterios de datos anonimizados y controles.
- `/demo` caso ficticio de referencia.

## Panel interno local

El panel interno local esta en `tools/internal_panel.py`.

```powershell
python -m pip install -e .[panel]
$env:PYTHONPATH="src"
python -m streamlit run tools/internal_panel.py
```

Ver `docs/PANEL_INTERNO_LOCAL.md`.

## Estado actual documentado

La foto actual de estructura, alcance, validaciones y siguientes pasos esta en `docs/ESTADO_ACTUAL_v2_0.md`.

## Estado del piloto

El estado inicial de `clients/cliente_001/client.yaml` es `intake_pending`.

Estados permitidos:

- `intake_pending`
- `privacy_review_required`
- `data_fix_required`
- `ready_for_analysis`
- `analysis_done`
- `pending_human_review`
- `approved_for_delivery`
- `delivered`
- `pilot_closed`

## Siguiente paso

Usar las plantillas de `templates/` para pedir datos anonimizados al primer cliente. Antes de procesar, ejecutar el preflight y completar los checklists.

Para preparar la conversacion comercial y la admision, usar:

- `docs/PAQUETE_COMERCIAL_PILOTO.md`
- `templates/aceptacion_piloto_controlado.md`
- `templates/checklist_recepcion_datos_cliente.md`

Para practicar el flujo sin datos reales, ejecutar el caso ficticio `demos/retail_santa_clara`. Ver `docs/CASO_DEMO_FICTICIO.md`.
