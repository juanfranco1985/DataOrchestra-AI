# DataOrchestra AI v2.1 - Version Integradora

Esta es la carpeta unica de trabajo para DataOrchestra AI.

Integra en una sola base operativa:

- backend Python para piloto controlado;
- CLI `dataorchestra`;
- tests automatizados;
- contratos de datos, plantillas y checklists;
- estructura de clientes;
- demo ficticio;
- panel interno local;
- documentacion operativa y comercial;
- web institucional Next.js;
- workflows de CI y deploy web.

Las carpetas anteriores quedan como archivo historico. Para trabajo nuevo, mantenimiento, pruebas, web, documentacion o pilotos, usar esta carpeta.

## Fuente canonica

```text
C:\Documentos\Aplicacion DATA ORCHESTRA\DataOrchestra_AI_v2_1_integrado
```

No usar como base de trabajo diario:

- `dataorchestra-web/`
- carpetas historicas de consolidacion o auditoria;
- `__audit_extract/`

## Estado del producto

DataOrchestra AI no esta definido como SaaS ni plataforma autoservicio. La definicion operativa vigente es:

```text
Servicio supervisado de diagnostico comercial para PyMEs con datos anonimizados, revision humana y entrega controlada.
```

Reglas duras:

- no usar datos personales reales;
- no modificar archivos `raw/`;
- no mezclar datos demo con datos de clientes;
- no entregar informes sin revision humana;
- bloquear el flujo ante dudas de privacidad;
- respaldar recomendaciones con metricas, alertas o evidencia registrada.

## Estructura principal

```text
DataOrchestra_AI_v2_1_integrado/
  src/dataorchestra/        Backend y CLI
  tests/                    Tests automatizados
  clients/cliente_001/      Estructura vacia para piloto
  templates/                Plantillas CSV y aceptacion
  contracts/                Contratos versionados de datos
  checklists/               Controles operativos
  docs/                     Documentacion tecnica, operativa y comercial
  exports/                  Kit comercial y manual operativo
  demos/                    Caso ficticio de prueba
  tools/                    Panel interno local
  dataorchestra-web/        Web institucional Next.js
  .github/workflows/        CI y deploy web
```

## Backend

Desde esta carpeta:

```powershell
$env:PYTHONPATH="src"
python -m pytest -q
python -m dataorchestra.cli --help
python -m dataorchestra.cli status --client-dir clients/cliente_001
python -m dataorchestra.cli readiness --client-dir clients/cliente_001
python -m dataorchestra.cli preflight --client-dir clients/cliente_001
```

Instalacion editable opcional:

```powershell
python -m pip install -e .
dataorchestra --help
```

## Flujo de piloto

1. Crear o preparar carpeta de cliente con `init-client`.
2. Cargar `ventas.csv`, `productos.csv` y `stock.csv` anonimizados en `raw/`.
3. Ejecutar `readiness`, `preflight`, `data-quality` y `analyze`.
4. Revisar el borrador internamente.
5. Aprobar con `approve` solo si hubo revision humana.
6. Exportar PDF si corresponde con `export-pdf`.
7. Registrar entrega con `mark-delivered`.
8. Cerrar el piloto con `close-pilot`.
9. Registrar retencion o borrado manual con `record-retention`.

Para datos reales, usar runtime externo al repo. Ver `docs/RUNTIME_SEGURO_DATOS_REALES.md`.

## Web institucional

La web vigente esta integrada en:

```text
dataorchestra-web/
```

Comandos:

```powershell
cd dataorchestra-web
cmd /c npm.cmd install
cmd /c npm.cmd run dev
cmd /c npm.cmd run build
```

Paginas incluidas:

- `/`
- `/servicio`
- `/privacidad`
- `/terminos-privacidad`
- `/demo`
- `/faq`

El formulario opera con webhook/CRM configurable o fallback por email. Ver `docs/FORMULARIO_CONTACTO_CONTROLADO.md`.

## Documentos de entrada

- `MANIFEST_v2_1_integrado.json`
- `CONTINUIDAD_CODEX.md`
- `docs/ESTADO_ACTUAL_v2_1.md`
- `docs/PUBLICACION_REPO_PRINCIPAL.md`
- `docs/RUNBOOK_PILOTO_REAL.md`
- `docs/READINESS_TECNICO_PILOTO.md`
- `docs/PROPUESTA_COMERCIAL_PILOTO.md`
- `exports/kit_comercial_dataorchestra/README.md`
- `exports/manual_operativo_dataorchestra/README.md`

## Siguiente paso recomendado

Usar esta version integrada para el primer piloto real controlado. Antes de agregar funcionalidad nueva, validar el flujo con 1 o 2 comercios reales de bajo riesgo y registrar objeciones, fricciones y formatos de datos reales.
