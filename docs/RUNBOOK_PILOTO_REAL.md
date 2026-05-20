# Runbook - Primer piloto real controlado

## 1. Admision

Completar `checklists/01_admision_cliente.md`. Si el cliente no acepta alcance limitado, privacidad y revision humana, no iniciar.

Antes de recibir datos, completar o adaptar:

- `templates/aceptacion_piloto_controlado.md`
- `templates/checklist_recepcion_datos_cliente.md`
- `templates/checklist_seguridad_pre_cliente_real.md`

Para cliente real, crear o usar runtime externo:

```powershell
$env:PYTHONPATH="src"
python -m dataorchestra.cli prepare-runtime --runtime-dir "C:\Documentos\DataOrchestra_Runtime"
```

No guardar datos reales dentro del repositorio.

## 2. Recepcion de datos

Para un cliente nuevo, crear primero su espacio operativo:

```powershell
$env:PYTHONPATH="src"
python -m dataorchestra.cli init-client --client-id cliente_002 --display-name "Cliente piloto 002"
```

Enviar las plantillas de `templates/`. El cliente debe devolver:

- `ventas.csv`
- `productos.csv`
- `stock.csv`

Los archivos se colocan en `clients/cliente_001/raw/`. No editar esos archivos.

Si se esta operando otro cliente, reemplazar `cliente_001` por el identificador creado con `init-client`.

## 3. Preflight

Consultar estado antes de ejecutar:

```powershell
$env:PYTHONPATH="src"
python -m dataorchestra.cli status --client-dir clients/cliente_001
```

Ejecutar readiness tecnico antes de avanzar:

```powershell
python -m dataorchestra.cli readiness --client-dir clients/cliente_001
```

Si `can_continue` es `false`, resolver bloqueos antes de ejecutar analisis, aprobacion o entrega.

Ejecutar:

```powershell
$env:PYTHONPATH="src"
python -m dataorchestra.cli preflight --client-dir clients/cliente_001
```

Si el paquete fue instalado en modo editable, se puede usar:

```powershell
dataorchestra preflight --client-dir clients/cliente_001
```

Si el estado es `privacy_review_required`, detener. Si el estado es `data_fix_required`, pedir correccion de archivos. Solo continuar con `ready_for_analysis`.

El reporte generado debe conservar los fingerprints SHA-256 de cada CSV recibido. Estos hashes sirven para demostrar que el analisis se hizo sobre los archivos originales recibidos en `raw/`.

Cada ejecucion queda identificada con `run_id` y se archiva en `clients/<cliente>/runs/<run_id>/preflight/`.

## 4. Analisis

Ejecutar el pipeline analitico cuando exista una entrada validada:

```powershell
dataorchestra analyze --client-dir clients/cliente_001
```

Si se ejecuta sin instalar el paquete:

```powershell
$env:PYTHONPATH="src"
python -m dataorchestra.cli analyze --client-dir clients/cliente_001
```

El analisis se bloquea si falta el preflight, si el preflight no esta en `ready_for_analysis` o si los CSV de `raw/` cambiaron despues del preflight aprobado.

Para ejecutar preflight y analisis en una sola accion controlada:

```powershell
$env:PYTHONPATH="src"
python -m dataorchestra.cli full-run --client-dir clients/cliente_001
```

`full-run` no aprueba informes ni reemplaza la revision humana.

Todo resultado debe quedar en `diagnostics/` o `reports/`. Los borradores generados quedan en:

- `reports/diagnostico_borrador.json`
- `reports/diagnostico_borrador.md`

El Markdown es el borrador ejecutivo legible para revision interna. No habilita entrega automatica.

## 5. Revision humana

Completar `checklists/04_revision_humana.md`. El informe debe permanecer como `pending_human_review` hasta aprobacion explicita.

Si la revision humana aprueba el borrador, registrar la aprobacion:

```powershell
dataorchestra approve --client-dir clients/cliente_001 --reviewer "Nombre responsable" --notes "Revision humana completada" --confirm-human-review
```

El comando crea `diagnostics/review/approval_record.json`, `reports/diagnostico_aprobado.json` y `reports/diagnostico_aprobado.md`. Si falta confirmacion humana, revisor, notas o analisis previo, la aprobacion se bloquea.

La aprobacion se archiva en `clients/<cliente>/runs/<run_id>/approval/`, usando el `run_id` del analisis aprobado.

## 6. Entrega controlada

Entregar solo `reports/diagnostico_aprobado.md` o una version revisada manualmente a partir de ese archivo. No entregar `diagnostico_borrador.*` ni archivos `raw/`.

Para una entrega mas ejecutiva, abrir `reports/diagnostico_aprobado.html` y exportar a PDF desde el navegador. Ver `docs/GUIA_EXPORTAR_INFORME_PDF.md`.

Tambien se puede generar PDF automaticamente:

```powershell
$env:PYTHONPATH="src"
python -m dataorchestra.cli export-pdf --client-dir clients/cliente_001
```

El comando se bloquea si no existe informe aprobado.

## 7. Cierre

Registrar feedback del cliente, tiempos, errores, objeciones, utilidad percibida y decision de continuidad.

Cerrar el piloto:

```powershell
python -m dataorchestra.cli close-pilot --client-dir clients/cliente_001 --reviewer "Nombre responsable" --notes "Cierre registrado" --outcome completed --confirm-close
```

Despues del cierre, revisar retencion o borrado segun `docs/POLITICA_DATOS_REALES.md`.
