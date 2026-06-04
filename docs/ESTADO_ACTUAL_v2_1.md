# Estado actual - DataOrchestra AI v2.1

DataOrchestra AI v2.1 es la version integradora canonica para operar el primer piloto real controlado.

## Carpeta canonica

```text
C:\Documentos\Aplicacion DATA ORCHESTRA\DataOrchestra_AI_v2_1_integrado
```

## Alcance real

Servicio supervisado de diagnostico comercial para PyMEs con datos anonimizados, revision humana y entrega controlada.

No es SaaS, plataforma autoservicio ni producto final escalable.

## Cambios frente a v2.0

- Unifica backend, web, docs, contratos, demos, tests y kits en una sola carpeta.
- Corrige `clients/cliente_001` para que coincida con `init-client`.
- Agrega registro operativo de entrega con `mark-delivered`.
- Agrega registro de retencion o borrado manual con `record-retention`.
- Endurece el formulario web: webhook solo HTTPS, timeout, sin credenciales y bloqueo si no hay canal configurado.
- Deja documentado el criterio para publicar esta carpeta como raiz del repo principal.

## Comandos base

```powershell
$env:PYTHONPATH="src"
python -m pytest -q
python -m dataorchestra.cli status --client-dir clients/cliente_001
python -m dataorchestra.cli readiness --client-dir clients/cliente_001 --repo-root .
```

## Flujo operativo

```powershell
python -m dataorchestra.cli preflight --client-dir <cliente>
python -m dataorchestra.cli data-quality --client-dir <cliente>
python -m dataorchestra.cli analyze --client-dir <cliente>
python -m dataorchestra.cli approve --client-dir <cliente> --reviewer "Responsable" --notes "Revision humana completada" --confirm-human-review
python -m dataorchestra.cli export-pdf --client-dir <cliente>
python -m dataorchestra.cli mark-delivered --client-dir <cliente> --recipient "Responsable cliente" --method email --notes "Informe aprobado enviado" --confirm-delivery
python -m dataorchestra.cli close-pilot --client-dir <cliente> --reviewer "Responsable" --notes "Cierre registrado" --outcome completed --confirm-close
python -m dataorchestra.cli record-retention --client-dir <cliente> --responsible "Responsable" --action raw_deleted --notes "Raw eliminado manualmente segun politica" --confirm-retention-review
```

## Web

```powershell
cd dataorchestra-web
cmd /c npm.cmd ci
cmd /c npm.cmd run build
```

Para publicar en GitHub Pages, ver `docs/PUBLICACION_REPO_PRINCIPAL.md` y `docs/DEPLOY_WEB_GITHUB_PAGES.md`.

## Pendientes antes de escalar

- Revision legal formal de terminos, privacidad y aceptacion del piloto.
- Validacion con 1 o 2 clientes reales de bajo riesgo.
- Definir canal real de contacto: email operativo, CRM o webhook protegido.
- Revisar precios despues de medir esfuerzo real.
